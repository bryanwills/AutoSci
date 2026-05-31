---
description: Run or schedule AutoSci's agent-first SciEvolve morph pass: reflect over SciDAG orchestration signals and evolve operator graphs and stage templates
argument-hint: "[setup|status] [wiki-root] [--target-template <name>] [--dry-run] [--apply] [--yolo]"
---

# /morph

Reflect over SciDAG orchestration signals with a pluggable policy runtime.
`/morph` is the auditable self-evolution loop for the **orchestration**
dimension: the system inspects feedback about DAG execution, operator
performance, and template suitability, then proposes concrete changes to
operator prompts, graph structures, verification nodes, and stage-specific
templates.

The policy runtime is the orchestration reasoning layer inside AutoSci's agent
boundary. Deterministic tools provide the sensors and effectors: they assemble
signal/template context, validate proposed patch targets, mutate only typed DAG
surfaces when enabled, and ledger the result for later SciDAG executions. This
split is the intended implementation: replaceable reasoning plus stable
validation is easier to audit than a hard-coded in-process judge.

The default mode is **dry-run/proposal-first**. Validated proposals are written
as inspectable artifacts; use `--apply` to additionally mutate template YAMLs
and operator prompt files. Use `--yolo` to allow destructive template changes
(archive-template, merge-templates).

Safety posture: `--dry-run` and `--yolo` gates are standard deployment
safeguards for agents that edit executable orchestration text. They do not
reduce `/morph`'s actual self-evolution capability: default finalization can
mutate validated template patches directly when `--apply` is passed, while
`--dry-run` keeps the run review-only.

Open `runtime/schema/scievolve.yaml` for the on-disk signal/proposal contract
and the exact operations rubric.

## Commands

- `/morph`: run a one-off orchestration-evolution pass now.
- `/morph setup`: verify `.github/workflows/morph.yml` exists, exposes `LLM_*`
  secrets in job `env:`, reads optional `config/morph.yml`, runs automatic
  sensing, and uses the same write-boundary guard as scheduled `/dream`.
- `/morph status`: inspect workflow presence, schedule, policy-runtime secret
  availability when visible, and recent local `wiki/outputs/evolution/morph/`
  artifacts.

## Inputs

- `wiki-root` (optional): default `wiki/`
- `--target-template` (optional): focus on a specific template; default is all
  templates that have `dimension=orchestration` signals
- `--dry-run` (optional): write proposal/report artifacts but do not modify
  template or prompt files. This is the default.
- `--apply` (optional): apply validated template/prompt patches directly
- `--yolo` (optional): additionally allow destructive ops: archive-template,
  merge-templates
- `--agent-response` (optional): path to strict JSON returned by the /morph agent
- `--run-dir` (optional): reuse a prepared run directory for deterministic finalization
- `--use-llm` (optional): call an OpenAI-compatible LLM for the agent reflection
- Scheduled runs use `.github/workflows/morph.yml` and optional
  `config/morph.yml` for mode, target template, signal limit, and `yolo`.

## Outputs

- Morph run directory: `wiki/outputs/evolution/morph/<run>/`
- Context artifacts: `morph_context.json`, `morph_context.md`
- Prompt artifact: `morph_agent_prompt.md`
- Agent response artifact: `morph_agent_response.json`
- Report artifact: `morph_report.md`
- Optional apply artifacts: `morph_apply_report.json`, `morph_apply_report.md`
- Shared SciEvolve proposal artifacts under `wiki/outputs/evolution/proposals/`

## Wiki Interaction

### Reads

- `wiki/outputs/evolution/signals.jsonl` — `dimension=orchestration` signals
- recurring orchestration signal patterns prepared from the last 30 days
- `scidag/templates/<stage>/*.yaml` — DAG template library
- `scidag/operators/prompts.py` — operator prompt texts
- `scidag/operators/registry.py` — operator descriptions and capabilities
- `wiki/log.md` — DAG invocation frequency (signal density hint)

### Writes

- `wiki/outputs/evolution/morph/<run>/*`
- `wiki/outputs/evolution/proposals/*` when finalizing
- `wiki/outputs/evolution/proposals.jsonl` when finalizing
- `wiki/outputs/evolution/applications.jsonl` when applications are attempted
- Template YAMLs (`scidag/templates/<stage>/<name>.yaml`) are mutated in place
  for patch-template, add-verification-node, prune-branch, and specialize-template
  when `--apply` is passed.
- Operator prompt file (`scidag/operators/prompts.py`) is mutated in place for
  patch-prompt when `--apply` is passed.
- Frontmatter (`scievolve_morph_notes`, `scievolve_last_morph`) and append-only
  `## SciEvolve Orchestration Evolution Note` are always written alongside the
  mutation.

## Workflow

**Pre-condition**: work from the AutoSci project root. Resolve `PYTHON_BIN` once:

```bash
if   [ -x .venv/bin/python ];         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then PYTHON_BIN=.venv/Scripts/python.exe
else                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

Set the wiki root and optional target template:

```bash
set -- $ARGUMENTS
WIKI_ROOT=wiki
MORPH_TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --target-template=*) MORPH_TARGET="${1#*=}"; shift ;;
    --target-template)   MORPH_TARGET="$2"; shift 2 ;;
    --*) shift ;;
    *) WIKI_ROOT="$1"; shift ;;
  esac
done
export WIKI_ROOT MORPH_TARGET
```

### Step 1: Prepare The Morph Scene

Run:

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --json
```

Read the returned `morph_context.md`, `morph_context.json`, and
`morph_agent_prompt.md`. The context contains orchestration signals grouped by
target template, recurring signal patterns, template library summaries, and
operator prompt previews. **Treat signals as evidence, not decisions.**

### Step 2: Perform Agentic Orchestration Reflection

Use the active policy runtime to act as the `/morph` orchestration-evolution
agent. In the slash-command path, Claude Code is the policy runtime; in headless
demos, `tools/research_wiki.py morph --use-llm` can call an OpenAI-compatible
model.

Ask these questions:

1. Which operators show stable underperformance in the signal evidence?
2. Which graph structures repeatedly fail or waste calls (e.g., untested branches)?
3. What concrete patch would address the root cause: prompt change, node addition,
   branch pruning, or template specialization?
4. Is the patch additive (add verification node, strengthen prompt) or destructive
   (prune branch, remove operator)?
5. Does the patch change the stage's core purpose? If yes, reject it.
6. What evidence supports each proposal? Cite signal ids, template names, and
   operator names.
7. What should be left alone because the evidence is too thin?

Prefer additive changes. A good `/morph` run usually has 0–3 proposals.

### Step 3: Write The Agent Response

Read the agent-response schema in `morph_agent_prompt.md` (prepared in Step 1), then write strict JSON to:

```text
wiki/outputs/evolution/morph/<run>/morph_agent_response.json
```

Use the same run directory returned by Step 1. Every proposal must cite known
evidence: signal ids, recurring pattern ids, template file paths, and operator
names from the prepared context.

### Step 4: Finalize And Apply

The default behavior is **dry-run**: write proposal/report artifacts without
modifying files. Run:

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --json
```

To apply validated template/prompt patches directly, add `--apply`:

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --apply \
  --json
```

The finalizer validates references, writes proposal artifacts, and mutates files
in place when `--apply` is passed. Operations applied:
- `patch-template` — YAML node list modification via safe text patch
- `patch-prompt` — operator prompt modification via bounded section match
- `add-verification-node` — append a `Test` or `Review` node to a template
- `prune-branch` — remove a weak branch from a template
- `specialize-template` — copy and adapt a template for a stage/problem type
- `create-template` — new template skeleton written to `scidag/templates/<stage>/`
- `archive-template` / `merge-templates` — only with `--yolo` and `confidence=high`
- Other operations — append-only note + frontmatter metadata

Use `--dry-run` to review without touching files:

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --dry-run \
  --json
```

If the finalizer rejects an item, fix the response JSON rather than loosening
the tool.

### Step 5: Report To The User

Report:

- morph run directory
- number of orchestration signals loaded
- signal density per targeted template
- proposal count by operation
- file mutation count (proposals applied to templates/prompts)
- rejected agent items, if any
- proposal artifact paths
- whether any template or prompt file was mutated

## Constraints

- `/morph` is agent-first. Deterministic scans prepare context; they do not make
  the orchestration judgment.
- `/morph` is policy-runtime agnostic. Claude Code, an API model, a local model,
  or a supplied response can provide the judgment as long as it satisfies the same
  evidence-grounded JSON contract.
- Show self-evolution, not maintenance. A good proposal changes the future shape
  of DAG execution by fixing a real operator weakness or graph inefficiency.
- Treat conservative defaults as safety posture, not a capability boundary.
  The development contract is the closed loop: validated proposal, guarded
  template/prompt mutation, application ledger, and changed future DAG behavior.
- Treat templates and operator prompts as the intended orchestration behavior
  surface. `/morph` should not rewrite arbitrary core runtime code; those
  changes belong to a higher-risk development path.
- Proposal-first by default. Proposals are recorded before mutation; `--apply`
  can apply validated patches, while `--dry-run` keeps the run review-only.
- Do not turn `/morph` into `/check`. Structural issues (broken YAML, malformed
  graph) remain `/check` concerns.
- Do not change a stage's core purpose. `/morph` improves operator robustness
  and graph efficiency; it does not re-scope the stage.
- Preserve provenance. Every proposal should make the agent's
  orchestration-organization judgment inspectable from artifacts and ledgers.
- Guarded apply validates evidence and preserves provenance. Template/prompt
  patches are allowed with `--apply` when line hints match uniquely or a section
  boundary is clear; archive/merge stays behind `--yolo` and high confidence.

## Reflection & Signal Recording

After the morph run completes, reflect on whether the run revealed systemic
orchestration issues worth recording. Record at most 1 signal if warranted.

```bash
python3 tools/scievolve_record.py \
  --wiki-root wiki \
  --source task \
  --dimension orchestration \
  --target /morph \
  --kind {review|warning|success} \
  --summary "<concise summary>" \
  --severity {info|low|medium|high|critical} \
  --confidence {low|medium|high}
```

Record a signal when:
- High agent-proposal rejection rate (>2x accepted) → `kind=review`
- A template accumulates >5 orchestration signals without a morph run → `kind=warning`
- Run completed with meaningful proposals → `kind=success` (use sparingly)
- A /dream or /forge change suggests DAG structure should adapt → cross-skill
  cascade signal with `dimension=orchestration`

If nothing notable happened, skip signal recording.

## Cross-Skill Cascade

`/morph` is intentionally not isolated. When `/dream` consolidates memory or
`/forge` revises a skill in ways that change the expected DAG input/output
contract, those stages should record an `orchestration` signal so `/morph` can
propose matching template changes. Conversely, when `/morph` specializes a
template for a new problem type, it should record a `memory` signal so `/dream`
can create or update the corresponding Topic/Method entity.

The three evolution dimensions form a closed loop:
- `/dream` (memory) → `compile-context` ranking → skill inputs → DAG execution
- `/forge` (workflow) → skill protocols → DAG invocation patterns
- `/morph` (orchestration) → templates/operators → execution traces → signals
