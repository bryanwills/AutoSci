---
description: SciDAG-augmented experiment design — design an experiment suite through a multi-agent operator DAG (method candidates + parallel reliability/test checks + consolidation) instead of a single pass, then write experiment pages using the same contract as /exp-design. Use for hard designs where one-shot planning is risky.
argument-hint: "<idea-slug> [--complexity 1-5] [--dag <name>] [--mock]"
---

# /exp-design-dag

> SciDAG augmentation of `/exp-design` (paper §5). The experimentation stage's
> priority is **reliability** — experiments are the most expensive step, so the
> design must be sound and runnable one-shot. This skill runs a **DAG of
> reusable operators** from the **experiment DAG library**, where the `test`
> (feasibility/logic) operator is prominent and appears on parallel branches, to
> stress the design before any compute is spent. It returns the result to the
> **same artifact contract as `/exp-design`** — `wiki/experiments/{exp-slug}.md`
> pages, a master design doc, and `tested_by` edges — so nothing downstream
> changes.
>
> This is an **additive** skill. It does **not** modify `/exp-design`; use
> `/exp-design` for the standard pipeline and `/exp-design-dag` when a design is
> hard or costly enough to warrant multi-agent reliability checking.

## Inputs

- `idea-slug` (required): the idea to design experiments for
  (`wiki/ideas/{slug}.md`).
- `--complexity 1-5` (optional): DAG size, scaled to design difficulty. Omit to
  use the **paper-figure architecture** (`candidate-doubletest-refine`).
- `--dag <name>` (optional): run a specific architecture from the experiment
  library (overrides `--complexity`). See `scidag/templates/experiment/`.
- `--mock` (optional): offline deterministic LLM (wiring test only).

## Outputs

Identical contract to `/exp-design`:
- `wiki/experiments/{exp-slug}.md` — one page per experiment block
  (`status: planned`, `linked_idea` set)
- `experiments/designs/{slug}-master.md` — master design document
- `wiki/graph/edges.jsonl` — `tested_by` edges (idea → each experiment)
- `wiki/ideas/{slug}.md` — updated `linked_experiments`
- `wiki/graph/context_brief.md`, `open_questions.md` — rebuilt
- **DESIGN_REPORT** (terminal) — plus the DAG architecture used

## How it relates to /exp-design

`/exp-design` Phase 2 (method candidate generation) and its iterative-ablation
loop are the parts this skill expresses as a DAG: parallel candidate designs,
each gated by a `test`, consolidated by `refine` (and `debate` for ablation
comparison in the larger architectures). Phases 1 (load context), 3 (benchmark
selection), and the persistence rules are **reused unchanged** from `/exp-design`.
Read the `/exp-design` SKILL.md "Outputs", "Wiki Interaction", and Phase 1–3
sections and apply them verbatim.

## Workflow

**Precondition**: working directory is the wiki project root (contains `wiki/`,
`raw/`, `tools/`, `scidag/`).

### Phase 1 — Load context (reuse /exp-design Phase 1)

Follow `/exp-design` Phase 1: read `wiki/ideas/{slug}.md` (hypothesis, approach,
risks, novelty), the pilot report if present, related `methods`/`papers`, and
existing experiments. Add benchmark/baseline context from `/exp-design` Phase 3.
Compress into a single **task brief** describing the idea, its hypothesis, the
hardware/compute budget, and the candidate method directions. This is the DAG's
task input.

### Phase 2 — Run the experiment DAG (replaces /exp-design Phase 2 + ablation loop)

1. **Pick the architecture**:
   ```bash
   python3 -m scidag.cli select --stage experiment [--complexity N]
   ```
   Use `--dag <name>` if the user named one. Larger architectures
   (`iterative-ablation`, `full-reliability-suite`) suit designs with many
   factors to ablate or high run cost.

2. **Run the DAG** with the task brief:
   ```bash
   python3 -m scidag.cli run --stage experiment --dag <name> \
       --task-file /tmp/expdesign_dag_task.md [--mock] --show-dag
   ```
   Extract the artifact (a consolidated experiment design) from between the
   `===SCIDAG-ARTIFACT-BEGIN/END===` markers. The design enumerates method
   candidate(s), benchmark + baselines + metrics, and the experiment blocks
   (main, ablation, sensitivity), each with a feasibility note from the DAG's
   `test` operator(s).

### Phase 3 — Benchmark finalization (reuse /exp-design Phase 3)

Reconcile the DAG's proposed benchmark/metrics with `/exp-design` Phase 3
standards (use field-standard datasets/metrics; verify baselines exist in the
wiki). Adjust the design if the DAG picked a non-standard benchmark.

### Phase 4 — Write to wiki (reuse /exp-design persistence)

Split the consolidated design into one `wiki/experiments/{exp-slug}.md` per block
(`status: planned`, `linked_idea: {idea-slug}`) following
`runtime/templates/experiments.md.tmpl`; write `experiments/designs/{slug}-master.md`;
add `tested_by` edges via `tools/research_wiki.py add-edge`; update the idea's
`linked_experiments`; rebuild `context_brief` / `open_questions`; append a
`wiki/log.md` entry noting `/exp-design-dag` with architecture `<name>`.

### Report

Emit the standard DESIGN_REPORT, adding:
`SciDAG: ran experiment architecture <name> (complexity c<N>, <k> LLM calls)`.

## Notes

- Calls the SciDAG engine in `scidag/`; same LLM config as `llm-review`
  (`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` in `.env`).
- The DAG `test` operator checks design **feasibility/logic** (oracle-free); it
  does not run real experiments. Actual execution remains `/exp-run`.
