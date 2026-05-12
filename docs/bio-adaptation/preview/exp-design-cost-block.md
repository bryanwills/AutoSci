# Preview — A6 structured `estimated_cost` block

> A6 is **pilot-merged as of 2026-05-11**. This file is no longer a "preview of what's coming"; it's a tightly-framed example of what's now live in the wiki, useful as a single-screen reference for storyboard scene 3.
>
> Per-experiment numbers and the changelog entry: [`../CHANGELOG.en.md`](../CHANGELOG.en.md) / [`../CHANGELOG.zh.md`](../CHANGELOG.zh.md) section "A6 pilot merge".

## What changed in `experiments/{slug}.md` frontmatter

**Before** (legacy single-number budget, kept as fallback):

```yaml
estimated_hours: 12
```

**After A6** (structured cost block, additive — `estimated_hours` kept alongside):

```yaml
estimated_hours: 12   # legacy; superseded by estimated_cost below — MD wall-clock dominates
estimated_cost:
  gpu_hours: 4               # Boltz-2 inference + DeepTernary scoring
  cpu_hours: 1
  md_wallclock_hours: 8      # 50 ns explicit-solvent MD per tuple × ~25 tuples; dominant cost
  wet_lab_usd: 0
  fte_weeks: 0.5
  dataset_access_lead_time_days: 0
```

## What this unlocks for a bio researcher

The single-number `estimated_hours: 12` previously hid four constraints that matter for actually running a PROTAC ternary-complex pipeline:

| Sub-field | Why a bio researcher cares |
|---|---|
| `md_wallclock_hours` | Molecular dynamics is the bottleneck on PROTAC pipelines that need PTM-occupied POI structures. Knowing MD is 8 h *separate from* GPU inference lets you batch differently, request specific node types, or substitute the MD-relaxed route with a cheaper Boltz-2 native CCD-PTM-token route. |
| `wet_lab_usd` | A wet-lab follow-up (e.g. cellular degradation assay validating a top-ranked PROTAC) lives on a wholly different procurement timeline. Hiding it inside hours makes wet-lab steps invisible to /exp-design's budget-cut order. |
| `dataset_access_lead_time_days` | TernaryDB and PROTAC-DB are public (0 days). DegronMD requires registration (~7 days). PhosphoSitePlus academic license (~3 days). Cohort data from clinical partners (30+ days). The number changes which experiments can start *this week* vs *next month* — orthogonal to compute cost. |
| `fte_weeks` | Researcher-time is the real scarce resource for academic labs. Even a 4-GPU-hour experiment that needs 0.75 FTE-weeks of preprocessing (custom dataset curation, manual structure inspection) deserves to be flagged. |

## The 8-experiment budget after A6

`sum(estimated_cost.gpu_hours)` = **96**, `sum(.md_wallclock_hours)` = **8**, total compute = **104 h** — matches the headline `≈104 GPU-h` from the 2026-05-02 `/exp-design` log entry. **MD wall-clock is now visible separately** (was previously collapsed inside `estimated_hours: 12` on the boltz2 ablation).

| Experiment | gpu | md | fte |
|---|---:|---:|---:|
| `deepternary-baseline-ternarydb-crbn-vhl-reproduction` | 4 | 0 | 0.25 |
| `phase0-noise-floor-calibration-deepternary-ptm-perturbations` | 24 | 0 | 1.0 |
| `calibrated-deltapternary-phospho-protac-ranking` | 16 | 0 | 0.75 |
| `ablation-uncalibrated-vs-calibrated-deltapternary` | 4 | 0 | 0.25 |
| **`ablation-boltz2-ptm-vs-md-relaxed-route`** | **4** | **8** | **0.5** |
| `ablation-deepternary-vs-protac-stan-scorer` | 16 | 0 | 0.5 |
| `robustness-cross-ptm-type-ubiq-methyl` | 16 | 0 | 0.5 |
| `robustness-mutant-isoform-track-y220c-r175h` | 12 | 0 | 0.5 |

## What's still drafted (next merge candidate after A6)

C2 (`/exp-design` SKILL.md upgrade) — once C2 lands, the next `/exp-design` invocation will populate `estimated_cost` directly instead of `estimated_hours`. Schema is ready; the prompt-side awareness is the remaining piece.

C3 (bio-lint, `tools/lint_bio.py`) — will warn when a bio-domain experiment has only `estimated_hours` set without a corresponding `estimated_cost` block.
