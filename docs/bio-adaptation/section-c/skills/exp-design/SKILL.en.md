---
description: Claim-driven experiment design — scope target claims → design experiment blocks (baseline/validation/ablation/robustness/negative-control/mechanism/dose-response/cross-context) → build run order → optional Review LLM review → write to wiki
argument-hint: <idea-slug-or-hypothesis> [--review] [--budget <gpu-hours>] [--wet-lab yes|no|skip]
---

<!-- bio-C4+C5+C6: Mirror of i18n/en/skills/exp-design/SKILL.md with three drafted bio-section items.
     Source of truth: i18n/en/skills/exp-design/SKILL.md. Do not run from this path; for testing, merge to source first.

     Section C-1 (Batch finish) — three bundled additions, all in this single SKILL.md:
       C4 [P0] block taxonomy gains: negative_control | mechanism | dose_response | cross_context
       C5 [P0] Step 1 wet-lab vs in-silico routing (keyword scan → 3-branch user prompt; non-interactive = skip+flag)
       C6 [P1] bio statistical defaults: bootstrap CI + stratified k-fold for n_test < 50; biological×technical replicates for wet-lab assays
     Cross-section dependencies: A1 (datasets/), A5 (experiments setup bio fields), A6 (estimated_cost block),
       A7 (claim evidence types/grade), B1 (bio relation edges — referenced in Step 5 review prompt only). -->

# /exp-design

> Given an idea (or a free-text hypothesis), design a complete experiment plan.
> Claims are the core: scope the claims to validate across three dimensions — Target, Decomposition, and Threats.
> Design four base experiment block types — baseline (reproduce baseline), validation (core verification), ablation (factor isolation), robustness (stress testing) — plus, when the idea touches a biological system, four bio-natural block types: negative_control (sham/scrambled placebo arm), mechanism (causal MoA via point mutagenesis or chemical probe), dose_response (titration sweep), cross_context (cross-organism / cross-cell-line generalization). <!-- bio-C4 -->
> Experiments are ordered by dependency with decision gates between stages (sanity fail → early stop).
> Optional Review LLM review checks experiment plan completeness. All experiments are written to wiki/experiments/ with graph edges.

## Inputs

- `idea`: one of:
  - A slug from wiki/ideas/ (e.g. `sparse-lora-for-edge-devices`)
  - A free-text hypothesis description (provide the experiment goal directly)
- `--review` (optional): enable Review LLM review to check experiment plan completeness
- `--budget <gpu-hours>` (optional): total compute budget cap (GPU hours), affects robustness experiment scope
- <!-- bio-C5 --> `--wet-lab yes|no|skip` (optional): pre-answers Step 1's wet-lab probe non-interactively. `yes` = plan a wet-lab block when keyword scan triggers; `no` = scope the idea to retrospective/in-silico-only and write the constraint into `conditions`; `skip` = no change, flag in report. Default when omitted **and** running interactively: prompt the user. Default in non-interactive mode (e.g. `/research` orchestration): `skip` with a flag in the report.

## Outputs

- `wiki/experiments/{slug}.md` — one page per experiment block (status: planned)
- `wiki/graph/edges.jsonl` — new tested_by edges: experiment → claim
- `wiki/ideas/{slug}.md` — updated linked_experiments field
- `wiki/graph/context_brief.md` — rebuilt
- `wiki/graph/open_questions.md` — rebuilt
- `wiki/log.md` — appended log entry
- **EXPERIMENT_PLAN_REPORT** (printed to terminal) — experiment block summary, run order, compute budget, <!-- bio-C5 --> wet-lab routing decision and any retrospective-only scope downgrades, <!-- bio-C6 --> chosen statistical protocol per block (multi-seed vs bootstrap-CI vs stratified-k-fold vs replicate matrix)

## Wiki Interaction

### Reads
- `wiki/ideas/{slug}.md` — idea's hypothesis, approach, risks, origin_gaps
- `wiki/claims/*.md` — target claims' current status, existing evidence, confidence
- `wiki/experiments/*.md` — existing experiments (avoid duplicate designs, reference setup configs)
- `wiki/papers/*.md` — related papers' baselines and experiment setups
- `wiki/concepts/*.md` — relevant technical concepts (guide experiment design)
- <!-- bio-C5 (depends on A1) --> `wiki/datasets/*.md` — existing dataset pages, used both for `setup.dataset` wikilink resolution and for picking a dataset whose `versions[]` matches the idea's data regime
- `wiki/graph/context_brief.md` — global context
- `wiki/graph/open_questions.md` — knowledge gaps (guide experiment priority)

### Writes
- `wiki/experiments/{slug}.md` — create experiment pages (one per experiment block)
- `wiki/ideas/{slug}.md` — update linked_experiments field
- `wiki/graph/edges.jsonl` — add tested_by edges
- `wiki/graph/context_brief.md` — rebuild
- `wiki/graph/open_questions.md` — rebuild
- `wiki/log.md` — append operation log

### Graph edges created
- `tested_by`: claim → experiment (the claim is validated by this experiment)

## Workflow

**Precondition**: confirm working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).

### Step 1: Load Context

1. **Parse idea input**:
   - If slug: read `wiki/ideas/{slug}.md`, extract `## Motivation`, `## Hypothesis`, `## Approach sketch`, `## Risks`, and the frontmatter fields `origin_gaps`, `tags`, `domain`, `priority` (per CLAUDE.md ideas template)
   - If free text: use directly as the hypothesis description
2. **Load relevant wiki context**:
   - Read `wiki/graph/context_brief.md` (global context)
   - Read `wiki/graph/open_questions.md` (knowledge gaps)
   - From the idea's `origin_gaps`, read the corresponding `wiki/claims/*.md` (target claims)
   - From each target claim's `source_papers` field, read the corresponding `wiki/papers/*.md` for baseline setups and prior experiment protocols — this is the canonical path from idea → claim → paper (ideas do **not** carry a `linked_papers` field; use `origin_gaps` → `source_papers` instead)
   - Read existing `wiki/experiments/*.md` to check for similar experiments
3. **If idea has no origin_gaps**: extract implied claims from the hypothesis description; search wiki/claims/ or flag as needing new claim creation
4. <!-- bio-C5 --> **Wet-lab dependency probe** (skip when the idea's `domain` is clearly CS — `NLP|CV|ML Systems|Robotics`):
   - **Keyword scan**: search the concatenated `## Hypothesis` + `## Approach sketch` + `## Risks` text (or the free-text hypothesis) for any of the following anchors. Hits are interpreted as evidence the idea will eventually need new wet-lab data:
     - **Cell-based assays**: `in cell`, `in cellulo`, `cellular target engagement`, `CETSA`, `nanoBRET`, `viability`, `apoptosis`, `proliferation`
     - **Animal / clinical**: `in vivo`, `xenograft`, `tumor regression`, `PK/PD`, `pharmacokinetic`, `mouse model`, `clinical trial`
     - **Biophysical**: `binding assay`, `IC50`, `EC50`, `Kd`, `ITC`, `SPR`, `BLI`, `thermal shift`, `DSF`
     - **Structural**: `cryo-EM`, `crystal structure`, `NMR` (when used as primary readout, not as a starting model)
     - **Interactome**: `Y2H`, `AP-MS`, `co-IP`, `BioID`, `proximity labeling`
     - **Genomics readouts**: `RNA-seq`, `ChIP-seq`, `CRISPR screen`, `MPRA`
   - **Branching**:
     - If `--wet-lab` was passed, take that branch directly without prompting.
     - If interactive and ≥1 keyword hits: prompt the user with the matched keyword list and three options:
       - `yes` → plan an additional wet-lab experiment block at Step 3 (type `validation`, with `setup.in_silico_or_wet: wet`, populate `setup.assay_type`, `setup.cell_line`, `setup.species`; record corresponding `estimated_cost.wet_lab_usd` and `estimated_cost.dataset_access_lead_time_days`)
       - `no` → narrow scope to retrospective / in-silico-only. Add a sentence to the experiment page's `## Setup` (or to the idea's `conditions` block when the idea is from wiki) stating "scoped to retrospective in-silico evaluation; no new wet-lab generation" and surface this in the final report.
       - `skip` → make no scope change, but record "wet-lab probe deferred" in the report so a future `/exp-design` rerun (or `/check`) can pick it back up.
     - If non-interactive and ≥1 keyword hits: default to `skip` with flag in report.
     - If 0 keyword hits: do nothing; treat the idea as in-silico-only by default.
   - **Output of this sub-step** (carried forward to Step 3): a `wet_lab_decision` value in `{plan|retrospective_only|deferred|none}` plus the matched keyword list.

### Step 2: Scope Claims

Scope the claims for this experiment plan across three dimensions. For each dimension, search wiki/claims/ for existing claims first; if none exist, create a new claim (status: proposed, confidence: 0.3).

1. **Target** (what to validate):
   - The claim corresponding to the idea's core hypothesis — the primary target this experiment plan directly validates
   - Typically 1, at most 2
2. **Decomposition** (what to decompose):
   - Individual contribution claims for each independent factor in the method
   - One claim per factor, used to design isolation experiments
3. **Threats** (what could falsify us):
   - Known risks, alternative explanations, boundary conditions
   - Sources: counter-evidence in wiki, paper limitations, open questions in claims
   - Guides robustness experiment design

Output: scoped claims list (slug list + dimension annotation + current status/confidence for each claim)

### Step 3: Design Experiment Blocks

Design experiment blocks for each scoped claim. The base four types apply to every plan; the four bio block types are conditionally added when the idea is biological in nature (`domain` matches A4's bio vocabulary `structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics | clinical-translation`, **or** Step 1 sub-step 4 produced any keyword hits). <!-- bio-C4 -->

**A. Baseline experiments (reproduce baseline)**:
- Purpose: confirm the problem exists and the baseline is reproducible
- Reproduce the core experiment from the most relevant paper
- Success criterion: baseline results deviate < 5% from reported paper values (this threshold is the same one used by the Stage 1 decision gate below — do not introduce a different number elsewhere)
- Compute: typically minimal

**B. Validation experiments (validate Target claim)**:
- Purpose: validate the core contribution on top of the baseline
- Metrics: statistically significant improvement over baseline
- <!-- bio-C6 --> **Statistical protocol** (default by sample size): if `n_test >= 50` and the experiment is in-silico, follow the legacy ML default — **>= 3 random seeds** with paired test against baseline. If `n_test < 50` (typical for bio held-out sets) **or** `domain` is bio per A4, the default escalates to **bootstrap CI (1000 resamples)** plus **stratified k-fold (k = min(5, n_positives))**; seeds-only is insufficient and must be flagged. For wet-lab experiments (`setup.in_silico_or_wet: wet`): default to **>= 3 biological replicates × >= 3 technical replicates**, with the distinction stated explicitly in `## Setup` (which is which); single-replicate is a flagged exception that must justify itself in the page body.
- Compute: moderate

**C. Ablation experiments (validate Decomposition claims)**:
- Purpose: isolate the contribution of each independent factor
- Each ablation removes one factor and validates the resulting performance drop
- N factors → N ablation experiments
- <!-- bio-C6 --> Same statistical-protocol selector as validation: small-n bio sets escalate to bootstrap CI + stratified k-fold; wet-lab ablations must specify biological×technical replicate matrix.
- Compute: similar to validation × N

**D. Robustness experiments (rule out Threats)**:
- Purpose: rule out known risks and alternative explanations; verify the method holds under varied conditions
- Variation dimensions: model size, dataset, hyperparameters, domain
- Test at least 2 variation dimensions
- Compute: depends on --budget

<!-- bio-C4: bio-natural blocks E–H, conditional on biological domain or wet-lab keyword hits. -->

**E. Negative-control experiments (sham / scrambled placebo arm)**:
- Purpose: distinguish a real effect from a non-specific or batch-driven artefact. **Distinct from a "PTM-blind baseline reproduction"**: a baseline reproduces the prior result *without* the new factor; a negative control adds a deliberately inert variant of the new factor (sham PTM site, scrambled sequence, mismatched ligand, untransfected wells, vehicle-only dose) and measures the same readout.
- When to add: any wet-lab block; any in-silico block where the contrast hinges on a single feature whose effect could be confounded by structural prior alone (e.g. PTM-conditioned scoring vs PTM-blind scoring on the same scaffold).
- Success criterion: the negative-control arm reproduces the baseline's null distribution (effect size within noise floor); a non-null negative control invalidates the validation block until the artefact is identified.
- Compute: typically equal to one validation block.

**F. Mechanism experiments (does the predicted MoA actually hold?)**:
- Purpose: test the *causal* mechanism the idea claims, not just the end-point readout. Targets a `mechanistic_basis` evidence claim per A7.
- Standard designs: point-mutagenesis at the predicted catalytic / binding / PTM residue (loss-of-function should kill the effect; rescue with WT should restore it); chemical-probe (inhibitor of the predicted upstream node should phenocopy the loss-of-function); orthogonal perturbation (RNAi vs CRISPR, two structurally distinct ligands) to rule out off-target.
- Success criterion: at least two orthogonal perturbations of the predicted mechanism produce concordant directional effects.
- Compute: usually 1–2× the validation block; high impact per dollar — drop a mechanism block before dropping a robustness block.

**G. Dose-response experiments (titration sweep)**:
- Purpose: characterise the relationship between perturbation magnitude and effect; **distinct from a hyperparameter sweep** — hyperparameters are model knobs, dose-response is a continuous biological variable (drug concentration, expression level, modifier stoichiometry, simulation length).
- Standard designs: ≥ 6 doses spanning ≥ 3 orders of magnitude on log scale; fit a 4-parameter Hill curve (or appropriate alternative); report EC50 / IC50 with 95% CI.
- Success criterion: monotonic dose-effect with Hill coefficient and EC50/IC50 inside a pre-registered range; flat dose-response on the predicted variable is itself an informative falsification.
- Compute: roughly 6–10× a single validation point per condition.

**H. Cross-context experiments (cross-organism / cross-cell-line generalization)**:
- Purpose: probe whether the effect generalizes outside the training context. Closer in spirit to ML "cross-dataset" but with biological-context-specific failure modes (species-specific PTM enzymes, paralogue redundancy, cell-line-specific co-factor expression, tumor-vs-normal proteome differences).
- When to add: the idea makes a claim that is implicitly species- or cell-line-bounded but the wet-lab plan only covers one context (e.g. trained on HEK293 but the application target is primary T cells).
- Success criterion: pre-register an effect-size retention threshold (e.g. ≥ 50% of the within-context effect size) and at least one cross-context failure should not invalidate the within-context claim — but it must downgrade the claim's scope.
- Compute: per-context cost similar to a validation block; budget by picking 1–2 most policy-relevant contexts.

Each experiment block includes:
- `title`: descriptive title
- `target_claim`: corresponding claim slug
- `hypothesis`: specific hypothesis the experiment tests
- `type`: <!-- bio-C4 --> `baseline | validation | ablation | robustness | negative_control | mechanism | dose_response | cross_context`
- `setup`: model, dataset, hardware, framework <!-- bio-C5 (via A5) --> plus optional bio fields when applicable: `in_silico_or_wet`, `species`, `cell_line`, `assay_type`, `force_field`, `solvent_model`, `simulation_length`, `weight_version`, `random_seed_protocol`
- `metrics`: list of evaluation metrics
- `baseline`: comparison baseline (negative-control blocks: the *placebo* arm; mechanism blocks: the WT/vehicle arm; dose-response: zero-dose; cross-context: within-context effect size) <!-- bio-C4 -->
- `success_criterion`: explicit pass/fail criterion
- <!-- bio-C6 --> `statistical_protocol`: one of `seeds_only` (legacy ML default; n_test ≥ 50, in-silico) | `bootstrap_ci` (1000 resamples; small-n in-silico) | `stratified_kfold` (k = min(5, n_positives); imbalanced classes) | `replicate_matrix_BxT` (biological × technical replicates; wet-lab) — fill exactly one
- `estimated_gpu_hours`: legacy field; kept for backward compat
- <!-- bio-C5 (via A6) --> `estimated_cost`: structured block when this experiment touches MD or wet-lab (set non-zero only the dimensions that apply): `gpu_hours`, `cpu_hours`, `md_wallclock_hours`, `wet_lab_usd`, `fte_weeks`, `dataset_access_lead_time_days`
- `seeds`: number of random seeds (only meaningful when `statistical_protocol == seeds_only`; recommend >= 3)

### Step 4: Build Run Order

Sort experiments by dependency and set decision gates:

```
Stage 0: Sanity check
  └── Small-scale run (1 epoch / 100 steps) to verify no code bugs, data loads, GPU available, loss decreasing
  └── Gate: sanity fails → stop, fix code

Stage 1: Baseline (reproduce baseline)
  └── Reproduce baseline results
  └── Gate: baseline deviation > 5% → stop, check implementation (same threshold as Step 3 success criterion)

Stage 2: Validation (core verification)
  └── Validate core method on top of baseline
  └── Run any planned negative-control block IN PARALLEL with the validation block (same Stage 2)  <!-- bio-C4 -->
  └── Gate: no improvement → stop, analyze reason (idea may not hold)
  └── Gate: negative control shows non-null effect → stop, the validation result is unsafe to interpret  <!-- bio-C4 -->

Stage 3: Ablation (factor isolation) + Mechanism (causal MoA)  <!-- bio-C4 -->
  └── Multiple ablations can run in parallel
  └── Mechanism blocks are scheduled here (depend on Stage 2 success; orthogonal to ablations)
  └── Gate: if a factor ablation shows no effect → record it, but continue other ablations
  └── Gate: if neither orthogonal mechanism perturbation shows the predicted directional effect → downgrade target claim's mechanistic_basis evidence to correlative; continue robustness only with a flag  <!-- bio-C4 -->

Stage 4: Robustness (robustness verification) + Dose-response + Cross-context  <!-- bio-C4 -->
  └── Only execute after Stage 2 succeeds
  └── Scope determined by remaining --budget; when budget is tight, drop in this priority order: cross_context → robustness → dose_response (drop dose_response last because it produces the most quantitatively useful claim per unit cost)
```

Output:
- Ordered experiment list (with dependencies)
- Decision gate conditions for each stage
- Total compute budget estimate (if exceeding --budget, adjust Stage 4 scope)

### Step 5: Optional Review LLM Review (--review)

If `--review` is specified:

```
mcp__llm-review__chat:
  system: "You are a senior researcher reviewing an experiment plan. The plan
           may include both ML-style blocks (baseline/validation/ablation/
           robustness) and bio-natural blocks (negative_control/mechanism/
           dose_response/cross_context).
           Focus on: missing baselines, missing ablations, unfair comparisons,
           statistical rigor (sample size, replicates, seeds vs bootstrap CI
           vs stratified k-fold), dataset selection and version pinning, and
           — for bio plans — whether negative controls are present where the
           contrast hinges on a single feature, whether mechanism blocks use
           ≥2 orthogonal perturbations, whether dose-response covers ≥3
           orders of magnitude, and whether cross-context blocks pre-register
           effect-size retention thresholds.
           For every issue found, suggest a concrete fix."  <!-- bio-C4+C6 -->
  message: |
    ## Experiment Plan
    {complete experiment plan: claims, blocks, run order, budgets, statistical_protocol per block}

    ## Context
    {target claims with current status, related papers' experiment setups, wet-lab decision from Step 1}

    ## Review Questions
    1. Are any critical experiments missing?
    2. Are the baselines fair and comprehensive?
    3. Is the ablation design sufficient to isolate each contribution?
    4. Are the success criteria well-defined and reasonable?
    5. Any statistical concerns (sample size, variance, seeds vs bootstrap CI vs stratified k-fold; wet-lab replicate matrix)?  <!-- bio-C6 -->
    6. <!-- bio-C4 --> For bio plans: is a negative-control block present wherever the contrast hinges on a single feature? Do mechanism blocks use ≥2 orthogonal perturbations? Does dose-response span ≥3 orders of magnitude? Are cross-context retention thresholds pre-registered?
    7. <!-- bio-C5 --> Did the wet-lab decision (`plan|retrospective_only|deferred|none`) match the idea's actual data dependencies? Any keyword hits the probe missed?
```

Revise the experiment plan based on Review LLM feedback (add missing experiments, correct unreasonable criteria, add missing negative-control / mechanism / dose-response / cross-context blocks).

### Step 6: Write to Wiki

1. **Create experiment pages**:
   For each experiment block:
   ```bash
   python3 tools/research_wiki.py slug "<experiment-title>"
   ```
   Create `wiki/experiments/{slug}.md` following the **CLAUDE.md experiments template exactly** — every field below must be present even if empty, because `/exp-run` later uses `tools/research_wiki.py set-meta` to update them, and `set-meta` refuses to create fields that don't already exist in the frontmatter (it only updates existing keys):
   ```yaml
   ---
   title: ""
   slug: ""
   status: planned
   target_claim: ""          # claim slug
   hypothesis: ""
   tags: []
   domain: ""
   setup:
     model: ""
     dataset: ""               # populate as [[datasets/{slug}]] wikilink when the dataset has a wiki page (depends on A1)
     hardware: ""
     framework: ""
     # bio-C5 (via A5): optional bio fields — fill only when applicable to this experiment
     in_silico_or_wet: ""      # "" | in_silico | wet | hybrid
     species: ""
     cell_line: ""             # CVCL_xxxx Cellosaurus ID preferred
     assay_type: ""            # e.g. CETSA | nanoBRET | RNA-seq | docking | MD | binding-affinity-prediction
     force_field: ""           # only for MD blocks
     solvent_model: ""         # only for MD blocks
     simulation_length: ""     # only for MD blocks (e.g. 100ns)
     weight_version: ""        # ML weight provenance, e.g. boltz-2.1.0
     random_seed_protocol: ""  # text describing how seeds are chosen
   metrics: []
   baseline: ""
   # bio-C4: extended type enum
   # type: baseline | validation | ablation | robustness
   #     | negative_control | mechanism | dose_response | cross_context
   # bio-C6: explicit statistical protocol (mandatory)
   statistical_protocol: ""    # seeds_only | bootstrap_ci | stratified_kfold | replicate_matrix_BxT
   outcome: ""                 # empty until /exp-run Phase 4 — succeeded | failed | inconclusive
   key_result: ""              # empty until /exp-run Phase 4
   linked_idea: "{idea-slug}"  # MANDATORY: the source idea slug (reverse link to wiki/ideas/{idea-slug}.md linked_experiments)
   date_planned: YYYY-MM-DD
   date_completed: ""          # empty until /exp-run Phase 4
   run_log: ""                 # empty until /exp-run Phase 2
   started: ""                 # empty until /exp-run Phase 2 (ISO timestamp, set via set-meta)
   estimated_hours: 0          # legacy field; kept for back-compat (deprecated by A6)
   # bio-C5 (via A6): structured cost block — fill non-zero only the dimensions that apply
   estimated_cost:
     gpu_hours: 0
     cpu_hours: 0
     md_wallclock_hours: 0
     wet_lab_usd: 0
     fte_weeks: 0
     dataset_access_lead_time_days: 0
   remote:                     # full block must exist so /exp-run --env remote can populate sub-fields via Edit
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ---

   ## Objective
   {what this experiment proves}

   ## Setup
   {detailed setup: model, dataset, hardware, hyperparameters}
   {bio-C5: when retrospective_only branch was chosen in Step 1, append the sentence
    "scoped to retrospective in-silico evaluation; no new wet-lab generation."}
   {bio-C6: when statistical_protocol == replicate_matrix_BxT, state explicitly which
    dimension is biological replicates and which is technical replicates, and how many of each.}

   ## Procedure
   {step-by-step execution plan}

   ## Results
   (to be filled after /exp-run)

   ## Analysis
   (to be filled after /exp-run)

   ## Claim updates
   (to be filled after /exp-eval)

   ## Follow-up
   {contingency plans: what to do if success / failure}
   ```

2. **Create new claims (if missing claims were identified in Step 2)**:
   ```bash
   python3 tools/research_wiki.py slug "<claim-title>"
   ```
   Create `wiki/claims/{slug}.md` (status: proposed, confidence: 0.3)

3. **Add graph edges**:
   ```bash
   # For each experiment → target claim
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "claims/{target-claim}" --to "experiments/{slug}" \
     --type tested_by --evidence "Designed by /exp-design"
   ```

4. **Update idea page** (if idea came from wiki):
   - Append all new experiment slugs to `linked_experiments` in `wiki/ideas/{idea-slug}.md`
   - If idea status is `proposed`, update to `in_progress`
   - <!-- bio-C5 --> If the wet-lab decision was `retrospective_only`, also append a `conditions` line documenting the scope downgrade (e.g. "scoped to retrospective in-silico evaluation per /exp-design 2026-MM-DD")

5. **Update index.md**: append entries under the experiments and claims (if new) categories

6. **Rebuild derived data**:
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

7. **Append log**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-design | {N} experiments designed for idea {slug} | claims: {claim-list} | wet_lab_decision: {plan|retrospective_only|deferred|none}"
   ```
   <!-- bio-C5: log line gains the wet_lab_decision tail for grep-ability -->

8. **Print EXPERIMENT_PLAN_REPORT to terminal**:
   ```markdown
   # Experiment Plan Report

   ## Target Idea
   - Idea: [[idea-slug]]
   - Hypothesis: {hypothesis}
   - Wet-lab decision: {plan | retrospective_only | deferred | none}    <!-- bio-C5 -->
   - Matched wet-lab keywords: {comma-separated list, or "—"}            <!-- bio-C5 -->

   ## Scoped Claims
   | Claim | Current status | Confidence | Dimension |
   |-------|---------------|------------|-----------|
   | [[claim-slug]] | proposed | 0.3 | target |
   | [[claim-slug]] | weakly_supported | 0.5 | decomposition |

   ## Experiment Blocks
   | # | Experiment | Type | Claim | Stat protocol | Cost (primary dim) | Stage |
   |---|-----------|------|-------|---------------|--------------------|-------|
   | 1 | [[baseline-slug]]       | baseline         | —              | seeds_only         | 2 GPU-h           | 1 |
   | 2 | [[validation-slug]]     | validation       | target         | bootstrap_ci       | 8 GPU-h           | 2 |
   | 3 | [[neg-ctrl-slug]]       | negative_control | target         | bootstrap_ci       | 8 GPU-h           | 2 |
   | 4 | [[ablation-1-slug]]     | ablation         | decomposition-1| stratified_kfold   | 8 GPU-h           | 3 |
   | 5 | [[mechanism-slug]]      | mechanism        | target         | replicate_matrix_BxT| $12k wet-lab     | 3 |
   | 6 | [[dose-response-slug]]  | dose_response    | target         | replicate_matrix_BxT| $8k wet-lab      | 4 |
   | 7 | [[cross-context-slug]]  | cross_context    | target         | bootstrap_ci       | 16 GPU-h          | 4 |

   ## Run Order
   Stage 0: Sanity → Stage 1: Baseline → Stage 2: Validation + Negative-Control → Stage 3: Ablation + Mechanism → Stage 4: Robustness + Dose-response + Cross-context
   Decision gates at each stage boundary, including the negative-control gate at Stage 2 and the orthogonal-perturbation gate at Stage 3.   <!-- bio-C4 -->

   ## Budget
   - Total estimated: {N} GPU-hours; {N} MD wall-clock hours; {USD} wet-lab; {N} FTE-weeks; {N} days dataset access lead time   <!-- bio-C5 (via A6) -->
   - Budget limit: {--budget or "unlimited"}

   ## Next Steps
   - Run `/exp-run [[baseline-slug]]` to start Stage 1
   - After each stage, run `/exp-eval` to update wiki
   ```

## Constraints

- **Every experiment must be linked to a claim**: `target_claim` cannot be empty (baseline experiments may link to the Target claim)
- **No duplicate experiments**: before creating, check wiki/experiments/ for existing experiments with the same target_claim + hypothesis
- **Scoped claims are not modified**: claims scoped in Step 2 are not updated for status/confidence during this plan — only /exp-eval may update them
- **Success criteria must be quantified**: each experiment block's success criterion must include a specific number (e.g. "> 2% accuracy improvement")
- <!-- bio-C6 --> **`statistical_protocol` must be filled**: every experiment block must declare exactly one of `seeds_only | bootstrap_ci | stratified_kfold | replicate_matrix_BxT`. The selector follows Step 3's defaults; deviations must be justified in `## Setup`.
- <!-- bio-C6 --> **At least 3 seeds, OR alternative protocol**: when `statistical_protocol == seeds_only`, must specify >= 3 random seeds. When the protocol is bootstrap_ci, declare resample count (default 1000); when stratified_kfold, declare k (default min(5, n_positives)); when replicate_matrix_BxT, declare biological × technical counts (default >= 3 × >= 3).
- <!-- bio-C5 --> **Wet-lab decision is recorded, not silently dropped**: every plan that ran the wet-lab probe (Step 1 sub-step 4) must record `wet_lab_decision` in the report and log line, even when the value is `none`. `retrospective_only` plans must also write the constraint into `## Setup` (and into the idea's `conditions` block when the idea is from wiki).
- <!-- bio-C4 --> **Negative-control gate is mandatory** when a negative-control block was planned: a non-null negative-control result halts the validation conclusion regardless of the validation block's pass/fail status — record this in `## Follow-up`.
- **Graph edges via tools/research_wiki.py**: do not manually edit edges.jsonl
- **Idea status advances only forward**: proposed → in_progress, irreversible
- **Slug uniqueness**: check for existing slug before creating

## Error Handling

- **Idea not found**: prompt user to check slug, list candidates in wiki/ideas/
- **Target claim does not exist**: auto-create new claim page (status: proposed, confidence: 0.3), flag in report
- **Similar experiment already exists**: list existing experiments, ask user whether to add or skip
- **Review LLM unavailable** (--review mode): skip Step 5, note "unreviewed — Review LLM unavailable" in report
- **Budget insufficient**: reduce Stage 4 scope using the priority order from Step 4 (drop `cross_context` → `robustness` → `dose_response`); note actual budget allocation in report   <!-- bio-C4 -->
- **Slug conflict**: append numeric suffix (e.g. `sparse-lora-ablation-v2`)
- **Wiki is empty**: proceed normally but baseline experiments have no prior results to reference; recommend running /ingest for relevant papers first
- <!-- bio-C5 --> **Wet-lab probe runs in non-interactive mode**: when keyword hits exist but no `--wet-lab` flag was provided and no human is at the prompt (e.g. `/research` orchestration), default to `skip` and surface a clear "wet-lab probe deferred — rerun /exp-design with --wet-lab to resolve" line in the report.
- <!-- bio-C6 --> **`n_test` cannot be determined from the dataset metadata**: emit a warning, default to `bootstrap_ci`, and ask the user to populate `wiki/datasets/{slug}.versions[*].n_test` so future runs can pick the right protocol automatically.

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — generate slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log

### MCP Servers
- `mcp__llm-review__chat` — Step 5 experiment plan review (optional)

### Claude Code Native
- `Read` — read wiki pages
- `Glob` — find existing experiments and claims
- `AskUserQuestion` — Step 1 sub-step 4 wet-lab probe interactive branch (skipped when `--wet-lab` is preset or session is non-interactive)   <!-- bio-C5 -->

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Step 5 Review LLM review independence (if enabled)

### Called by
- `/research` Stage 2 (experiment design stage)
- User directly
