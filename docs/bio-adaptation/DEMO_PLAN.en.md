# Bio-Adaptation Demo Plan (v2 — user-facing)

> Mirror to its zh counterpart: [`DEMO_PLAN.zh.md`](DEMO_PLAN.zh.md). Substantive edits must be applied to both.
>
> v1 organized around integration mechanics (commit timeline, lint metrics, claims→ideas migration). v2 organizes around what a bio researcher gets — added features, behaviour changes, and a worked example. v1's integration narrative is preserved in [`REPORT.en.md`](REPORT.en.md).

## 1. Pitch (one-liner per audience)

- **Repo visitor**: ΩmegaWiki / bio-adaptation makes the CS-shaped upstream usable for biology research — datasets, proteins, DOI papers become first-class; the graph carries bio relation edges; skills understand wet-lab budgets and GRADE evidence. We proved it on a real PTM-aware degrader nomination workflow.
- **Bio researcher**: Drop a PROTAC or PTM paper in. The wiki creates a typed entry with bio identifiers, links datasets and target proteins, captures clinical evidence with GRADE confidence. `/exp-design` gives a realistic budget that includes wet-lab USD and dataset-access lead time, not just GPU hours.
- **Contributor**: 20 backlog items (A1–A8, B1–B3, C1–C9) are drafted as merge-ready mirrors under `docs/bio-adaptation/section-{a,b,c}/`. Live wiki has already absorbed the schema-neutral upgrades (ideas lifecycle, people Recent-work). Section A/B/C are additive and ready for adoption.

## 2. Feature catalogue

Three blocks. Each row shows (a) what the feature does, (b) what a user sees, (c) live/drafted status.

### 2.1 Schema (Section A — 8 items)

| # | Feature | What a user sees | Status |
|---|---------|------------------|--------|
| A1 | `datasets/` as 10th entity type | `[[ternarydb]]` wikilinks with version, access tier, source papers | **pilot-merged 2026-05-11** (minimal slice; full ingest-time auto-create deferred to C1) |
| A2 | Protein anchors on `concepts/` | `concepts/p53.md` carries `uniprot_id`, `pdb_ids`, `species` | **A2 light pilot-merged 2026-05-11** (4 optional fields on concepts/; first specific-protein concept page `concepts/crbn.md` authored with HGNC + UniProt + PDB + species filled; A2 heavy / `proteins/` entity type deferred) |
| A3 | Bio paper IDs in `papers/` frontmatter | DOI / PMID / bioRxiv / s2_id slots, not just `arxiv` | **A3 minimal pilot-merged 2026-05-11** (doi + pmid added; one paper populated; biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species deferred to C1 bio NER) |
| A4 | `paper_style` aware of venue | `/paper-draft` switches to result-first for bio venues | drafted |
| A5 | `setup.dataset` as wikilink | `/exp-design` outputs `[[ternarydb]]` instead of plain string | **pilot-merged 2026-05-11** (single-experiment slice; remaining 7 experiments still plain-string, full A5 bio modality fields deferred) |
| A6 | Structured `estimated_cost` block | gpu_hours / md_wallclock_hours / wet_lab_usd / fte_weeks / dataset_access_lead_time_days | drafted |
| A7 | Extended evidence verbs + GRADE | `wet_lab_validated`, `clinical_validated`, `mechanistic_basis`, `correlative`, `predicts`; optional `grade: very-low \| low \| moderate \| high` | **A7 minimal pilot-merged 2026-05-11** (top-level optional `grade` field on ideas/; one idea populated `grade: low`; per-edge GRADE + extended evidence verbs deferred) |
| A8 | Bio domain vocabulary | `domain: structural-bio \| chembio \| comp-drug-discovery \| ...` enforced by lint | drafted |

### 2.2 Graph (Section B — 3 items)

| # | Feature | What a user sees | Status |
|---|---------|------------------|--------|
| B1 | Bio relation edges | Graph carries `targets_protein`, `binds`, `inhibits`, `activates`, `degrades`, `phosphorylates`, `ubiquitinates`, `methylates`, `acetylates`, `is_substrate_of` | **B1 full pilot-merged 2026-05-11** (10/10 verbs registered; 3 live edges: `targets_protein` + `ubiquitinates` + `binds`; remaining 7 verbs await C1 bio NER for systematic live-edge content) |
| B2 | Validation / translation edges | `clinical_trial_for`, `fda_approved_for`, `validates_in_species` with typed metadata (trial id, phase, species) | **B2 minimal pilot-merged 2026-05-11** (3/3 verbs registered; 1 live `validates_in_species` edge with typed `metadata: {species: human, source_db: uniprotkb-swissprot}` enabled by the `add-edge --metadata` CLI extension; remaining 2 verbs await wiki content with clinical-trial/FDA-approval anchors) |
| B3 | Dataset-version provenance edge | `experiment → dataset` carries `dataset_version_used` with `metadata.version` | **pilot-merged 2026-05-11** (edge type registered; 1 live edge `deepternary-baseline → ternarydb`; version info in `evidence` string for now, typed `metadata.version` deferred until add-edge CLI is extended) |

### 2.3 Skills (Section C — 9 items)

| # | Skill | What a user sees | Status |
|---|-------|------------------|--------|
| C1 | `/ingest` | Bio NER pre-pass; auto-links datasets/proteins; preserves DOI/PMID; JATS-XML treated as `.tex` | **C1 minimal pilot-merged 2026-05-11** (new Step 2.5 in SKILL.md asks LLM agent to populate doi+pmid + upgrade dataset mentions to `[[ ]]` wikilinks; full fetcher tools + structured NER + DOI/PMID inputs deferred) |
| C2 | `/exp-design` | Structured cost block; realistic wet-lab / MD budgeting; budget-cut order fixed | **C2 minimal pilot-merged 2026-05-11** (Step 6 frontmatter template emits A6 `estimated_cost` block on every new experiment; closes A6 ↔ C2 loop; automated framework-driven inference + fixed budget-cut order deferred) |
| C3 | `/check` | New `tools/lint_bio.py` validates bio frontmatter (UniProt format, GRADE consistency, dataset version drift) | drafted |
| C4 | `/ideate` | Surfaces bio relation gaps (untargeted proteins, unverified phosphorylation) alongside claim gaps | drafted |
| C5 | `/novelty` | GRADE-weighted scoring; bio prior-art search (Semantic Scholar bio subset) | drafted |
| C6 | `/paper-plan` | Venue-aware `paper_style` resolution (Nature wins over claim domain on disagreement) | drafted |
| C7 | `/paper-draft` | Result-first writing for bio claims; embedded biostatistics; bio caption format | drafted |
| C8 | `/rebuttal` | Bio reviewer concerns (mechanism, clinical relevance, cohort generalisation) | drafted |
| C9 | `/exp-run`, `/discover` | Wet-lab handoff hooks; bio paper discovery profiles | drafted |

Item-by-item rationale: [`CHANGELOG.en.md`](CHANGELOG.en.md).

## 3. Already live in the wiki

These changes are merged and you can verify them right now:

| Change | Live since | Effect for the user |
|--------|-----------|---------------------|
| Upstream v1.1.0 SSOT runtime + visualize | `53cfdb8` | One source of truth for templates/edges; SPA at `http://127.0.0.1:8765/` |
| Upstream v1.2.0 daily-arxiv pipeline | `8efea8c` | `python tools/daily_arxiv.py prepare/recommend-llm/finalize` runs end-to-end with DeepSeek v4-flash |
| `people/` schema refactor | `b07c030` | Person pages use `## Recent work` (not the deprecated `## Key papers`) |
| **claims/ → ideas/ lifecycle migration** | `8d46f52` | 15 former claims now live as ideas with richer status (`proposed`/`tested`/`validated`/`failed`); 21 graph edges re-pointed; lint goes from 26 🟡 to 0 🟡 |
| Graph edge direction fix | `aba1670` | `tested_by` edges flow `experiment → idea` per new convention |
| Gitignore cleanups | `3e56592`, `acc0c47` | Generated artifacts (visualize outputs, `.checkpoints/`) stay out of git |

Snapshot at `feat/qwt-ptm-degrader-ideate @ acc0c47` (2026-05-11): lint `0 🔴 / 0 🟡 / 11 🔵`, wiki carries 11 papers / 22 ideas / 8 experiments / 16 people / 73 graph edges + 1 citation.

## 4. Worked example — PTM-aware degrader workflow

The whole adaptation was driven by trying to do real biology research. The pipeline we ran end-to-end:

1. **Seed wiki** with 11 structural-biology / PTM / drug-design papers — AlphaFold 2 & 3, AlphaFold-DB 2024, MusiteDeep, geometric DL for molecules, E3 ubiquitin ligase platforms (Ronai), multi-omics for targeted therapy, DegronMD-style PTM-substrate networks.
2. **`/ideate`** on the seeded wiki → 3 ideas proposed with priorities 5/4/5, 2 ideas filtered out to banlist. Anchor: [`ideas/ptm-aware-degrader-target-nomination`](../../wiki/ideas/ptm-aware-degrader-target-nomination.md) — uses noise-floor-calibrated ΔpTernary to rank PTM-isoform-selective degraders.
3. **`/exp-design`** on that anchor → 8 experiments across 5 stages (sanity → baseline → Phase-0 noise-floor → primary validation → ablations → robustness), total budget ≈ 104 GPU-h. Each links back to the idea via `linked_idea`; each idea decomposition writes `target_claim` (legacy field name from pre-migration).
4. **`/daily-arxiv`** with a 9-paper q-bio.BM sample feed → DeepSeek v4-flash ranks 5 strong / 3 maybe / 1 skip. Output preserved in [`examples/output/digest-sample.md`](../../examples/output/digest-sample.md).
5. **Where each feature shows up in this workflow** (today's live shape vs proposed shape):

| Feature | Where it surfaces | Today | After section A/B/C merge |
|---------|-------------------|-------|---------------------------|
| A3 bio IDs | `wiki/papers/musitedeep-...md` frontmatter | `arxiv: ""` (no slot for the DOI in the body) | `doi: 10.1093/nar/gkaa275` populated |
| A5 dataset wikilink | `wiki/experiments/deepternary-baseline.md` `setup.dataset` | **live** — `[[ternarydb]] CRBN+VHL test split ...` wikilink, plus `wiki/datasets/ternarydb.md` page. 7 sibling experiments still plain-string by design (backward-compat demo). | full A5 will rewire all 8 experiments and extend `setup` with `in_silico_or_wet`, `species`, `cell_line`, `assay_type`, `force_field` |
| A6 structured cost | same experiment, `estimated_*` fields | `estimated_hours: 4` | `estimated_cost: { gpu_hours: 4, dataset_access_lead_time_days: 7, ... }` |
| A7 GRADE evidence | `wiki/ideas/ptm-aware-degrader-target-nomination.md` `origin_gaps` evidence | only `confidence: 0.6` on the gap claim | + `grade: moderate`, evidence type `mechanistic_basis` |
| B1 bio edges | `wiki/graph/edges.jsonl` | 8 edge types live; no bio relations | + `targets_protein`, `phosphorylates`, …; emitted by `/ingest` C1 |
| C7 bio writing | `/paper-draft` output for a future bio paper | CS claim-first | result-first with embedded biostatistics |

## 5. Demo deliverables

Already produced this session:

- ✅ [`REPORT.en.md`](REPORT.en.md) / [`REPORT.zh.md`](REPORT.zh.md) — full evidence, integration timeline, lint metrics, section-A/B/C status
- ✅ [`demo/run-demo.sh`](../../demo/run-demo.sh) — runnable 3-step daily-arxiv pipeline with bilingual headers; gracefully degrades without DeepSeek key
- ✅ [`demo/sample-feed.json`](../../demo/sample-feed.json) — 9-paper q-bio.BM mock feed
- ✅ [`examples/output/digest-sample.md`](../../examples/output/digest-sample.md) — pre-rendered DeepSeek-ranked output (no API quota needed)
- ✅ `wiki/log.md` milestone entry for 2026-05-11
- ✅ README.md bilingual bio-adaptation hero section

Open deliverables (split below):

- ⏳ `assets/demo.gif` — 30–60s walkthrough per §6 storyboard (user records)
- ⏳ `assets/canvas-ptm-focus.png` — Obsidian canvas export, PTM neighborhood (user exports)
- ⏳ `assets/graph-view.png` — SPA full graph screenshot (user captures)
- ❓ `assets/feature-preview-*.png` — static mockups for drafted-but-not-live features (see §8 data audit for which scenes need them)

## 6. New GIF storyboard — 5 scenes × ~10s ≈ 50s

The storyboard is anchored on real wiki pages. Each scene calls out which feature is live vs drafted so the demo stays honest.

| # | Time | Content | Feature highlighted | Live or drafted? |
|---|------|---------|---------------------|------------------|
| 1 | 8s | Open `wiki/papers/musitedeep-deep-learning-based-webserver-protein.md` — show rich frontmatter: `doi: 10.1093/nar/gkaa275`, `pmid: 32324217` (A3 minimal pilot), `domain: Bioinformatics`, `venue: Nucleic Acids Research`, `code_url: github.com/duolinwang/MusiteDeep_web`; caption notes the remaining A3 fields (biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species) are deferred to C1 bio NER | live A3 minimal | **live** (DOI/PMID visible); remaining A3 caption |
| 2 | 12s | Open `wiki/ideas/ptm-aware-degrader-target-nomination.md` — scroll past Motivation / Hypothesis / Approach; highlight `grade: low` (A7 minimal pilot), `linked_experiments` (8 entries), `status: in_progress`, `pilot_result` slot, `origin_gaps` wikilinks; caption: per-edge GRADE + extended evidence verbs (wet_lab_validated, mechanistic_basis, …) are full-A7 territory, deferred | live A7 minimal + ideas-lifecycle | **live** (GRADE on idea + status/links); full A7 caption |
| 3 | 12s | Open `wiki/experiments/deepternary-baseline-ternarydb-crbn-vhl-reproduction.md` — `setup.dataset` resolves to `[[ternarydb]]`; click through to `wiki/datasets/ternarydb.md` (Overview / Versions / Access / Used by experiments / Known caveats); pan back to the experiment; `estimated_hours: 4` still single-number with side caption showing the section-a structured `estimated_cost` block | A1 + A5 live; A6 caption | **live** (experiment + datasets/ternarydb.md as of pilot merge 2026-05-11); A6 caption only |
| 4 | 12s | Open SPA at `http://127.0.0.1:8765/` — pan around the PTM-aware degrader neighborhood; hover bio edges across all three section-b families: B1 — `targets_protein`, `ubiquitinates`, `binds`; B2 — `validates_in_species` (musitedeep → post-translational-modification-site-prediction, **typed metadata `{species: human, source_db: uniprotkb-swissprot}`**); B3 — `dataset_version_used` ×2 (deepternary-baseline → ternarydb with version in evidence string; phase0-noise-floor → ternarydb with **typed metadata `{version: v1, subset: crbn-vhl-training}`**); also show an `experiment → idea` `tested_by` edge for direction comparison; caption overlay names the 7 B1 verbs + 2 B2 verbs that lack live edges pending C1 bio NER | live `tested_by` + 6× bio edges across B1/B2/B3 | **live** (35 edge types; **all 3 section-b families have live edges**; 2 edges demonstrate typed `metadata.*` via the new `add-edge --metadata` CLI) |
| 5 | 8s | Terminal pane: `bash demo/run-demo.sh` → digest.md opens, showing DeepSeek strong/maybe/skip recommendations | live daily-arxiv | live |

**Tooling**: Linux/WSL: `peek` or OBS + `gifski`; macOS: `Kap`; terminal-only segments: `asciinema rec` + `agg`. Encode with `ffmpeg -i input.mp4 -vf fps=12,scale=900:-1 -f image2pipe - | gifski - -o demo.gif`. Target < 5 MB for GitHub.

## 7. Task split

### Claude can do (no manual interaction)

- [ ] Refactor `REPORT.{en,zh}.md` so §2 leads with the feature catalogue (currently leads with integration timeline). Integration timeline becomes appendix.
- [ ] Tighten README hero with a "what bio researchers get" 3-bullet lede before the comparison table.
- [ ] Optionally author static feature-preview pages under `docs/bio-adaptation/preview/` to support scenes 1–4 (see §8 for which are needed). Bilingually mirrored.

### User must do (local / interactive)

- [ ] Record `assets/demo.gif` per §6 storyboard.
- [ ] Obsidian: export `assets/canvas-ptm-focus.png`.
- [ ] Browser: capture `assets/graph-view.png` from `http://127.0.0.1:8765/`.
- [ ] Drop assets into `assets/`; push branch.

## 8. Data audit — what's still missing for the storyboard

The user offered to re-run any pipeline that produces data the demo needs. **The honest answer: there is no missing pipeline data. The gap is feature-status, not data.** Each storyboard scene currently shows real wiki state; what's "missing" is the *drafted features* that haven't been merged into source-of-truth files yet.

Per-scene readiness:

| Scene | Live data ready? | Gap | What helps |
|-------|------------------|-----|------------|
| 1 (paper page) | ✅ `musitedeep-...md` is rich; **`doi`+`pmid` populated** (A3 minimal pilot 2026-05-11) | Remaining 6 A3 fields (biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species) still drafted | Caption overlay names the deferred 6; `docs/bio-adaptation/preview/paper-with-bio-ids.md` shows full A3 form for reference. C1 (bio NER) ingest-time auto-fill remains the unblocking move for non-pilot papers. |
| 2 (idea page) | ✅ `ptm-aware-degrader-target-nomination.md` is rich; live ideas-lifecycle status visible; **`grade: low` populated** (A7 minimal pilot 2026-05-11) | `pilot_result` slot is empty (no /exp-run done); per-edge GRADE and extended evidence verbs still drafted | Caption-only for full A7. *pilot_result* would require running `/exp-run` on at least the baseline experiment — heavy (real GPU compute) — **not recommended as a demo prep task** |
| 3 (experiment page) | ✅ `deepternary-baseline-...md` is rich; `setup.dataset: [[ternarydb]]` is live; `wiki/datasets/ternarydb.md` is live | A6 structured cost block still drafted; `estimated_hours: 4` remains the live shape | Static caption overlay showing section-a's `estimated_cost` proposal. A6 pilot merge remains an open option if the storyboard wants this live too. |
| 4 (SPA graph) | ✅ 79 edges, **35 edge types live**; **6 live bio edges across all 3 section-b families** (3 B1 + 1 B2 + 2 B3); ternarydb + ubiquitin-ligase-e3 + post-translational-modification-site-prediction concepts are connected hubs; **`add-edge --metadata` CLI extension live** — 2 of 6 edges carry typed `metadata.*` (1 B2 + 1 B3) | 7/10 B1 verbs and 2/3 B2 verbs still lack live edges pending C1 bio NER for systematic content extraction | Adding more live edges is a small additive step now that the CLI supports typed metadata; major remaining unblock is the C1 skill-prompt update (bio NER pre-pass in `/ingest`). |
| 5 (digest) | ✅ `digest-sample.md` ready, `run-demo.sh` ready | None | — |

**Things a re-run would NOT help with** (because the features aren't merged):

- Re-running `/ingest` on a bio paper today produces the same shape we already have — no DOI/PMID frontmatter, no bio NER pre-pass.
- Re-running `/exp-design` reproduces the same `estimated_hours` field.
- Re-running `/novelty` is not GRADE-weighted yet.
- Re-running `/visualize` may regenerate canvas files but won't introduce bio edge types.

**Things a re-run WOULD help with**:

- **`/daily-arxiv` on a fresh feed** — produces a real-day digest instead of the mock. Useful for "this works in production today" framing but not strictly needed for the storyboard.
- **`/exp-status` snapshot for the GIF caption** — quick read of current state. Tiny.

**If you want scenes 1–4 to show features *live* rather than via caption overlays, the unblocking move is a pilot merge of one or two A/B items.** Two cheap candidates:

- **A6 (structured cost) + a one-off rewrite of 8 experiment pages** — small mechanical edit; immediately gives scene 3 a live structured-cost demo. **Remaining open option.**
- ~~**A5 + A1 minimal (create `wiki/datasets/ternarydb.md` + repoint one experiment's `setup.dataset`)**~~ — **landed on 2026-05-11**; see CHANGELOG entry of that date for the per-file diff.

Neither requires touching upstream skill prompts (C1–C9) or graph rules (B1–B3); they are isolated additive schema moves. Decision is yours — flag if you want me to do either.

## 9. Open / undecided

- **Push target.** `origin/dev` upstream is deleted; the project's "branch from dev → PR to dev" convention does not currently apply. Confirm PR target before pushing.
- **Section A/B/C merge timing.** 20 drafted items — single PR or staged by section? Demo strength depends on this.
- **Section H validation.** Sub-area items (DNA seq, transcriptomics, single-cell, microbiome, clinical genomics, phylogenomics) are extrapolated; re-validate at first ingest in each sub-area.

## Resume instructions for a new conversation

```
Session 2026-05-11 closed with 13 pilots merged in the working tree (not committed).
Read docs/bio-adaptation/CHECKPOINT-2026-05-11.en.md first — it has the full snapshot,
commit-split proposal, and outstanding decisions.

Branch feat/qwt-ptm-degrader-ideate @ acc0c47 (last committed); lint clean (0/0/11).
Section coverage: A 6/8 + B 14/14 edge types + C 2/9; A2 light added the first specific
protein concept page (crbn.md); add-edge CLI now accepts --metadata KEY=VALUE.

If continuing pilots: pick from CHECKPOINT §7 or DEMO_PLAN §7.
If committing: execute CHECKPOINT §6 (5-commit split), then decide push target.
If recording demo assets: DEMO_PLAN §6 storyboard is accurate against current state.
```
