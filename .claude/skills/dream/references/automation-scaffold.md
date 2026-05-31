# /dream Automation

GitHub Actions is the unattended scheduler for `/dream`. It runs the same
agent-first memory loop as a manual slash pass and finalizes through
`tools/research_wiki.py dream`; the workflow is not a separate implementation.

## Source Of Truth

- `.github/workflows/dream.yml`: scheduled executor and manual dispatch.
- `config/dream.yml` (optional): user-owned scheduled defaults for mode,
  context limits, and `yolo`.
- `tools/research_wiki.py dream`: context preparation, response validation,
  proposal writing, guarded apply, and context rebuild.
- `tools/research_wiki.py scievolve-sense`: automatic sensing for durable
  failed states and apply-skip signals before context preparation.
- `wiki/outputs/evolution/dream/`: per-run context, prompt, response, report,
  and apply artifacts.
- `wiki/outputs/evolution/proposals.jsonl` and `applications.jsonl`: shared
  SciEvolve ledger entries.

## Workflow Behavior

- Scheduled run: `43 18 * * *` UTC.
- Scheduled runs read `config/dream.yml` when present. If absent, they use
  `mode=auto-apply`, default context limits, and `yolo=false`.
- Manual dispatch may set `mode=auto-apply` or `mode=propose-only`, tune the
  context limits, and explicitly override `yolo`.
- `yolo=true` can be set in `config/dream.yml` for unattended runs or in manual
  dispatch inputs. Page archive/merge mutations still require high-confidence,
  evidence-grounded proposals accepted by the deterministic finalizer.
- These defaults are safety posture for unattended CI, not a capability limit:
  scheduled `/dream` can still auto-apply validated memory updates, and explicit
  `yolo=true` enables high-confidence archive/merge apply paths.
- Claude Code Action is preferred when `ANTHROPIC_API_KEY` or
  `CLAUDE_CODE_OAUTH_TOKEN` is present. The workflow prepares context first,
  runs `scievolve-sense`, snapshots the wiki, asks Claude only to write
  `dream_agent_response.json`,
  rejects any pre-finalization wiki/source edits, then finalizes the same
  prepared run directory with a deterministic Python step.
- If Claude auth is absent, the fallback path calls
  `tools/research_wiki.py dream --use-llm` with the OpenAI-compatible `LLM_*`
  environment variables.
- If no policy runtime is available, the workflow fails closed.

## Secrets

Primary policy runtime:

- `ANTHROPIC_API_KEY`
- `CLAUDE_CODE_OAUTH_TOKEN`

Fallback policy runtime:

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LLM_FALLBACK_MODEL` (optional)

The fallback Python process reads `LLM_*` values from environment variables, so
the workflow exposes those secrets in the job-level `env:` block. Adding a repo
secret without exposing it to the job is not sufficient.

## Artifacts And Writeback

Each run uploads:

- `.dream/run/config.json`
- `.dream/run/instructions.md`
- `.dream/run/sense.json`
- `.dream/run/prepare.json` when Claude auth is used
- `.dream/run/dream_agent_response.json`
- `.dream/run/finalize.json`
- `.dream/run/stage-paths.txt`
- `wiki/outputs/evolution/dream/**`
- shared proposal/application ledgers and `wiki/graph/context_brief.md`

The workflow force-stages only paths declared by the finalizer, because the repo
intentionally ignores generated wiki outputs by default. That includes run
artifacts, sensed signals, proposal ledgers, safe memory metadata/body notes,
archive paths when `yolo` is enabled, and rebuilt downstream context.

## Setup And Status Checks

`/dream setup` should inspect:

- workflow file presence and `43 18 * * *` schedule
- optional `config/dream.yml` values for mode, context limits, and `yolo`
- job-level exposure of `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, and optional
  `LLM_FALLBACK_MODEL`
- Claude Code Action auth guidance for `ANTHROPIC_API_KEY` or
  `CLAUDE_CODE_OAUTH_TOKEN`
- write-boundary guard presence before finalization
- force-staging of finalizer-declared paths instead of broad `git add wiki`

`/dream status` should inspect the same workflow health plus recent local
`wiki/outputs/evolution/dream/` runs when present.

## Failure Behavior

- Missing policy secrets: fail before running a fake report-only loop.
- Missing Claude response file: fail before finalization.
- Claude writes outside `.dream/run/dream_agent_response.json`: fail before
  deterministic finalization and before any commit.
- Invalid agent response: finalization records rejected items; no unsafe apply
  happens.
- No meaningful proposals: write an empty response and finalized report so the
  unattended pass remains inspectable.
