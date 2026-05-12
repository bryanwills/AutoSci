# OmegaWiki — Bioinformatics Adaptation Backlog

> A working list of CS-centric assumptions in OmegaWiki that hurt bioinformatics use, plus a feasibility audit of the 8 experiments designed by `/exp-design ptm-aware-degrader-target-nomination` on 2026-05-02. Items are tagged P0 (blocks bio work or produces actively misleading output), P1 (significant friction), P2 (nice-to-have polish).
>
> Verify and tackle items one at a time. Each entry is independent.
>
> **Scope**: Sections A-G are grounded in a single protein / PTM / drug-design `/exp-design` run. They cover that vertical well but under-represent the rest of bioinformatics — DNA sequencing, transcriptomics, epigenomics, single-cell, microbiome, clinical genomics, population/statistical genetics, phylogenomics. **Section H** (added 2026-05-02) extrapolates items for those sub-areas from general bio practice, but unlike A-G, H is **not yet grounded in observed wiki failures**. Re-validate each H item the first time the wiki actually ingests a paper or runs `/exp-design` in that sub-area; expect some items to turn out unnecessary or differently shaped.
>
> **What stays unchanged**: the 9-page-type skeleton, wikilink syntax, bidirectional reverse-link rule, log/index conventions, graph-via-tool discipline. Bio adaptations are additive.
>
> **Sync convention**: this file mirrors `bioinformatics-adaptation-backlog.zh.md`. Any substantive change to either must be applied to the other.

---

## Section A — Schema additions (page templates and frontmatter)

### A1 — [P0] Add `datasets/` as a first-class entity type

**Evidence**: Throughout this `/exp-design` run I referenced **TernaryDB**, **PROTAC-DB**, **DegronMD**, **AlphaFold-DB**, **PhosphoSitePlus**, **dbPTM**, **UniProt**, **PDB**, **PROTAC-DB CRBN+VHL subset** as free text. None resolves to a wikilink. Future ideas in this domain will keep re-introducing them, with no canonical place to record (a) what the dataset is, (b) which version was used, (c) what the access constraints are, (d) which papers it appears in.

**Fix**: Add `wiki/datasets/{slug}.md` with frontmatter:

```yaml
---
title: ""
slug: ""
aliases: []
tags: []
maturity: stable          # stable | active | emerging | deprecated
access: public            # public | registration | restricted | wet-lab-derived
versions: []              # list of {version, released, url, n_entries, notes}
canonical_url: ""
license: ""
key_papers: []            # reverse-linked from papers
key_concepts: []
date_updated: YYYY-MM-DD
---
```

**Impact**: `/ingest` should auto-detect dataset mentions; `/exp-design` should auto-link `setup.dataset` to a wikilink target.

**Validation**: migrate **TernaryDB** as a pilot; re-run `/exp-design` on a sibling idea; confirm dataset reference becomes a wikilink.

---

### A2 — [P1] Add `proteins/` (or extend `concepts/`) for UniProt-anchored entities

**Evidence**: I referenced **p53**, **CRBN**, **VHL**, **MDM2**, **IAP**, **EZH2**, **BTK**, **ABL1**, **BCL-XL**, **BRCA1**, **HIF1α**, **14-3-3**, **PCNA**, **FOXO3a**, **Pol-η**, **HER2** without entity pages. These are not "concepts"; they are specific gene products with UniProt accessions, sequences, known PTMs, structures, and drug binders. Currently each appears only as inline text inside paper / claim bodies.

**Fix option (lightweight)**: extend `concepts/` template with optional `gene_symbol`, `uniprot_id`, `pdb_ids`, `species` fields; lint enforces format if present.

**Fix option (heavier)**: a new `proteins/{uniprot-id}.md` entity type that auto-resolves wikilinks like `[[p53]]` or `[[P04637]]`.

**Recommendation**: Start lightweight. If by 50+ protein references we want graph queries like "drugs targeting kinase X", upgrade to a separate type.

---

### A3 — [P0] Bio-native identifiers in `papers/` frontmatter

**Evidence**: `papers/` template currently has `arxiv: ""` as the canonical identifier. Out of the 11 papers in this wiki, the bio-relevant ones (Drug Design, Ubiquitin Ligases, AlphaFold-DB 2024, Towards Proteome-Scale, MusiteDeep, From Data to Cure) have **no arXiv ID** but **do** have DOI/PMID. The template's CS-shaped identifier list is a poor fit.

**Fix**: extend frontmatter:

```yaml
arxiv: ""                  # keep (some bio papers do hit bioRxiv → arXiv)
doi: ""                    # add — primary for bio
pmid: ""                   # add — PubMed ID
biorxiv: ""                # add — bioRxiv DOI suffix
pdb_ids: []                # add — structures the paper introduces
uniprot_ids: []            # add — proteins the paper characterizes
nct_ids: []                # add — clinical trials referenced
gene_symbols: []           # add — HGNC symbols
species: []                # add — model organism(s) used
```

`/ingest` should populate these from CrossRef/PubMed/EuropePMC instead of (or in addition to) Semantic Scholar.

---

### A4 — [P1] Replace `domain` enum with bio taxonomy

**Evidence**: `runtime-page-templates.en.md` example domains are `NLP / CV / ML Systems / Robotics`. Half of this wiki's pages now carry domains like `Computational Drug Design / Chemical Biology`, `Cancer biology / Molecular oncology`, `Structural Bioinformatics`, `Computational Biology / ML for Science`. The string-form is a pragmatic punt; there's no controlled vocabulary, so consistency drifts.

**Fix**: define a small bio taxonomy controlled list (suggest: `structural-bio`, `chembio`, `comp-drug-discovery`, `cancer-bio`, `systems-bio`, `bioinformatics`, `clinical-translation`, plus existing CS slots). Allow free-form override but lint-warn on non-listed values to encourage consolidation. Stat: `/check` already hits enum mismatches for status fields; extend the same machinery.

---

### A5 — [P0] `experiments/` setup block needs bio fields

**Evidence**: Looking at the 8 experiments I just wrote, the `setup` block is `{model, dataset, hardware, framework}` — pure ML pipeline shape. I had to encode all the bio specifics in free-text body sections:
- "AMBER ff14SB + phosaa14SB or equivalent force field" (force field choice)
- "50 ns explicit-solvent" (simulation length / solvent model)
- "100-step minimisation + 1 ns NPT equilibration" (protocol)
- "Boltz-2 (Jan 2026 weights) with native CCD-PTM tokens" (weight version & tokenization)
- No species / cell line / assay type because all 8 are in-silico

**Fix**: extend `setup` with optional sub-fields. None required, all populated by skill when applicable:

```yaml
setup:
  # existing
  model: ""
  dataset: ""
  hardware: ""
  framework: ""
  # bio additions
  in_silico_or_wet: in_silico   # in_silico | wet_lab | mixed
  species: []                    # human | mouse | yeast | etc
  cell_line: ""                  # Cellosaurus ID preferred
  assay_type: ""                 # Y2H | AP-MS | cryo-EM | NMR | MD | docking | scoring
  force_field: ""                # MD only
  solvent_model: ""              # explicit | implicit | vacuum
  simulation_length: ""          # MD only
  weight_version: ""             # for ML models with multiple released checkpoints
  random_seed_protocol: ""       # ranking-shuffle | bootstrap | LOO-CV
```

---

### A6 — [P1] Compute estimation beyond `estimated_hours`

**Evidence**: I wrote `estimated_hours: 12` for `ablation-boltz2-ptm-vs-md-relaxed-route`. That experiment is 25 tuples × 5 MD seeds × 50 ns explicit-solvent MD on CRBN-VHL ternary systems (~500 residues). Realistic wall-clock per run: 24-48 GPU-h. **Real total: ~3000 GPU-h, off by ~250×.** The `estimated_hours` field's units and provenance are undefined; it's effectively a guess.

**Fix**: switch to a structured cost block with bio-realistic dimensions:

```yaml
estimated_cost:
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0      # MD often dominates; tracked separately
  wet_lab_usd: 0             # antibodies, cell culture, sequencing
  fte_weeks: 0               # postdoc/RA time for non-automatable steps
  dataset_access_lead_time_days: 0   # registration, MTAs, IRB
```

Tooling: a small reference table per assay/MD-system-size in `docs/bio-compute-references.md` — populated as we accumulate experience. `/exp-design` reads from it instead of asking the model to guess.

---

### A7 — [P1] Evidence types and strength beyond CS-isms

**Evidence**: claim `evidence` list currently uses `type: supports | contradicts | tested_by | invalidates` and `strength: weak | moderate | strong`. Bio evidence is more textured:
- A clinical trial reading out positive is not the same evidentiary class as a single in-vitro assay.
- A mechanistic biochem study (point mutation kills activity) is qualitatively different from a correlative observation.
- GRADE (very low / low / moderate / high) is the medicine standard for evidence strength.

**Fix**: add types `wet_lab_validated`, `clinical_validated`, `mechanistic_basis`, `correlative`, `predicts`. Add optional `grade: very-low | low | moderate | high` alongside existing `strength`. Keep existing `strength` for backward compat.

---

### A8 — [P2] Reproducibility metadata for wet-lab-touching experiments

**Evidence**: For purely-in-silico experiments, code commit + checkpoint hash is enough. For bio experiments that ingest wet-lab data (the phospho-PROTAC positive set in V1 came from literature degraders), reproducibility requires antibody clone IDs (RRID), cell line IDs (Cellosaurus), plasmid IDs (Addgene), batch/lot numbers. None tracked.

**Fix**: optional `reproducibility` block on `experiments/`:

```yaml
reproducibility:
  rrid: []                   # antibody / reagent RRID
  cellosaurus: []            # cell line CVCL_xxxx
  addgene: []                # plasmid IDs
  pdb_versions: []           # specific PDB entry + version
  dataset_versions: []       # {dataset_slug, version, accessed_date}
```

---

## Section B — Edge taxonomy

### B1 — [P1] Bio relationship edges

**Evidence**: When wiring up edges for the 8 experiments I only used `tested_by`. The graph has no way to say "drug X targets protein Y", "kinase A phosphorylates substrate B", "E3 ligase C ubiquitinates substrate D" — all of which were prose in claim bodies.

**Fix**: add edge types (paper/claim/concept/protein → protein):
- `targets_protein`, `binds`, `inhibits`, `activates`, `degrades`
- `phosphorylates`, `ubiquitinates`, `methylates`, `acetylates` (PTM-specific)
- `is_substrate_of` (reverse of the four above)

These should require `confidence: high|medium|low` like other semantic edges.

---

### B2 — [P1] Validation/translation edges

**Evidence**: Claims like "asciminib is FDA-approved for CML/Ph+ ALL" or "tazemetostat is FDA-approved for epithelioid sarcoma" appear in body text only. The graph cannot answer "which claims have an FDA-approved drug as evidence?".

**Fix**: edges:
- `clinical_trial_for {nct_id, phase}`
- `fda_approved_for {indication, year}`
- `validates_in_species {species}`

---

### B3 — [P2] Provenance edges from experiments to dataset versions

**Evidence**: TernaryDB will release a v2 someday. Phase-0 noise floor calibrated on v1 will not be valid for v2. There's no edge type `dataset_version_used`.

**Fix**: when an experiment references a dataset, also add `dataset_version_used {slug, version}` edge. Tied to A1 (datasets/) and A6 (cost/version tracking).

---

## Section C — Skill workflow gaps

### C1 — [P0] `/ingest` is arXiv/Semantic-Scholar-shaped

**Evidence**: bio papers (this wiki has 6 of them) often have DOI + PMID + journal but no arXiv. Semantic Scholar coverage of bio is moderate; the canonical sources are PubMed, EuropePMC, bioRxiv, medRxiv.

**Fix**: in `/ingest`:
1. Detect input as DOI / PMID / bioRxiv URL / PMC URL and route accordingly.
2. Add fallback chain: CrossRef API → PubMed E-utilities → EuropePMC → bioRxiv API → DeepXiv → Semantic Scholar.
3. Auto-populate the bio identifier fields from A3.
4. Run a NER pass (a lightweight bio-NER model or LLM-prompt) to extract gene symbols, protein names, drug names, disease terms; pre-populate suggested wikilinks.

---

### C2 — [P1] `/discover` should index bio corpora

**Evidence**: `session-resume.md` notes "DeepXiv search index is sparse for biology/structure domain — keep WebSearch as primary." This is a known degradation. The session was not blocked, but discovery quality is much lower than for CS.

**Fix**: `/discover` should query in parallel: PubMed E-utilities, EuropePMC, bioRxiv, Semantic Scholar, DeepXiv. Merge by DOI/PMID dedup. Bio researchers want recall over precision in the discovery phase.

---

### C3 — [P1] `/ideate` banlist needs domain scoping

**Evidence**: this wiki's banlist already contains `ptm-site-disorder-predictor` with reason "saturated by SAPP / PhosAF / GraphPhos / AstraPTM2 / DeepPCT / MTPrompt-PTM". Those tools saturate the **single-PTM phospho-prediction** subspace, but the same architectural family may be unsaturated in plant biology, in microbial PTMs, in cross-species transfer. Current banlist is global — no `scope` field.

**Fix**: add `scope` to failed-idea metadata: `species`, `disease_area`, `data_regime` (high-data / low-data). Banlist hits only when scope overlaps.

---

### C4 — [P0] `/exp-design` block taxonomy is ML-pipeline-shaped

**Evidence**: the 4 block types (baseline / validation / ablation / robustness) work for ML methods but missed bio-natural blocks during this run:
- **negative control** (sham/scrambled — distinct from a "PTM-blind baseline reproduction"; closer in spirit to a placebo arm)
- **mechanism / MoA** (does the predicted causal mechanism actually hold? typically via point mutagenesis or chemical probe)
- **dose-response** (titration sweep — distinct from hyperparameter sweep)
- **cross-organism / cross-cell-line generalization** (closer to ML "cross-dataset" but with biological-context-specific failure modes)

**Fix**: extend type enum with `negative_control | mechanism | dose_response | cross_context`. Update SKILL.md text to prompt for each.

---

### C5 — [P0] `/exp-design` does not gate wet-lab vs in-silico

**Evidence**: every one of the 8 experiments I designed is in-silico. But the source idea references real experimental phospho-PROTACs (phospho-BCL-XL family) as the held-out positive set. Those data exist because someone did wet-lab work; future ideas in this area will inevitably need their own wet-lab validation step. The skill never asked "does this idea require new wet-lab data?".

**Fix**: in Step 1 (Load Context), add a wet-lab dependency probe: scan idea hypothesis for terms like "in cell", "cellular target engagement", "in vivo", "tumor regression", "binding assay". If hits, prompt user: do you have wet-lab access? if yes, plan a wet-lab block; if no, scope the idea to retrospective-only and document the constraint in `conditions`.

---

### C6 — [P1] `/exp-design` statistical defaults are ML-shaped

**Evidence**: skill says ">= 3 random seeds" for validation/ablation. For my V1 with n_test ≈ 50 phospho-PROTACs, ranking-shuffle multi-seed is OK, but the bigger issue is that bio test sets are often n < 20 with strong class imbalance. Bio-standard practice is bootstrap CI + leave-one-out CV + stratified CV — none of these are mentioned in the skill.

**Fix**: in skill prompt, add: "if n_test < 50, default to bootstrap CI (1000 resamples) and stratified k-fold (k = min(5, n_positives)); seeds-only is insufficient." Also: "for wet-lab assays, default to >= 3 biological × >= 3 technical replicates; specify which is which."

---

### C7 — [P1] `/exp-run` directory layout assumes train.py

**Evidence**: CLAUDE.md says "Experiment code goes in experiments/code/{slug}/: /exp-run writes code to this path (train.py, config.yaml, run.sh, requirements.txt)". For an MD experiment, the natural files are `mdrun.sh`, `system.gro` / `system.pdb`, `system.top`, `mdp/*.mdp` — not train.py. For a wet-lab experiment, the canonical artefact is `protocol.md` plus `analysis.ipynb` against the resulting CSV.

**Fix**: extend `/exp-run` SKILL.md to detect setup type (ML / MD / wet-lab / docking) and write the corresponding directory layout. Templates per type live in `skills/exp-run/references/templates/{ml,md,wet-lab,docking}/`.

---

### C8 — [P1] `/check` lacks bio-specific lints

**Evidence**: `/check` ran clean on this wiki, but it's missing bio-specific structural checks that would catch real bugs:
- **PDB ID format** (4-char like `6XYZ` or 8-char extended)
- **UniProt accession format** (regex `^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$`)
- **Stale dataset version** (compare `dataset_versions` references against `datasets/{slug}.md` `versions:` list)
- **Species mismatch** (experiment uses mouse data but parent claim is about human therapeutics)
- **Force-field provenance** (MD experiment must specify `force_field` if `assay_type: MD`)

**Fix**: add `tools/lint_bio.py` with the above checks; `/check` invokes if any bio fields are present.

---

### C9 — [P1] `/novelty` should query PubMed for bio claims

**Evidence**: `/novelty` currently uses WebSearch + Semantic Scholar + Review LLM. Bio prior art is overwhelmingly in PubMed (>30M abstracts) and only partially indexed by Semantic Scholar. Missing PubMed coverage means novelty checks under-report bio-prior-art collisions.

**Fix**: add PubMed E-utilities query as a parallel novelty channel; weight PubMed hits at full strength for biological claims.

---

### C10 — [P2] `/paper-draft` and `/paper-plan` assume CS paper structure

**Evidence**: not exercised in this run, but the underlying assumption matters. ML papers go Introduction → Related Work → Method → Experiments → Discussion. Bio papers go Introduction → Results → Discussion → Methods (Methods often last and de-emphasized; Results is the main scaffold). Citation style: bio uses Vancouver (numeric, ordered by appearance); CS uses author-year. Author lists: bio papers commonly 20-100 authors; CS rarely > 10.

**Fix**: add a `paper_style: cs | bio | clinical` parameter to `/paper-plan`; downstream `/paper-draft` consumes it. Templates: `skills/paper-draft/references/templates/{cs,bio,clinical}/`.

---

### C11 — [P2] `/rebuttal` should track promised follow-up wet-lab experiments

**Evidence**: not exercised here, but bio reviewers routinely demand additional wet-lab experiments as conditions for acceptance. These promises become tracked deliverables. Currently `/rebuttal` produces text only; there's no mechanism to spawn a new `experiments/{slug}.md` page representing each promised follow-up.

**Fix**: when a rebuttal commits to a new experiment, `/rebuttal` should optionally call `/exp-design` to scaffold the experiment page, with a `triggered_by_rebuttal: <paper-id>` provenance field.

---

## Section D — Convention conflicts

### D1 — [P1] Phase-N (bio) vs Stage-N (CS) numbering

**Evidence**: the source idea uses **Phase-0 / Phase-1 / Phase-2** in standard drug-discovery convention (Phase 0 = preclinical pilot; Phase 1-3 = clinical trial phases). The `/exp-design` skill imposes **Stage-0 / Stage-1 / .../ Stage-4** (sanity / baseline / validation / ablation / robustness). I had to translate between them in the report ("Phase-0 → Stage 2a"), which is confusing in a domain where "Phase 1" already has a different fixed meaning.

**Fix**: rename skill internal stages to **Block-A / Block-B / Block-C / Block-D / Block-E** (or "Step 1..N") so "Phase" is reserved for the user's domain-natural meaning. Update SKILL.md, decision-gate diagrams, EXPERIMENT_PLAN_REPORT template.

---

### D2 — [P2] Maturity scale needs a bio gradient

**Evidence**: `concepts/` `maturity: stable | active | emerging | deprecated` is ML-feature-flavored. Bio concepts have a different gradient: a finding can be `consensus` (textbook), `well-supported` (review-level multi-study), `contested` (active disagreement), `hypothesis` (single primary source), `falsified` (refuted but still cited). "Stable" maps poorly onto a contested but heavily-studied finding.

**Fix**: add bio-gradient values; allow either CS or bio gradient per concept. Lint-warn on mixing.

---

## Section E — CS-isms baked into the source idea / experiment text

These are NOT skill bugs; they are limitations of the model (me) reasoning about bio with CS framing. Worth noting because they propagate into the wiki and become part of its style:

### E1 — Success criteria as percentages

I wrote "baseline mean abs deviation < 5%" for B1. For DeepTernary score reproduction this is reasonable. For cellular assay reproduction, ±5% is unrealistic — IC50 values that are 2× apart are still considered reproducible in most bio contexts. Domain-specific success-criterion guidance would help.

### E2 — "Multi-seed" as the canonical statistical replication

Multi-seed is a property of stochastic ML training. For purely deterministic scorer inference (DeepTernary on a fixed structure), multiple "seeds" don't add information about the score; they only randomize ranking-shuffle. I wrote "5 seeds" in places where bootstrap CI would have been more appropriate (V1, A1).

### E3 — Confidence as a single 0.0-1.0 number

I set the two new claims to `confidence: 0.3`. For bio claims, that single number conflates: (a) prior probability the mechanism is real, (b) precision of the supporting measurement, (c) generalizability across patient populations. The `evidence_strength` rework in A7 partially addresses this.

---

## Section F — Feasibility audit of the 8 experiments designed today

User cannot run the experiments due to time. Below are pre-flight risk assessments per experiment. Each notes (a) compute realism, (b) scientific gotchas, (c) recommended fix before any run.

### F1 — `deepternary-baseline-ternarydb-crbn-vhl-reproduction` (Stage 1 baseline)

- **Compute**: 4 GPU-h is realistic if checkpoint + data are public. ✓
- **Risk**: TernaryDB test-split labels may not match the paper's exact split. The DeepTernary repo's `test/` directory may be the same split as published, but verify the per-tuple ID list against Supplementary Table S2 explicitly.
- **Pre-fix**: before running, write a `verify_split.py` that asserts every test-tuple ID in the repo also appears in the paper's supplementary table. If it fails, baseline reproduction is meaningless.

### F2 — `phase0-noise-floor-calibration-deepternary-ptm-perturbations` (Stage 2a, load-bearing gate)

- **Compute**: 24 GPU-h is realistic for ~100 POI × 200 inferences.
- **Risk (P0)**: I wrote "≈80 Da, ≈3 Å radius — neutral, no charge, no H-bond donors/acceptors" as the perturbation chemistry. **A real phospho group is dianionic at physiological pH and forms multiple H-bonds.** A chemically inert mock will UNDERESTIMATE the noise floor — the scorer's response to a real phospho includes a contribution from the charge / H-bonding / specific geometry that the mock does not probe. Phase-0 with my mock will fire false positives.
- **Pre-fix**: replace "neutral mock" with a small library of real PTM analogs at chemically-realistic positions (phospho-Ser/Thr/Tyr, methyl-Lys at random non-modified Lys). Use multiple replicates per PTM-position pair. The noise floor is then the variance of "real PTM at random non-modified site", not "fake mock at random surface position". This matches the actual scorer-perturbation distribution we want to compare against.

### F3 — `calibrated-deltapternary-phospho-protac-ranking` (Stage 2b primary validation)

- **Compute**: 16 GPU-h is realistic IF Boltz-2 inference dominates. With ~50 (POI, E3, PROTAC) tuples × 5 seeds × {WT, PTM} → 500 Boltz-2 runs. At ~30 min per run for a CRBN ternary system, that's ~250 GPU-h, NOT 16. **Compute estimate is off by ~15×.**
- **Risk (P0)**: I described positives as "true experimental phospho-PROTACs (~8-10) + synthetic positives from kinase-substrate phospho-degron pairs (~30-50)". **Mixing these two populations into a single AUC is statistically dangerous** — synthetic positives are easy (the kinase-substrate relationship is well-known); true experimental phospho-PROTACs are hard (they survived medicinal chemistry optimization). The headline AUC will be inflated by the synthetic majority.
- **Pre-fix**: report two AUCs side-by-side (true positives only; synthetic positives only). Headline number is the true-positive AUC. Synthetic AUC is a sanity check that the pipeline can detect easy positives.
- **Risk (P1)**: "matched negatives" should match on POI MW + linker length + E3 ligand chemistry. I only specified the first two. Mismatched E3 ligand chemistry will leak signal.

### F4 — `ablation-uncalibrated-vs-calibrated-deltapternary` (Stage 3)

- **Compute**: 4 GPU-h is right (cached scores, ranking-only). ✓
- **Risk**: low. Self-contained; only needs F3's cached scores.
- **Pre-fix**: none beyond F3's fixes.

### F5 — `ablation-boltz2-ptm-vs-md-relaxed-route` (Stage 3)

- **Compute (P0)**: I wrote 12 GPU-h. **Real cost: ~3000 GPU-h.** 25 tuples × 5 MD seeds × 50 ns explicit-solvent MD on a CRBN-VHL ternary (~500 residues, ~50k atoms with solvent) is 24-48 GPU-h per run on commodity hardware. **Off by ~250×.** This experiment as currently scoped is computationally infeasible without serious cluster access.
- **Pre-fix options**:
  1. Reduce to 5 tuples × 3 MD seeds × 20 ns (still substantial: ~150-300 GPU-h, plausible).
  2. Use implicit solvent (GBSA) for 10× speedup at cost of accuracy in the PTM region — acceptable for a route-comparison test, NOT for a primary mechanism claim.
  3. Use Boltz-2 with side-chain-only repacking as the "non-Boltz-2-PTM-token" baseline instead of MD. Sidesteps the MD cost entirely. Less faithful to the source idea but feasible.
- **Risk (P1)**: 50 ns is short for capturing PTM-induced rearrangement on substrates with disorder-to-order transitions (14-3-3 binding, for example). The route comparability claim may hold only for stable/preformed binding modes.

### F6 — `ablation-deepternary-vs-protac-stan-scorer` (Stage 3)

- **Compute**: 16 GPU-h is realistic. ✓
- **Risk (P1)**: PROTAC-STAN may not have a public checkpoint. Verify before scoping the experiment.
- **Risk (P1)**: each scorer has its OWN Phase-0 noise floor. The "mini-Phase-0" I described is real work (100 perturbations × ~100 POIs); should be budgeted explicitly.
- **Pre-fix**: confirm checkpoint availability; budget the mini-Phase-0 as +6 GPU-h.

### F7 — `robustness-cross-ptm-type-ubiq-methyl` (Stage 4)

- **Compute**: 16 GPU-h is realistic for the methylation track (small modifications) but **not** for the ubiquitylation track. Mono-Ub is ~8.5 kDa — attaching it via Boltz-2 + scoring is a much larger structural perturbation than the original idea's noise-floor model contemplates.
- **Risk (P0)**: **The ΔpTernary-as-noise-perturbation framing breaks for ubiquitylation.** Ub is a domain, not a side-chain modification. Noise-floor calibration with ~8.5 kDa "perturbations" produces a null distribution dominated by the Ub mass itself; the calibrated threshold becomes meaningless. The pipeline mathematics does not transfer.
- **Pre-fix**: split this experiment into two:
  1. **Methylation track** (≈14-42 Da): same protocol as phospho, Phase-0 noise floor scaled to methyl mass.
  2. **Ubiquitylation track**: a different validation protocol — likely "does Boltz-2 mono-Ub-conjugated POI structure differ from WT in DeepTernary-relevant interface features beyond what mono-Ub mass alone would predict?". This is a different scientific question and probably warrants its own idea page rather than a robustness experiment under this idea.

### F8 — `robustness-mutant-isoform-track-y220c-r175h` (Stage 4)

- **Compute**: 12 GPU-h is realistic. ✓
- **Risk (P0)**: **Boltz-2 training data leakage.** p53 mutants Y220C and R175H are extensively studied; mutant p53 structures are likely in the PDB (and therefore in Boltz-2 training data). The "predict mutant POI structure from sequence" step is not actually a prediction; it's recall. The headline AUC on this track is contaminated.
- **Pre-fix**: before running, query Boltz-2 training data manifest (if released; if not, query PDB for `p53` + `Y220C` / `R175H` deposit dates and cross-reference Boltz-2 weight cutoff). If leakage confirmed, pivot the experiment to either (a) holding out Boltz-2 from the mutant-track entirely and using AlphaFold2 (different training cutoff), or (b) using brand-new mutant-isoform PROTACs published after Boltz-2's training cutoff (very small set).
- **Risk (P1)**: n=6-10 is too small for a reliable AUC. Use bootstrap CI with at least 1000 resamples; report 95% CI alongside point estimate.

### Summary table

| Exp | Compute realism | Worst risk | Action before any run |
|-----|-----------------|------------|------------------------|
| F1 baseline | OK | split-mismatch | verify split IDs |
| F2 noise-floor | OK | mock chemistry too benign | use real PTM analogs at random sites |
| F3 primary validation | **15× under-budget** | true-vs-synthetic positive mixing | report two AUCs, fix matched negatives |
| F4 calibration ablation | OK | low | none |
| F5 MD route ablation | **250× under-budget** | infeasible at current scope | reduce scope or implicit-solvent |
| F6 scorer substitution | OK | PROTAC-STAN checkpoint availability | verify access; budget mini-Phase-0 |
| F7 cross-PTM robustness | OK for methyl, broken for Ub | Ub framing invalid | split into two experiments |
| F8 mutant-isoform robustness | OK | Boltz-2 training-data leakage | leakage audit; consider AF2 substitute |

---

## Section H — Bio sub-areas beyond protein / drug-design (extrapolated)

> **Caveat**: items in this section are not grounded in observed wiki failures. They extrapolate from general bioinformatics practice to sub-areas the wiki has not yet exercised. Re-validate each H item against an actual `/ingest` or `/exp-design` run in that sub-area before deep investment.

### H1 — [P0] Sequencing-modality fields in `experiments/` setup

**Evidence**: A5 added `species`, `cell_line`, `assay_type` for protein-side experiments. For omics experiments the equivalents are sequencing modality, platform, reference genome build, depth, sample size, cohort descriptor — none of which have a home in the current setup block.

**Fix**: extend `experiments/` setup with an optional `sequencing` sub-block:

```yaml
sequencing:
  modality: ""              # bulk-rna-seq | sc-rna-seq | spatial-rna | wgs | wes | atac-seq | chip-seq | wgbs | hi-c | 16s | shotgun-metagenomics
  platform: ""              # illumina-novaseq | ont | pacbio | 10x-chromium
  reference_genome: ""      # GRCh38 | T2T-CHM13 | mm39 | etc.
  read_length: 0
  paired_end: true
  depth: ""                 # mean coverage (WGS) or reads/cell (scRNA)
  n_samples: 0
  cohort_descriptor: ""     # human-readable, e.g. "TCGA-BRCA n=1098"
```

**Validation**: at first `/ingest` of a sequencing paper, confirm fields capture what the paper actually reports.

---

### H2 — [P0] Genomic identifiers on `papers/` / `concepts/` / `claims/`

**Evidence**: A3 added DOI, PMID, PDB, UniProt, NCT, gene symbols, species — anchored on the protein side. Genomics papers anchor on a different identifier stack.

**Fix**: add to `papers/`, `concepts/`, `claims/` frontmatter:

```yaml
genomic_ids:
  ensembl: []        # ENSG... / ENST... / ENSP...
  refseq: []         # NM_... / NP_... / NR_...
  entrez: []         # numeric Gene IDs
  dbsnp: []          # rs... variant IDs
  hgvs: []           # standard variant notation (c. / p. / g.)
  clinvar: []        # ClinVar variation IDs
  cosmic: []         # COSMIC mutation IDs
  go_terms: []       # Gene Ontology IDs (GO:NNNNNNN)
  kegg: []           # KEGG pathway / map IDs
  reactome: []       # Reactome pathway IDs
```

**Impact**: enables `/check` to lint identifier formats; enables `/discover` queries by variant ID; enables cross-paper roll-ups (e.g. "all papers studying rs334").

---

### H3 — [P0] Sequencing-cohort `datasets/` entries

**Evidence**: A1 added the `datasets/` entity. For sequencing the canonical entries include **TCGA**, **GTEx**, **ENCODE**, **Roadmap Epigenomics**, **GEO**, **SRA**, **ENA**, **gnomAD**, **UK Biobank**, **1000 Genomes**, **HCA (Human Cell Atlas)**. Each has a different access tier (public / registration / restricted / IRB-required), citation requirement, and version cadence.

**Fix**: A1's schema already supports versioning + access tier; just need to populate. Pre-seed the major cohorts when the first omics paper is ingested.

**Validation**: confirm `access: restricted` correctly flags downstream `/exp-design` that the dataset has lead time before any `/exp-run` can start.

---

### H4 — [P0] Statistical defaults for genomics in `/exp-design`

**Evidence**: C6 added bootstrap CI / stratified CV for small-N protein-side experiments. Genomics has its own defaults the skill should know:
- GWAS genome-wide significance threshold: **p < 5×10⁻⁸**
- Multiple-testing correction: **Benjamini-Hochberg FDR** is universal; specify q-value threshold (typically q < 0.05)
- **Power analysis** required for any cohort study; n must be justified
- Survival outcomes: **Kaplan-Meier + log-rank**; **Cox proportional hazards** with PH-violation check
- Differential expression: log fold-change threshold (typically |log2FC| > 1) **alongside** adjusted p-value, not instead of

**Fix**: extend C6 prompt with: "if `setup.assay_type` matches a genomics modality (any value in H1's `modality` list), default to BH-FDR multiple-testing correction; for GWAS use 5e-8 threshold and pre-register power analysis; for survival outcomes default to Cox PH with violation check; for DE always pair effect size with adjusted p-value."

---

### H5 — [P0] `/ingest` NER vocabulary differs by bio sub-area

**Evidence**: C1 proposed adding bio-NER to `/ingest`. The vocabulary is not uniform across bio: a drug-discovery paper extracts gene symbols + drug names + PROTAC + kinase + ligand. An omics paper extracts cohort sizes + adjusted p-values + fold-changes + eQTL/sQTL terms + GO enrichment terms + cell type annotations. A clinical paper extracts NCT IDs + indications + endpoints + hazard ratios. A single bio-NER pipeline will under-extract for all of them.

**Fix**: in `/ingest`, after detecting paper sub-area (heuristic: keywords in abstract + venue + journal taxonomy), pick the matching NER profile:
- `protein-drug` profile (protein names, drug names, PROTAC components, kinase-substrate pairs)
- `omics` profile (gene symbols, cohort sizes, adjusted p-values, fold-changes, GO/KEGG terms, cell type annotations)
- `clinical` profile (NCT IDs, indications, endpoints, hazard ratios, cohort sizes)
- `microbiome` profile (taxonomy strings, OTU/ASV identifiers, alpha/beta diversity terms)

**Validation**: ingest a TCGA paper and confirm cohort sample sizes are extracted to wiki frontmatter, not just left buried in the body.

---

### H6 — [P1] Domain taxonomy expansion (supplements A4)

**Evidence**: A4 proposed CS slots + a few protein-side bio slots. Add: `genomics`, `transcriptomics`, `epigenomics`, `single-cell`, `metagenomics`, `clinical-genomics`, `pharmacogenomics`, `population-genetics`, `phylogenomics`, `functional-genomics`, `cancer-genomics`.

**Fix**: append to A4's controlled list; same lint behavior.

---

### H7 — [P1] `/exp-run` directory layout for workflow managers

**Evidence**: C7 covered ML / MD / wet-lab / docking. Omics pipelines almost universally use **snakemake** or **nextflow** as the canonical workflow manager — they are bio's equivalent of `train.py`. The current skill has no template for either.

**Fix**: add templates `skills/exp-run/references/templates/{snakemake,nextflow}/`:
- Snakemake: `Snakefile` + `config.yaml` + `envs/*.yaml` (conda) + `scripts/*.py|.R`
- Nextflow: `main.nf` + `nextflow.config` + `modules/*.nf` + `bin/*` + (optional) `nf-core/` template

`/exp-run` selects template by `setup.framework` (`snakemake` / `nextflow`) or by the modality field from H1.

---

### H8 — [P1] Sequencing cost model in A6 cost block

**Evidence**: A6 added MD wall-clock + wet-lab USD. Sequencing cost has its own structure: per-sample × depth × platform. NovaSeq lane USD; 10x scRNA library prep USD per sample; long-read USD per Gb. Storage matters too — raw + processed for a moderate cohort easily reaches multi-TB. Alignment CPU-hours scale roughly linearly with read count.

**Fix**: extend A6's cost block:

```yaml
estimated_cost:
  # existing
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0
  wet_lab_usd: 0
  fte_weeks: 0
  dataset_access_lead_time_days: 0
  # sequencing additions
  sequencing_usd: 0
  per_sample_sequencing_usd: 0
  storage_tb: 0           # raw + processed
```

---

### H9 — [P1] Edges for variant–disease and expression–outcome associations

**Evidence**: B1/B2 added protein-side relationship and validation edges. Genomics needs:
- `variant_associated_with_disease {odds_ratio, ci, p_value}`
- `gene_underlies_disease {evidence_level, mode_of_inheritance}` (Mendelian)
- `expression_correlates_with_outcome {hazard_ratio, ci, cohort}`
- `cell_type_marker_for {ontology_id}`
- `gene_in_pathway {pathway_id, db}` (KEGG / Reactome)
- `transcript_isoform_of {gene_id}`

**Fix**: extend B1/B2 edge type lists; same `confidence: high|medium|low` requirement; carry the quantitative attributes as edge metadata.

---

### H10 — [P2] Cell type, tissue, disease ontology references

**Evidence**: For single-cell work: **Cell Ontology** (CL:NNNNNNN). For tissue / biospecimen: **UBERON**, **BRENDA Tissue Ontology**. For disease classification: **MONDO**, **ICD-10/11**, **MeSH**, **HPO** (Human Phenotype Ontology) for phenotypes.

**Fix**: add optional `ontology_refs` block to `concepts/`, `claims/`, `datasets/`:

```yaml
ontology_refs:
  cell_type: []        # CL:NNNNNNN
  tissue: []           # UBERON:NNNNNNN
  disease: []          # MONDO / ICD-10 / MeSH
  phenotype: []        # HP:NNNNNNN
```

**Impact**: lower priority because these mostly become useful at scale (cross-paper synthesis, ontology-rooted lookups). Pay back when wiki has 100+ omics or clinical papers.

---

## Section G — Recommended starting order

If you tackle these in order, each step unlocks the next. **H items are interleaved with their A/B/C counterparts** — building a schema field for protein-side identifiers and a parallel one for genomic identifiers in the same change is much cheaper than two separate passes.

1. **A1 + H3 (datasets/ entity, with both protein-side and sequencing-cohort entries)** — touches every future bio ingest; cheapest to add, highest leverage.
2. **A3 + H2 (bio identifiers on papers / concepts / claims, both protein and genomic stacks)** — schema scaffolding for everything downstream.
3. **C1 + H5 (`/ingest` with PubMed/EuropePMC fallback + per-sub-area NER profiles)** — once schema accepts DOI/PMID + genomic IDs, ingest can populate them differently per sub-area.
4. **A5 + H1 + A6 + H8 (experiments setup with sequencing fields + cost block with sequencing cost model)** — fixes both the F5 / F3 compute-blindness class of problem (protein side) AND the analogous omics-cost-blindness before the wiki ever encounters it.
5. **C4 + C5 + H4 (`/exp-design` block taxonomy + wet-lab gating + genomics statistical defaults)** — addresses the Section F class of problems systemically and pre-empts the parallel class for omics.
6. **D1 (Phase vs Stage rename)** — small, frequently-encountered confusion, easy fix.
7. **C8 (bio-specific lints, including H2 identifier formats)** — pays back as wiki grows.
8. **A2 + B1 + H9 (proteins/ entity + protein-side relationship edges + genomic relationship edges)** — only worth it once you have ≥30-50 protein references or ≥10-20 omics papers; revisit at next milestone.
9. **C7 + H7 (`/exp-run` directory layouts incl. snakemake/nextflow)** — when first non-ML / non-MD experiment lands.
10. **H6 (domain taxonomy expansion)** — fold into A4 when the lint catches the first uncategorised bio domain.
11. **C10 (paper-draft bio template)** — only when you're ready to write a bio paper from this wiki.
12. **H10, A8, B2, B3, C9, C11, D2 (ontology references, wet-lab reproducibility metadata, validation edges, dataset-version provenance, /novelty PubMed, /rebuttal follow-up tracking, bio maturity gradient)** — long tail; pick up as specific gaps surface.

---

## How to use this backlog

Each item has an ID (A1, B1, C1, ...). When you start working on one:

1. Open this file, mark the item with `**STATUS: in progress (YYYY-MM-DD)**` after the severity tag.
2. For schema changes (Section A), update `i18n/en/CLAUDE.md` and corresponding `docs/runtime-page-templates.en.md`, then run `./setup.sh --lang en` to sync.
3. For skill changes (Section C), update the skill's SKILL.md; if behavior changes, add a note to `wiki/log.md` so future reads know.
4. For Section F items: those are fixes to the experiments already in `wiki/experiments/`. Edit those pages directly (the `## Setup` / `## Procedure` / `## Follow-up` sections) before any `/exp-run`.
5. When done, mark `**STATUS: done (YYYY-MM-DD)**` and add a one-line note about what the validation showed.

Items can be re-prioritized as new bio ideas surface gaps not anticipated here.

---

## Sync convention

- This file (en) and **`bioinformatics-adaptation-backlog.zh.md`** (zh) are mirrors.
- Any substantive change to one (adding/removing items, updating STATUS, re-prioritizing, recording validation findings) must be applied to the other in the same change.
- Pure copy-edits to one file may be deferred but should be folded in on the next substantive update.
