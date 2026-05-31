# SciDAG Stage DAG Libraries (§2 — stage specialization)

Each research stage keeps its **own DAG library** — a set of 4–6 reusable
operator-graph architectures, ordered simple → complex. Every architecture is a
genuine **DAG** (it branches: some node has multiple parents or multiple
children), never a pure linear chain — even the complexity-1 templates fan out
from the root and vote at the end. Each library contains **the architecture
shown in the paper figure** (marked `paper_figure: true`).

A SciFlow skill picks one architecture from the matching library and runs it via
`DAGExecutor`, getting back one artifact under the skill's existing contract.

| Library | Replaces | Stage emphasis (paper §2) | Paper-figure architecture |
|---|---|---|---|
| `ideation/` | `/ideate` | diverse generation + debate | `explore-debate-test` |
| `experiment/` | `/exp-design` | reliability checks (test) | `candidate-doubletest-refine` |
| `writing/` | `/paper-plan` | evidence fidelity + review→polish | `review-polish` |

## Architecture format

Each `*.yaml` is one architecture: light metadata (`name`, `stage`,
`complexity` 1–5, `paper_figure`, `description`) + a `nodes:` list in layer
order. A node's `parents` are `root` or 0-based indices of earlier nodes.
Load via `scidag.builder.load_from_library(stage, name)` /
`list_library(stage)`.

## ideation/ — replaces `/ideate` (diverse generation + debate)

`/ideate` = landscape scan → dual-model brainstorm (5 paths A–E) → novelty /
feasibility screening. The library scales that from a two-draft vote to a
broad parallel explore-debate-refine sweep:

| c | name | shape |
|---|---|---|
| 1 | `dual-draft-vote` | root → {Generate, GenerateCoT} → vote |
| 2 | `diamond-explore` | GenerateCoT → {Refine, Variation} → vote |
| 2 | `debate-screen` | Generate → {Debate, Variation} → Test |
| 3 | `explore-debate-test` ★ | MultiGenerate → {Variation, Debate} → Test |
| 4 | `broad-explore-converge` | MultiGenerate → {Variation, Debate, Refine} → Test |

## experiment/ — replaces `/exp-design` (reliability / test)

`/exp-design` = method candidates → benchmark → iterative ablation. Per the
paper's stage emphasis, this library is built on the experiment-stage **core
operators {generate, test, refine}** — `Test` is prominent (reliability) and
exploration operators are de-emphasized. **4 of 5 DAGs use core operators only**;
one mixed DAG adds variation/debate for harder, exploratory designs.

| c | name | core-only | shape |
|---|---|:--:|---|
| 1 | `dual-generate-test` | ✓ | {Generate, GenerateCoT} → Test |
| 2 | `generate-refine-test` | ✓ | GenerateCoT → {Refine, Test} → Test |
| 3 | `multigen-test-refine` ★ | ✓ | MultiGenerate → {Test, Refine→Test} → Refine |
| 4 | `iterative-test-refine` | ✓ | GenCoT→Test→Refine→Test ∥ Gen→Test → Refine |
| 4 | `candidate-variation-suite` | + Variation/Debate | MultiGenerate → {Variation→Test, Refine→Test} → Debate |

## writing/ — replaces `/paper-plan` (evidence fidelity + review→polish)

`/paper-plan` = evidence map → narrative structure → section/figure/citation
plan, with **mandatory review**. Per the paper's stage emphasis, this library is
built on the writing-stage **core operators {review, polish}** (plus a producer
to draft). **3 of 5 DAGs use core operators only**; two mixed DAGs add
refine / debate for harder outlines.

| c | name | core-only | shape |
|---|---|:--:|---|
| 1 | `draft-dual-review-polish` | ✓ | Generate → {Review, Review} → Polish |
| 2 | `dual-draft-review-polish` ★ | ✓ | {Generate, GenerateCoT} → Review each → Polish |
| 3 | `review-polish-review` | ✓ | GenCoT → Review→Polish→Review ∥ Review → Polish |
| 3 | `refine-review-polish` | + Refine | GenerateCoT → {Refine, Review} → Polish |
| 4 | `debate-review-polish-suite` | + Variation/Debate | MultiGenerate → {Variation, Debate, Review} → Polish |

> ★ = paper-figure architecture. "core-only" = uses only the stage's preferred
> operators (experiment: generate/test/refine; writing: producers + review/polish).
> This realizes the paper's claim that experiment and writing stages favor
> different operator sets.

★ = the architecture shown in the paper figure.

## Try it

```bash
python3 -m scidag.examples.run --stage ideation --list
python3 -m scidag.examples.run --stage experiment --dag candidate-doubletest-refine --mock
python3 -m scidag.examples.run --stage writing --dag review-polish "your paper topic"
```
