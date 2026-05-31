"""Schema access API for OmegaWiki.

Hand-written, fully data-driven loader.  Reads runtime/schema/*.yaml at import
time and exposes:

  - raw YAML:        ENTITIES, EDGES, XREF, CONVENTIONS, WRITERS, PIPELINE
  - derived dicts:   ENTITY_DIRS, REQUIRED_FIELDS, VALID_VALUES, FIELD_DEFAULTS,
                     EDGE_TYPE_SPECS
  - derived sets:    PAPER_PAPER_EDGE_TYPES, PAPER_CONCEPT_EDGE_TYPES,
                     SYMMETRIC_EDGE_TYPES, CONFIDENCE_REQUIRED_EDGE_TYPES,
                     VALID_EDGE_TYPES
  - static enums:    EDGE_CONFIDENCE_VALUES, CITATION_EDGE_TYPES, CITATION_SOURCES
  - legacy sets:     LEGACY_EDGE_TYPES, LEGACY_PAPER_PAPER_EDGE_TYPES,
                     LEGACY_PAPER_CONCEPT_EDGE_TYPES
  - helpers:         edge_types_matching, edge_type_spec, edge_is_symmetric,
                     edge_requires_confidence, edge_expected_endpoint,
                     edge_endpoint_matches, edge_is_legacy_for_endpoint,
                     edge_legacy_replacement_message
  - pipeline:        PIPELINE + pipeline_required_fields, pipeline_field_enums,
                     pipeline_stage_log_lines, pipeline_stage_log_states,
                     pipeline_current_stage_map

All derivations are dict comprehensions over ENTITIES / EDGES — adding a new
entity or edge to YAML automatically propagates without any code change here.
"""

from __future__ import annotations

from pathlib import Path
import yaml

# ── Raw YAML ────────────────────────────────────────────────────────────────

_SCHEMA = Path(__file__).resolve().parent / 'schema'
_POLICY = Path(__file__).resolve().parent / 'policy'

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding='utf-8'))

ENTITIES    = _load(_SCHEMA / 'entities.yaml')
EDGES       = _load(_SCHEMA / 'edges.yaml')
XREF        = _load(_SCHEMA / 'xref.yaml')
CONVENTIONS = _load(_SCHEMA / 'conventions.yaml')
WRITERS     = _load(_POLICY / 'writers.yaml')
PIPELINE    = _load(_SCHEMA / 'pipeline.yaml')

# ── Static / wildcard constants ─────────────────────────────────────────────

ANY_ENDPOINT        = "*"
DIRECTION_DIRECTED  = "directed"
DIRECTION_SYMMETRIC = "symmetric"
CONFIDENCE_REQUIRED = "required"
CONFIDENCE_NONE     = "none"

EDGE_CONFIDENCE_VALUES = {"high", "medium", "low"}
CITATION_EDGE_TYPES    = {"cites"}
CITATION_SOURCES       = set(EDGES['cites']['attributes']['source']['values'])

# Legacy edge types kept for /lint backwards-compat reports.
LEGACY_EDGE_TYPES = {"extends", "supersedes"}
LEGACY_PAPER_PAPER_EDGE_TYPES   = LEGACY_EDGE_TYPES | {"inspired_by", "contradicts", "supports"}
LEGACY_PAPER_CONCEPT_EDGE_TYPES = {"supports", "extends"}

# ── Derived constants (data-driven dict comprehensions) ─────────────────────

ENTITY_DIRS = list(ENTITIES.keys())

REQUIRED_FIELDS = {
    kind: [n for n, f in e['fields'].items() if f.get('required')]
    for kind, e in ENTITIES.items()
}

# Valid enum/range values per "{entity}.{field}".  Kept as string sets to match
# the historical /lint contract (importance "1".."5", outcome includes "").
def _valid_values_for(kind: str, fname: str, fspec: dict) -> set[str] | None:
    if fspec.get('type') == 'enum':
        vals = {str(v) for v in fspec['values']}
        if kind == 'experiments' and fname == 'outcome':
            vals.add('')
        return vals
    if fspec.get('type') == 'int' and 'range' in fspec:
        lo, hi = fspec['range']
        return {str(i) for i in range(int(lo), int(hi) + 1)}
    return None

def _build_valid_values() -> dict[str, set[str]]:
    out = {}
    for kind, e in ENTITIES.items():
        for fname, fspec in e['fields'].items():
            v = _valid_values_for(kind, fname, fspec)
            if v is not None:
                out[f"{kind}.{fname}"] = v
    return out

VALID_VALUES = _build_valid_values()

def _fmt_default(v):
    if isinstance(v, list) and not v:
        return '[]'
    return str(v)

def _build_field_defaults() -> dict[str, dict[str, str]]:
    out = {}
    for kind, e in ENTITIES.items():
        d = {n: _fmt_default(f['default'])
             for n, f in e['fields'].items()
             if f.get('required') and 'default' in f}
        if d:
            out[kind] = d
    return out

FIELD_DEFAULTS = _build_field_defaults()

# Edge specs (the cites edge is excluded — it has its own CITATION_* registry).
EDGE_TYPE_SPECS: dict[str, dict[str, str]] = {
    et: {
        'from_kind':  e['endpoints']['from'],
        'to_kind':    e['endpoints']['to'],
        'direction':  e['direction'],
        'confidence': (CONFIDENCE_REQUIRED
                       if e.get('attributes', {}).get('confidence', {}).get('required')
                       else CONFIDENCE_NONE),
        'workflow':   e['workflow'],
    }
    for et, e in EDGES.items()
    if et != 'cites'
}

# ── Helper functions (operate on EDGE_TYPE_SPECS) ───────────────────────────

def _spec_matches(spec: dict, key: str, value):
    return value is None or spec.get(key) == value


def edge_types_matching(*, from_kind=None, to_kind=None, direction=None,
                        confidence=None, workflow=None) -> set[str]:
    """Return edge types whose registry metadata matches all provided filters."""
    return {
        et for et, spec in EDGE_TYPE_SPECS.items()
        if _spec_matches(spec, 'from_kind',  from_kind)
        and _spec_matches(spec, 'to_kind',    to_kind)
        and _spec_matches(spec, 'direction',  direction)
        and _spec_matches(spec, 'confidence', confidence)
        and _spec_matches(spec, 'workflow',   workflow)
    }


def edge_type_spec(edge_type: str):
    return EDGE_TYPE_SPECS.get(edge_type)


def edge_is_symmetric(edge_type: str) -> bool:
    spec = edge_type_spec(edge_type)
    return bool(spec and spec.get('direction') == DIRECTION_SYMMETRIC)


def edge_requires_confidence(edge_type: str) -> bool:
    spec = edge_type_spec(edge_type)
    return bool(spec and spec.get('confidence') == CONFIDENCE_REQUIRED)


def edge_expected_endpoint(edge_type: str, endpoint: str) -> str:
    spec = edge_type_spec(edge_type)
    if not spec:
        return ANY_ENDPOINT
    return spec.get(f'{endpoint}_kind', ANY_ENDPOINT)


def edge_endpoint_matches(edge_type: str, from_kind: str, to_kind: str) -> bool:
    spec = edge_type_spec(edge_type)
    if not spec:
        return True
    expected_from = spec.get('from_kind', ANY_ENDPOINT)
    expected_to   = spec.get('to_kind',   ANY_ENDPOINT)
    return ((expected_from == ANY_ENDPOINT or expected_from == from_kind)
            and (expected_to == ANY_ENDPOINT or expected_to == to_kind))


def edge_is_legacy_for_endpoint(edge_type: str, from_kind: str, to_kind: str) -> bool:
    if from_kind == 'papers' and to_kind == 'papers':
        return edge_type in LEGACY_PAPER_PAPER_EDGE_TYPES
    if from_kind == 'papers' and to_kind == 'concepts':
        return edge_type in LEGACY_PAPER_CONCEPT_EDGE_TYPES
    return False


def edge_legacy_replacement_message(edge_type: str, from_kind: str, to_kind: str) -> str:
    if from_kind == 'papers' and to_kind == 'papers':
        return f"Legacy paper-paper edge {edge_type!r}; use the new paper relation types"
    if from_kind == 'papers' and to_kind == 'concepts':
        return (f"Legacy paper-concept edge {edge_type!r}; use introduces_concept, "
                "uses_concept, extends_concept, or critiques_concept")
    return f"Legacy edge {edge_type!r}"


# ── Derived sets used by call sites ─────────────────────────────────────────

PAPER_PAPER_EDGE_TYPES         = edge_types_matching(from_kind='papers', to_kind='papers',  workflow='ingest')
PAPER_CONCEPT_EDGE_TYPES       = edge_types_matching(from_kind='papers', to_kind='concepts', workflow='ingest')
SYMMETRIC_EDGE_TYPES           = edge_types_matching(direction=DIRECTION_SYMMETRIC)
CONFIDENCE_REQUIRED_EDGE_TYPES = edge_types_matching(confidence=CONFIDENCE_REQUIRED)
VALID_EDGE_TYPES               = set(EDGE_TYPE_SPECS) | LEGACY_EDGE_TYPES


# ── Generic edge-attribute validator (used by lint + research_wiki) ─────────

def validate_edge_attributes(edge_type: str, attrs: dict) -> list[str]:
    """Validate a dict of edge attributes against edges.yaml::attributes spec.
    Returns a list of error messages (empty if valid)."""
    errors = []
    spec = EDGES.get(edge_type, {}).get('attributes', {})
    for attr_name, attr_spec in spec.items():
        value = attrs.get(attr_name)
        if attr_spec.get('required') and not value:
            errors.append(f"{edge_type} requires --{attr_name}")
            continue
        if value is None:
            continue
        if attr_spec.get('type') == 'enum':
            if value not in attr_spec['values']:
                errors.append(
                    f"{edge_type}.{attr_name}={value!r} not in {attr_spec['values']}"
                )
    return errors


# ── Lifecycle transition validator ──────────────────────────────────────────

def validate_lifecycle_transition(kind: str, from_state: str, to_state: str) -> str | None:
    """Return None if transition is legal, an error message otherwise.
    Returns None if the entity has no lifecycle declared (no validation)."""
    transitions = ENTITIES.get(kind, {}).get('lifecycle', {}).get('transitions', {})
    if not transitions:
        return None
    if from_state == to_state:
        return None
    legal = transitions.get(from_state, [])
    if to_state not in legal:
        return (f"{kind}: illegal transition {from_state!r} → {to_state!r}; "
                f"legal from {from_state!r}: {legal}")
    return None


# ── Pipeline-progress schema accessors ──────────────────────────────────────

def pipeline_required_fields() -> list[str]:
    return list(PIPELINE['frontmatter']['required'])


def pipeline_field_enums() -> dict[str, set[str]]:
    out = {}
    for fname, fspec in PIPELINE['frontmatter']['fields'].items():
        if fspec.get('type') == 'enum':
            out[fname] = {str(v) for v in fspec['values']}
    return out


def pipeline_stage_log_lines() -> list[dict]:
    return [dict(line) for line in PIPELINE['stage_log']['lines']]


def pipeline_stage_log_states() -> set[str]:
    return set(PIPELINE['stage_log']['line_states'])


def pipeline_current_stage_map() -> dict[str, list[str]]:
    return {k: list(v) for k, v in PIPELINE['current_stage_map'].items()}


# ── Pipeline-progress validator (pure logic; entity_status injected by tools) ─


def _pipeline_norm_slug(value) -> str:
    s = str(value).strip().strip('"').strip("'")
    while s.startswith('[') and s.endswith(']'):
        s = s[1:-1].strip()
    return s


def _pipeline_slug_list(value) -> list[str]:
    if not value:
        return []
    items = value if isinstance(value, list) else [value]
    return [_pipeline_norm_slug(x) for x in items if str(x).strip()]


def validate_pipeline(frontmatter: dict, stage_log: dict, *, entity_status=None) -> list[tuple[str, str]]:
    """Validate a parsed pipeline-progress snapshot. Pure logic, no I/O.
    `entity_status` is an optional callable (kind, slug) -> status|None used for
    cross-entity rules (R4); when None those rules are skipped. Returns a list of
    (severity, message) tuples; severity in {"BLOCK","WARN"}; empty == valid."""
    fm = frontmatter or {}
    log = stage_log or {}
    issues: list[tuple[str, str]] = []
    B, W = "BLOCK", "WARN"

    # R1: required fields
    for f in pipeline_required_fields():
        if f not in fm or fm.get(f) in (None, ""):
            issues.append((B, f"missing required frontmatter field {f!r}"))

    # R1: frontmatter enums
    for fname, allowed in pipeline_field_enums().items():
        if fname in fm and fm[fname] is not None and str(fm[fname]) not in allowed:
            issues.append((B, f"{fname}={fm[fname]!r} not in {sorted(allowed)}"))

    # stage-log key set + state validity
    lines = pipeline_stage_log_lines()
    keys = [l["key"] for l in lines]
    order = {k: i for i, k in enumerate(keys)}
    valid_states = pipeline_stage_log_states()
    for k, st in log.items():
        if k not in order:
            issues.append((B, f"unknown stage-log line {k!r}"))
        elif st not in valid_states:
            issues.append((B, f"stage-log {k} state {st!r} not in {sorted(valid_states)}"))

    def state_of(k):
        return log.get(k)

    # R2: a still-pending stage must not be followed by any already-completed stage
    completed_orders = [order[k] for k in keys if state_of(k) == "completed"]
    last_completed = max(completed_orders) if completed_orders else -1
    for k in keys:
        if state_of(k) == "pending" and order[k] < last_completed:
            issues.append((B, f"stage-log {k} is still pending but a later stage is already completed"))

    # R3: current_stage <-> stage-log coherence
    cmap = pipeline_current_stage_map()
    cur = str(fm.get("current_stage")) if fm.get("current_stage") is not None else ""
    if cur in cmap:
        cur_keys = set(cmap[cur])
        cur_idx = min(order[k] for k in cur_keys)
        for k in keys:
            if k in cur_keys:
                continue
            st = state_of(k)
            if order[k] < cur_idx:
                if st not in ("completed", "skipped"):
                    issues.append((B, f"current_stage={cur} but earlier stage-log {k} is {st!r} (expected completed/skipped)"))
            else:
                if st not in ("pending", None):
                    issues.append((B, f"current_stage={cur} but later stage-log {k} is {st!r} (expected pending)"))

    # R4a (no entity lookup needed): stage5 completed => status completed
    if state_of("stage5") == "completed" and str(fm.get("status")) != "completed":
        issues.append((B, f"stage5 is completed but status is {fm.get('status')!r} (expected completed)"))

    # R4b: cross-entity existence + lifecycle (needs entity_status)
    if entity_status is not None:
        idea = _pipeline_norm_slug(fm.get("idea_slug") or "")
        exps = _pipeline_slug_list(fm.get("experiment_slugs"))
        linked = _pipeline_slug_list(fm.get("linked_idea_slugs"))

        if idea and entity_status("ideas", idea) is None:
            issues.append((B, f"idea_slug {idea!r} does not resolve to an existing idea page"))
        for e in exps:
            if entity_status("experiments", e) is None:
                issues.append((B, f"experiment_slug {e!r} does not resolve to an existing experiment page"))
        for lnk in linked:
            if entity_status("ideas", lnk) is None:
                issues.append((B, f"linked_idea_slug {lnk!r} does not resolve to an existing idea page"))

        at_verdict = cur in ("stage4", "stage5") or state_of("stage4") == "completed"
        at_label = cur if cur in ("stage4", "stage5") else "stage4-or-later"
        if at_verdict:
            for e in exps:
                st = entity_status("experiments", e)
                if st is not None and st not in ("completed", "abandoned"):
                    issues.append((B, f"at {at_label}, experiment {e!r} status is {st!r} (expected completed/abandoned)"))
            if idea:
                ist = entity_status("ideas", idea)
                if ist is not None and ist not in ("tested", "validated", "failed"):
                    issues.append((B, f"at {at_label}, idea {idea!r} status is {ist!r} (expected tested/validated/failed)"))

    # R5 (soft): running but every non-skippable stage already completed
    non_skippable = [l["key"] for l in lines if not l.get("skippable")]
    if str(fm.get("status")) == "running" and non_skippable and all(state_of(k) == "completed" for k in non_skippable):
        issues.append((W, "status is running but all non-skippable stages are completed (stale snapshot?)"))

    return issues
