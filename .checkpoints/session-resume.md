# Session resume — last updated 2026-04-30

> One-page index for picking up this project mid-thread. Update on each significant skill run; do not let it grow into a journal.

## Where we are

- Branch: `main`
- HEAD: `615e940` — `ideate: structure-aware PTM modelling — 3 proposed + 2 failed ideas, 16 edges, banlist seeded`
- Branch is **28 commits ahead of origin/main** — push if cross-machine resume is needed.
- Working tree clean (untracked `.codex`, `.claude/scheduled_tasks.lock` are session-local; leave them).
- Wiki maturity: **warm** (papers=11, claims=15, ideas=5, edges=57, coverage=0.51).

## Workflow position

Last completed skills, in order:
1. `/init medpredict` — 12 user PDFs ingested in parallel via worktrees → 11 papers (1 off-topic magnetar paper pruned later).
2. `/edit` — removed off-topic magnetar paper (5 wiki pages, 3 edges, raw + prepared sidecars).
3. `/ideate` — direction "structure-aware PTM modelling for drug discovery"; produced 3 proposed + 2 failed ideas.

Pipeline state for the active research direction:

| Idea slug | Status | Priority | Composite | Next action |
|-----------|--------|----------|-----------|-------------|
| [[ptm-aware-degrader-target-nomination]] | proposed | 5 | 16 | `/exp-design ptm-aware-degrader-target-nomination` — start with Phase-0 ΔpTernary noise-floor calibration on CRBN+VHL TernaryDB subset |
| [[ptm-resolved-structurally-modeled-interactome]] | proposed | 5 | 10 | `/exp-design ptm-resolved-structurally-modeled-interactome` — pre-register 4-case holdout (14-3-3/Cdc25C, HIF1α/pVHL, PCNA/Pol-η-K164, FOXO3a/14-3-3) before any proteome-scale fold |
| [[ptm-conditioned-ensemble-prediction]] | proposed | 4 | 13 | `/exp-design ptm-conditioned-ensemble-prediction` — design a PTM adapter for Boltz-2; keep Boltz-sample (bioRxiv Jan 2026) as a head-to-head baseline |
| [[ptm-site-disorder-predictor]] | failed | 1 | — | banlist anti-repetition; do not revisit (saturated by SAPP/PhosAF/GraphPhos/AstraPTM2) |
| [[chirality-aware-af3-diffusion]] | failed | 1 | — | banlist; AF3 weights non-commercial, do not revisit unless we get DeepMind access |

Default next move: **`/exp-design ptm-aware-degrader-target-nomination`** (rank-1 idea, highest composite, Phase-0 noise-floor calibration is cheap and either kills or de-risks the idea fast).

## Constraints to clear before next /ideate or /novelty run

These tools were unavailable this session and degraded Phase-1/Phase-4 of `/ideate`:

- **Review LLM**: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` are empty in `/home/yukino/OmegaWiki/.env`. Without these, `/review` and `/novelty` cross-model verification skip the second-model independence step. Run `/setup` to configure.
- **Semantic Scholar**: `SEMANTIC_SCHOLAR_API_KEY` empty → public-tier rate limits hit immediately and block `/discover`, `/novelty`, `/daily-arxiv`. Free key at https://www.semanticscholar.org/product/api → `/setup`.
- **DeepXiv token**: auto-registered this session (token saved to `~/.env`, daily limit 1000). Search index is sparse for biology/structure domain — keep WebSearch as primary. No action needed unless coverage matters.

## Useful commands for resume

```bash
# Quick status
git log --oneline -10
"$PYTHON_BIN" tools/research_wiki.py maturity wiki/ --json
ls wiki/ideas/

# View top idea
cat wiki/ideas/ptm-aware-degrader-target-nomination.md

# Follow recommended next step
/exp-design ptm-aware-degrader-target-nomination

# Or alternative paths
/discover                       # find more papers around the active gaps
/ingest <pdf-or-arxiv>          # add a specific paper
/ideate <new-direction>         # start a new idea-generation arc

# Push to origin if resuming on another machine
git push origin main
```

## Key context anchors

- Active research direction (auto-selected): "structure-aware PTM modelling for drug discovery" — at the intersection of [[musitedeep-deep-learning-based-webserver-protein]], [[drug-design-targeting-active-posttranslational-modification]], [[alphafold-protein-structure-database-2024-providing]], [[towards-structurally-resolved-human-protein-interaction]].
- Saturated literature areas to avoid (Phase-1 finding): single-PTM phospho predictors (SAPP, PhosAF, GraphPhos, AstraPTM2, DeepPCT, MTPrompt-PTM); generic PROTAC ternary structure benchmarks (DeepTernary, PROTAC-STAN, ET-PROTACs); generic AF cryptic-pocket finders (SiteAF3 etc.).
- Known scoop risk: **Boltz-sample** (bioRxiv 2025-01-23, "Steering Conformational Sampling in Boltz-2 via Pair Representation Scaling") — directly threatens [[ptm-conditioned-ensemble-prediction]] if extended to PTM. Re-check before substantial investment in that idea.
- Off-topic paper removed: `s41586-021-04101-1.pdf` (magnetar giant flare) — do not re-ingest.

## Open `/init` checkpoints

`.checkpoints/init-*.json` (init-final-selection / init-pdf-titles / init-plan / init-prepare / init-sources) are kept as reference. The `init-session` task checkpoint was cleared at the end of `/init`.
