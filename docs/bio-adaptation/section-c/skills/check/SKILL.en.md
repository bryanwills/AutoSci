---
description: Scan the full wiki to detect health issues and produce a tiered fix-recommendation report (covers all 10 entity types + graph consistency, with optional bio-lint pass)
---

<!-- bio-C8: Mirror of i18n/en/skills/check/SKILL.md with the C8 bio-lint pass drafted.
     Source of truth: i18n/en/skills/check/SKILL.md. Do not run from this path; for testing, merge to source first.
     New tool referenced (`tools/lint_bio.py`) does NOT yet exist; this mirror lists it under
     Dependencies as a planned follow-up. Until the tool lands the bio pass is silently skipped
     (the existing `tools/lint.py` keeps running as today). Cross-section dependencies:
       A1 (datasets/) — version-drift check anchors against datasets/{slug}.versions[]
       A3 (papers/ bio identifiers) — DOI/PMID/PDB/UniProt format checks
       A5 (experiments setup bio fields) — force-field-on-MD check; species-mismatch check
       A8 (reproducibility.dataset_versions) — companion to dataset version-drift check
       B3 (dataset_version_used edge) — completeness check against datasets/{slug}.versions[]
       C4 (statistical_protocol enum) — value-completeness check on experiments
       C6 (statistical_protocol selector) — same field, downgraded as a non-deterministic suggestion
     -->

# /check

> Scans the full wiki to detect structural, link, field, and graph health issues, and generates a tiered fix-recommendation report.
> Covers all 10 entity types <!-- bio-C8 (depends on A1) -->, including claims confidence plausibility, idea failure-reason completeness,
> experiment-claim link validity, graph edge consistency, and — when bio fields are present — a bio-lint pass that checks identifier formats, dataset version drift, force-field provenance on MD experiments, and species/scope coherence.

## Inputs

- Full wiki directory (default `wiki/`)
- Optional: `--json` flag (output JSON format via tools/lint.py)
- Optional: `--fix` flag (auto-fix deterministic issues)
- Optional: `--fix --dry-run` (preview fixes without applying them)
- Optional: `--suggest` flag (show recommendations for issues that cannot be auto-fixed)
- <!-- bio-C8 --> Optional: `--bio` flag (force the bio-lint pass even on a wiki where no bio fields are detected); default behavior: auto-enable when any of `papers/*.md doi|pmid|pdb_ids|uniprot_ids`, `experiments/*.md setup.in_silico_or_wet|setup.assay_type|setup.force_field`, or `datasets/*.md` is non-empty.
- <!-- bio-C8 --> Optional: `--no-bio` flag (force-skip the bio-lint pass even on a wiki where bio fields are present); useful when iterating on CS-only changes.

## Outputs

- Lint report (reported directly to the user)
- Optional file write: `wiki/outputs/lint-report-{date}.md`

## Wiki Interaction

### Reads
- `wiki/papers/*.md` — paper page fields and links
- `wiki/concepts/*.md` — concept page fields and links
- `wiki/topics/*.md` — topic page fields and links
- `wiki/people/*.md` — people page fields and links
- `wiki/ideas/*.md` — idea status, failure_reason, origin_gaps
- `wiki/experiments/*.md` — experiment status, target_claim, outcome
- `wiki/claims/*.md` — claim confidence, status, evidence, source_papers
- `wiki/Summary/*.md` — survey page fields
- <!-- bio-C8 (depends on A1) --> `wiki/datasets/*.md` — dataset page fields, `versions[]`, `access`, `key_papers`
- `wiki/graph/edges.jsonl` — semantic graph edge consistency check
- `wiki/graph/citations.jsonl` — bibliographic citation consistency check
- `wiki/index.md` — cross-check page completeness

### Writes
- Does not directly modify wiki content (reports only, no fixes)
- `wiki/log.md` — records lint result summary via `tools/research_wiki.py log`

## Workflow

**Pre-conditions**: confirm the working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).
Set `WIKI_ROOT=wiki/`.

### Step 1: Run the Automated Lint Tool

**Default mode (report only)**:
```bash
python3 tools/lint.py --wiki-dir wiki/ --json
```

**Auto-fix mode** (when user specifies `--fix`):
```bash
python3 tools/lint.py --wiki-dir wiki/ --fix --json
```
Auto-fixes deterministic issues (xref reverse-link completion, missing fields filled with default values) and outputs a fix report.

**Preview mode** (when user specifies `--fix --dry-run`):
```bash
python3 tools/lint.py --wiki-dir wiki/ --fix --dry-run --json
```
Previews what would be fixed without applying any changes.

Parse the JSON output to obtain all automatically detected issues (and fix results).

### Step 2: Structural Completeness (automated coverage)

The automated tool checks:

1. **Broken wikilinks**: `[[slug]]` target file does not exist
2. **Orphan pages**: pages with no incoming links
3. **Missing required fields** (all 10 entity types) <!-- bio-C8 -->:
   - papers: title, slug, tags, importance
   - concepts: title, tags, maturity, key_papers
   - topics: title, tags
   - people: name, tags
   - Summary: title, scope, key_topics
   - ideas: title, slug, status, origin, tags, priority
   - experiments: title, slug, status, target_claim, hypothesis, tags
   - claims: title, slug, status, confidence, tags, source_papers, evidence
   - <!-- bio-C8 (depends on A1) --> datasets: title, slug, tags, maturity, access, versions, date_updated

### Step 3: Field Value Validation (automated coverage)

1. **Enum value checks**:
   - papers.importance ∈ {1,2,3,4,5}
   - concepts.maturity ∈ {stable, active, emerging, deprecated}
   - ideas.status ∈ {proposed, in_progress, tested, validated, failed}
   - ideas.priority ∈ {1,2,3,4,5}
   - experiments.status ∈ {planned, running, completed, abandoned}
   - experiments.outcome ∈ {succeeded, failed, inconclusive}
   - <!-- bio-C8 (depends on C4) --> experiments.type ∈ {baseline, validation, ablation, robustness, negative_control, mechanism, dose_response, cross_context}
   - <!-- bio-C8 (depends on C6) --> experiments.statistical_protocol ∈ {seeds_only, bootstrap_ci, stratified_kfold, replicate_matrix_BxT}
   - claims.status ∈ {proposed, weakly_supported, supported, challenged, deprecated}
   - <!-- bio-C8 (depends on A7) --> claims.evidence[*].type ∈ base set ∪ bio extension; claims.evidence[*].grade ∈ {very-low, low, moderate, high} when present
   - <!-- bio-C8 (depends on A1) --> datasets.maturity ∈ {stable, active, emerging, deprecated}; datasets.access ∈ {public, registration, restricted, wet-lab-derived}
2. **Claim confidence** ∈ [0.0, 1.0]
3. **Idea failure_reason**: must be non-empty when status=failed (anti-repetition memory)
4. **Experiment target_claim**: the referenced claim must exist

### Step 4: Cross Reference Symmetry (automated coverage)

Check all bidirectional link rules defined in CLAUDE.md:

| Forward link | Reverse link checked |
|----------|---------------|
| concepts.key_papers → papers | papers.Related contains concept link |
| papers → people (wikilink) | people.Key papers contains paper |
| claims.source_papers → papers | papers.Related contains claim link |
| ideas.origin_gaps → claims | claims.Linked ideas contains idea |
| experiments.target_claim → claims | claims.evidence contains experiment |
| <!-- bio-C8 (depends on A1) --> papers → datasets (wikilink in body or `[[ternarydb]]`-style frontmatter) | datasets.key_papers contains paper |
| <!-- bio-C8 (depends on A1) --> experiments.setup.dataset → datasets | datasets `## Used by experiments` lists experiment |

### Step 5: Graph Edge Consistency (automated coverage)

1. **JSON format validity**: every line is valid JSON
2. **Required fields**: each edge has from, to, type
3. **Edge type validity**: semantic edges use the current endpoint-aware type sets; legacy paper-paper / paper-concept types produce migration warnings
4. **Edge confidence**: `/ingest` paper-paper and paper-concept semantic edges use `confidence: high|medium|low`
5. <!-- bio-C8 (depends on B1/B2/B3) --> **Bio-edge metadata completeness**: B1 bio-relation edges must carry `confidence`; B2 (`clinical_trial_for {nct_id, phase}`, `fda_approved_for {indication, year}`, `validates_in_species {species}`) and B3 (`dataset_version_used {slug, version}`) must carry the typed `metadata` keys declared in `tools/_schemas.py::EDGE_METADATA_REQUIRED`. Missing required keys → 🔴.
6. **Citation layer**: `graph/citations.jsonl` rows use `type: cites`, valid source/date, paper endpoints, and no confidence field
7. **Dangling nodes**: wiki pages referenced by from/to must exist

### Step 6: Content Quality (LLM-assisted)

Items detectable by the automated tool:
1. Papers with importance=5 have no concept page referencing them
2. Concepts with maturity=stable have only 1 key_paper
3. Topics have empty Open problems sections

Additional LLM judgments (requires reading content):
1. **Concept near-duplicate detection**: scan all concept page titles + aliases and assess whether any pairs are semantically identical or highly similar (e.g. "attention mechanism" and "self-attention"). Output merge recommendations for suspected duplicates.
2. Contradictory statement detection (inconsistent descriptions of the same fact across different pages)
3. SOTA records not updated in over 6 months
4. people Recent work not updated in over 6 months
5. Claim confidence inconsistent with evidence quantity/strength
6. High-priority idea stuck in proposed status for a long time

<!-- bio-C8 -->

### Step 6b: Bio-Lint Pass (auto-detected, or forced via --bio / --no-bio)

Skip when none of `papers/*.md`, `experiments/*.md`, or `datasets/*.md` carry any bio field, or when `--no-bio` was passed. Otherwise:

```bash
python3 tools/lint_bio.py --wiki-dir wiki/ --json
```

The bio-lint tool emits the same JSON shape as `tools/lint.py` (one issue per row, with `severity ∈ {🔴, 🟡, 🔵}`, `file`, `field`, `message`, and `fix-rule`) so the existing report generator in Step 7 can ingest it without changes. Categories:

1. **Identifier-format checks** (deterministic, severity 🔴 on hard violation, 🟡 on plausible-but-non-canonical):
   - **DOI** (`papers.doi`, citations rows): regex `^10\.\d{4,9}/[-._;()/:A-Z0-9]+$` (case-insensitive). Reject empty or malformed.
   - **PMID** (`papers.pmid`): bare numeric, 1–9 digits. Reject leading-zero pads or `PMID:` prefix in the field value (the prefix is a UI affordance only).
   - **bioRxiv DOI** (`papers.biorxiv`): regex `^10\.1101/\d{4}\.\d{2}\.\d{2}\.\d{6}$`. medRxiv shares the prefix `10.1101/` but its date range starts mid-2019; warn (not error) on bioRxiv DOIs predating 2013.
   - **PDB ID** (`papers.pdb_ids[*]`, `experiments.setup.pdb_versions`): 4-char short form `^[0-9][A-Za-z0-9]{3}$` OR 8-char extended `^pdb_[0-9a-z]{8}$`.
   - **UniProt accession** (`papers.uniprot_ids[*]`, `concepts.uniprot_id`): regex `^[OPQ][0-9][A-Z0-9]{3}[0-9]$` OR `^[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}$`.
   - **NCT ID** (`papers.nct_ids[*]`, `clinical_trial_for.metadata.nct_id`): regex `^NCT[0-9]{8}$`.
   - **Cellosaurus ID** (`experiments.setup.cell_line`): regex `^CVCL_[A-Z0-9]{4}$`. Plain text cell line names produce a 🟡 "consider promoting to CVCL" suggestion, not an error.
   - **HGNC gene symbol** (`papers.gene_symbols[*]`, `concepts.gene_symbol`): regex `^[A-Z][A-Z0-9]{0,9}(-[A-Z0-9]{1,4})?$`. The check is conservative — it lets through symbols like `HLA-DRB1` and `BRCA2` but flags lowercase or whitespace-bearing values.

2. **Dataset version drift** (deterministic, severity 🔴 on missing edge, 🟡 on stale version):
   - For every `experiments/*.md` whose `setup.dataset` resolves to a `[[datasets/{slug}]]` link, check that an outgoing `dataset_version_used` edge exists in `graph/edges.jsonl` (B3 dependency).
   - For every existing `dataset_version_used` edge, check `metadata.version` is present in the target `datasets/{slug}.versions[*].version` list. Mismatch → 🟡 "stale or unknown version pinned".
   - When `experiments.reproducibility.dataset_versions[*].version` is set, cross-check it against the same `versions[]` list. Out-of-list → 🟡.

3. **Force-field provenance on MD experiments** (deterministic, severity 🔴):
   - When `experiments.setup.assay_type == 'MD'` (case-insensitive match), require `setup.force_field` to be non-empty. Same rule for `setup.solvent_model` and `setup.simulation_length`.
   - When `setup.force_field` is non-empty but `setup.assay_type` is empty or non-MD, emit a 🔵 nudge: "force_field set on a non-MD experiment — confirm assay_type".

4. **Species-mismatch coherence** (LLM-assisted, severity 🟡):
   - For each `experiments/*.md` whose `setup.species` is non-empty, follow `target_claim` to the parent claim and check whether the claim text or `evidence[*].grade` implies a different translational scope.
   - Heuristic: if the claim mentions "human", "patient", "clinical", "therapeutic" but the experiment's `setup.species` is `mouse`/`rat`/`zebrafish`, emit a 🟡 "species-claim scope mismatch — explicit cross-context block (C4) recommended".
   - This check is intentionally an LLM-assisted nudge rather than a hard error, because cross-species evidence is often the *correct* substrate for a human claim — the goal is to surface unacknowledged scope drift.

5. **Statistical-protocol completeness** (deterministic, severity 🟡):
   - For every `experiments/*.md` written after C6 lands (heuristic: `date_planned >= 2026-05-04`), `statistical_protocol` must be set to one of the four enum values. Empty → 🟡 "statistical_protocol unset; default selector documented in /exp-design Step 3".
   - For pre-C6 experiments (`date_planned < 2026-05-04`), unset `statistical_protocol` is treated as a 🔵 migration nudge with `--fix`'s deterministic-fill applying `seeds_only` only when `seeds >= 3` AND no bio-domain marker is present; otherwise leave unset and let the user choose.

6. **Domain vocabulary coherence** (deterministic, severity 🔵):
   - Where the legacy CS-vocabulary `domain` strings (`Computational Drug Design / Chemical Biology`, `Cancer biology / Molecular oncology`, `Structural Bioinformatics`, …) appear, suggest the closest A4 controlled-vocabulary value. Suggestions only — `/check` does not auto-rewrite free-text domain values.

### Step 7: Generate Report

Output sorted by priority:

```
## Lint Report — YYYY-MM-DD

**Summary**: N 🔴, M 🟡, K 🔵
{when bio-lint ran:} **Bio-lint**: N_bio 🔴, M_bio 🟡, K_bio 🔵 (out of the totals above)   <!-- bio-C8 -->

### 🔴 Fix Immediately
1. [file] — {issue description}

### 🟡 Recommended Fixes
1. [file] — {issue description}

### 🔵 Optional Improvements
1. [file] — {issue description}
```

Classification:
- **🔴 Fix Immediately**: broken links, missing required fields, invalid enum values, failed idea without failure_reason, invalid JSON in edges, confidence out of range, <!-- bio-C8 --> identifier-format hard violations, missing required B2/B3 edge metadata, missing `dataset_version_used` edge, missing force_field on MD experiment
- **🟡 Recommended Fixes**: xref asymmetry, dangling graph edges, broken claim references, unknown edge types, <!-- bio-C8 --> stale dataset version, species-claim scope mismatch, missing `statistical_protocol` on post-C6 experiments
- **🔵 Optional Improvements**: orphan pages, quality suggestions, empty sections, <!-- bio-C8 --> CS-vocabulary `domain` values, plain-text cell line names without CVCL ID

Append log:
```bash
python3 tools/research_wiki.py log wiki/ "check | report: N 🔴, M 🟡, K 🔵 | bio-lint: {ran|skipped}"
```
<!-- bio-C8: log line tail records whether the bio pass ran -->

## Constraints

- **Report-only by default**: without `--fix`, only reports, no modifications
- **`--fix` only repairs deterministic issues**: xref reverse-link completion, missing fields filled with safe default values. Non-deterministic issues output recommendations (`--suggest`) for user approval
- **raw/ is read-only**: do not modify files under `raw/`
- **graph/ is read-only**: lint does not modify graph files, checks consistency only
- **LLM judgments labeled by source**: automated checks and LLM judgments are clearly distinguished in the report
- **Idempotent**: running multiple times produces the same result (unless wiki content changes)
- <!-- bio-C8 --> **Bio-lint is auto-detected**: bio pass runs only when bio fields exist or `--bio` is passed; never modifies non-bio behavior. The boundary between `tools/lint.py` (cross-section structural) and `tools/lint_bio.py` (bio-specific) is strict — they do not share state and emit the same JSON shape.
- <!-- bio-C8 --> **Identifier-format auto-fix is disabled**: even with `--fix`, bio-lint never rewrites a malformed DOI/PMID/PDB/UniProt — those are user-provided ground truth and a "fix" would silently corrupt provenance.

## Error Handling

- **wiki/ does not exist**: report error and suggest running `/init`
- **graph files do not exist**: skip the missing graph-file checks, note in report
- **Partial directory missing**: skip checks for missing directories, list missing directories in report
- <!-- bio-C8 --> **`tools/lint_bio.py` does not exist** (current state, until Batch C-2 follow-up tooling lands): note "bio-lint pass skipped — tools/lint_bio.py not installed" in the report; the rest of `/check` continues unchanged.
- <!-- bio-C8 --> **`datasets/` directory empty but bio fields present in papers/experiments**: emit a 🟡 "datasets/ schema is live but no entries authored — TernaryDB pilot recommended; see CHANGELOG entry 2026-05-04 for the wiring procedure".

## Dependencies

### Tools（via Bash）
- `python3 tools/lint.py --wiki-dir wiki/ [--json] [--fix] [--dry-run] [--suggest]` — automated structural check + fix (core dependency)
- <!-- bio-C8 --> `python3 tools/lint_bio.py --wiki-dir wiki/ [--json]` — bio-lint pass (planned follow-up tool, not yet implemented)
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/research_wiki.py stats wiki/` — get statistics (optional, for the report)

<!-- bio-C8: Planned follow-up tool design

`tools/lint_bio.py` should:
- Reuse `tools/_env.py` for repo-root resolution.
- Walk `wiki/papers/`, `wiki/experiments/`, `wiki/datasets/`, `wiki/concepts/`, `wiki/claims/` and emit one JSON line per issue with shape:
    {"severity": "🔴|🟡|🔵",
     "file": "wiki/...",
     "field": "frontmatter.<dotted-path>" or "body",
     "message": "<one-line>",
     "fix-rule": "deterministic|suggestion|none"}
- Implement the six check categories listed in Step 6b above.
- Take `--wiki-dir` and `--json` (matching tools/lint.py CLI).
- Exit code matches `tools/lint.py`: **1 when any 🔴 issue is found, 0 otherwise**. `/check` consumes the JSON output rather than the exit code, so non-zero exit doesn't block the rest of the pass — it's there so CI pipelines that shell-call the linter directly can fail on hard violations.
- Cross-reference `tools/_schemas.py::EDGE_METADATA_REQUIRED` for B2/B3 metadata key checks.
- Be additive: `tools/lint.py` does NOT call `lint_bio.py`; `/check` orchestrates both.
-->
