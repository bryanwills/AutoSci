# SciEvolve Store

This directory is managed by `tools/research_wiki.py scievolve-*` commands.
It is the append-friendly evidence store for the full AutoSci agent boundary:
policy runtime, skills, deterministic tools, wiki memory, and DAG templates.
The policy runtime makes semantic proposals; deterministic tools validate,
apply, and ledger them.

- `signals.jsonl` records user/task/open-environment signals.
- `proposals.jsonl` indexes proposal artifacts.
- `proposals/` stores proposal Markdown/JSON pairs.
- `applications.jsonl` records guarded proposal applications.
- `reports/` stores dry-run evolution reports.
- `dream/`, `forge/`, and `morph/` store stage-specific run artifacts.
- `scievolve-sense` may append deduped signals from failed entity states,
  workflow log failures, and dream/forge apply skips.

Stage-specific skills extend this same substrate:

- `/dream` uses `dimension: memory`.
- `/forge` uses `dimension: workflow`.
- `/morph` uses `dimension: orchestration`.

The default mode is proposal-first. Recording signals and generating reports
does not mutate wiki entity pages, skills, templates, or DAGs.

Applied mutations target typed behavioral surfaces that downstream code already
consumes: SciEvolve memory metadata, skill protocols, and DAG templates/prompts.
Automatic self-evolution does not mean arbitrary source-code rewriting; core
runtime/schema changes remain a higher-risk code-review path.

`/dream` and `/forge` also have unattended GitHub Actions paths in
`.github/workflows/dream.yml` and `.github/workflows/forge.yml`. Scheduled runs
finalize through the same proposal/application store; `/dream` rebuilds
`wiki/graph/context_brief.md` whenever safe memory mutations are applied, and
`/forge` commits only finalizer-declared skill mutations.
