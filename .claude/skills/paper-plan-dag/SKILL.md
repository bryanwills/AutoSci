---
description: SciDAG-augmented paper planning — compile a paper outline through a multi-agent operator DAG (draft + review + refine + polish) instead of a single pass, then write PAPER_PLAN using the same contract as /paper-plan. Use for hard or high-stakes outlines where one drafting pass is not enough.
argument-hint: "<idea-slugs...> --venue <ICLR|NeurIPS|ICML|ACL|CVPR|IEEE> [--complexity 1-5] [--dag <name>] [--title <t>] [--mock]"
---

# /paper-plan-dag

> SciDAG augmentation of `/paper-plan` (paper §5). The writing stage's priority
> is **evidence fidelity and refinement**: the plan must faithfully express the
> ideas and their evidence. This skill runs a **DAG of reusable operators** from
> the **writing DAG library**, built around the **review→polish** pair (a draft
> is independently reviewed and refined in parallel, then polished), to catch
> unsupported claims and structural gaps before the outline is committed. It
> returns the result to the **same artifact contract as `/paper-plan`** — a
> `PAPER_PLAN.md` in `wiki/outputs/`, a manuscript record, and `derived_from`
> edges — so nothing downstream changes.
>
> This is an **additive** skill. It does **not** modify `/paper-plan`; use
> `/paper-plan` for the standard pipeline and `/paper-plan-dag` when an outline
> is hard or high-stakes enough to warrant multi-agent review.

## Inputs

- `ideas` (required): target idea slugs (space-separated); same eligibility
  rules as `/paper-plan` (`validated`, or `in_progress` with a succeeded
  experiment).
- `--venue` (required): target venue (ICLR / NeurIPS / ICML / ACL / CVPR / IEEE).
- `--complexity 1-5` (optional): DAG size. Omit to use the **paper-figure
  architecture** (`review-polish`).
- `--dag <name>` (optional): run a specific architecture from the writing
  library (overrides `--complexity`). See `scidag/templates/writing/`.
- `--title <t>` (optional): working title.
- `--mock` (optional): offline deterministic LLM (wiring test only).

## Outputs

Identical contract to `/paper-plan`:
- `wiki/outputs/paper-plan-{slug}-{date}.md` — the PAPER_PLAN
- `wiki/manuscripts/{slug}.md` — manuscript record (`status: drafting`)
- `wiki/graph/edges.jsonl` — `derived_from` edges (plan → ideas/papers)
- `wiki/graph/context_brief.md` — rebuilt
- **PAPER_PLAN_REPORT** (terminal) — plus the DAG architecture used

## How it relates to /paper-plan

`/paper-plan` makes Review LLM review **mandatory**; this skill makes review a
first-class DAG operator and pairs it with refine + polish. The DAG produces the
outline core (narrative structure + section plan); `/paper-plan`'s Step 1
(load idea graph), Step 2 (evidence map), the figure/citation planning, and the
persistence rules are **reused unchanged**. Read the `/paper-plan` SKILL.md
"Outputs", "Wiki Interaction", and Step 1–2 sections and apply them verbatim.

## Workflow

**Precondition**: working directory is the wiki project root (contains `wiki/`,
`raw/`, `tools/`, `scidag/`).

### Phase 1 — Load idea graph + evidence map (reuse /paper-plan Steps 1–2)

Follow `/paper-plan` Step 1 (read target ideas, their `linked_experiments`,
`origin_gaps` concepts/topics, approach-sketch methods/papers) and Step 2
(compile the evidence map: ideas → evidence → sections). Compress this into a
single **task brief** containing the venue + page limit, the evidence map, and
the candidate narrative thrust. This is the DAG's task input.

### Phase 2 — Run the writing DAG (replaces /paper-plan drafting + review)

1. **Pick the architecture**:
   ```bash
   python3 -m scidag.cli select --stage writing [--complexity N]
   ```
   Use `--dag <name>` if the user named one. Larger architectures
   (`full-review-suite`) suit multi-idea papers needing several review lenses.

2. **Run the DAG** with the task brief:
   ```bash
   python3 -m scidag.cli run --stage writing --dag <name> \
       --task-file /tmp/paperplan_dag_task.md [--mock] --show-dag
   ```
   Extract the artifact (the outline: narrative structure + section plan, already
   reviewed and polished) from between the `===SCIDAG-ARTIFACT-BEGIN/END===`
   markers.

### Phase 3 — Figure + citation plan (reuse /paper-plan)

The DAG produces narrative + sections; add the **figure plan** and **citation
plan** following `/paper-plan` (each section → figures/tables it needs; each
claim → wiki evidence + verified BibTeX). Keep `/paper-plan`'s citation
discipline (`citation-verification.md`).

### Phase 4 — Write PAPER_PLAN (reuse /paper-plan persistence)

Assemble the full PAPER_PLAN.md (narrative + sections from the DAG, plus figure
and citation plans) and write it to `wiki/outputs/paper-plan-{slug}-{date}.md`;
create/update `wiki/manuscripts/{slug}.md` (`status: drafting`); add
`derived_from` edges via `tools/research_wiki.py add-edge`; rebuild
`context_brief`; append a `wiki/log.md` entry noting `/paper-plan-dag` with
architecture `<name>`.

### Report

Emit the standard PAPER_PLAN_REPORT, adding:
`SciDAG: ran writing architecture <name> (complexity c<N>, <k> LLM calls)`.

## Notes

- Calls the SciDAG engine in `scidag/`; same LLM config as `llm-review`
  (`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` in `.env`). The DAG's `review`
  operator is the in-engine analogue of `/paper-plan`'s mandatory Review LLM step.
