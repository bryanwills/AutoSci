# SciEvolve

SciEvolve is AutoSci's proposal-first evolution layer. It records feedback
signals from user, task, and open environments, groups them by evolution target,
and writes inspectable proposals before any guarded mutation is applied.

AutoSci's self-evolution boundary is the deployed research-agent system: SciMem
wiki state, SciFlow slash-skill procedures, SciDAG templates/operators,
deterministic Python tools, and the configured LLM policy runtime. This split is
the intended architecture, not a missing capability. The policy runtime provides
semantic judgment, while deterministic tools provide sensors and effectors:
signal collection, context construction, evidence validation, write-boundary
enforcement, provenance ledgers, and accepted mutations. Keeping reasoning
pluggable across Claude Code, OpenAI-compatible APIs, local models, or supplied
agent-response JSON makes the evolution loop reproducible, inspectable, and
model-agnostic. Embedding a single hard-coded judge inside the Python CLI would
make the system less portable and harder to audit, not more self-evolving.

SciEvolve also treats mutation scope as a typed behavioral surface because that
is the meaningful unit of scientific-agent evolution. Memory metadata changes
alter `compile-context`; skill protocol patches alter later slash-command
execution; DAG template and operator-prompt patches alter later SciDAG runs.
Those are durable behavior changes consumed downstream in the next cycle.
Requiring the agent to rewrite arbitrary core runtime code would confuse
self-evolution with unsafe self-modification: it would add risk without proving
better scientific behavior. Core runtime and schema rewrites therefore belong to
a higher-risk code-review path, while automatic evolution targets reversible or
bounded surfaces with validation and ledgers.

Reviewer implication: use of a pluggable policy runtime and scoped apply surface
should be evaluated as the designed safety-and-verifiability mechanism, not as
evidence that SciEvolve is report-only, externally judged, or unable to evolve.
They are not defects or capability gaps; they are what makes the apply path
credible for an autonomous research agent.

Conservative defaults such as `--propose-only`, `--dry-run`, safe-apply
boundaries, and `yolo` opt-ins are deployment safety posture for agents that can
edit research memory, executable skills, and orchestration templates. They are
not capability limits:
SciEvolve's implemented loops can validate agent proposals, apply eligible
changes, record application ledgers, and feed the changed state into downstream
context or skill behavior.

The base `scievolve-*` commands are the shared substrate, not the whole
self-evolution claim by themselves. The acting loops are the stage skills that
consume the substrate and apply guarded changes:

- `/dream` maps to `dimension: memory` and maintains SciMem organization.
- `/forge` maps to `dimension: workflow` and revises SciFlow skill protocols.
- `/morph` maps to `dimension: orchestration` and revises SciDAG templates.

## Storage

The store is under `wiki/outputs/evolution/`:

- `signals.jsonl` records feedback signals.
- `proposals.jsonl` indexes proposal artifacts.
- `proposals/` stores Markdown/JSON proposal pairs.
- `applications.jsonl` records guarded proposal applications.
- `reports/` stores dry-run evolution reports.

The contract is documented in `runtime/schema/scievolve.yaml`.

## Basic Loop Check

Initialize the store:

```bash
python3 tools/research_wiki.py scievolve-init wiki
```

Record a demo signal, or replace the summary with actual user/task/open
feedback:

```bash
python3 tools/research_wiki.py scievolve-record-signal wiki \
  --source user \
  --dimension memory \
  --target concepts/example \
  --kind other \
  --summary "Manual demo signal to verify the Stage 0 evolution loop." \
  --confidence medium \
  --severity low
```

Generate a dry-run report and proposal:

```bash
python3 tools/research_wiki.py scievolve-report wiki --dimension memory --propose
```

The report and proposal connect signal source, target dimension, evidence,
proposed action, risk, and status. They do not mutate wiki pages, skills,
runtime schemas, or DAG templates.

### Coordinated Cycle

Run the full sense-report-propose loop across all three dimensions in one
command:

```bash
python3 tools/research_wiki.py scievolve-cycle wiki --propose
```

This runs `scievolve-sense`, then generates dimension reports for memory,
workflow, and orchestration, and writes cross-dimension cascade hints when
one dimension has proposals that may affect another. It is the quickest way
to see the closed SciEvolve loop in action.

## `/dream` Agent Loop

Stage 1 adds an agent-first memory evolution path. The natural interface for
interactive users is the Claude Code slash skill:

```text
/dream wiki
```

For proposal-only runs, keep validated proposals review-only:

```text
/dream wiki --propose-only
```

`/dream` separates the memory-evolution substrate from the policy runtime. The
policy runtime may be the Claude Code session, an OpenAI-compatible API model
via `--use-llm`, a local model, or any external agent that writes the same
strict JSON response. The deterministic command is the substrate: it prepares
compact memory context, writes a checkpoint prompt, validates the policy
runtime's JSON response, records accepted forgetting/consolidation/association
proposals through the shared SciEvolve store, and can optionally apply
medium/high-confidence proposals as reversible SciEvolve memory metadata.

The autonomy mechanism is policy-runtime agnostic: the same closed loop works
across Claude Code, OpenAI-compatible models, local models, or supplied JSON:
SciMem state -> policy judgment -> evidence validation -> proposal store ->
guarded memory mutation -> rebuilt downstream context.

For `/dream`, the guarded default is already an acting loop: finalization can
auto-apply validated medium/high-confidence memory proposals as reversible
metadata and audit notes. The `--propose-only` and `yolo=false` modes are
safety choices for demos or unattended deployments, not missing automation
capability.

For debugging or demos, prepare the same dream context directly:

```bash
python3 tools/research_wiki.py dream wiki --json
```

After the slash skill writes `dream_agent_response.json`, finalize directly and
apply safe medium/high-confidence memory updates:

```bash
python3 tools/research_wiki.py dream wiki \
  --agent-response path/to/dream_agent_response.json \
  --json
```

To finalize without applying mutations:

```bash
python3 tools/research_wiki.py dream wiki \
  --agent-response path/to/dream_agent_response.json \
  --propose-only \
  --json
```

To run the same loop without the Claude Code slash-command policy runtime:

```bash
python3 tools/research_wiki.py dream wiki --use-llm --json
```

Each run writes:

- `wiki/outputs/evolution/dream/<run>/dream_context.json`
- `wiki/outputs/evolution/dream/<run>/dream_context.md`
- `wiki/outputs/evolution/dream/<run>/dream_agent_prompt.md`
- `wiki/outputs/evolution/dream/<run>/dream_agent_response.json` when an agent response exists
- `wiki/outputs/evolution/dream/<run>/dream_report.md`
- `wiki/outputs/evolution/dream/<run>/dream_apply_report.*` when safe
  applications are attempted

The context includes deterministic memory cues and recurring signal patterns,
but those cues are not proposals. The agent must cite context evidence before
the tool will write a proposal artifact.

Safe auto-apply is intentionally narrow. It never rewrites page bodies, graph
edges, skills, schemas, or templates. It only writes reversible frontmatter
metadata such as `scievolve_memory_weight`,
`scievolve_consolidates_with`, `scievolve_associations`,
`scievolve_last_dream`, and `scievolve_dream_notes`, appends an audit-only
`SciEvolve Memory Evolution Note`, records the application in
`applications.jsonl`, marks the proposal `applied`, and rebuilds
`wiki/graph/context_brief.md` so `/ideate`, `/research`, `/ask`, and other
context-consuming skills can see the evolved memory state. Applied memory
metadata is consumed by `compile-context`: downweighted pages are deprioritized,
consolidated related pages are folded into their canonical target, and
associations are surfaced in the SciEvolve guidance section.

### Scheduled `/dream`

`.github/workflows/dream.yml` runs the same `/dream` finalizer on a daily GitHub
Actions schedule (`43 18 * * *` UTC) and through manual dispatch. It commits the
resulting `wiki/` changes: recurring dream context, agent responses, proposal
artifacts, application ledger entries, and rebuilt `wiki/graph/context_brief.md`.
The workflow first runs `scievolve-sense` so durable failure states can enter
the same signal stream before the agent policy step.

The scheduler uses the first available policy runtime:

- Claude Code Action when `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is
  configured.
- OpenAI-compatible fallback when `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`
  are configured.

Those `LLM_*` secrets are exposed in the workflow job `env:` block because the
Python fallback reads them from process environment variables. If no policy
runtime is available, the workflow fails closed rather than producing a
report-only imitation of self-evolution.

The Claude Code Action path snapshots `wiki/` after deterministic context
preparation and rejects any Claude-side edit outside the generated response
before finalization. Finalization reuses the prepared run directory with
`--run-dir`, so the response is validated against the same context Claude saw.
The commit step force-stages only finalizer-declared paths because generated
evolution artifacts are ignored by default in the template repository.

Manual dispatch can run:

```bash
gh workflow run dream.yml --ref main -f mode=propose-only
```

Scheduled runs read optional non-secret defaults from `config/dream.yml`.
Manual dispatch inputs override that config for one run:

```yaml
mode: auto-apply
max_entities: 120
max_signals: 30
max_candidates: 30
yolo: true
```

When `yolo=true`, page archive/merge mutations are still gated by the same
deterministic finalizer: proposals must be evidence-grounded and `high`
confidence before any page-level mutation is applied.

## Signal Sources

Signals enter the evolution loop through three paths:

1. **Automatic sensing**: `scievolve-sense` reads durable failed states,
   workflow log failures, and dream/forge apply skips, then writes deduped
   `task` signals.

   ```bash
   python3 tools/research_wiki.py scievolve-sense wiki --json
   ```

2. **Skill-explicit**: After executing a skill, the LLM policy runtime
   reflects on the execution and calls `tools/scievolve_record.py` if there is
   feedback worth recording. This is the LLM-first path: the executing agent
   decides what, if anything, to record.

   ```bash
   python3 tools/scievolve_record.py \
     --wiki-root wiki \
     --source {user|task|open} \
     --dimension {memory|workflow|orchestration} \
     --target <skill-or-entity> \
     --kind <kind> \
     --summary "<one-line summary>"
   ```

3. **Manual CLI**: Humans or CI scripts can record signals directly:

   ```bash
   python3 tools/research_wiki.py scievolve-record-signal wiki \
     --source user --dimension memory --target concepts/example \
     --kind correction --summary "User feedback"
   ```

4. **Cross-skill cascade**: A skill may record signals about another skill's
   behavior (e.g. `/dream` recording a signal about high agent-proposal rejection
   rates, which `/forge` may later consume).

The `source` field distinguishes:
- `user` — human corrections, preferences, or redirections
- `task` — execution outcomes, failures, or unexpected tool behavior
- `open` — external changes such as new papers, venue shifts, or SOTA updates

The `dimension` field routes signals to the correct stage skill:
- `memory` -> `/dream`
- `workflow` -> `/forge`
- `orchestration` -> `/morph`

## `/forge` Agent Loop

Stage 2 adds an agent-first **workflow** evolution path. It consumes
`dimension=workflow` signals and proposes concrete patches to skills and
protocols.

```text
/forge wiki
```

Focus on a specific skill:

```text
/forge wiki --target-skill discover
```

`/forge` follows the same agent-first, proposal-first pattern as `/dream`, but
operates on skills instead of memory entities. The default mode finalizes and
applies validated skill patches directly. This includes targeted
`patch-prompt`, `reorder-steps`, `rename-step`, and `create-skill` mutations,
plus provenance frontmatter and an append-only `## SciEvolve Workflow Evolution
Note`.

Use `--dry-run` when you want proposal artifacts without touching skill files:

```text
/forge wiki --dry-run
```

The conservative modes are safety controls for executable workflow text, not a
reduction in self-evolution capability. The implemented `/forge` apply path can
mutate skills after evidence validation. Default prompt/step patches require a
unique line hint or a bounded section match, preserve markdown structure, and
are skipped when the target is missing, ambiguous, or structurally unsafe.
`--yolo` additionally enables high-confidence `archive-skill` and
`merge-skills` operations.

### Scheduled `/forge`

`.github/workflows/forge.yml` runs `/forge` weekly (`23 19 * * 0` UTC) and
through manual dispatch. It follows the same deterministic boundary as
scheduled `/dream`: run `scievolve-sense`, prepare a forge context, let the
policy runtime write only `forge_agent_response.json`, finalize the same run
with `--run-dir`, then stage only finalizer-declared paths.

Scheduled defaults live in optional `config/forge.yml`:

```yaml
mode: auto-apply
target_skill: ""
max_signals: 40
yolo: false
```

Manual dispatch inputs override that config for one run. The scheduler uses
Claude Code Action auth when configured and falls back to OpenAI-compatible
`LLM_*` secrets; without a policy runtime it fails closed.

## `/morph` Agent Loop

Stage 3 adds an agent-first **orchestration** evolution path. It consumes
`dimension=orchestration` signals and proposes concrete changes to SciDAG
templates, operator graphs, and operator prompts.

```text
/morph wiki
```

Focus on a specific template:

```text
/morph wiki --target-template explore-debate-test
```

`/morph` follows the same agent-first, proposal-first pattern as `/dream` and
`/forge`, but operates on DAG templates and operator prompts. The default mode
is **dry-run**: it writes proposal artifacts without modifying files. Add
`--apply` to mutate validated template/prompt patches directly.

```text
/morph wiki --apply
```

Operations applied with `--apply`:
- `patch-template` — safe YAML text patch via line hint or section match
- `patch-prompt` — operator prompt modification in `scidag/operators/prompts.py`
- `add-verification-node` — append a `Test` or `Review` node to a template
- `prune-branch` — remove a weak branch from a template
- `specialize-template` / `create-template` — new template skeletons
- `--yolo` enables high-confidence `archive-template` and `merge-templates`

Use `--dry-run` to review without touching files:

```text
/morph wiki --dry-run
```

### Scheduled `/morph`

`.github/workflows/morph.yml` runs `/morph` weekly (`13 17 * * 3` UTC) and
through manual dispatch. It follows the same deterministic boundary as
scheduled `/dream` and `/forge`: run `scievolve-sense`, prepare a morph
context, let the policy runtime write only `morph_agent_response.json`,
finalize the same run with `--run-dir`, then stage only finalizer-declared
paths.

Scheduled defaults live in optional `config/morph.yml`:

```yaml
mode: dry-run
target_template: ""
max_signals: 30
yolo: false
```

Manual dispatch inputs override that config for one run.

## The SciEvolve Closed Loop

The three evolution dimensions are intentionally wired together rather than
isolated:

1. **Memory → Workflow → Orchestration**
   - `/dream` evolves SciMem organization. Changed `compile-context` ranking
     alters the evidence that skills receive, which changes DAG inputs and
     execution outcomes.
   - `/forge` evolves SciFlow skills. Revised skill protocols change which
     DAG templates are invoked and how stage boundaries are drawn.
   - `/morph` evolves SciDAG templates. Changed operator graphs change the
     execution traces that produce signals for `/dream` and `/forge`.

2. **Cross-skill signal cascade**
   - When `/dream` consolidates memory in a way that changes expected DAG
     inputs, it may record an `orchestration` signal for `/morph`.
   - When `/forge` revises a skill that changes DAG invocation patterns, it
     may record an `orchestration` signal for `/morph`.
   - When `/morph` specializes a template for a new problem type, it may
     record a `memory` signal so `/dream` creates or updates the matching
     Topic/Method entity.

3. **Unified sensing**
   - `scievolve-sense` scans durable failure states across all three
     dimensions: failed entities (memory), log failures (workflow), and
     skipped apply reports (all dimensions).
   - A single `scievolve-report --propose` can surface proposals for any
     dimension by filtering with `--dimension`.

4. **Downstream consumption**
   - Applied `/dream` metadata is consumed by `compile-context` (deprioritize
     downweighted pages, fold consolidation sources, surface associations).
   - Applied `/forge` mutations are consumed by the next skill execution
     (changed prompts, checks, handoffs).
   - Applied `/morph` mutations are consumed by the next DAG execution
     (changed templates, operator prompts, graph structure).

This wiring makes SciEvolve a single closed loop rather than three separate
utilities.

## Automatic Sensing

`scievolve-sense` turns durable failure states into idempotent SciEvolve
signals:

```bash
python3 tools/research_wiki.py scievolve-sense wiki --json
```

It currently senses:

- failed or rejected idea pages and failed experiment pages as `dimension=memory`
  signals for `/dream`
- failure-like entries in `wiki/log.md` as `dimension=workflow` signals for
  `/forge`
- skipped `/dream` or `/forge` apply reports as workflow warning signals

Automatic signals carry stable `dedupe_key` values, so scheduled and manual
reruns do not duplicate the same sensed event. Skill-explicit reflection remains
available, but it is no longer the only signal source.

For an artifact-only demo:

```bash
python3 tools/research_wiki.py forge wiki --json
```

After writing `forge_agent_response.json`, finalize:

```bash
python3 tools/research_wiki.py forge wiki \
  --agent-response path/to/forge_agent_response.json \
  --json
```

With the default apply path:

```bash
python3 tools/research_wiki.py forge wiki \
  --agent-response path/to/forge_agent_response.json \
  --json
```

Each run writes:

- `wiki/outputs/evolution/forge/<run>/forge_context.json`
- `wiki/outputs/evolution/forge/<run>/forge_context.md`
- `wiki/outputs/evolution/forge/<run>/forge_agent_prompt.md`
- `wiki/outputs/evolution/forge/<run>/forge_agent_response.json` when an agent response exists
- `wiki/outputs/evolution/forge/<run>/forge_report.md`
- `wiki/outputs/evolution/forge/<run>/forge_apply_report.*` when safe applications are attempted
