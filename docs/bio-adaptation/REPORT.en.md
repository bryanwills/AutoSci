# ΩmegaWiki — Bio-Adaptation Report

> Mirror to its zh counterpart: [`REPORT.zh.md`](REPORT.zh.md). Substantive edits must be applied to both.
>
> Full evidence for reviewers and future contributors. For the visual demo (hero / GIF / canvas screenshots) see the project [README](../../README.md). For the work plan that produced this report see [DEMO_PLAN.en.md](DEMO_PLAN.en.md) / [DEMO_PLAN.zh.md](DEMO_PLAN.zh.md).
>
> Snapshot: branch `feat/qwt-ptm-degrader-ideate` @ `acc0c47`, 2026-05-11. Lint: `0 🔴 / 0 🟡 / 11 🔵`. Wiki: 11 papers / 22 ideas / 8 experiments / 16 people / 73 graph edges + 1 citation.

## 1. Why this fork

Upstream ΩmegaWiki was built for CS/AI research — page templates, lint rules, and skill prompts all assume an arXiv-shaped paper, a `claims/` ledger, and CS-style evidence verbs (`supports | contradicts | tested_by`). When we drove the wiki through a real bioinformatics workflow — `/exp-design ptm-aware-degrader-target-nomination` on 2026-05-02 — the CS-shaped assumptions broke down in concrete, repeated ways:

- Dataset references (TernaryDB, PROTAC-DB, DegronMD, AlphaFold-DB, PhosphoSitePlus, dbPTM, UniProt, PDB) had no canonical page to anchor to — they appeared only as inline plain text, with no version, no access tier, no reverse link.
- Bio-native paper identifiers (DOI, PMID, bioRxiv) were not first-class — `papers/` frontmatter exposed only `arxiv`, so 6 of the 11 papers we ingested had no canonical ID slot.
- Evidence verbs (`supports`, `contradicts`) could not express `wet_lab_validated`, `clinical_validated`, `mechanistic_basis`, `correlative`, `predicts` — the verbs domain experts actually use.
- Experiment cost was a single `estimated_hours` field, collapsing GPU-hours, MD wall-clock, wet-lab USD, and dataset-access lead time into one number that hid the real budget constraints.
- The graph carried no edge types for bio relations (`targets_protein`, `binds`, `degrades`, `phosphorylates`, `ubiquitinates`, …), validation/translation events (`clinical_trial_for`, `fda_approved_for`), or dataset-version provenance (`dataset_version_used`).

Full audit with one P0/P1/P2 entry per finding: [`docs/bioinformatics-adaptation-backlog.en.md`](../bioinformatics-adaptation-backlog.en.md) (zh: [`bioinformatics-adaptation-backlog.zh.md`](../bioinformatics-adaptation-backlog.zh.md)). Sections A–H were drafted on 2026-05-02; the eight A1–A8 schema items are the ones that have landed so far.

## 2. Integration timeline

Ten commits on top of upstream base `3ed31ed` (chronological):

```
53cfdb8 chore(integrate): pull upstream v1.1.0 — SSOT runtime + visualize + tools refactor
8efea8c chore(integrate): pull upstream v1.2.0 — daily-arxiv pipeline + workflow
e5cb75b chore(integrate): regenerate .claude/skills + CLAUDE.md from new i18n via setup.sh
b07c030 refactor(people): merge ## Key papers into ## Recent work for new schema
8d46f52 refactor(claims): migrate 15 wiki/claims/*.md → wiki/ideas/* per new schema
a83b15b feat(ptm): close PTM ideate cycle + finish claims-to-ideas migration for WIP
aba1670 refactor(graph): align WIP tested_by edges with experiment → idea direction
3e56592 chore(gitignore): exclude visualize-generated artifacts
787803b chore(integrate): pull upstream app/ SPA missed during v1.1.0 surgical-checkout
acc0c47 chore(gitignore): exclude .checkpoints/ (skill local state)
```

Reproduce locally: `git log --graph --oneline 3ed31ed..HEAD`.

The pattern is **three upstream pulls + three forward-migrations + four cleanup commits**:
- Upstream pulls (`53cfdb8`, `8efea8c`, `787803b`) bring in v1.1.0's SSOT runtime/visualize/tools refactor, v1.2.0's daily-arxiv pipeline, and the SPA bundle missed during the v1.1.0 surgical checkout.
- Forward-migrations (`b07c030`, `8d46f52`, `aba1670`) reshape the old wiki content to the new schema — people `Key papers → Recent work`, claims-to-ideas, and graph edge-direction fixes that fell out of the entity rename.
- Cleanup commits (`e5cb75b`, `a83b15b`, `3e56592`, `acc0c47`) regenerate `.claude/skills` from the new `i18n/`, close the PTM ideate cycle, and gitignore generated artifacts so the working tree stays clean.

## 3. Schema migration: `claims/` → `ideas/`

The largest forward-migration was the claims-to-ideas refactor (`8d46f52`). Upstream v1.1.0 deprecated `wiki/claims/` as a top-level entity and folded its content into `wiki/ideas/` with a richer lifecycle. We rewrote 15 pages and re-pointed 21 graph references.

Status field mapping (from upstream `runtime/schema/entities.yaml`):

| Old `claims/` status | New `ideas/` status | Meaning |
|---|---|---|
| `supported` | `validated` | Multiple independent supporting lines of evidence; high confidence |
| `weakly_supported` | `tested` | Some evidence but not yet conclusive |
| `disputed` | `tested` | Conflicting evidence; remains in active investigation |
| `unverified` | `proposed` | No direct evidence yet; hypothesis only |
| `refuted` | `failed` | Evidence rules out the hypothesis |

Migration touched:
- **15 page rewrites** — `wiki/claims/*.md` → `wiki/ideas/*.md`, frontmatter reshaped to ideas schema, `evidence` arrays converted to `pilot_result` + `failure_reason` where applicable.
- **21 graph-edge re-pointings** — `wiki/graph/edges.jsonl` references from `claims/{slug}` to `ideas/{slug}`.
- **1 index merge** — `wiki/index.md` `claims:` section folded into `ideas:`.
- **Graph edge direction fix** (`aba1670`) — `tested_by` edges that previously pointed `claim → experiment` were inverted to `experiment → idea` per the new edges-schema direction convention.
- **`wiki/claims/` deletion** — directory removed entirely; the entity type is gone from the wiki.

## 4. Lint metrics across the integration window

Captured by checking out each commit and running `tools/lint.py`. The columns are red (errors) / yellow (warnings) / blue (informational).

| # | Commit | State | 🔴 | 🟡 | 🔵 | Notes |
|---|---|---|---:|---:|---:|---|
| 0 | `3ed31ed` | Pre-integration baseline (old wiki + old lint) | 0 | 0 | 11 | Old lint over old wiki: clean. The 11 blue are pre-existing low-key_paper informational warnings. |
| 1 | `e5cb75b` | Post-integration, pre-migration (new lint + new templates + old wiki content) | 0 | **43** | 11 | New lint applied to old-shaped content surfaces 43 schema-mismatch warnings — mostly `claims/` pages and `people/` pages with the deprecated `## Key papers` section. |
| 2 | `b07c030` | After people migration (`Key papers → Recent work`) | 0 | **26** | 11 | -17 warnings (`people/` shape now aligned). Remaining yellows are `claims/` pages awaiting migration. |
| 3 | `8d46f52` | After claims-to-ideas migration | 0 | **0** | 11 | Fully clean against the new lint. |
| 4 | `acc0c47` | HEAD prior to pilot merges | 0 | 0 | 11 | Cleanliness preserved through PTM ideate cycle + graph edge-direction fix. |
| 5 | working tree (post pilots A1 minimal + A5 slice + A6 + B3 + A7 + A3 minimal + B1 full + B2 minimal + add-edge --metadata, 2026-05-11) | 0 | 0 | 11 | 10th entity `datasets/` registered + ternarydb authored; one experiment `setup.dataset` wikilinked; structured `estimated_cost` on all 8 experiments; **14 new edge types registered** (all 10 B1 + 3 B2 + 1 B3) → **35 total**; **Section B fully schema-registered 14/14**; **6 live bio edges** (3 B1 + 1 B2 + 2 B3, 2 of which carry typed metadata); `grade: low` on the PTM idea; `doi`+`pmid` on musitedeep paper. Identical blue informational set as row 4 — all pilots remain fully additive. |

The 11 remaining blue informational entries are documented in [section 6 / future work](#6-future-work) — they are `key_paper` counts ≤1 on `concepts/` pages that we know need broader citation coverage. Two are orphan `ideas/` pages with no incoming `tested_by` yet (the PTM ideate cycle proposed them but no experiment block addresses them).

**Note on the demo GIF storyboard.** The current `DEMO_PLAN.zh.md` Scene 1 promises that checking out `3ed31ed` and running lint will show "red and yellow all over." That expectation is incorrect — at `3ed31ed` the wiki is clean because both the wiki and the lint are still old-shaped. The lint warnings only appear *after* the upstream pulls (rows 1 → 2 → 3 above). The GIF should re-frame scene 1 as "before any migration, the upstream-merged state at `e5cb75b` shows 43 schema warnings; after both migrations, HEAD shows 0." User to decide whether to revise the storyboard or keep the current framing.

## 5. Section-level adaptation status

Schema-only changes (templates, frontmatter, lint hooks, skill prompts) are drafted under `docs/bio-adaptation/section-{a,b,c}/` as mirror copies of their source-of-truth files. When each section is adopted, the mirror hunks are merged back and the corresponding `CHANGELOG` entry is marked `STATUS: merged`.

| Section | Scope | Mirror location | Backlog items covered | Adoption status |
|---|---|---|---|---|
| A — Schema additions | Page templates + frontmatter (datasets/, protein anchors, bio identifiers, GRADE evidence, structured experiment cost) | [`section-a/runtime-page-templates.en.md`](section-a/runtime-page-templates.en.md), [`section-a/runtime-page-templates.zh.md`](section-a/runtime-page-templates.zh.md), [`section-a/CLAUDE.md`](section-a/CLAUDE.md) | A1–A8 | **A1 (minimal) + A2 (light) + A3 (minimal) + A5 (single-experiment slice) + A6 + A7 (minimal) all pilot-merged 2026-05-11; A4/A8 still drafted** |
| B — Graph rules | Bio relation edges, validation/translation edges, dataset-version provenance | [`section-b/runtime-support-files.en.md`](section-b/runtime-support-files.en.md), [`section-b/runtime-support-files.zh.md`](section-b/runtime-support-files.zh.md), [`section-b/CLAUDE.md`](section-b/CLAUDE.md) | B1–B3 | **Section B fully schema-registered 2026-05-11**: B1 (10/10 verbs, 3 live edges) + B2 (3/3 verbs, **1 live: validates_in_species with typed metadata `species=human`**) + B3 (1/1, **2 live, one with typed metadata `version=v1`**) — 14/14 total (35 edge types overall). `tools/research_wiki.py add-edge` now accepts `--metadata KEY=VALUE` (repeatable); 2 of 6 live bio edges carry typed `metadata.*` attributes. Loader-level nested-schema validation still deferred. |
| C — Skill prompts | Per-skill changes to `/ingest`, `/exp-design`, `/check`, `/ideate`, `/novelty`, `/paper-plan`, `/paper-draft`, `/rebuttal`, `/exp-run`, `/discover` | [`section-c/skills/{skill}/SKILL.{en,zh}.md`](section-c/skills/) | C1–C9 | **C1 + C2 minimal pilot-merged 2026-05-11** (C1: `/ingest` Step 2.5 bio identifier extraction; C2: `/exp-design` Step 6 emits A6 `estimated_cost` block — closes A6 ↔ C2 loop). Full versions of both still defer the planned bio fetcher / NER / cost-inference automation. C3–C9 still drafted. |

Cumulative item-by-item diff and rationale: [`CHANGELOG.en.md`](CHANGELOG.en.md) / [`CHANGELOG.zh.md`](CHANGELOG.zh.md).

## 6. Future work

Open at this snapshot:

- **Merge Section A, B, C mirrors into source-of-truth files**. Each section's CHANGELOG entry transitions from `STATUS: drafted` → `STATUS: merged` and the corresponding hunk is applied to `i18n/en/`, `i18n/zh/`, `runtime/schema/`, and the active skill prompts under `.claude/skills/`. Mirror cleanup follows.
- **Backlog Sections D–G** — skills not yet covered in Section C (paper-compile, ask, edit, …) and lint extensions that depend on A/B landing first.
- **Backlog Section H** — sub-area items (DNA sequencing, transcriptomics, single-cell, microbiome, clinical/population genomics, phylogenomics) are *extrapolated*, not grounded in observed wiki failures yet. Re-validate each on the first ingest in that sub-area.
- **The 11 blue informational lint entries** — 9 `concepts/` pages with single `key_paper` and 2 orphan `ideas/` pages (`chirality-aware-af3-diffusion`, `ptm-site-disorder-predictor`) flagged for incoming-link coverage. These accumulate naturally as more papers ingest.
- **Push target unresolved** — `origin/dev` upstream is deleted; the project's stated "branch from dev → PR to dev" convention does not currently apply. Confirm PR target (main? rebuild dev?) before pushing this branch.

For the running per-item changelog see [`CHANGELOG.en.md`](CHANGELOG.en.md) / [`CHANGELOG.zh.md`](CHANGELOG.zh.md).
