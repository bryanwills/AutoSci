---
description: Run or schedule AutoSci's agent-first SciEvolve forge pass: reflect over workflow signals and apply proposal-first skill patches
description-zh: 运行或调度 AutoSci 的 agent-first SciEvolve forge 流程：反思工作流信号并应用 proposal-first 的技能补丁
argument-hint: "[setup|status] [wiki-root] [--target-skill <name>] [--dry-run] [--yolo]"
---

# /forge

Reflect over SciEvolve workflow signals with a pluggable policy runtime. `/forge`
is the auditable self-evolution loop for the **workflow** dimension: the system
inspects feedback about skill execution, decides which skills need patches, and
proposes concrete, evidence-backed updates to prompts, checks, handoffs, and
recovery protocols.

The policy runtime is the reasoning layer of the AutoSci agent, not an external
reviewer of a passive Python script. Python tools prepare workflow evidence,
validate line/section targets, apply guarded patches, and write provenance so
later skill executions consume the changed protocol. This split is the intended
implementation: replaceable reasoning plus stable validation is easier to audit
than a hard-coded in-process judge.

The default mode **directly mutates skill files**. Validated proposals are applied
immediately: `patch-prompt`, `reorder-steps`, and `rename-step` use unique line
hints or bounded section matches; unsafe, missing, or ambiguous patches are
skipped. `create-skill` builds skeletons. Every mutation also appends a
`SciEvolve Workflow Evolution Note` and updates frontmatter metadata for
provenance.

Use `--dry-run` to review without modifying skill files. Use `--yolo` to additionally
allow destructive ops (`archive-skill`, `merge-skills`).

Safety posture: `--dry-run`, evidence validation, and `--yolo` gates are
standard deployment safeguards for agents that edit executable workflow text.
They do not reduce `/forge`'s actual self-evolution capability: default
finalization can mutate validated skill patches directly, while `--yolo`
expands the apply path to high-confidence archive/merge operations.

Use these local references on demand:

- `references/workflow-operations.md` — the rubric for patch-prompt, add-check,
  adjust-handoff, and add-recovery operations
- `references/evidence-and-boundaries.md` — evidence rules and safety constraints
- `references/agent-response-schema.md` — exact JSON shape expected by the finalizer

Open `runtime/schema/scievolve.yaml` for the on-disk signal/proposal contract.

## Commands

- `/forge`: run a one-off workflow-evolution pass now.
- `/forge setup`: verify `.github/workflows/forge.yml` exists, exposes `LLM_*`
  secrets in job `env:`, reads optional `config/forge.yml`, runs automatic
  sensing, and uses the same write-boundary guard as scheduled `/dream`.
- `/forge status`: inspect workflow presence, schedule, policy-runtime secret
  availability when visible, and recent local `wiki/outputs/evolution/forge/`
  artifacts.

## Inputs

- `wiki-root` (optional): default `wiki/`
- `--target-skill` (optional): focus on a specific skill; default is all skills
  that have `dimension=workflow` signals
- `--dry-run` (optional): write proposal/report artifacts but do not modify skill files
- `--yolo` (optional): additionally allow archive-skill and merge-skills
- `--agent-response` (optional): path to strict JSON returned by the /forge agent
- `--run-dir` (optional): reuse a prepared run directory for deterministic finalization
- `--use-llm` (optional): call an OpenAI-compatible LLM for the agent reflection
- Scheduled runs use `.github/workflows/forge.yml` and optional
  `config/forge.yml` for mode, target skill, signal limit, and `yolo`.

## Outputs

- Forge run directory: `wiki/outputs/evolution/forge/<run>/`
- Context artifacts: `forge_context.json`, `forge_context.md`
- Prompt artifact: `forge_agent_prompt.md`
- Agent response artifact: `forge_agent_response.json`
- Report artifact: `forge_report.md`
- Optional safe-apply artifacts: `forge_apply_report.json`, `forge_apply_report.md`
- Shared SciEvolve proposal artifacts under `wiki/outputs/evolution/proposals/`

## Wiki Interaction

### Reads

- `wiki/outputs/evolution/signals.jsonl` — `dimension=workflow` signals
- recurring workflow signal patterns prepared from the last 30 days
- `i18n/en/skills/<target>/SKILL.md` and `.claude/skills/<target>/SKILL.md` —
  skill content for targeted skills
- `wiki/log.md` — skill invocation frequency (signal density hint)

### Writes

- `wiki/outputs/evolution/forge/<run>/*`
- `wiki/outputs/evolution/proposals/*` when finalizing
- `wiki/outputs/evolution/proposals.jsonl` when finalizing
- `wiki/outputs/evolution/applications.jsonl` when safe applications are attempted
- Skill files (`i18n/en/skills/<target>/SKILL.md`, `.claude/skills/<target>/SKILL.md`)
  are mutated in place for patch-prompt, reorder-steps, rename-step, and create-skill.
  Frontmatter (`scievolve_forge_notes`, `scievolve_last_forge`) and append-only
  `## SciEvolve Workflow Evolution Note` are always written alongside the mutation.

## Workflow

**Pre-condition**: work from the AutoSci project root. Resolve `PYTHON_BIN` once:

```bash
if   [ -x .venv/bin/python ];         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then PYTHON_BIN=.venv/Scripts/python.exe
else                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

Set the wiki root:

```bash
WIKI_ROOT=wiki
FORGE_TARGET=""
for arg in $ARGUMENTS; do
  case "$arg" in
    --target-skill=*) FORGE_TARGET="${arg#*=}" ;;
    --target-skill)   FORGE_TARGET="${arg}" ;;
    --*) ;;
    *) WIKI_ROOT="$arg" ;;
  esac
done
export WIKI_ROOT FORGE_TARGET
```

### Step 1: Prepare The Forge Scene

Run:

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --json
```

Read the returned `forge_context.md`, `forge_context.json`, and
`forge_agent_prompt.md`. The context contains workflow signals grouped by target
skill, recurring signal patterns, and skill content previews. **Treat signals as
evidence, not decisions.**

### Step 2: Perform Agentic Workflow Reflection

Use the active policy runtime to act as the `/forge` workflow-evolution agent. In
the slash-command path, Claude Code is the policy runtime; in headless demos,
`tools/research_wiki.py forge --use-llm` can call an OpenAI-compatible model.

Ask these questions:

1. Which skills have the highest signal density or recurring patterns?
2. What concrete patch would address the root cause, not the symptom?
3. Is the patch additive (append check, add recovery) or destructive (rewrite prompt)?
4. Does the patch change the skill's core purpose? If yes, reject it.
5. What evidence supports each proposal? Cite signal ids or recurring pattern
   ids, plus skill line hints.
6. What should be left alone because the evidence is too thin?

Prefer additive changes. A good `/forge` run usually has 0–3 proposals.

### Step 3: Write The Agent Response

Read `references/agent-response-schema.md`, then write strict JSON to:

```text
wiki/outputs/evolution/forge/<run>/forge_agent_response.json
```

Use the same run directory returned by Step 1. Every proposal must cite known
evidence: signal ids or recurring pattern ids and skill file paths from the
prepared context.

### Step 4: Finalize And Apply

The default behavior **applies validated proposals directly to skill files**. Run:

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --agent-response wiki/outputs/evolution/forge/<run>/forge_agent_response.json \
  --json
```

The finalizer validates references, writes proposal artifacts, and mutates skill
files in place. Operations applied:
- `patch-prompt` / `reorder-steps` / `rename-step` — content replacement via a
  unique `line_hint` or bounded heading section; ambiguous, missing, or
  markdown-breaking patches are skipped
- `create-skill` / `add-skill` — new skeleton written to `i18n/en/skills/<target>/`
- `archive-skill` / `merge-skills` — only with `--yolo` and `confidence=high`
- Other operations — append-only note + frontmatter metadata

Use `--dry-run` to review without touching skill files:

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --agent-response wiki/outputs/evolution/forge/<run>/forge_agent_response.json \
  --dry-run \
  --json
```

If the finalizer rejects an item, fix the response JSON rather than loosening
the tool.

### Step 5: Report To The User

Report:

- forge run directory
- number of workflow signals loaded
- signal density per targeted skill
- proposal count by operation
- skill mutation count (proposals applied to skill files)
- rejected agent items, if any
- proposal artifact paths
- whether any skill frontmatter or append-only note was applied

## Constraints

- `/forge` is agent-first. Deterministic scans prepare context; they do not make
  the workflow judgment.
- `/forge` is policy-runtime agnostic. Claude Code, an API model, a local model,
  or a supplied response can provide the judgment as long as it satisfies the
  same evidence-grounded JSON contract.
- Show self-evolution, not maintenance. A good proposal changes the future shape
  of workflow execution by fixing a real failure mode or coordination gap.
- Treat conservative defaults as safety posture, not a capability boundary.
  The development contract is the closed loop: validated proposal, guarded skill
  mutation, application ledger, and changed future skill behavior.
- Treat skill files as the intended procedural memory surface. `/forge` should
  not rewrite arbitrary core runtime code; those changes belong to a higher-risk
  development path.
- Proposal-first by default. Proposals are recorded before mutation; default
  finalization can apply validated skill patches, while `--dry-run` keeps the
  run review-only.
- Do not turn `/forge` into `/check`. Structural issues (broken links, malformed
  markdown) remain `/check` concerns.
- Do not change a skill's core purpose. `/forge` improves robustness and clarity;
  it does not re-scope the skill.
- Preserve provenance. Every proposal should make the agent's
  workflow-organization judgment inspectable from artifacts and ledgers.
- Guarded apply validates evidence and preserves provenance. Prompt/step
  patches are allowed by default when line hints match uniquely or a section
  boundary is clear; archive/merge stays behind `--yolo` and high confidence.

## Reflection & Signal Recording

After the forge run completes, reflect on whether the run revealed systemic
workflow issues worth recording. Record at most 1 signal if warranted.

```bash
python3 tools/scievolve_record.py \
  --wiki-root wiki \
  --source task \
  --dimension workflow \
  --target /forge \
  --kind {review|warning|success} \
  --summary "<concise summary>" \
  --severity {info|low|medium|high|critical} \
  --confidence {low|medium|high}
```

Record a signal when:
- High agent-proposal rejection rate (>2x accepted) → `kind=review`
- A skill accumulates >5 workflow signals without a forge run → `kind=warning`
- Run completed with meaningful proposals → `kind=success` (use sparingly)

If nothing notable happened, skip signal recording.
