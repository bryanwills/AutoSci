"""Command-line entry point for SciDAG, used by the SciDAG-augmented skills.

A SciFlow skill shells out to this CLI to run an operator DAG as a tool and get
back one artifact, keeping the skill's own contract unchanged. Subcommands:

    list   --stage S                       list a module's DAG library
    select --stage S [--complexity N]      pick an architecture (default: paper-figure)
    run    --stage S --dag NAME --task "…" run an architecture, print the artifact

`run` reads the task from --task or --task-file, runs the chosen DAG via the
configured LLM (LLM_API_KEY/BASE_URL/MODEL in .env), and prints the final
artifact between explicit markers so the caller can extract it. With --mock it
uses the deterministic offline LLM (no network), for wiring tests.

Examples:
    python3 -m scidag.cli list --stage ideation
    python3 -m scidag.cli select --stage experiment --complexity 3
    python3 -m scidag.cli run --stage writing --dag review-polish --task "RLHF survey" --mock
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .builder import list_library, load_from_library, is_nonlinear, STAGES
from .executor import DAGExecutor
from .llm import LLMClient, MockLLMClient

ARTIFACT_BEGIN = "===SCIDAG-ARTIFACT-BEGIN==="
ARTIFACT_END = "===SCIDAG-ARTIFACT-END==="


def _select(stage: str, complexity=None) -> dict:
    """Pick one architecture from a stage library.

    Default: the paper-figure architecture (the module's canonical DAG). If
    --complexity N is given, pick the architecture whose complexity is closest
    to N (ties → the simpler one), so a skill can scale graph size to task
    difficulty without a learned controller.
    """
    lib = list_library(stage)
    if complexity is None:
        for e in lib:
            if e["paper_figure"]:
                return e
        return lib[0]
    return min(lib, key=lambda e: (abs(e["complexity"] - complexity), e["complexity"]))


def cmd_list(args) -> int:
    lib = list_library(args.stage)
    if args.json:
        print(json.dumps(lib, indent=2))
        return 0
    print(f"# {args.stage} DAG library (simple → complex)  — replaces {_REPLACES[args.stage]}\n")
    for e in lib:
        star = "  ★paper-figure" if e["paper_figure"] else ""
        print(f"  [c{e['complexity']}] {e['name']} ({e['n_nodes']} nodes){star}")
        print(f"        {e['description']}")
    return 0


def cmd_select(args) -> int:
    e = _select(args.stage, args.complexity)
    if args.json:
        print(json.dumps(e, indent=2))
    else:
        print(e["name"])
    return 0


async def _run(args) -> int:
    dag = load_from_library(args.stage, args.dag)
    if args.task_file:
        with open(args.task_file) as f:
            task = f.read().strip()
    else:
        task = args.task or ""
    if not task:
        print("error: provide --task or --task-file", file=sys.stderr)
        return 2

    llm = MockLLMClient(_mock()) if args.mock else LLMClient()
    if not args.mock and not llm.is_configured():
        print("error: LLM_API_KEY not configured (.env). Use --mock for an offline test.",
              file=sys.stderr)
        return 3

    if args.show_dag:
        print(dag.pretty_print(), file=sys.stderr)
        print(f"non-linear DAG: {is_nonlinear(dag)}", file=sys.stderr)

    result = await DAGExecutor(llm).run(dag, task=task)
    print(f"[scidag] stage={args.stage} dag={args.dag} llm_calls={result['n_calls']}",
          file=sys.stderr)
    # artifact to stdout, fenced for easy extraction by the calling skill
    print(ARTIFACT_BEGIN)
    print(result["idea"])
    print(ARTIFACT_END)
    return 0


def cmd_run(args) -> int:
    return asyncio.run(_run(args))


def _mock():
    from .examples.mock import mock_responder
    return mock_responder


_REPLACES = {
    "ideation": "/ideate",
    "experiment": "/exp-design",
    "writing": "/paper-plan",
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scidag", description="SciDAG operator-DAG runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="list a stage's DAG library")
    pl.add_argument("--stage", choices=STAGES, required=True)
    pl.add_argument("--json", action="store_true")
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser("select", help="pick an architecture from a stage library")
    ps.add_argument("--stage", choices=STAGES, required=True)
    ps.add_argument("--complexity", type=int, default=None,
                    help="1..5; default picks the paper-figure architecture")
    ps.add_argument("--json", action="store_true")
    ps.set_defaults(func=cmd_select)

    pr = sub.add_parser("run", help="run an architecture and print the artifact")
    pr.add_argument("--stage", choices=STAGES, required=True)
    pr.add_argument("--dag", required=True, help="architecture name from the stage library")
    pr.add_argument("--task", default=None, help="the stage task text")
    pr.add_argument("--task-file", default=None, help="read the task text from a file")
    pr.add_argument("--mock", action="store_true", help="offline deterministic LLM")
    pr.add_argument("--show-dag", action="store_true", help="print the DAG to stderr")
    pr.set_defaults(func=cmd_run)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
