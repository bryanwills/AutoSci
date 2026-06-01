---
description: SciDAG-augmented ideation — generate research ideas through a multi-agent operator DAG (diverse generation + debate + feasibility screen) instead of a single brainstorm pass, then write the surviving idea(s) to the wiki using the same contract as /ideate. Use for hard or high-stakes ideation where one pass is not enough.
argument-hint: "[research-direction-or-topic] [--complexity 1-5] [--dag <name>] [--max-ideas N] [--mock]"
---

# /ideate-dag

> SciDAG augmentation of `/ideate` (paper §5). Instead of a single dual-model
> brainstorm, this skill runs a **directed acyclic graph of reusable research
> operators** (generate / variation / debate / refine / test / ensemble) from
> the **ideation DAG library**, then returns the result to the **same artifact
> contract as `/ideate`** — `wiki/ideas/{slug}.md` pages plus graph edges — so
> nothing downstream changes. The DAG recovers the error-correction and
> iteration that a linear brainstorm lacks: ideas are explored, debated, and
> feasibility-screened before they are written.
>
> This is an **additive** skill. It does **not** modify `/ideate`; use `/ideate`
> for the standard linear pipeline and `/ideate-dag` when a direction is hard
> enough to warrant multi-agent search.

## Inputs

- `direction` (optional): research direction / keywords / problem statement.
  If omitted, pick the most valuable direction from `wiki/graph/open_questions.md`
  (same rule as `/ideate`).
- `--complexity 1-5` (optional): how large a DAG to run, scaled to task
  difficulty. Omit to use the **paper-figure architecture** (`explore-debate-test`).
- `--dag <name>` (optional): run a specific architecture from the ideation
  library (overrides `--complexity`). See `scidag/templates/ideation/`.
- `--max-ideas N` (optional, default 3): max idea pages to write.
- `--mock` (optional): run the DAG with the offline deterministic LLM (wiring
  test only; produces placeholder ideas).

## Outputs

Identical contract to `/ideate`:
- `wiki/ideas/{slug}.md` — one page per idea (`status: proposed`)
- `wiki/graph/edges.jsonl` — `addresses_gap` / `inspired_by` edges
- `wiki/graph/context_brief.md`, `wiki/graph/open_questions.md` — rebuilt
- **IDEA_REPORT** (terminal) — plus a note of which DAG architecture ran

## How it relates to /ideate

`/ideate` Phase 2 ("dual-model brainstorm") is the step this skill replaces with
a DAG. Phases 1 (landscape scan), 3 (novelty/feasibility validation), and 4
(write to wiki) are **reused unchanged**: this skill produces the candidate
idea(s) via the DAG, then follows `/ideate`'s own "Write ideas to wiki" rules to
persist them. Read the `/ideate` SKILL.md "Outputs", "Wiki Interaction", and
Phase 4 sections and apply them verbatim for persistence.

## Workflow

**Precondition**: working directory is the wiki project root (contains `wiki/`,
`raw/`, `tools/`, `scidag/`).

### Phase 1 — Landscape scan (reuse /ideate Phase 1)

Follow `/ideate` Phase 1 to assemble the context for the target direction:
wiki internal context (`context_brief.md`, `open_questions.md`, relevant
`papers`/`concepts`/`methods`/`topics`) + external search (WebSearch + S2 +
DeepXiv). Compress this into a single **task brief** — a few paragraphs naming
the direction, the known gaps, and the most relevant prior work. This brief is
the DAG's task input.

### Phase 2 — Run the ideation DAG (replaces /ideate Phase 2)

1. **Pick the architecture**:
   ```bash
   # default = paper-figure architecture; or pass --complexity / --dag
   python3 -m scidag.cli select --stage ideation [--complexity N]
   ```
   If the user passed `--dag <name>`, use that name directly. Otherwise use the
   `select` result (a heuristic: larger DAG for harder/broader directions).

2. **Run the DAG** with the task brief from Phase 1:
   ```bash
   # write the task brief to a file to avoid shell-quoting issues
   python3 -m scidag.cli run --stage ideation --dag <name> \
       --task-file /tmp/ideate_dag_task.md [--mock] --show-dag
   ```
   The artifact (a research idea following the Title / Motivation / Hypothesis /
   Approach / Why / Risks format) is printed between
   `===SCIDAG-ARTIFACT-BEGIN===` and `===SCIDAG-ARTIFACT-END===`. Extract it.

3. **For multiple ideas** (`--max-ideas N > 1`): run the DAG N times (or run a
   broader architecture once and treat each leaf candidate as an idea). Keep the
   N strongest distinct ideas.

### Phase 3 — Validation (reuse /ideate Phase 3, optional)

The chosen DAG already includes a feasibility `test` operator. For high-stakes
ideas, additionally run `/novelty` (and `/review`) on each surviving idea exactly
as `/ideate` Phase 3 does, and drop ideas that fail.

### Phase 4 — Write to wiki (reuse /ideate Phase 4)

Persist each surviving idea using `/ideate`'s Phase 4 rules: map the DAG
artifact's sections onto `runtime/templates/ideas.md.tmpl` + `entities.yaml`,
create `wiki/ideas/{slug}.md` (`status: proposed`), add `addresses_gap` /
`inspired_by` edges via `tools/research_wiki.py add-edge`, then rebuild
`context_brief` and `open_questions`. Append a `wiki/log.md` entry noting that
ideas were produced by `/ideate-dag` with architecture `<name>`.

### Report

Emit the standard IDEA_REPORT, adding one line:
`SciDAG: ran ideation architecture <name> (complexity c<N>, <k> LLM calls)`.

## Notes

- This skill calls the SciDAG engine in `scidag/` (operators + DAG executor).
  The engine uses the same LLM config as the `llm-review` MCP server
  (`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` in `.env`).
- Conditional-edge pruning and a learned architecture controller are not yet
  implemented; architecture choice is via `--complexity` / `--dag` / the
  paper-figure default.
