---
description: Full experiment execution pipeline — prepare code → deploy → monitor → collect results, supporting three run modes; setup-type detection routes to ML / MD / wet-lab / docking / workflow-manager directory templates
argument-hint: <experiment-slug> [--review] [--collect] [--full] [--env local|remote] [--setup-type {auto|ml|md|wet-lab|docking|snakemake|nextflow}]
---

<!-- bio-C7: Mirror of i18n/en/skills/exp-run/SKILL.md with C7 (per-setup-type directory layouts) drafted.
     Source of truth: i18n/en/skills/exp-run/SKILL.md. Do not run from this path; for testing, merge to source first.
     Cross-section dependencies:
       A5 — experiments[*].setup.assay_type / in_silico_or_wet / force_field drive the setup-type auto-detector.
       A6 — estimated_cost.md_wallclock_hours / wet_lab_usd surface in DEPLOY_REPORT for non-ML types.
       C4 — experiment.type {negative_control, mechanism, dose_response, cross_context} routes to the right Phase-1 procedure.
       C6 — statistical_protocol drives results-aggregation in Phase 4 (replicate_matrix_BxT collapses to mean±SEM
            across biological reps, not seeds).
     Per-type templates live (planned) at:
       skills/exp-run/references/templates/{ml,md,wet-lab,docking,snakemake,nextflow}/
     Templates are NOT yet authored — referenced as planned follow-up tooling. Until templates land,
     the auto-detector can still pick a type and write a stub layout; the user fills in the bio-specific bits. -->

# /exp-run

> Execute an experiment that has been planned in wiki/experiments/.
> **Three run modes** for different scenarios:
> - **Default (deploy)**: Phase 1-2 only — deploy and return immediately. Best for experiments that take hours or days.
> - **`--collect`**: Phase 3-4 only — check whether a deployed experiment has finished; collect results if so (`--check` is an alias).
> - **`--full`**: All four phases end-to-end. Best for short local experiments that finish in minutes.
>
> <!-- bio-C7 --> **Setup-type routing**: in Phase 1, detect whether the experiment is ML / MD / wet-lab / docking / Snakemake / Nextflow shaped from `setup` frontmatter (`assay_type`, `in_silico_or_wet`, `framework`, `force_field`) and write the corresponding directory layout from `references/templates/{type}/`. Falls back to the legacy `train.py + config.yaml + run.sh + requirements.txt` ML layout when no bio fields are populated.
>
> Recommended flow: `/exp-run <slug>` to deploy → `/exp-status` to monitor → `/exp-run <slug> --collect` to collect.

## Inputs

- `experiment`: slug from wiki/experiments/
  - deploy mode: status must be `planned`
  - --collect mode: status must be `running`
  - --full mode: status must be `planned`
- `--review` (optional): enable Review LLM code review for experiment code in Phase 1 (valid in deploy / full mode)
- `--collect` (optional): collect mode — check if the experiment has finished and collect results; `--check` is an alias
- `--full` (optional): full mode — execute all 4 phases (best for quick local experiments)
- `--env local|remote` (optional, default `local`): deployment environment
  - `local`: run directly on local GPU
  - `remote`: deploy to remote machine via SSH (requires `config/server.yaml`)
- <!-- bio-C7 --> `--setup-type {auto|ml|md|wet-lab|docking|snakemake|nextflow}` (optional, default `auto`): force the directory-layout template selection. `auto` infers from `setup` frontmatter (see Phase 1 step 3 detection rule). Use this only when the auto-detector picks the wrong template — the better fix is usually to populate the missing `setup` field.

## Outputs

- **deploy mode**:
  - Experiment code: `experiments/code/{slug}/` (generated in Phase 1) — directory layout depends on detected setup type   <!-- bio-C7 -->
  - `wiki/experiments/{slug}.md` — status: planned → running
  - **DEPLOY_REPORT** (printed to terminal) — deployment confirmation, session info, next steps, <!-- bio-C7 --> detected setup-type and template path
  - `wiki/log.md` — appended deploy log
- **collect mode** (experiment has finished):
  - `wiki/experiments/{slug}.md` — status: running → completed; outcome/key_result/date_completed filled in
  - **RUN_REPORT** (printed to terminal) — result summary, metrics comparison, next step suggestions
  - `wiki/log.md` — appended collect log
- **collect mode** (experiment still running):
  - Progress report printed to terminal only; wiki is not modified
- **full mode**: all outputs from both deploy and collect

## Wiki Interaction

### Reads
- `wiki/experiments/{slug}.md` — experiment config: setup, metrics, baseline, hypothesis, target_claim, <!-- bio-C7 --> setup-type detector inputs (`assay_type`, `in_silico_or_wet`, `force_field`, `solvent_model`, `framework`)
- `wiki/claims/{target-claim}.md` — target claim context (understand experiment purpose)
- `wiki/ideas/{linked-idea}.md` — linked idea's approach sketch (guide code implementation)
- `wiki/papers/*.md` — related papers' method details and hyperparameters (implementation reference)
- `wiki/experiments/*.md` — other experiments on the same claim (reference setup, avoid known mistakes)
- <!-- bio-C7 (depends on A1) --> `wiki/datasets/*.md` — dataset access tier and version info (drives wet-lab block lead-time and MD block input pinning)

### Writes
- `experiments/code/{slug}/` — experiment code directory (Phase 1, deploy / full mode); shape depends on detected setup type   <!-- bio-C7 -->
  - **ml** (legacy default): `train.py`, `config.yaml`, `run.sh`, `requirements.txt`
  - <!-- bio-C7 --> **md**: `mdrun.sh`, `system.gro`/`system.pdb` (input structure), `system.top` (topology), `mdp/em.mdp` + `mdp/nvt.mdp` + `mdp/npt.mdp` + `mdp/prod.mdp` (run-stage configs), `analysis.ipynb`, `requirements.txt`
  - <!-- bio-C7 --> **wet-lab**: `protocol.md` (experimentalist-readable), `materials.csv` (RRIDs / Cellosaurus / Addgene IDs / catalog numbers), `analysis.ipynb` (against the resulting CSV), `data/raw/` (placeholder), `data/processed/` (placeholder), `requirements.txt`
  - <!-- bio-C7 --> **docking**: `dock.sh`, `receptor.pdbqt`, `ligand_library.smi`, `box.txt` (search-box definition), `scoring.yaml`, `analysis.ipynb`, `requirements.txt`
  - <!-- bio-C7 --> **snakemake**: `Snakefile`, `config.yaml`, `envs/*.yaml`, `rules/*.smk`, `scripts/*.py`, `requirements.txt`
  - <!-- bio-C7 --> **nextflow**: `main.nf`, `nextflow.config`, `modules/*.nf`, `params.yaml`, `scripts/*.py`, `requirements.txt`
- `wiki/experiments/{slug}.md` — update status, outcome, key_result, date_completed, run_log, remote block
- `wiki/log.md` — append operation log

### Graph edges created
- **None**. The tested_by edges between experiments and claims are created by /exp-design.

## Workflow

**Precondition**: confirm working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).

---

### Deploy Mode (default, status == planned)

**Phase 1: Prepare**

1. **Read experiment page**:
   - `wiki/experiments/{slug}.md`: extract setup (model, dataset, hardware, framework), metrics, baseline, hypothesis
   - <!-- bio-C7 --> Also extract bio fields when present: `setup.in_silico_or_wet`, `setup.assay_type`, `setup.species`, `setup.cell_line`, `setup.force_field`, `setup.solvent_model`, `setup.simulation_length`, `setup.weight_version`, `experiment.type` (C4 enum), `statistical_protocol` (C6 enum)
   - Verify status == `planned`
   - If status is `running`, prompt user to use `--collect` mode
   - If status is `completed`/`abandoned`, refuse to execute

2. **Load implementation context**:
   - Read linked idea's approach sketch (implementation guide)
   - Read related papers' method descriptions (algorithm details)
   - Read other experiments on the same claim (reference code structure)

3. <!-- bio-C7 --> **Detect setup type** (skip if `--setup-type` was passed explicitly):

   Apply the following decision rule in order — first match wins:

   | Signal | Detected type |
   |--------|---------------|
   | `setup.in_silico_or_wet == "wet"` OR `setup.in_silico_or_wet == "hybrid"` | **wet-lab** |
   | `setup.assay_type` ∈ `{MD, MD-relaxation, FEP, GROMACS, AMBER}` (case-insensitive) OR `setup.force_field` non-empty | **md** |
   | `setup.assay_type` ∈ `{docking, virtual-screen, AutoDock, Vina, Glide, Schrödinger}` | **docking** |
   | `setup.framework` mentions `snakemake` OR Snakefile in linked-idea/paper context | **snakemake** |
   | `setup.framework` mentions `nextflow` / `nf-core` | **nextflow** |
   | none of the above (legacy CS path) | **ml** |

   Print the detected type in the DEPLOY_REPORT. When the detector picks `ml` despite bio fields being populated, that is almost always a setup-fields-undeclared problem — surface a 🟡 nudge in the report rather than blocking deployment.

4. **Write experiment code** to `experiments/code/{slug}/` from `references/templates/{detected-type}/`:

   **ml** (legacy default, unchanged from CS workflow):
   - `train.py`: generate training/evaluation script based on setup config, including:
     - Argument parsing (argparse, all hyperparameters configurable)
     - Data loading (support setup.dataset)
     - Model initialization (support setup.model and baseline model)
     - Training/inference loop
     - Metric computation (matching metrics list)
     - Result saving (JSON format, path: `results/{slug}/seed_{N}.json`)
     - Random seed control (multi-seed runs)
     - Checkpoint save/restore (`checkpoints/{slug}/`)
   - `config.yaml`: all hyperparameters (learning_rate, batch_size, epochs, seeds, etc.)
   - `run.sh`: complete launch command wrapper (includes CUDA_VISIBLE_DEVICES, logging, conda activation)
   - `requirements.txt`: experiment-specific dependencies (if different from main project requirements)

   <!-- bio-C7 -->

   **md**: Generate from the MD template. Required fills (refuse to deploy when any required field is empty):
   - `mdrun.sh`: GROMACS-style launch (`gmx grompp` + `gmx mdrun`) with seed pinning and per-stage checkpoints. Honor `setup.force_field`, `setup.solvent_model`, `setup.simulation_length`.
   - `system.gro` / `system.pdb` (placeholder + a clear comment naming the source PDB ID and any preprocessing required — solvation, ions, minimization).
   - `system.top` (topology — generated by `gmx pdb2gmx` against `setup.force_field`).
   - `mdp/em.mdp` (energy-min), `mdp/nvt.mdp` (NVT equilibration), `mdp/npt.mdp` (NPT equilibration), `mdp/prod.mdp` (production). Fill `nsteps` from `setup.simulation_length` (e.g. `100ns` → `nsteps = 50000000` at 2-fs dt).
   - `analysis.ipynb`: scaffold cells for RMSD, RMSF, radius-of-gyration, secondary-structure assignment; annotated as "fill after collect".
   - `results/{slug}/`: results saved as `traj.xtc` + `summary.json` (the analysis notebook reads from here in Phase 4).

   **wet-lab**: Generate from the wet-lab template. Required fills:
   - `protocol.md`: human-readable bench protocol with sections — Materials, Reagents, Equipment, Step-by-step procedure, Read-out, Pause points, Safety. The auto-generator pre-fills `setup.assay_type`, `setup.cell_line`, `setup.species`, and the C6 replicate counts (biological × technical).
   - `materials.csv`: columns `kind | name | identifier | identifier_type | catalog | vendor | lot | url`. `identifier_type` ∈ `{RRID, CVCL, Addgene, NCBI-Taxonomy, ChEBI, free-text}`. Refuse to deploy with no materials when `assay_type ∈ {immunoblot, IF, IHC, flow}` — those assays have antibody-quality reproducibility risk and need RRIDs.
   - `analysis.ipynb`: scaffold cells assuming a CSV result file; for `replicate_matrix_BxT` (C6), pre-fills the per-replicate aggregation (mean±SEM across biological reps, raw points across technical reps).
   - `data/raw/.gitkeep` and `data/processed/.gitkeep` placeholders.
   - **Phase-2 deploy** for wet-lab is intentionally a no-op (see Phase 2 below).

   **docking**: Generate from the docking template. Required fills:
   - `dock.sh`: AutoDock Vina-style launch by default; honor `setup.framework` if it names a different docker.
   - `receptor.pdbqt` (placeholder + the source PDB ID).
   - `ligand_library.smi` (placeholder + the source library name and version, e.g. ZINC22 subset).
   - `box.txt` (search-box center + dimensions; fill from `setup.binding_site` if present, else placeholder with a clear "TODO" comment).
   - `scoring.yaml`: scoring function selection + reproducibility seed.
   - `analysis.ipynb`: top-N pose extraction, redocking RMSD, scoring distribution.

   **snakemake / nextflow**: Generate from the corresponding workflow-manager template. Required fills:
   - `Snakefile` / `main.nf`: top-level rules / processes per workflow stage.
   - `config.yaml` / `params.yaml`: parameters with defaults; honor `setup` fields.
   - `envs/*.yaml` (Snakemake) or per-process container directives (Nextflow): pin tool versions for reproducibility.
   - `rules/*.smk` / `modules/*.nf`: per-stage logic; the auto-generator emits skeletal `rule` / `process` blocks based on the experiment's metric list and refuses to fabricate logic the user has to fill in.
   - `requirements.txt`: workflow runner version (`snakemake>=8`, `nextflow>=24.04`).

5. **Optional Review LLM code review** (`--review`):
   ```
   mcp__llm-review__chat:
     system: "You are a senior {ML | MD | wet-lab | docking | workflow-manager} engineer reviewing experiment code.   <!-- bio-C7 -->
              Focus on: correctness of the core procedure, proper evaluation protocol,
              fair baseline comparison, reproducibility (seeds / determinism / replicate
              matrix / version pinning), proper metric computation, and common pitfalls
              (data leakage, wrong split, gradient accumulation bugs;
              MD: incomplete equilibration, wrong barostat/thermostat coupling, periodic-image artefacts;
              wet-lab: missing RRID, no biological replicates, missing positive control;
              docking: wrong protonation state, undefined search box, scoring-function bias;
              snakemake/nextflow: undeclared inputs/outputs, missing container pinning)."
     message: |
       ## Experiment
       {experiment title and hypothesis, plus detected setup-type}     <!-- bio-C7 -->

       ## Code
       {generated code}

       ## Expected Behavior
       {setup details from wiki page}

       Review for correctness and potential issues.
   ```
   Fix code based on Review LLM feedback. The system-prompt vocabulary is specialized to the detected type so the reviewer flags type-appropriate failure modes (an MD reviewer should not silently apply ML pitfalls to a `gmx mdrun` script).

6. **Sanity check (small-scale validation)**:
   - **ml**: run at minimal scale (1 epoch / 100 steps / small subset); verify loss decreases.
   - <!-- bio-C7 --> **md**: run a 100-step `gmx mdrun -nsteps 100`; verify trajectory file is written and energies are finite. Drop-in replacement for "loss decreases".
   - <!-- bio-C7 --> **docking**: dock 5 ligands; verify pose files generated and scores are within plausible range (-15 to 0 kcal/mol for AutoDock).
   - <!-- bio-C7 --> **snakemake / nextflow**: dry-run (`snakemake --dry-run` / `nextflow run main.nf -with-trace --stub`) — verify DAG resolves, rules/processes have all declared inputs.
   - <!-- bio-C7 --> **wet-lab**: sanity check is N/A; skip with a note in the DEPLOY_REPORT — wet-lab "sanity" is a researcher's bench review of the protocol, not an automated check.
   - If sanity fails → fix code, retry once; if still failing, report error and stop.

**Phase 2: Deploy**

#### Local mode (`--env local` or default)

<!-- bio-C7: Phase-2 routing per detected type -->

For **ml** experiments (legacy path, unchanged):

1. **Check GPU**: `nvidia-smi` to confirm GPU available and sufficient VRAM
2. **Launch**:
   ```bash
   screen -dmS exp-{slug} bash -c \
     "cd $(pwd) && bash experiments/code/{slug}/run.sh 2>&1 | tee logs/exp-{slug}.log"
   ```
3. Update `wiki/experiments/{slug}.md`:
   - status: `running`
   - run_log: `logs/exp-{slug}.log`
4. **Estimate runtime** and write to frontmatter:
   Estimate based on `setup.hardware` (GPU model/count), `setup.model` (parameter count), `setup.dataset` (scale):

   | Typical scenario | Estimated range |
   |-----------------|-----------------|
   | Single GPU + small dataset (CIFAR / small NLP benchmark) | 0.5 – 3h |
   | Single A100 + medium dataset (ImageNet / GLUE) | 4 – 12h |
   | Multi-GPU or large model fine-tuning (≥7B) | 8 – 48h |

   ```bash
   python3 tools/research_wiki.py set-meta \
     wiki/experiments/{slug}.md started "{YYYY-MM-DDTHH:MM}"
   python3 tools/research_wiki.py set-meta \
     wiki/experiments/{slug}.md estimated_hours {N}
   ```
5. Append log:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | deployed {slug} | env: local | session: exp-{slug} | eta: {N}h | type: ml"
   ```

<!-- bio-C7 -->

For **md** experiments:

1. **Check GPU**: same as ML; MD on CPU is allowed but flag a 🟡 nudge in the report (~10× slower).
2. **Launch**:
   ```bash
   screen -dmS exp-{slug} bash -c \
     "cd $(pwd) && bash experiments/code/{slug}/mdrun.sh 2>&1 | tee logs/exp-{slug}.log"
   ```
3. Update wiki frontmatter as for ml.
4. **Estimate MD wall-clock** from `setup.simulation_length` and hardware. Reference table (single A100, GROMACS 2024, AMBER ff14SB, ~50k-atom system):

   | simulation_length | Estimated wall-clock |
   |-------------------|----------------------|
   | 100 ns            | 8 – 16h              |
   | 500 ns            | 1.5 – 3 days         |
   | 1 µs              | 3 – 7 days           |
   | 10 µs             | 1 – 2 months         |

   Write to `estimated_cost.md_wallclock_hours` (A6); legacy `estimated_hours` is set to the same number for backward compat.
5. Append log with `type: md`.

For **docking** experiments:

1. **Check GPU**: docking can run CPU-only for small libraries; require GPU only when library size > 10k.
2. **Launch**: same `screen -dmS` pattern; entrypoint is `dock.sh`.
3. Estimate from `ligand_library` size: ~0.5–2s/ligand on a single GPU; refuse to deploy a 10M-ligand library without explicit user confirmation.
4. Write to `estimated_cost.gpu_hours` and `estimated_cost.cpu_hours`.

For **snakemake / nextflow** experiments:

1. **Pre-deploy DAG check**: `snakemake --dry-run` / `nextflow run main.nf -with-trace --stub` (already done in Phase 1 sanity); refuse to deploy if the DAG does not resolve.
2. **Launch**: `screen -dmS exp-{slug} bash -c "snakemake --cores all"` or `screen -dmS exp-{slug} bash -c "nextflow run main.nf -resume"`.
3. Estimate from longest-stage cost; nextflow `-resume` lets a re-deploy pick up where the last run left off.

For **wet-lab** experiments:

1. **Phase-2 deploy is a no-op for wet-lab**. Print the protocol path in DEPLOY_REPORT and instruct the user to run the experiment at the bench.
2. Set status to `running` and `started` to today's date so `/exp-status` can track elapsed time.
3. Write to `estimated_cost.wet_lab_usd` and `estimated_cost.fte_weeks` from the `setup` fields.
4. Append log with `type: wet-lab` so `/exp-status --collect-ready` knows not to poll for a screen session that doesn't exist.

#### Remote mode (`--env remote`)

**Prerequisite**: user has configured `config/server.yaml`.

1. **Confirm connectivity**: `python3 tools/remote.py status`
   - If unreachable → report error and suggest checking config/server.yaml
2. **Find free GPU**: `python3 tools/remote.py gpu-status`
   - If no free GPU → report each GPU's usage, suggest waiting
3. **Sync code**: `python3 tools/remote.py sync-code`
4. **Install dependencies** (first time or if requirements changed): `python3 tools/remote.py setup-env`
5. **Launch remote experiment**:
   ```bash
   python3 tools/remote.py launch \
     --name "exp-{slug}" \
     --cmd "{entrypoint per setup-type: bash run.sh | bash mdrun.sh | bash dock.sh | snakemake --cores all | nextflow run main.nf}"   <!-- bio-C7 -->
     --gpu {gpu_index}
   ```
6. Update `wiki/experiments/{slug}.md` frontmatter — all of these fields already exist (empty) because `/exp-design` wrote the full CLAUDE.md template:
   ```bash
   # Top-level scalar fields — use set-meta
   python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md status running
   python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md run_log "logs/exp-{slug}.log"
   ```

   The nested `remote:` block cannot be updated via `set-meta` (it only handles top-level scalar fields). Use the `Edit` tool directly to replace the five empty sub-field values in place. The pre-existing block in the file looks like:
   ```yaml
   remote:
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ```
   Use five Edit calls (one per sub-field) to set `server`, `gpu`, `session`, `started`. Leave `completed: ""` — Phase 4 fills that. If you find the `remote:` block missing from the file, that means `/exp-design` did not write the full CLAUDE.md template; stop and report the bug rather than trying to append the block here (appending would drift the file away from the canonical order and break future edits).

7. **Estimate runtime** and write to frontmatter (same per-type logic as local mode; <!-- bio-C7 --> populate `estimated_cost.*` rather than only `estimated_hours` for non-ML types).
8. Append log with `type: {detected}`:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | deployed {slug} | env: remote | server: {host} | gpu: {gpu} | eta: {N}h | type: {detected}"
   ```

**Print DEPLOY_REPORT to terminal**:

```markdown
# Deploy Report: {experiment title}

### Status: DEPLOYED ✅

- Setup type: {ml | md | wet-lab | docking | snakemake | nextflow}    <!-- bio-C7 -->
- Template: skills/exp-run/references/templates/{type}/                <!-- bio-C7 -->
- Session: exp-{slug}
- Environment: local | remote ({host} GPU {gpu})
- Log file: logs/exp-{slug}.log
- Code: experiments/code/{slug}/
- Estimated: ~{N}h ({estimated_cost.* primary dim — md_wallclock_hours / gpu_hours / wet_lab_usd / fte_weeks})    <!-- bio-C7 -->

### Next Steps

1. Monitor progress: `/exp-status`
2. Check this experiment: `/exp-run {slug} --collect`
3. In /research pipeline: progress saved to wiki/outputs/pipeline-progress.md
{wet-lab only:} 4. Run the experiment at the bench using protocol.md; once results.csv is in place, `/exp-run {slug} --collect`.   <!-- bio-C7 -->

### Quick Commands
```bash
# Local: check if still running
screen -ls | grep exp-{slug}

# Local: tail log
tail -f logs/exp-{slug}.log
```
```

---

### Collect Mode (`--collect` or `--check`, status == running)

**Phase 3: Monitor / Check Run Status**

1. **Read deployment info**: from `wiki/experiments/{slug}.md` frontmatter, get environment (local or remote) and session name. <!-- bio-C7 --> Also re-read the detected setup-type from the deploy log line.

2. **Check whether the process is still alive** (skip for wet-lab):
   - **Local**: `screen -ls | grep exp-{slug}`
   - **Remote**: `python3 tools/remote.py check --name "exp-{slug}"`, parse `alive` field
   - <!-- bio-C7 --> **wet-lab**: there is no process to check. Look for `data/processed/results.csv` (or whatever path the protocol's read-out section names); if absent, prompt the user.

3. **If experiment is still running (alive == true)**:
   - Fetch recent logs:
     - Local: `tail -30 logs/exp-{slug}.log`
     - Remote: `python3 tools/remote.py tail-log --name "exp-{slug}" --lines 30`
   - **Anomaly detection** (per setup-type) <!-- bio-C7 -->:
     - **ml**: `loss: nan`, `loss: inf`, `CUDA out of memory`, Python tracebacks
     - **md**: NaN energies, LINCS warnings, "Step ... has too large of a force", periodic-image artefacts surfacing as huge instantaneous forces
     - **docking**: zero poses returned, all scores below -100 (likely a bug, not a real result)
     - **snakemake / nextflow**: rule/process failed; surface the failed step and its log path
   - **Automatic fix attempt** (if anomaly detected, at most 1 attempt):
     - **ml** NaN/exploding → resume from latest checkpoint, reduce learning rate
     - **ml** OOM → reduce batch size, restart
     - **md** LINCS warning at start → re-do energy minimization with tighter `emtol`
     - **docking** zero poses → enlarge search box by 50% (warn the user)
     - workflow-manager: do not auto-retry — surface the failed stage and let the user decide
   - **Print progress report** (do not modify wiki, report only):
     ```
     Experiment {slug}: RUNNING
     Type: {detected setup-type}     <!-- bio-C7 -->
     Progress: step {N} / epoch {E}  (md: ns simulated; docking: ligands processed; workflow: stages complete)
     Latest metric: {metric} = {value}
     Anomalies: {none | NaN detected | ...}
     Estimated remaining: ~{N} hours
     Run `/exp-status` to monitor all running experiments.
     ```
   - **Return** (do not execute Phase 4)

4. **If experiment has finished (alive == false / session gone, or wet-lab CSV present)**:
   - Continue to Phase 4

**Phase 4: Collect Results**

1. **Pull remote results** (remote mode only): same `tools/remote.py pull-results` flow; the path inside `results/{slug}/` depends on setup-type.

2. **Check result files exist**:
   - **ml**: `results/{slug}/seed_*.json`
   - <!-- bio-C7 --> **md**: `results/{slug}/traj.xtc` + `results/{slug}/summary.json` (energies, RMSD time-series)
   - <!-- bio-C7 --> **docking**: `results/{slug}/poses_*.pdbqt` + `results/{slug}/scores.csv`
   - <!-- bio-C7 --> **wet-lab**: `data/processed/results.csv` (the primary read-out, exact path per protocol's read-out section)
   - <!-- bio-C7 --> **snakemake / nextflow**: declared output channels per the workflow definition

3. **Parse results** (per setup-type, with C6 statistical_protocol awareness) <!-- bio-C7 -->:
   - **ml** (`seeds_only`): mean ± std per metric across seeds
   - **md**: read summary.json — RMSD steady-state, RMSF, radius-of-gyration; bootstrap CI from per-frame samples
   - **docking**: top-N pose scores + redocking RMSD; report median + 95% range
   - **wet-lab** (`replicate_matrix_BxT`): mean ± SEM across biological replicates; raw points across technical replicates; do not collapse the two
   - **bootstrap_ci**: 1000 resamples; report 95% CI (use `scipy.stats.bootstrap` or equivalent)
   - **stratified_kfold**: per-fold metric + macro mean; do not average across folds blindly when class balance differs
   - Compare with baseline, compute improvement delta with the matching statistical-protocol confidence interval

4. **Update experiment page** `wiki/experiments/{slug}.md`:
   - status: `completed`
   - outcome: `succeeded` / `failed` / `inconclusive`
     - succeeded: all success criteria met
     - failed: core metrics did not reach target
     - inconclusive: mixed results or excessive variance
   - key_result: one-sentence summary of the core finding
   - date_completed: today's date
   - Fill `## Results` section: complete results table, with the statistical protocol named in the caption   <!-- bio-C7 (depends on C6) -->
   - Fill `## Analysis` section: preliminary analysis
   - If remote mode: update `remote.completed` timestamp

5. **Append log**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | completed {slug} | outcome: {outcome} | key: {key_result} | type: {detected}"
   ```

6. **Print RUN_REPORT to terminal**:
   ```markdown
   # Run Report: {experiment title}

   ## Outcome: {succeeded / failed / inconclusive}
   ## Setup type: {ml / md / wet-lab / docking / snakemake / nextflow}    <!-- bio-C7 -->
   ## Statistical protocol: {seeds_only / bootstrap_ci / stratified_kfold / replicate_matrix_BxT}    <!-- bio-C7 (C6) -->

   ## Results
   | Metric | Baseline | Ours ({mean±std | mean±SEM | bootstrap-CI | per-fold}) | Δ |
   |--------|----------|-------------------------------------------------------|---|
   | {metric} | {baseline-value} | {ours} | +{delta} |

   ## Key Finding
   {key_result}

   ## Next Steps
   - Run `/exp-eval {slug}` to update claims in wiki
   - {if succeeded: proceed to next experiment in plan}
   - {if failed: analyze failure, consider /exp-design revision}
   ```

---

### Full Mode (`--full`, status == planned)

Execute all 4 phases in sequence (Phase 1 → Phase 2 → Phase 3 → Phase 4) without returning.

Use case: quick local CPU/GPU experiments that finish in minutes (sanity checks, toy dataset validation, etc.).

In Phase 3, instead of checking "is it still running", wait for the screen session to actually exit before executing Phase 4:
```bash
# Wait for session to end (polling)
while screen -ls | grep -q "exp-{slug}"; do
  sleep 30
done
# Session gone, proceed to Phase 4
```

<!-- bio-C7 --> `--full` mode is **not supported** for `wet-lab` setup-type — wet-lab cannot complete in minutes. Refuse with a clear message: "wet-lab experiments use the deploy + bench-execute + collect flow; use `/exp-run {slug}` then run protocol.md, then `/exp-run {slug} --collect`."

---

## Constraints

- **Deploy mode only accepts planned experiments**: if status is running, prompt to use --collect; if completed, refuse
- **Collect mode only accepts running experiments**: if status is planned, prompt to deploy first; if completed, note it is already done
- **Collect mode: do not write wiki when alive**: only report progress, do not modify any wiki files
- **Code goes in experiments/code/{slug}/**: do not write to project root or any other location
- **Do not update claims**: experiment results are written only to experiments/ pages; claim updates are handled by /exp-eval
- **Sanity check must pass**: Phase 1 sanity failure blocks deployment (unless user explicitly overrides). <!-- bio-C7 --> Wet-lab is the only exception — sanity is N/A.
- **Results must be saved**: all experiment results saved as JSON in `results/{slug}/seed_{N}.json` <!-- bio-C7 --> for ml; per-type artefacts for md / docking / wet-lab / workflow-manager (see Phase 4 step 2).
- **Multi-seed results use mean**: report mean ± std, not single-run results. <!-- bio-C7 --> When `statistical_protocol != seeds_only`, report the matching aggregation (bootstrap CI / per-fold / replicate matrix) — do not silently default to mean ± std.
- **Graph edges are not created here**: tested_by edges were created by /exp-design
- **Automatic fix attempts are limited to 1**: prevents infinite restart loops
- <!-- bio-C7 --> **Setup-type auto-detection is not authoritative**: the user can override via `--setup-type`. The detector is a heuristic over `setup` fields and will mis-route when those fields are empty. The fix is almost always to populate the missing field, not to silently override the detector.
- <!-- bio-C7 --> **Wet-lab template requires materials**: refuse to deploy a wet-lab experiment whose `materials.csv` is empty or whose `assay_type` implies antibodies but no RRID is recorded — the reproducibility loss is too high.

## Error Handling

- **Experiment not found**: prompt user to check slug, list candidates in wiki/experiments/ (status=planned or running)
- **Deploy mode but status == running**: prompt "already running — use `/exp-run {slug} --collect` to check status"
- **Collect mode but status == completed**: prompt "already completed — run `/exp-eval {slug}` directly"
- **GPU unavailable**: report error, suggest using --env remote or waiting for GPU to free up
- **Review LLM unavailable** (--review mode): skip code review, note "unreviewed" in DEPLOY_REPORT
- **Sanity check fails**: report detailed error, attempt one automatic fix, if still failing stop and suggest manual debugging
- **Remote connection fails**: report SSH error, suggest checking connection config and config/server.yaml
- **Result files missing** (collect mode): report which seeds are missing results; summarize available results normally; if successful seeds < 2, mark inconclusive
- **Experiment crashed** (traceback detected in collect mode): include crash info and suggested fix directions in report
- **--full mode wait timeout**: if screen session persists beyond 2× the estimated time, warn user but do not force-terminate
- <!-- bio-C7 --> **Setup-type detector picks `ml` despite bio fields**: surface a 🟡 nudge, deploy with the `ml` template anyway; the user can re-deploy after populating the missing field.
- <!-- bio-C7 --> **Required setup-type template not yet authored**: when `references/templates/{type}/` does not exist (current state, until follow-up tooling lands), generate a stub directory with `protocol.md` (or per-type entrypoint) containing only the section headers and a comment "fill from setup fields"; warn the user that template scaffolding is incomplete.
- <!-- bio-C7 --> **wet-lab CSV missing in collect mode**: do not auto-mark `inconclusive`; prompt the user "drop your CSV at data/processed/results.csv and rerun /exp-run {slug} --collect" — the experiment is genuinely still running at the bench.

## Dependencies

### Skills（via Skill tool）
- No direct sub-skill calls

### Tools（via Bash）
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md <field> <value>` — update top-level scalar
- `python3 tools/remote.py <command>` — remote operations (status, gpu-status, sync-code, setup-env, launch, check, tail-log, pull-results)
- `nvidia-smi` — local GPU status
- `screen` — local background process management
- <!-- bio-C7 --> `gmx grompp` / `gmx mdrun` (GROMACS, MD path) — invoked from `mdrun.sh`; not a `/exp-run` direct dep
- <!-- bio-C7 --> `vina` / `smina` / `gnina` (docking path) — invoked from `dock.sh`; not a `/exp-run` direct dep
- <!-- bio-C7 --> `snakemake` / `nextflow` — invoked from the workflow-manager templates

### Configuration
- `config/server.yaml` — remote server config (required only with `--env remote`)

### MCP Servers
- `mcp__llm-review__chat` — Phase 1 code review (optional, when `--review` is used). System prompt is specialized to the detected setup-type.   <!-- bio-C7 -->

### Claude Code Native
- `Read` — read wiki pages and log files
- `Write` — write experiment code to `experiments/code/{slug}/`
- `Bash` — execute deployment commands, monitor processes

### Local References
- <!-- bio-C7 --> `skills/exp-run/references/templates/ml/` (existing implicit pattern)
- <!-- bio-C7 --> `skills/exp-run/references/templates/md/` (planned)
- <!-- bio-C7 --> `skills/exp-run/references/templates/wet-lab/` (planned)
- <!-- bio-C7 --> `skills/exp-run/references/templates/docking/` (planned)
- <!-- bio-C7 --> `skills/exp-run/references/templates/snakemake/` (planned)
- <!-- bio-C7 --> `skills/exp-run/references/templates/nextflow/` (planned)

### Called by
- `/research` Stage 3a (deploy mode) and Stage 3c (collect mode)
- `/exp-status --collect-ready` (collect mode)
- User directly
