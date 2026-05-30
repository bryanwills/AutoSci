# SciEvolve

SciEvolve is AutoSci's proposal-first evolution layer. It records feedback
signals from user, task, and open environments, groups them by evolution target,
and writes inspectable proposals before any core file is changed.

This Stage 0 spine does not claim fully autonomous evolution. It creates the
shared substrate that `/dream`, `/forge`, and `/morph` extend:

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

## Reviewer Demo

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

## `/dream` Agent Loop

Stage 1 adds an agent-first memory evolution path. The natural interface is the
Claude Code slash skill:

```text
/dream wiki --propose
```

For a closed-loop reviewer demo, use the guarded self-application mode:

```text
/dream wiki --apply-safe
```

The skill uses the current Claude Code session as the memory-evolution agent.
The deterministic command is only a helper: it prepares compact memory context,
writes a checkpoint prompt, validates the agent's JSON response, records
accepted forgetting/consolidation/association proposals through the shared
SciEvolve store, and can optionally apply medium/high-confidence proposals as
reversible SciEvolve memory metadata.

For debugging or demos, prepare the same dream context directly:

```bash
python3 tools/research_wiki.py dream wiki --json
```

After the slash skill writes `dream_agent_response.json`, finalize directly:

```bash
python3 tools/research_wiki.py dream wiki \
  --agent-response path/to/dream_agent_response.json \
  --propose \
  --json
```

To finalize and safely apply in one pass:

```bash
python3 tools/research_wiki.py dream wiki \
  --agent-response path/to/dream_agent_response.json \
  --apply-safe \
  --json
```

Each run writes:

- `wiki/outputs/evolution/dream/<run>/dream_context.json`
- `wiki/outputs/evolution/dream/<run>/dream_context.md`
- `wiki/outputs/evolution/dream/<run>/dream_agent_prompt.md`
- `wiki/outputs/evolution/dream/<run>/dream_agent_response.json` when an agent response exists
- `wiki/outputs/evolution/dream/<run>/dream_report.md`
- `wiki/outputs/evolution/dream/<run>/dream_apply_report.*` when `--apply-safe` is used

The context includes deterministic memory cues, but those cues are not
proposals. The agent must cite context evidence before the tool will write a
proposal artifact.

`--apply-safe` is intentionally narrow. It never edits page bodies, graph
edges, skills, schemas, or templates. It only writes reversible frontmatter
metadata such as `scievolve_memory_weight`,
`scievolve_consolidates_with`, `scievolve_associations`,
`scievolve_last_dream`, and `scievolve_dream_notes`, then records the
application in `applications.jsonl`, marks the proposal `applied`, and rebuilds
`wiki/graph/context_brief.md` so `/ideate`, `/research`, `/ask`, and other
context-consuming skills can see the evolved memory state.
