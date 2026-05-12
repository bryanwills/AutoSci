# Bio-Adaptation Session Checkpoint — 2026-05-11

> Mirror to its zh counterpart: [`CHECKPOINT-2026-05-11.zh.md`](CHECKPOINT-2026-05-11.zh.md). Substantive edits must be applied to both.
>
> Frozen snapshot of bio-adaptation pilot progress as of end-of-session 2026-05-11. **Nothing is committed yet** — the next conversation can either continue piling on pilots or proceed to the commit-split / push.

## 1. Where the branch stands

- **Branch**: `feat/qwt-ptm-degrader-ideate`
- **HEAD commit** (last committed): `acc0c47` — `chore(gitignore): exclude .checkpoints/ (skill local state)`
- **Working tree**: 27 modified + 5 untracked dirs/files. **All uncommitted.**
- **Lint**: `0 🔴 / 0 🟡 / 11 🔵` (identical blue-informational set to baseline — all pilots are fully additive)
- **Push target**: still undecided (`origin/dev` is deleted; project's `branch-from-dev → PR-to-dev` convention not currently applicable)

## 2. The 13 pilots merged this session

| # | Pilot | Type | Status |
|---|---|---|---|
| 1 | A1 minimal | schema (new entity type) | `datasets/` registered + ternarydb.md authored |
| 2 | A2 light | schema (new optional fields) | concepts/ gets gene_symbol+uniprot_id+pdb_ids+species; crbn.md authored |
| 3 | A3 minimal | schema (new optional fields) | papers/ gets doi+pmid; musitedeep populated |
| 4 | A5 slice | content rewire | deepternary-baseline setup.dataset wikilinked |
| 5 | A6 | schema (new structured block) | estimated_cost on all 8 experiment pages |
| 6 | A7 minimal | schema (new optional field) | ideas/ gets grade enum; PTM idea filled `grade: low` |
| 7 | B1 full | 10 new edge types | targets_protein, binds, inhibits, activates, degrades, phosphorylates, ubiquitinates, methylates, acetylates, is_substrate_of |
| 8 | B2 minimal | 3 new edge types | clinical_trial_for, fda_approved_for, validates_in_species |
| 9 | B3 minimal | 1 new edge type | dataset_version_used |
| 10 | `add-edge --metadata` CLI | first Python code change | typed metadata serialization in edge JSON |
| 11 | C1 minimal | skill prompt | /ingest Step 2.5 bio identifier extraction (LLM-in-prompt NER) |
| 12 | C2 minimal | skill prompt | /exp-design Step 6 emits A6 estimated_cost block — closes A6↔C2 loop |
| 13 | A2 light B1 follow-up | live content | binds edge from PROTAC drug class to CRBN with typed metadata |

(A2 light is a pair: schema change + first live protein concept + B1 edge — counted as one pilot.)

## 3. Final data snapshot

```
entities: 10                            (datasets/ as 10th, A1 minimal)
edge types: 35                          (+14 from upstream baseline of 21)
  ├── Section B coverage: 14/14         (B1 ×10 + B2 ×3 + B3 ×1)
  └── live bio relation edges: 7         (3 B1 + 1 B2 + 2 B3 + 1 more B1 from CRBN)

graph edges: 80                          (+7 bio relation edges)
edges with typed metadata.*: 3          (via add-edge --metadata CLI)

specific protein concept pages: 1       (crbn.md, A2 light)
A6 structured-cost coverage: 8/8 experiments  (sum 96 gpu_h + 8 md_wallclock_h = 104 h)

SKILL.md updated: 2 of 24 skills        (ingest 297→327, exp-design 351→366)
runtime/schema/entities.yaml: +datasets entity + 5 field-set extensions (papers/concepts/ideas/experiments) + bio-A6 estimated_cost block
runtime/schema/edges.yaml: +14 bio edge types
tools/research_wiki.py: +metadata flag in add-edge CLI (~10 LoC net)

lint: 0 🔴 / 0 🟡 / 11 🔵                (informational set unchanged across all 13 pilots)
```

## 4. Section-by-section coverage

| Section | Status | What's merged | What's drafted |
|---|---|---|---|
| **A — Schema additions** | **6/8 items merged** | A1 minimal, A2 light, A3 minimal, A5 slice, A6, A7 minimal | A4 (domain controlled vocab), A8 (paper_style) |
| **B — Graph rules** | **14/14 edge types registered** | B1 full, B2 minimal, B3 minimal (schema complete; live-edge density varies) | typed metadata nested-schema validation; full content via C1 bio NER |
| **C — Skill prompts** | **2/9 items merged** | C1 minimal (`/ingest`), C2 minimal (`/exp-design`) | C3 (lint_bio.py), C4 (/ideate), C5 (/novelty), C6 (/paper-plan), C7 (/paper-draft), C8 (/rebuttal), C9 (/exp-run, /discover) |
| **Infrastructure** | 1 Python change | `add-edge --metadata KEY=VALUE` (repeatable) | `validate_edge_attributes` nested-metadata schema validation |
| **Outside scope (this session)** | — | — | Sections D–G (other skills), Section H (sub-area validation) |

## 5. Working-tree manifest

**Modified (27 files):**

```
.claude/skills/exp-design/SKILL.md       # C2 minimal
.claude/skills/ingest/SKILL.md           # C1 minimal
README.md                                 # bio-adaptation hero + See-it-live (en+zh)
docs/runtime-page-templates.en.md         # A1/A2/A3/A6/A7 template updates
docs/runtime-page-templates.zh.md         # same (zh mirror)
i18n/en/skills/exp-design/SKILL.md        # C2 minimal source
i18n/en/skills/ingest/SKILL.md            # C1 minimal source
i18n/zh/skills/exp-design/SKILL.md        # C2 minimal zh source
i18n/zh/skills/ingest/SKILL.md            # C1 minimal zh source
runtime/schema/edges.yaml                 # +14 bio edge types (B1+B2+B3)
runtime/schema/entities.yaml              # +datasets + concepts protein anchors + ideas.grade + papers doi/pmid + experiments.estimated_cost
tools/research_wiki.py                    # add-edge --metadata extension
wiki/experiments/*.md (8 files)            # A6 estimated_cost block
wiki/graph/context_brief.md                # rebuilt
wiki/graph/edges.jsonl                     # +7 bio relation edges (3 with metadata)
wiki/graph/open_questions.md               # rebuilt
wiki/ideas/ptm-aware-degrader-target-nomination.md   # A7 grade: low
wiki/index.md                              # datasets: + crbn concept
wiki/log.md                                # session milestones (×14)
wiki/papers/musitedeep-deep-learning-based-webserver-protein.md   # A3 doi+pmid
```

**Untracked (new files):**

```
demo/run-demo.sh                          # daily-arxiv replay
demo/sample-feed.json                     # 9-paper mock feed
docs/bio-adaptation/                      # this whole directory
  ├── CHANGELOG.{en,zh}.md                 # cumulative diffs incl. all 13 pilots
  ├── DEMO_PLAN.{en,zh}.md                 # v2 user-facing plan
  ├── REPORT.{en,zh}.md                    # full evidence
  ├── CHECKPOINT-2026-05-11.{en,zh}.md     # this file
  ├── preview/                              # 3 caption-material previews
  └── section-{a,b,c}/                      # original drafts
docs/bioinformatics-adaptation-backlog.{en,zh}.md   # P0/P1/P2 audit
examples/output/digest-sample.md          # pre-rendered LLM-ranked output
runtime/templates/datasets.md.tmpl        # A1 minimal
wiki/concepts/crbn.md                     # A2 light first protein concept
wiki/datasets/ternarydb.md                # A1 minimal first dataset page
```

## 6. Recommended commit-split (4 commits)

This is the **revised** version of the earlier 3-commit proposal — pilots 10–13 added enough surface (Python CLI change, skill prompt changes, new concept page) that splitting into 4 reads more cleanly. All `git add <file>` only — no `-p` hunk surgery needed.

```bash
# ============================================================
# Commit 1: Bio-adaptation foundations (backlog + design docs)
# ============================================================
git add docs/bioinformatics-adaptation-backlog.en.md
git add docs/bioinformatics-adaptation-backlog.zh.md
git add docs/bio-adaptation/                # all CHANGELOG/REPORT/DEMO_PLAN/CHECKPOINT/section/preview
git add demo/ examples/                     # demo + pre-rendered output

# ============================================================
# Commit 2: Pilot merges — schema + content (Sections A + B)
# ============================================================
git add runtime/schema/entities.yaml         # A1, A2 light, A3, A6, A7
git add runtime/schema/edges.yaml            # B1 full, B2 minimal, B3 minimal
git add runtime/templates/datasets.md.tmpl   # A1 minimal template
git add docs/runtime-page-templates.en.md docs/runtime-page-templates.zh.md
git add wiki/datasets/ wiki/concepts/crbn.md
git add wiki/experiments/                    # A6 on all 8
git add wiki/papers/musitedeep-deep-learning-based-webserver-protein.md   # A3
git add wiki/ideas/ptm-aware-degrader-target-nomination.md                 # A7
git add wiki/index.md
git add wiki/log.md
git add wiki/graph/edges.jsonl wiki/graph/context_brief.md wiki/graph/open_questions.md

# ============================================================
# Commit 3: Tools — add-edge --metadata CLI extension
# ============================================================
git add tools/research_wiki.py

# ============================================================
# Commit 4: Skill prompts — C1 + C2 minimal
# ============================================================
git add i18n/en/skills/exp-design/SKILL.md i18n/zh/skills/exp-design/SKILL.md   # C2
git add i18n/en/skills/ingest/SKILL.md i18n/zh/skills/ingest/SKILL.md           # C1
git add .claude/skills/exp-design/SKILL.md .claude/skills/ingest/SKILL.md       # active synced

# ============================================================
# Commit 5: README hero
# ============================================================
git add README.md
```

This is actually 5 commits — clearer separation between content (commit 2), tools (3), and skill prompts (4). Alternatively, lump 3+4 if the user wants 4 commits flat.

## 7. Outstanding decisions for the user

| Decision | Options |
|---|---|
| Push target | `origin/dev` rebuild? Direct PR to main? Stay un-pushed? |
| Commit grouping | 5-commit split above, or different boundaries (e.g. lump infra + skills)? |
| Asset recording | Record `assets/demo.gif`, export `assets/canvas-ptm-focus.png`, capture `assets/graph-view.png` (per DEMO_PLAN §6 storyboard, now factually accurate against the 13-pilot state) |
| Continue piloting? | A4, C5, C7, C3 (Python tool), …  — see DEMO_PLAN §7 |

## 8. Resume instructions for a new conversation

```
Read docs/bio-adaptation/CHECKPOINT-2026-05-11.en.md (or .zh.md). Branch
feat/qwt-ptm-degrader-ideate @ acc0c47; lint clean (0 🔴 / 0 🟡 / 11 🔵).

13 bio-adaptation pilots are merged in the working tree but NOT committed yet.
The 5-commit-split proposal lives in CHECKPOINT §6; outstanding decisions in §7.
Section coverage in §4 — A 6/8 items, B 14/14 edge types, C 2/9 items.

To resume piloting: pick from §7 "Continue piloting?" or DEMO_PLAN §7.
To resume on commits: execute §6 then decide push target.
To resume on assets/demo: DEMO_PLAN §6 storyboard is accurate against
current 13-pilot state.
```

## 9. What this session unblocks

Most of the value of this session is **schema and prompt-level capability**, not graph content:

- Future `/ingest` calls on bio papers will auto-populate `doi`/`pmid` and wikilink dataset mentions (C1 minimal).
- Future `/exp-design` calls will emit A6-compliant `estimated_cost` blocks (C2 minimal).
- All 14 Section B edge types are immediately usable via `add-edge` — no further schema work needed before populating live edges.
- `add-edge --metadata KEY=VALUE` lets any future edge carry typed attributes without further Python changes.
- A2 light's `concepts/` protein-anchor pattern means the next 49 specific-protein concept pages can be added without touching schema. The 50th would justify the A2 heavy `proteins/` entity-type promotion.

The bio research workflow that originally motivated the fork (PTM-aware degrader ideate cycle, 8 experiments, 11 papers) is now end-to-end represented in bio-shaped data structures, not CS-shaped text fields.
