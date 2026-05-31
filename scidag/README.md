# SciDAG — DAG-Based Multi-Agent Augmentation

Implementation of the **SciDAG** module from the AutoSci paper (Agent4S @ BAAI
2026, §5). SciDAG lets a hard SciFlow skill call a directed acyclic graph of
reusable research operators as a tool: given a stage task `z`, it runs an
operator graph `G = (V, E)` and returns **one research idea** under the same
artifact contract, so the calling skill is unchanged.

The operator and DAG-execution logic is adapted from the MaAS repository
(`MaAS-main`); the LLM call layer is rewired to AutoSci's OpenAI-compatible
endpoint and the artifacts are reframed from code to **research ideas (text)**.

> Status: **step 2 — full 9-operator library + DAG executor.** No MetaGPT
> dependency. The learned controller (architecture-layer selection),
> conditional-edge routing (execution-layer pruning), and the trace/experience
> repository come in later steps.

## Layout

| Path | Role | Paper mapping |
|---|---|---|
| `operators/` | the 7 reusable operators + prompts + registry | §1 operator library |
| `dag.py` | `SampledDAG` / `DAGNode` graph data structure | §1 operator graph |
| `executor.py` | `DAGExecutor` — topological run, lanes, merge vote | §1 adaptive operator graph |
| `builder.py` | build a DAG from a spec; load/list stage libraries | §2 stage templates |
| `templates/<stage>/` | per-module DAG library (5 architectures each) | §2 stage specialization |
| `llm.py` | thin async OpenAI-compatible client (+ mock) | (runtime) |
| `examples/` | runnable demo / offline smoke | — |

## Operators (the paper's full 9, reframed code → research idea)

| Operator | Calls | Role | Inputs → Output | Source |
|---|---|---|---|---|
| `Generate` | 1 | producer | task → idea | MaAS Generate |
| `GenerateCoT` | 1 | producer (reasoning) | task → idea | MaAS GenerateCoT |
| `MultiGenerate` | N (3) | producer (fan-out) | task → N idea lanes | MaAS MultiGenerateCoT |
| `Variation` | 1 | consumer (explore) | task, idea → different idea | MaAS Variation |
| `Refine` | 1 | consumer (improve) | task, idea → sharpened idea | MaAS SelfRefine |
| `Debate` | 4 | consumer (two experts A→B→A→B) | task, idea → refined idea | MaAS Debate |
| `Test` | 1 (+≤1 repair) | verifier (feasibility/logic, oracle-free) | task, idea → {result, solution} | MaAS Test (re-adapted) |
| `Review` | 1 | consumer (scored critique) | task, idea → {response=idea+feedback, score, verdict} | new |
| `Polish` | 1 | consumer (review-guided edit) | task, idea → polished idea | new |
| `Ensemble` | 1 | aggregator (never sampled) | task, ideas → strongest idea | MaAS ScEnsemble |
| `EarlyStop` | 0 | control signal | — | MaAS EarlyStop |

`Review` produces an independent, scored critique (novelty / soundness /
feasibility / clarity + an overall `Score: N/10` and `Verdict`) and appends it
to the idea as a `## Review feedback` block; `Polish` consumes that block,
applies the presentational suggestions, and returns a clean write-up — the
paper's writing-stage critique→edit pair. `Ensemble` is used only for
multi-parent merge and the final leaf vote; `EarlyStop` is a control action for
branch pruning, never executed as a node.

### Prompt adaptation

All operator prompts (`operators/prompts.py`) are written for the **research**
task, not MaAS's code task. The key adaptation: MaAS prompts optimize a single
axis — code *correctness* — whereas research ideas are judged on **novelty,
specificity, and falsifiability**. Generation/transformation prompts therefore
push for concrete, non-obvious ideas with a testable hypothesis and honest
risks; `Test` checks feasibility/logic instead of running code; `Ensemble` and
`Review` score on research criteria rather than pass/fail. Every idea follows a
shared `IDEA_FORMAT` (Title / Motivation / Hypothesis / Approach / Why / Risks)
so SciFlow skills can map it onto a wiki entity page.

## Execution model (carried over from MaAS)

- **Lanes**: a node's output is a list of candidate ideas. `MultiGenerate`
  emits N lanes; a 1-lane parent broadcasts to a wider child; lanes propagate.
- **Multi-parent merge**: when several parent ideas feed one lane slot, they are
  voted by `Ensemble` into one before the operator runs.
- **Final aggregation**: ideas across all leaves are voted into one delivered
  idea (single leaf → passthrough, no extra call).
- Producers ignore parents (layer 0); consumers share `(task, idea)` shape.

## Run

```bash
# from the AutoSci repo root (AutoSci_contest/)
# list a stage's DAG library (simple → complex; ★ = paper-figure architecture)
python3 -m scidag.examples.run --stage ideation --list

# run one architecture — real LLM needs LLM_API_KEY / LLM_BASE_URL / LLM_MODEL in .env
python3 -m scidag.examples.run --stage ideation --dag explore-debate-test "improve RLHF"

# offline smoke — deterministic mock LLM, no API key
python3 -m scidag.examples.run --stage writing --dag review-polish --mock
```

## Stage DAG libraries

Each stage has its own library of 4–6 reusable architectures (simple → complex,
all genuine DAGs, each including the paper-figure architecture). See
[`templates/README.md`](templates/README.md).

| Library | Augmented by skill | Emphasis | Paper-figure DAG |
|---|---|---|---|
| `templates/ideation/` | `/ideate-dag` (augments `/ideate`) | diverse generation + debate | `explore-debate-test` |
| `templates/experiment/` | `/exp-design-dag` (augments `/exp-design`) | reliability checks (test) | `candidate-doubletest-refine` |
| `templates/writing/` | `/paper-plan-dag` (augments `/paper-plan`) | evidence fidelity + review→polish | `review-polish` |

## Skill integration (additive)

Three **new** skills wire the libraries into SciFlow without touching the
existing skills (paper §5: SciDAG is an optional augmentation that returns to
the same artifact contract):

| New skill | Augments | Replaces that skill's | Returns the same artifact |
|---|---|---|---|
| `/ideate-dag` | `/ideate` | dual-model brainstorm (Phase 2) | `wiki/ideas/{slug}.md` + edges |
| `/exp-design-dag` | `/exp-design` | candidate generation + ablation loop | `wiki/experiments/*` + master doc |
| `/paper-plan-dag` | `/paper-plan` | drafting + review | `PAPER_PLAN.md` + manuscript record |

Each skill gathers context like the original, runs a DAG via the CLI, then reuses
the original skill's persistence rules — so downstream stages are unchanged.

## CLI (how skills call the engine)

```bash
python3 -m scidag.cli list   --stage ideation
python3 -m scidag.cli select --stage experiment --complexity 3   # -> architecture name
python3 -m scidag.cli run    --stage writing --dag review-polish \
        --task-file task.md [--mock] --show-dag
```
`run` prints the artifact between `===SCIDAG-ARTIFACT-BEGIN/END===` on stdout
(DAG/diagnostics go to stderr), so a skill extracts it cleanly. `select` with
no `--complexity` returns the paper-figure architecture.

## Configuration

Reads `.env` (project root or `~/.env`), same keys as `mcp-servers/llm-review`:
`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_FALLBACK_MODEL`.
