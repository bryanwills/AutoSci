# AutoSci Schema Modification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phases A–C of `newIdea.md` — expand the long-term knowledge schema (topic neighborhood, foundation grounding, paper↔method & paper→foundation typed edges, concept↔concept edges, people contributions, Summary removal, `parent_topic`→`parent_topics`), add the active-research `manuscripts`/`reviews` entities, and create the non-wiki `research_methodology/` scaffold — keeping the whole system loadable, lintable, and renderable.

**Architecture:** The wiki contract is data-driven YAML in `runtime/schema/*.yaml`, read by `runtime/loader.py` and consumed by `tools/{lint,research_wiki,serve,visualize}.py`. The SPA frontend (`app/modules/*.js`) consumes `/api/graph` schema metadata with local fallbacks; `config/visualize.json` is the authoritative color/category config. Most changes are YAML + template + config + UI-metadata; a few hardcoded Python/JS spots (entity lists, enum validation, color maps) need surgical edits. `wiki/` is an empty scaffold, so no data migration is needed.

**Tech Stack:** Python 3.12 (PyYAML), vanilla ES-module JS, JSON config. No test framework — verification is via `py_compile`, `node --check`, JSON parse, and `lint.py --json` runs plus small smoke fixtures.

---

## Decisions & Spec Reconciliations (read first)

The spec (`newIdea.md`) contradicts itself twice; resolved as below. These bind the tasks.

1. **Paper→Foundation = edge, not field.** §3.2 lists a frontmatter field `papers.contributes_to_foundations`; §3.4 defines a typed edge `contributes_to_foundation`. Per §1.2 (evidence-bearing relations ⇒ edges) and example §11.1, implement the **edge only**; do *not* add the frontmatter field. Foundation reverse `## Contributed by papers` is populated from the edge.
2. **Topics template gains `## Subtopics` + `## Related topics`.** §3.1's template listing omits them, but the MUST xref rules `topics.parent_topics → topics ## Subtopics` and `topics.related_topics → topics ## Related topics` require them. Add both sections (§9.2 name-consistency).

Additional binding choices:
- `concepts.grounded_in` / `methods.grounded_in` = frontmatter `list_link`; reverse → foundations body `## Grounds concepts` / `## Grounds methods`.
- Paper↔Method reverse uses three sections `## Proposed by` / `## Applied by` / `## Extended by` (the xref fixer writes only the source slug, so one shared section would lose the relation type).
- Concept↔Concept edges are **symmetric** → no body reverse (graph canonicalizes both directions). Deferred to Phase B per §3.5.
- `uses_foundation` edge, People→* typed edges, and `papers.contributes_to_foundations` field are **DEFER** (not implemented).
- **Skill docs (`.claude/skills/*`, `i18n/*`) are NOT touched** — the working tree has an unrelated uncommitted EN→ZH language switch the user does not want committed, and the spec frames skill-workflow edits as Phase D. The schema supports the new relations now; SKILL.md prompt updates come later.
- Foundations stops being terminal: remove `terminal: true` (entities.yaml) and drop `foundations` from `terminal_targets` (xref.yaml) so its reverse sections are checked/repaired.

Commit policy: only `git add` the files this plan changes. Never stage the pre-existing `.claude/skills/*`, `CLAUDE.md`, or deleted `README.md` changes. Do not commit unless the user asks.

---

## File Structure Map

**Schema/contract (YAML):**
- `runtime/schema/entities.yaml` — add topic/foundation/concept/method/people/paper fields; add `manuscripts`,`reviews`; remove `Summary`; `parent_topic`→`parent_topics`; drop foundations `terminal`.
- `runtime/schema/edges.yaml` — add `proposes_method`,`applies_method`,`extends_method`,`contributes_to_foundation` (A); `shares_mechanism_with`,`shares_assumption_with`,`related_problem_formulation`,`contrasts_with_concept` (B).
- `runtime/schema/xref.yaml` — add parent_topics/grounding/paper-method/paper-foundation/reviews rules; replace parent_topic rule; remove foundations from terminal_targets.
- `runtime/policy/writers.yaml` — rename `concepts.parent_topic`; add manuscript/review fields; add new edges as `[ingest]`.

**Templates:** `runtime/templates/{topics,concepts,methods,foundations}.md.tmpl` (modify), `manuscripts.md.tmpl` + `reviews.md.tmpl` (create), `Summary.md.tmpl` (delete).

**Tools (Python):** `tools/lint.py` (schema-driven enum check), `tools/research_wiki.py` (stats: drop Summary, add manuscripts/reviews), `tools/visualize.py` (CANVAS_COLOR_MAP). `serve.py`/`loader.py`/`reset_wiki.py` need no edits (data-driven) — verify only.

**Frontend (JS):** `app/modules/{schema,graph,reader,dashboard}.js`.

**Config/JSON:** `config/visualize.json`.

**Wiki scaffold:** create `wiki/manuscripts/.gitkeep`, `wiki/reviews/.gitkeep`; delete `wiki/Summary/`; rewrite `wiki/index.md`.

**Non-wiki scaffold:** `research_methodology/*.md` (10 files).

---

## Phase A — Long-Term Schema Minimal Closed Loop

### Task A1: entities.yaml — topic neighborhood + parent_topics + grounding, remove Summary, parent_topic→parent_topics, foundations non-terminal

**Files:**
- Modify: `runtime/schema/entities.yaml`

- [ ] **Step 1: Expand `topics` fields.** Replace the current `topics:` block body's `fields:` with (keep `dir`):

```yaml
topics:
  dir: wiki/topics/
  fields:
    title:          { type: str, required: true }
    tags:           { type: list_str, required: true, default: [] }
    topic_kind:
      type: enum
      values: [domain, subfield, problem, bridge, project_area]
      required: true
      default: subfield
    domains:        { type: list_str, default: [] }
    parent_topics:  { type: list_link, to: topics, default: [] }
    key_venues:     { type: list_str, default: [] }
    related_topics: { type: list_link, to: topics, default: [] }
    key_people:     { type: list_link, to: people, default: [] }
    key_papers:     { type: list_link, to: papers, default: [] }
    key_foundations: { type: list_link, to: foundations, default: [] }
    key_concepts:   { type: list_link, to: concepts, default: [] }
    key_methods:    { type: list_link, to: methods, default: [] }
    linked_ideas:   { type: list_link, to: ideas, default: [] }
```

- [ ] **Step 2: concepts — replace `parent_topic` with `parent_topics`, add `grounded_in`.** In the `concepts:` block change the line `parent_topic: { type: link, to: topics }` to:

```yaml
    parent_topics:    { type: list_link, to: topics, default: [] }
    grounded_in:      { type: list_link, to: foundations, default: [] }
```

- [ ] **Step 3: methods — add `parent_topics` and `grounded_in`.** Under `methods:` `fields:` append:

```yaml
    parent_topics:     { type: list_link, to: topics, default: [] }
    grounded_in:       { type: list_link, to: foundations, default: [] }
```

- [ ] **Step 4: papers — add `parent_topics`.** Under `papers:` `fields:` append:

```yaml
    parent_topics:     { type: list_link, to: topics, default: [] }
```

- [ ] **Step 5: people — add `parent_topics`, `key_papers`, `contributed_methods`, `contributed_foundations`.** Under `people:` `fields:` append (before or after `type:` object — order free):

```yaml
    parent_topics:           { type: list_link, to: topics, default: [] }
    key_papers:              { type: list_link, to: papers, default: [] }
    contributed_methods:     { type: list_link, to: methods, default: [] }
    contributed_foundations: { type: list_link, to: foundations, default: [] }
```

- [ ] **Step 6: foundations — add `parent_topics`, remove `terminal: true`.** Change the `foundations:` block: delete the `terminal: true` line and add under `fields:`:

```yaml
    parent_topics:    { type: list_link, to: topics, default: [] }
```

- [ ] **Step 7: Remove the entire `Summary:` entity block** (lines defining `Summary: dir: wiki/Summary/ ...`).

- [ ] **Step 8: Verify schema loads and Summary is gone.**

Run: `python3 -c "from runtime.loader import ENTITIES, ENTITY_DIRS; assert 'Summary' not in ENTITIES; assert 'parent_topics' in ENTITIES['concepts']['fields']; assert 'parent_topic' not in ENTITIES['concepts']['fields']; assert ENTITIES['topics']['fields']['topic_kind']['type']=='enum'; assert not ENTITIES['foundations'].get('terminal'); print('OK', ENTITY_DIRS)"`
Expected: `OK [...]` with no `Summary`.

- [ ] **Step 9: Confirm nothing else reads entities `terminal`.**

Run: `grep -rn "terminal" tools/ runtime/ app/ | grep -iv terminal_targets`
Expected: only comments / unrelated matches (no code branching on `ENTITIES[...]['terminal']`). If a real consumer exists, leave terminal handling and note it.

---

### Task A2: edges.yaml — Paper↔Method and Paper→Foundation typed edges

**Files:**
- Modify: `runtime/schema/edges.yaml`

- [ ] **Step 1: Append the four directed edges** after the Paper→Concept block (before the workflow-edges section), each with required confidence+evidence (mirrors `introduces_concept`):

```yaml
# -----------------------------------------------------------------------------
# Paper → Method semantic edges  (written by /ingest)
# -----------------------------------------------------------------------------

proposes_method:
  endpoints: { from: papers, to: methods }
  direction: directed
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

applies_method:
  endpoints: { from: papers, to: methods }
  direction: directed
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

extends_method:
  endpoints: { from: papers, to: methods }
  direction: directed
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

# -----------------------------------------------------------------------------
# Paper → Foundation contribution edge  (written by /ingest)
# -----------------------------------------------------------------------------

contributes_to_foundation:
  endpoints: { from: papers, to: foundations }
  direction: directed
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }
```

- [ ] **Step 2: Verify edges load and derive correctly.**

Run: `python3 -c "from runtime.loader import EDGE_TYPE_SPECS, CONFIDENCE_REQUIRED_EDGE_TYPES; [print(e, EDGE_TYPE_SPECS[e]) for e in ['proposes_method','applies_method','extends_method','contributes_to_foundation']]; assert 'proposes_method' in CONFIDENCE_REQUIRED_EDGE_TYPES"`
Expected: prints 4 specs with `from_kind`/`to_kind`/`workflow=ingest`, no error.

---

### Task A3: xref.yaml — parent_topics, grounding, paper-method, paper-foundation rules; foundations non-terminal

**Files:**
- Modify: `runtime/schema/xref.yaml`

- [ ] **Step 1: Replace the `concepts.parent_topic → topics ## Concepts` rule** (the last rule before `terminal_targets`) with the parent_topics membership rules:

```yaml
  # entity.parent_topics ↔ topics.key_<kind>
  - forward: { kind: papers,      frontmatter_field: parent_topics, target: topics }
    reverse: { kind: topics,      frontmatter_field: key_papers,     action: append_slug }
  - forward: { kind: foundations, frontmatter_field: parent_topics, target: topics }
    reverse: { kind: topics,      frontmatter_field: key_foundations, action: append_slug }
  - forward: { kind: concepts,    frontmatter_field: parent_topics, target: topics }
    reverse: { kind: topics,      frontmatter_field: key_concepts,   action: append_slug }
  - forward: { kind: methods,     frontmatter_field: parent_topics, target: topics }
    reverse: { kind: topics,      frontmatter_field: key_methods,    action: append_slug }
  - forward: { kind: people,      frontmatter_field: parent_topics, target: topics }
    reverse: { kind: topics,      frontmatter_field: key_people,     action: append_slug }

  # topics.parent_topics → topics ## Subtopics ; topics.related_topics → topics ## Related topics
  - forward: { kind: topics,      frontmatter_field: parent_topics,  target: topics }
    reverse: { kind: topics,      body_section: "Subtopics",         action: append_slug }
  - forward: { kind: topics,      frontmatter_field: related_topics, target: topics }
    reverse: { kind: topics,      body_section: "Related topics",    action: append_slug }

  # Foundation grounding reverses (foundations is no longer terminal)
  - forward: { kind: concepts,    frontmatter_field: grounded_in,    target: foundations }
    reverse: { kind: foundations, body_section: "Grounds concepts",  action: append_slug }
  - forward: { kind: methods,     frontmatter_field: grounded_in,    target: foundations }
    reverse: { kind: foundations, body_section: "Grounds methods",   action: append_slug }

  # Paper → Method typed edges → method body sections
  - forward: { kind: papers,      edge_type: proposes_method,        target: methods }
    reverse: { kind: methods,     body_section: "Proposed by",       action: append_slug }
  - forward: { kind: papers,      edge_type: applies_method,         target: methods }
    reverse: { kind: methods,     body_section: "Applied by",        action: append_slug }
  - forward: { kind: papers,      edge_type: extends_method,         target: methods }
    reverse: { kind: methods,     body_section: "Extended by",       action: append_slug }

  # Paper → Foundation contribution edge → foundation body section
  - forward: { kind: papers,      edge_type: contributes_to_foundation, target: foundations }
    reverse: { kind: foundations, body_section: "Contributed by papers", action: append_slug }
```

- [ ] **Step 2: Change `terminal_targets`** at the bottom of the file from `terminal_targets: [foundations]` to:

```yaml
terminal_targets: []
```

- [ ] **Step 3: Verify xref loads and references resolve.**

Run: `python3 -c "from runtime.loader import XREF; r=XREF['rules']; ets={x['forward'].get('edge_type') for x in r}; assert {'proposes_method','applies_method','extends_method','contributes_to_foundation'} <= ets; assert XREF['terminal_targets']==[]; print('rules', len(r))"`
Expected: prints rule count, no error.

---

### Task A4: writers.yaml — rename concepts.parent_topic, add new ingest edges

**Files:**
- Modify: `runtime/policy/writers.yaml`

- [ ] **Step 1: Rename the field key.** Change `concepts.parent_topic:` to `concepts.parent_topics:` (keep `{ writers: [ingest, init, edit] }`).

- [ ] **Step 2: Add new edges under `edges:`** after `critiques_concept:` line:

```yaml
  proposes_method:          [ingest]
  applies_method:           [ingest]
  extends_method:           [ingest]
  contributes_to_foundation: [ingest]
```

- [ ] **Step 3: Verify it parses.**

Run: `python3 -c "from runtime.loader import WRITERS; assert 'concepts.parent_topics' in WRITERS['fields']; assert 'concepts.parent_topic' not in WRITERS['fields']; assert WRITERS['edges']['proposes_method']==['ingest']; print('OK')"`
Expected: `OK`.

---

### Task A5: Templates — topics, concepts, methods, foundations

**Files:**
- Modify: `runtime/templates/topics.md.tmpl`
- Modify: `runtime/templates/concepts.md.tmpl`
- Modify: `runtime/templates/methods.md.tmpl`
- Modify: `runtime/templates/foundations.md.tmpl`

- [ ] **Step 1: Rewrite `topics.md.tmpl`** to (preserves Timeline/Seminal works/SOTA tracker/Key benchmarks/Known gaps/Methodological gaps/Concepts; adds spec sections + the two xref-reverse sections Subtopics/Related topics):

```markdown
---
{{ frontmatter }}
---

## Overview

## Timeline

## Scope

## Domain assumptions

## Vocabulary bridge

## Seminal works

## SOTA tracker

## Key benchmarks

## Key papers

## Key concepts

## Key methods

## Foundations

## Subtopics

## Related topics

## Cross-domain mappings

## Open problems

### Known gaps

### Methodological gaps

## Synthesis notes

## Concepts
```

- [ ] **Step 2: `concepts.md.tmpl`** — add `## Foundation grounding` after `## Relationship to foundations`. New body order:

```markdown
---
{{ frontmatter }}
---

## Definition

## Intuition

## Variants

## Comparison

## Known limitations

## Open problems

## Relationship to foundations

## Foundation grounding

## Realized by

## My understanding
```

- [ ] **Step 3: `methods.md.tmpl`** — add `## Foundation grounding`, `## Justification`, and the three Paper-relation reverse sections:

```markdown
---
{{ frontmatter }}
---

## Problem setting

## Mechanism

## Procedure

## Assumptions

## Limitations

## Tradeoff profile

## Foundation grounding

## Justification

## Proposed by

## Applied by

## Extended by

## Evaluated by
```

- [ ] **Step 4: `foundations.md.tmpl`** — add the three reverse sections:

```markdown
---
{{ frontmatter }}
---

## Definition

## Intuition

## Formal notation

## Key variants

## Known limitations

## Open problems

## Relevance to active research

## Grounds concepts

## Grounds methods

## Contributed by papers
```

- [ ] **Step 5: Verify section/xref consistency.**

Run: `python3 - <<'PY'
import re
from runtime.loader import XREF
tmpl = {p: open(f"runtime/templates/{p}.md.tmpl").read() for p in ["topics","concepts","methods","foundations"]}
def has(kind, sect): return re.search(rf"^##\s+{re.escape(sect)}\s*$", tmpl[kind], re.M)
for rule in XREF["rules"]:
    rv = rule["reverse"]
    if "body_section" in rv:
        k = rv["kind"]
        if k in tmpl:
            assert has(k, rv["body_section"]), f"missing ## {rv['body_section']} in {k}"
print("all reverse body_sections present in templates")
PY`
Expected: `all reverse body_sections present in templates`.

---

### Task A6: config/visualize.json — remove Summary, rename parent_topic, add new edge groups

**Files:**
- Modify: `config/visualize.json`

- [ ] **Step 1:** In `entity_colors`, remove the `"Summary": {...}` line.

- [ ] **Step 2:** Replace the whole `edge_category_groups` object with (drops `fm_Summary_key_topics`; `fm_concepts_parent_topic`→`fm_concepts_parent_topics`; adds topic membership, foundation grounding, paper↔method groups):

```json
  "edge_category_groups": {
    "Citations": ["cites"],
    "Paper relations": [
      "same_problem_as", "similar_method_to",
      "builds_on", "challenges"
    ],
    "Paper ↔ Concept": [
      "introduces_concept", "uses_concept",
      "extends_concept", "critiques_concept",
      "fm_concepts_key_papers", "fm_concepts_related_concepts",
      "fm_concepts_linked_ideas", "fm_concepts_parent_topics"
    ],
    "Paper ↔ Method": [
      "proposes_method", "applies_method", "extends_method"
    ],
    "Method genealogy": [
      "fm_methods_source_papers", "fm_methods_parent_methods",
      "fm_methods_child_methods", "fm_methods_realizes_concepts"
    ],
    "Foundation grounding": [
      "fm_concepts_grounded_in", "fm_methods_grounded_in",
      "contributes_to_foundation"
    ],
    "Topic membership": [
      "fm_topics_key_papers", "fm_topics_key_people",
      "fm_topics_key_foundations", "fm_topics_key_concepts",
      "fm_topics_key_methods", "fm_topics_related_topics",
      "fm_topics_parent_topics", "fm_topics_linked_ideas",
      "fm_papers_parent_topics", "fm_foundations_parent_topics",
      "fm_concepts_parent_topics", "fm_methods_parent_topics",
      "fm_people_parent_topics"
    ],
    "People contributions": [
      "fm_people_key_papers", "fm_people_contributed_methods",
      "fm_people_contributed_foundations"
    ],
    "Concept relations": [
      "shares_mechanism_with", "shares_assumption_with",
      "related_problem_formulation", "contrasts_with_concept"
    ],
    "Active research": [
      "fm_reviews_linked_manuscript"
    ],
    "Workflow (ideas / experiments)": [
      "fm_experiments_linked_idea", "fm_experiments_evaluates_methods",
      "fm_ideas_origin_gaps", "fm_ideas_linked_experiments",
      "supports", "contradicts", "tested_by",
      "invalidates", "addresses_gap",
      "derived_from", "inspired_by"
    ]
  },
```

- [ ] **Step 3:** In `entity_colors`, add manuscripts/reviews after `foundations` (Phase C also uses these; adding now keeps one config edit):

```json
    "foundations":  { "hex": "#95A5A6", "rgb": 9807270 },
    "manuscripts":  { "hex": "#9B59B6", "rgb": 10181046 },
    "reviews":      { "hex": "#16A085", "rgb": 1480837 }
```

(Remove the trailing comma issue: ensure `reviews` is the last key in `entity_colors`.)

- [ ] **Step 4: Verify valid JSON.**

Run: `python3 -c "import json; c=json.load(open('config/visualize.json')); assert 'Summary' not in c['entity_colors']; assert 'manuscripts' in c['entity_colors']; assert 'Foundation grounding' in c['edge_category_groups']; print('OK')"`
Expected: `OK`.

---

### Task A7: tools/lint.py — schema-driven enum/range validation

**Files:**
- Modify: `tools/lint.py` (function `check_field_values`, ~lines 242-279)

- [ ] **Step 1: Replace the hardcoded `enum_checks` dict + novelty_score special-case** with a schema-driven loop. Replace the body of `check_field_values` (everything inside the `for slug, fpath in pages.items():` loop, from the `# Check enum fields` comment through the novelty range block) with:

```python
        ent = ENTITIES.get(page_type)
        if not ent:
            continue
        for fname, fspec in ent['fields'].items():
            ftype = fspec.get('type')
            valid_key = f"{page_type}.{fname}"
            val = extract_frontmatter_value(content, fname)
            if val is None or val == "":
                continue
            # enum / int-range fields populate VALID_VALUES at load time
            if valid_key in VALID_VALUES:
                if val not in VALID_VALUES[valid_key]:
                    issues.append(LintIssue("🔴", "invalid-value", rel,
                                            f"{fname}={val!r} not in {VALID_VALUES[valid_key]}"))
            elif ftype == 'int' and 'range' in fspec:
                lo, hi = fspec['range']
                try:
                    n = int(val)
                    if not (lo <= n <= hi):
                        issues.append(LintIssue("🔴", "invalid-value", rel,
                                                f"{fname}={n} out of range [{lo}, {hi}]"))
                except ValueError:
                    issues.append(LintIssue("🔴", "invalid-value", rel,
                                            f"{fname}={val!r} is not an integer"))
```

Note: `VALID_VALUES` already covers both enums and int-range fields (loader `_valid_values_for`), so the int-range `elif` only triggers for ranges loader didn't pre-expand — harmless. Ensure `ENTITIES` is imported (it is, line ~37).

- [ ] **Step 2: Verify it compiles and validates new + old enums.**

Run: `python3 -m py_compile tools/lint.py && python3 -c "
from runtime.loader import VALID_VALUES
assert 'topics.topic_kind' in VALID_VALUES
assert 'manuscripts.status' in VALID_VALUES  # after Phase C; ok if KeyError now
print('enum keys present')" 2>/dev/null || echo "topic_kind present (manuscripts added in Phase C)"`
Expected: compiles; topic_kind present.

---

### Task A8: tools/visualize.py — CANVAS_COLOR_MAP

**Files:**
- Modify: `tools/visualize.py` (CANVAS_COLOR_MAP, ~lines 46-56)

- [ ] **Step 1:** In `CANVAS_COLOR_MAP`, remove the `"Summary": "5",` line and add `"manuscripts": "6",` and `"reviews": "2",` entries.

- [ ] **Step 2: Verify compiles.**

Run: `python3 -m py_compile tools/visualize.py && python3 -c "import importlib.util,sys; print('OK')"`
Expected: `OK`.

---

### Task A9: Frontend — schema.js, graph.js (entity lists, edge groups; Summary removal)

**Files:**
- Modify: `app/modules/schema.js`
- Modify: `app/modules/graph.js`

- [ ] **Step 1: `schema.js` ENTITY_DIRS** — remove `"Summary"`, add `"manuscripts", "reviews"`:

```javascript
export const ENTITY_DIRS = Object.freeze([
  "papers", "concepts", "topics", "people",
  "ideas", "experiments", "methods", "foundations",
  "manuscripts", "reviews",
]);
```

- [ ] **Step 2: `schema.js` TYPE_PRECEDENCE** — remove `"Summary"`, append new kinds:

```javascript
export const TYPE_PRECEDENCE = Object.freeze([
  "papers", "concepts", "topics", "methods", "people",
  "ideas", "experiments", "foundations", "manuscripts", "reviews",
]);
```

- [ ] **Step 3: `schema.js` ENTITY_LABEL** — remove `Summary:`, add:

```javascript
  foundations: "Foundations",
  manuscripts: "Manuscripts",
  reviews: "Reviews",
```

- [ ] **Step 4: `schema.js` EDGE_CATEGORY_GROUPS** — replace the object with the same groups as `config/visualize.json` Task A6 Step 2 (JS array syntax; `"Paper ↔ Concept"` / `"Paper ↔ Method"` use the literal arrow char). Keep it a `Object.freeze({...})`.

- [ ] **Step 5: `schema.js` EDGE_TYPE_WORKFLOW** — add the new explicit edges (all `ingest`) before the closing brace:

```javascript
  proposes_method: "ingest",
  applies_method: "ingest",
  extends_method: "ingest",
  contributes_to_foundation: "ingest",
  shares_mechanism_with: "ingest",
  shares_assumption_with: "ingest",
  related_problem_formulation: "ingest",
  contrasts_with_concept: "ingest",
```

- [ ] **Step 6: `schema.js` EDGE_PRESETS** — update `"All"` to list every group name used in EDGE_CATEGORY_GROUPS (Citations, Paper relations, Paper ↔ Concept, Paper ↔ Method, Method genealogy, Foundation grounding, Topic membership, People contributions, Concept relations, Active research, Workflow (ideas / experiments)). Optionally add `"Foundations": ["Foundation grounding"]` preset.

- [ ] **Step 7: `graph.js` ENTITY_HEX** — remove `Summary:` line, add:

```javascript
  foundations: "#95A5A6",
  manuscripts: "#9B59B6",
  reviews: "#16A085",
```

- [ ] **Step 8: Verify JS parses.**

Run: `node --check app/modules/schema.js && node --check app/modules/graph.js && echo OK`
Expected: `OK`.

- [ ] **Step 9: Verify low-confidence filter is preset-independent (spec §9.5).** Inspect `graph.js`: confirm `applyPreset` does NOT write `hideLowConfidence`, and the toggle has its own handler. If a preset resets it, add a guard so the user toggle persists across preset switches.

Run: `grep -n "hideLowConfidence" app/modules/graph.js`
Expected: assignments only in init + the toggle change handler — not inside preset logic.

---

### Task A10: Frontend — reader.js editable fields (long-term fields), dashboard.js (no Summary)

**Files:**
- Modify: `app/modules/reader.js`
- Modify: `app/modules/dashboard.js`

- [ ] **Step 1: `reader.js` EDITABLE_FIELDS** — remove the `Summary:` line; extend long-term kinds with the new editable link fields:

```javascript
const EDITABLE_FIELDS = {
  papers: ["tags", "importance", "tldr", "contribution_type", "datasets", "code_url", "venue", "year", "parent_topics"],
  concepts: ["tags", "aliases", "maturity", "definition", "related_concepts", "parent_topics", "grounded_in"],
  topics: ["tags", "topic_kind", "domains", "key_venues", "parent_topics", "related_topics", "key_foundations", "key_concepts", "key_methods"],
  people: ["research_areas", "affiliation", "homepage", "scholar", "parent_topics", "key_papers", "contributed_methods", "contributed_foundations"],
  ideas: ["tags", "status", "priority", "target_venue", "novelty_score", "failure_reason"],
  experiments: ["tags", "status", "outcome", "key_result"],
  methods: ["tags", "type", "code_repo", "source_papers", "parent_topics", "grounded_in"],
  foundations: ["tags", "aliases", "status", "parent_topics"],
};
```

- [ ] **Step 2: `reader.js` LIST_FIELDS** — add the new list fields so the UI treats them as multi-value:

```javascript
const LIST_FIELDS = new Set([
  "tags", "aliases", "related_concepts", "research_areas",
  "key_venues", "key_topics", "contribution_type", "datasets",
  "source_papers", "parent_topics", "related_topics", "grounded_in",
  "domains", "key_foundations", "key_concepts", "key_methods",
  "key_papers", "contributed_methods", "contributed_foundations",
]);
```

- [ ] **Step 3: `dashboard.js`** — no Summary reference exists in the headline; leave as-is for Phase A. (Manuscript/review cells added in Phase C, Task C6.)

- [ ] **Step 4: Verify JS parses.**

Run: `node --check app/modules/reader.js && node --check app/modules/dashboard.js && echo OK`
Expected: `OK`.

---

### Task A11: tools/research_wiki.py — stats: drop Summary, add manuscripts/reviews

**Files:**
- Modify: `tools/research_wiki.py` (stats dict ~lines 1444-1452, 1519)

- [ ] **Step 1: Read the exact stats region** (`grep -n "summaries\|count_md\|stats\[" tools/research_wiki.py | head`) and remove the `"summaries": count_md("Summary"),` line; add `"manuscripts": count_md("manuscripts"),` and `"reviews": count_md("reviews"),`. Update the `stats.get("summaries" if k == "Summary" else k, 0)` expression (~line 1519) to plain `stats.get(k, 0)` since the key now matches the kind.

- [ ] **Step 2: Verify compiles.**

Run: `python3 -m py_compile tools/research_wiki.py && python3 -c "import sys; print('OK')"`
Expected: `OK`.

---

### Task A12: Wiki scaffold — remove Summary dir, regenerate index, add new dirs

**Files:**
- Delete: `wiki/Summary/` (dir + `.gitkeep`)
- Create: `wiki/manuscripts/.gitkeep`, `wiki/reviews/.gitkeep`
- Modify: `wiki/index.md`

- [ ] **Step 1: Remove Summary dir and create new entity dirs.**

Run: `git rm -r wiki/Summary 2>/dev/null || rm -rf wiki/Summary; mkdir -p wiki/manuscripts wiki/reviews && touch wiki/manuscripts/.gitkeep wiki/reviews/.gitkeep && echo done`

- [ ] **Step 2: Regenerate `wiki/index.md` from the schema** (matches `reset_wiki.INDEX_TEMPLATE`):

Run: `python3 -c "
from runtime.loader import ENTITY_DIRS
open('wiki/index.md','w').write('# Wiki Index\n\n' + '\n\n'.join(f'{e}:' for e in ENTITY_DIRS) + '\n')
print(open('wiki/index.md').read())"`
Expected: index lists all entity dirs incl. manuscripts/reviews, no `Summary`.

- [ ] **Step 3: Delete the orphan Summary template.**

Run: `git rm runtime/templates/Summary.md.tmpl 2>/dev/null || rm -f runtime/templates/Summary.md.tmpl; echo done`

---

### Task A13: Phase A integration verification

- [ ] **Step 1: Everything compiles / parses / lints.**

Run:
```bash
python3 -m py_compile tools/lint.py tools/research_wiki.py tools/serve.py tools/visualize.py runtime/loader.py && \
python3 -c "import runtime.loader; print('schema loads')" && \
python3 tools/lint.py --wiki-dir wiki --json && echo "lint exit: $?" && \
node --check app/modules/schema.js && node --check app/modules/graph.js && \
node --check app/modules/reader.js && node --check app/modules/dashboard.js && \
python3 -c "import json; json.load(open('config/visualize.json')); print('json ok')"
```
Expected: all succeed; lint prints `[]` (empty wiki) and exits 0.

- [ ] **Step 2: Smoke test — long-term relations project + xref repairs.** Create minimal fixtures and verify graph projection + reverse repair:

```bash
mkdir -p /tmp/wfix && cp -r wiki /tmp/wt && cd /tmp/wt
# topic
printf -- '---\ntitle: Reasoning Agents\ntags: []\ntopic_kind: subfield\n---\n\n## Key papers\n\n## Key methods\n\n## Foundations\n' > topics/reasoning-agents.md
# foundation
printf -- '---\ntitle: Reinforcement Learning\nslug: reinforcement-learning\ndomain: cs\nstatus: mainstream\n---\n\n## Grounds methods\n\n## Contributed by papers\n' > foundations/reinforcement-learning.md
# method with parent_topics + grounded_in
printf -- '---\nname: Agentic Self Training\nslug: agentic-self-training\ntype: training\ntags: []\nparent_topics: [reasoning-agents]\ngrounded_in: [reinforcement-learning]\n---\n\n## Proposed by\n' > methods/agentic-self-training.md
# paper with parent_topics + an edge
printf -- '---\ntitle: Foo\nslug: foo-paper\ntags: []\nimportance: 3\nparent_topics: [reasoning-agents]\n---\n\n## Related\n' > papers/foo-paper.md
python3 /home/litiansuo/projects/omegawiki-contest/tools/research_wiki.py add-edge . --from papers/foo-paper --to methods/agentic-self-training --type proposes_method --confidence high --evidence "introduces it"
python3 /home/litiansuo/projects/omegawiki-contest/tools/research_wiki.py add-edge . --from papers/foo-paper --to foundations/reinforcement-learning --type contributes_to_foundation --confidence medium --evidence "advances RL"
python3 /home/litiansuo/projects/omegawiki-contest/tools/lint.py --wiki-dir . --fix
echo "--- topic key_methods (should contain agentic-self-training) ---"; grep -n "agentic-self-training\|foo-paper" topics/reasoning-agents.md
echo "--- foundation reverses ---"; cat foundations/reinforcement-learning.md
echo "--- method Proposed by ---"; cat methods/agentic-self-training.md
# idempotency: second --fix changes nothing
python3 /home/litiansuo/projects/omegawiki-contest/tools/lint.py --wiki-dir . --fix
cd /home/litiansuo/projects/omegawiki-contest
```
Expected: topic `key_methods`/`key_papers` gain the slugs; foundation `## Grounds methods` gets `[[agentic-self-training]]`, `## Contributed by papers` gets `[[foo-paper]]`; method `## Proposed by` gets `[[foo-paper]]`; second `--fix` reports no new fixes (idempotent). Clean up `/tmp/wt` after.

---

## Phase B — Long-Term Schema Completion

### Task B1: edges.yaml — Concept↔Concept symmetric typed edges

**Files:**
- Modify: `runtime/schema/edges.yaml`

- [ ] **Step 1: Append the four symmetric edges** after the Paper→Concept block:

```yaml
# -----------------------------------------------------------------------------
# Concept ↔ Concept typed relations  (written by /ingest, symmetric)
# -----------------------------------------------------------------------------

shares_mechanism_with:
  endpoints: { from: concepts, to: concepts }
  direction: symmetric
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

shares_assumption_with:
  endpoints: { from: concepts, to: concepts }
  direction: symmetric
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

related_problem_formulation:
  endpoints: { from: concepts, to: concepts }
  direction: symmetric
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }

contrasts_with_concept:
  endpoints: { from: concepts, to: concepts }
  direction: symmetric
  workflow:  ingest
  attributes:
    confidence: { type: enum, values: [high, medium, low], required: true }
    evidence:   { type: str, required: true }
```

- [ ] **Step 2: Add to `writers.yaml` `edges:`** the four edges as `[ingest]`.

- [ ] **Step 3: Verify symmetric derivation + canonicalization.**

Run: `python3 -c "from runtime.loader import SYMMETRIC_EDGE_TYPES; assert {'shares_mechanism_with','shares_assumption_with','related_problem_formulation','contrasts_with_concept'} <= SYMMETRIC_EDGE_TYPES; print('symmetric OK')"`
Expected: `symmetric OK`.

- [ ] **Step 4: Smoke — symmetric edge canonicalized (no A→B/B→A dup).** In a temp wiki, `add-edge` `shares_mechanism_with` from c-a→c-b then b→a; second should report `exists`. Verify single line in `graph/edges.jsonl`.

---

### Task B2: People contribution — confirm projection + UI

**Files:** (schema fields added in A1 Step 5; this task wires UI/config)

- [ ] **Step 1:** Confirm `config/visualize.json` (A6) and `schema.js` EDGE_CATEGORY_GROUPS already include `fm_people_*` and `Concept relations`. If not, add them.
- [ ] **Step 2:** Confirm `reader.js` EDITABLE_FIELDS.people (A10) includes the contribution fields.
- [ ] **Step 3: Smoke — people fields project as `fm_people_*` edges.** Create a `people/example-lab.md` with `contributed_methods: [agentic-self-training]`; run `research_wiki.py rebuild-projected-edges`; grep for `fm_people_contributed_methods` in the projected output.

---

### Task B3: Phase B verification

- [ ] **Step 1:** Re-run the full compile/parse/lint/node-check battery from A13 Step 1. All pass.

---

## Phase C — Active Memory Entities + Methodology Scaffold

### Task C1: entities.yaml — manuscripts + reviews

**Files:**
- Modify: `runtime/schema/entities.yaml`

- [ ] **Step 1: Append the two entity blocks** at end of file:

```yaml
manuscripts:
  dir: wiki/manuscripts/
  fields:
    title:  { type: str, required: true }
    slug:   { type: str, required: true }
    status:
      type: enum
      values: [drafting, revised, submitted, final_version]
      required: true
      default: drafting
    tags:   { type: list_str, required: true, default: [] }
  lifecycle:
    transitions:
      drafting:      [revised, submitted]
      revised:       [revised, submitted]
      submitted:     [revised, final_version]
      final_version: []

reviews:
  dir: wiki/reviews/
  fields:
    title: { type: str, required: true }
    slug:  { type: str, required: true }
    feedback_type:
      type: enum
      values: [feedback, rebuttal, final_decision]
      required: true
    resolution_status:
      type: enum
      values: [open, addressed, superseded]
      required: true
      default: open
    linked_manuscript: { type: link, to: manuscripts, required: true }
```

- [ ] **Step 2: Verify.**

Run: `python3 -c "from runtime.loader import ENTITIES, VALID_VALUES, validate_lifecycle_transition as v; assert 'manuscripts' in ENTITIES and 'reviews' in ENTITIES; assert VALID_VALUES['manuscripts.status']; assert v('manuscripts','drafting','revised') is None; assert v('manuscripts','final_version','drafting') is not None; print('OK')"`
Expected: `OK`.

---

### Task C2: xref.yaml — reviews.linked_manuscript → manuscripts ## Reviews

**Files:**
- Modify: `runtime/schema/xref.yaml`

- [ ] **Step 1: Add the rule** in `rules:` (before `terminal_targets`):

```yaml
  # reviews.linked_manuscript → manuscripts ## Reviews
  - forward: { kind: reviews,      frontmatter_field: linked_manuscript, target: manuscripts }
    reverse: { kind: manuscripts,  body_section: "Reviews",              action: append_slug }
```

- [ ] **Step 2: Verify.**

Run: `python3 -c "from runtime.loader import XREF; assert any(r['forward'].get('frontmatter_field')=='linked_manuscript' for r in XREF['rules']); print('OK')"`
Expected: `OK`.

---

### Task C3: writers.yaml — manuscript/review lifecycle fields

**Files:**
- Modify: `runtime/policy/writers.yaml`

- [ ] **Step 1: Add under `fields:`:**

```yaml
  # Active research memory — manuscript/review lifecycle.
  manuscripts.status:        { writers: [paper-plan, paper-draft, refine, rebuttal, decision, edit] }
  reviews.feedback_type:     { writers: [review, rebuttal, decision, edit] }
  reviews.resolution_status: { writers: [refine, rebuttal, decision, edit] }
```

- [ ] **Step 2: Verify.**

Run: `python3 -c "from runtime.loader import WRITERS; assert WRITERS['fields']['manuscripts.status']; assert WRITERS['fields']['reviews.feedback_type']; print('OK')"`
Expected: `OK`.

---

### Task C4: Templates — manuscripts + reviews

**Files:**
- Create: `runtime/templates/manuscripts.md.tmpl`
- Create: `runtime/templates/reviews.md.tmpl`

- [ ] **Step 1: `manuscripts.md.tmpl`:**

```markdown
---
{{ frontmatter }}
---

## Working notes

## Evidence map

## Version history

## Current draft

## Submission record

## Reviews

## Final version notes
```

- [ ] **Step 2: `reviews.md.tmpl`:**

```markdown
---
{{ frontmatter }}
---

## Summary

## Concerns

## Action items

## Response / Resolution

## Manuscript changes

## Evidence gaps
```

- [ ] **Step 3: Verify the `## Reviews` reverse section exists on the manuscripts template** (xref target):

Run: `grep -n "## Reviews" runtime/templates/manuscripts.md.tmpl`
Expected: one match.

---

### Task C5: Frontend + visualize.py — manuscripts/reviews metadata

**Files:**
- Modify: `app/modules/schema.js`, `app/modules/reader.js`, `tools/visualize.py`

(Entity dirs/labels/precedence/colors for manuscripts/reviews were added in A8/A9; this task adds editable fields.)

- [ ] **Step 1: `reader.js` EDITABLE_FIELDS** — add:

```javascript
  manuscripts: ["tags", "status"],
  reviews: ["tags", "feedback_type", "resolution_status"],
```

- [ ] **Step 2:** Confirm `schema.js` ENTITY_DIRS/ENTITY_LABEL/TYPE_PRECEDENCE include manuscripts/reviews (from A9). Confirm `graph.js` ENTITY_HEX includes them (A9). Confirm `visualize.py` CANVAS_COLOR_MAP includes them (A8).

- [ ] **Step 3: Verify.**

Run: `node --check app/modules/reader.js && python3 -m py_compile tools/visualize.py && echo OK`
Expected: `OK`.

---

### Task C6: dashboard.js — manuscript/review counts

**Files:**
- Modify: `app/modules/dashboard.js` (headline cells, ~lines 127-133)

- [ ] **Step 1: Add two cells** to the `cells` array (counts read dynamically from `state.entitiesByType`):

```javascript
    { label: "Manuscripts", value: counts.manuscripts || 0, color: "#9B59B6" },
    { label: "Reviews", value: counts.reviews || 0, color: "#16A085" },
```

- [ ] **Step 2: Verify.**

Run: `node --check app/modules/dashboard.js && echo OK`
Expected: `OK`.

---

### Task C7: research_methodology/ scaffold (non-wiki)

**Files:**
- Create: `research_methodology/{index,literature-reading,topic-selection,idea-development,experiment-design,evidence-management,cross-project-collaboration,manuscript-writing,review-and-rebuttal,project-retrospective}.md`

- [ ] **Step 1: Create the directory and 9 sparse template files** (each from the §5.5 template):

```markdown
# <Methodology Topic>

## Scope

## Principles

## Checklist

## Anti-patterns

## Cross-project notes

## Open questions
```

`index.md` gets a short intro + a list linking the other 9 files. `cross-project-collaboration.md` additionally appends the §5.5 extra sections:

```markdown
## Collaboration contracts

## Handoff rules

## Shared vocabulary

## Conflict resolution

## Reusable project patterns
```

Use a small Python heredoc to write all files with the correct `# <Title>` headings.

- [ ] **Step 2: Verify it is NOT a wiki entity.**

Run: `python3 -c "from runtime.loader import ENTITY_DIRS; assert 'research_methodology' not in ENTITY_DIRS; print('not an entity')" && grep -rn "research_methodology" runtime/ tools/serve.py app/modules/schema.js && echo "UNEXPECTED ref" || echo "no schema/graph references — good"`
Expected: `not an entity`; no references in schema/graph code.

---

### Task C8: Phase C verification (full acceptance battery)

- [ ] **Step 1: Compile/parse/lint/node-check all.** Re-run A13 Step 1 battery — all pass; lint on empty wiki exits 0 with no `Summary`.

- [ ] **Step 2: Smoke — manuscript + linked review.** In a temp wiki copy:

```bash
cp -r wiki /tmp/wt2 && cd /tmp/wt2
printf -- '---\ntitle: AutoSci Paper\nslug: autosci-paper\nstatus: drafting\ntags: []\n---\n\n## Reviews\n' > manuscripts/autosci-paper.md
printf -- '---\ntitle: Internal Feedback\nslug: autosci-paper-internal\nfeedback_type: feedback\nresolution_status: open\nlinked_manuscript: autosci-paper\n---\n\n## Summary\n' > reviews/autosci-paper-internal.md
python3 /home/litiansuo/projects/omegawiki-contest/tools/lint.py --wiki-dir . --fix
echo "--- manuscript ## Reviews should link the review ---"; grep -n "autosci-paper-internal" manuscripts/autosci-paper.md
python3 /home/litiansuo/projects/omegawiki-contest/tools/lint.py --wiki-dir . --json && echo "lint exit $?"
cd /home/litiansuo/projects/omegawiki-contest && rm -rf /tmp/wt2
```
Expected: manuscript `## Reviews` gains `[[autosci-paper-internal]]`; lint exits 0.

- [ ] **Step 3: Verify `/api/graph`-shape data exposes new types** (offline check of the projection + loader, no server needed):

```bash
python3 -c "
from runtime.loader import EDGE_TYPE_SPECS, ENTITY_DIRS
for e in ['proposes_method','applies_method','extends_method','contributes_to_foundation','shares_mechanism_with']:
    assert e in EDGE_TYPE_SPECS, e
assert 'manuscripts' in ENTITY_DIRS and 'reviews' in ENTITY_DIRS and 'Summary' not in ENTITY_DIRS
print('graph schema exposes new entity + edge types')"
```
Expected: success line.

---

## Phase D — DEFERRED (documented, not implemented)

Per spec §10 Phase D and the commit-isolation constraint, skill-workflow wiring is out of scope here. When undertaken, edit `i18n/{zh,en}/skills/...` sources (not the generated `.claude/skills/*` copies) and re-sync via `./setup.sh`. Future tasks:
- `/paper-plan` create manuscript draft record; `/paper-draft` update `## Current draft`.
- `/review --write-review` create `feedback` review; `/refine` advance `drafting`→`revised` + version history.
- `/rebuttal` create `rebuttal` review; new/extended `/decision` create `final_decision` review + push `final_version`.
- Optional: `research_wiki.py add-edge --repair-xref` flag; dashboard schema-coverage metric; methodology-guidance opt-in reads.

---

## Final Acceptance Checklist (spec §9.5)

- [ ] `python3 -m py_compile tools/lint.py tools/research_wiki.py tools/serve.py tools/visualize.py` passes.
- [ ] `python3 tools/lint.py --wiki-dir wiki --json` passes (exit 0) on the empty scaffold.
- [ ] `node --check` passes for schema.js / graph.js / reader.js / dashboard.js.
- [ ] Empty/new wiki initializes with no `Summary` page and no `concepts.parent_topic` field.
- [ ] Minimal topic/paper/foundation/method/concept/people sample shows topic membership + new typed relations in projected graph.
- [ ] Manuscript + linked review: review links manuscript; manuscript reverse `## Reviews` repaired by `lint --fix`.
- [ ] `research_methodology/` exists, user-editable markdown only, absent from graph/schema/xref/edges.
- [ ] Graph data includes new entity + edge types; unknown types use fallback without loss.
- [ ] "Hide low-confidence edges" persists across preset/filter switches.
- [ ] `git diff` (of staged files) excludes `.pdf`/`.tex`/runtime-generated wiki/tmp-viz and the unrelated `.claude/skills/*` + `README.md` changes.

## Self-Review Notes

- Spec coverage: §3.1 (A1,A3,A5,A6,A9), §3.2 (A1,A3,A5), §3.3 (A2,A3,A5), §3.4 (A2,A3,A5), §3.5 (B1), §3.6 (A1,B2), §3.7 (A3 + verified existing fixer), §3.8 (A6,A9,A10), §4 (C1–C6), §5 (C7), §7 (A4,B1,C3), §8 (A9,A10,C5,C6), §9.3 Summary removal (A1,A6,A8,A9,A10,A11,A12), §9.4 parent_topic (A1,A3,A4,A6,A9).
- DEFER honored: uses_foundation, people→* edges, papers.contributes_to_foundations field, dashboard coverage metric, all skill workflow wiring, methodology auto-read.
- Type consistency: edge names identical across edges.yaml / xref.yaml / writers.yaml / visualize.json / schema.js; `fm_<kind>_<field>` projection names match field names added in A1.
