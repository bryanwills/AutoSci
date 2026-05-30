---
description: Run AutoSci's agent-first SciEvolve dream pass: reflect over SciMem and write proposal-first self-evolution artifacts for forgetting, consolidation, and association
argument-hint: "[wiki-root] [--propose]"
---

# /dream

Reflect over SciMem as the memory-evolution agent. `/dream` is the visible
self-evolution loop for reviewers: the system inspects its own scientific
memory, decides what should fade, what should be reorganized, and what latent
associations should be proposed for future work. Use tools to prepare the memory
scene, then make the actual forgetting / consolidation / association judgments
in this Claude Code session. The Python helper is a context and artifact layer;
it is not the dream.

Use these local references on demand:

- `references/memory-operations.md` — the rubric for forgetting, consolidation, and association proposals
- `references/evidence-and-boundaries.md` — evidence rules, `/check` boundary, and reviewer-facing safety constraints
- `references/agent-response-schema.md` — exact JSON shape expected by the finalizer, plus examples

Open `runtime/schema/scievolve.yaml` for the on-disk signal/proposal contract.
Open `docs/scievolve.md` only when you need reviewer-facing command examples.

## Inputs

- `wiki-root` (optional): default `wiki/`
- `--propose` (optional): write validated proposal artifacts after the agent
  response is prepared. Without it, stop after the dream report / response draft.
- `--apply-safe` (optional): imply `--propose`, then apply medium/high-confidence
  validated proposals as reversible SciEvolve metadata on memory pages.
- Existing wiki pages, graph edges, projected frontmatter edges, citations, and
  SciEvolve memory signals.

## Outputs

- Dream run directory: `wiki/outputs/evolution/dream/<run>/`
- Context artifacts: `dream_context.json`, `dream_context.md`
- Prompt artifact: `dream_agent_prompt.md`
- Agent response artifact: `dream_agent_response.json`
- Report artifact: `dream_report.md`
- Optional safe-apply artifacts: `dream_apply_report.json`,
  `dream_apply_report.md`
- Optional shared SciEvolve proposal artifacts under
  `wiki/outputs/evolution/proposals/`

## Wiki Interaction

### Reads

- `wiki/{papers,concepts,topics,people,ideas,experiments,methods,foundations,manuscripts,reviews}/*.md`
- `wiki/graph/edges.jsonl`
- `wiki/graph/citations.jsonl`
- frontmatter-projected links from `runtime/schema/entities.yaml`
- `wiki/outputs/evolution/signals.jsonl`
- optional existing `/check` or lint reports only as supporting context

### Writes

- `wiki/outputs/evolution/dream/<run>/*`
- `wiki/outputs/evolution/proposals/*` only when finalizing with `--propose`
- `wiki/outputs/evolution/proposals.jsonl` only when finalizing with `--propose`
- `wiki/outputs/evolution/applications.jsonl` only when finalizing with
  `--apply-safe`
- entity page frontmatter only when finalizing with `--apply-safe`, limited to
  `scievolve_*` memory metadata fields
- `wiki/graph/context_brief.md` rebuilt after successful `--apply-safe` so
  downstream skills consume the evolved memory state

Do not edit entity page bodies, skills, templates, schemas, graph files,
`index.md`, or `log.md` from `/dream`.

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
DREAM_PROPOSE=false
DREAM_APPLY_SAFE=false
for arg in $ARGUMENTS; do
  case "$arg" in
    --propose) DREAM_PROPOSE=true ;;
    --apply-safe) DREAM_APPLY_SAFE=true; DREAM_PROPOSE=true ;;
    --*) ;;
    *) WIKI_ROOT="$arg" ;;
  esac
done
export WIKI_ROOT DREAM_PROPOSE DREAM_APPLY_SAFE
```

### Step 1: Prepare The Dream Scene

Run:

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" --json
```

Read the returned `dream_context.md`, `dream_context.json`, and
`dream_agent_prompt.md`. The context may contain deterministic candidate cues.
**Treat them as observations only; do not copy them mechanically into proposals.**

### Step 2: Perform Agentic Memory Reflection

Act as the `/dream` agent in this Claude Code session. Read
`references/memory-operations.md` before deciding proposal types. Read
`references/evidence-and-boundaries.md` before accepting any proposal that looks
like lint repair, deletion, or unsupported science.

Make a small, high-signal set of proposals. A good `/dream` run usually has
0-5 proposals, not a sweep of every weak cue.

Ask these questions:

1. Which memories are polluting retrieval or repeating failed traces?
2. Which scattered pages are really one memory neighborhood?
3. Which non-obvious associations would help future research if reviewed?
4. What evidence already exists in the wiki or signal store?
5. How would this proposal improve the next research or retrieval cycle?
6. What should be left alone because the evidence is too thin?

### Step 3: Write The Agent Response

Read `references/agent-response-schema.md`, then write strict JSON to:

```text
wiki/outputs/evolution/dream/<run>/dream_agent_response.json
```

Use the same run directory returned by Step 1. Every proposal must cite known
context evidence: entity ids, candidate ids, signal ids, or edge ids from the
prepared context.

### Step 4: Finalize Through The Shared SciEvolve Store

If the user did not pass `--propose` (`DREAM_PROPOSE=false`), stop after writing
the agent response and summarize what would be proposed.

If `--propose` was requested, run:

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" \
  --agent-response wiki/outputs/evolution/dream/<run>/dream_agent_response.json \
  --propose \
  --json
```

The finalizer validates references and writes proposal artifacts through the
shared SciEvolve store. If it rejects an item, fix the response JSON rather than
loosening the tool.

If `--apply-safe` was requested, run the same finalizer with `--apply-safe`
instead of `--propose`. This is the closed-loop path: it validates the agent
response, records proposals, applies only safe reversible memory metadata, logs
the application event, rebuilds downstream context, and marks applied proposals
as `applied`.

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" \
  --agent-response wiki/outputs/evolution/dream/<run>/dream_agent_response.json \
  --apply-safe \
  --json
```

### Step 5: Report To The User

Report:

- dream run directory
- number of candidate cues read
- proposal count by operation
- safe application count, when `--apply-safe` was used
- whether `context_brief.md` was rebuilt for downstream skills
- rejected agent items, if any
- proposal artifact paths, when `--propose` was used
- whether any memory metadata was applied; page bodies are never mutated

## Constraints

- `/dream` is agent-first. Deterministic scans prepare context; they do not make
  the memory judgment.
- Show self-evolution, not maintenance. A good proposal changes the future shape
  of memory by fading noise, consolidating fragments, or opening a useful new
  research association.
- Proposal-first by default. No deletion, archival, edge write,
  non-SciEvolve frontmatter edit, or page rewrite.
- Closed-loop safe apply is allowed only through `--apply-safe`, and only for
  reversible `scievolve_*` metadata produced from validated medium/high
  confidence proposals.
- Do not turn `/dream` into `/check`. Broken links, malformed graph rows,
  missing required fields, and xref asymmetry remain `/check` concerns.
- Do not fabricate scientific associations. Low confidence is acceptable only
  when evidence is cited and the proposal is clearly marked for review.
- Preserve provenance. Every proposal should make it easy for a reviewer to see
  why the agent made the memory-organization judgment.
