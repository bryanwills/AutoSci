"""Run any SciDAG stage architecture from its module library.

List a module's library:
    python -m scidag.examples.run --stage ideation --list

Run one architecture (real LLM — needs LLM_API_KEY/BASE_URL/MODEL in .env):
    python -m scidag.examples.run --stage ideation --dag explore-debate-test "your task"

Offline smoke (deterministic mock LLM, no API key):
    python -m scidag.examples.run --stage writing --dag review-polish --mock

Stages: ideation (replaces /ideate), experiment (replaces /exp-design),
writing (replaces /paper-plan).
"""
import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scidag.builder import list_library, load_from_library, is_nonlinear, STAGES  # noqa: E402
from scidag.executor import DAGExecutor  # noqa: E402
from scidag.llm import LLMClient, MockLLMClient  # noqa: E402
from scidag.examples.mock import mock_responder  # noqa: E402


def print_library(stage: str):
    print(f"# {stage} DAG library (simple → complex)\n")
    for e in list_library(stage):
        star = " ★paper-figure" if e["paper_figure"] else ""
        print(f"  [{e['complexity']}] {e['name']}{star}  ({e['n_nodes']} nodes)")
        print(f"        {e['description']}")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES, default="ideation")
    ap.add_argument("--dag", help="architecture name from the stage library")
    ap.add_argument("--list", action="store_true", help="list the stage library and exit")
    ap.add_argument("--mock", action="store_true", help="use the offline mock LLM")
    ap.add_argument("task", nargs="?", default="improve sample efficiency of RLHF for small models")
    args = ap.parse_args()

    if args.list or not args.dag:
        print_library(args.stage)
        return

    dag = load_from_library(args.stage, args.dag)
    print(dag.pretty_print())
    print(f"\nnon-linear DAG: {is_nonlinear(dag)}")

    llm = MockLLMClient(responder=mock_responder) if args.mock else LLMClient()
    if not args.mock and not llm.is_configured():
        print("\nNo LLM_API_KEY configured; re-run with --mock for an offline smoke test.")
        return

    print("\n--- running ---\n")
    result = await DAGExecutor(llm).run(dag, task=args.task)
    print(f"LLM calls: {result['n_calls']}")
    print("\n=== Final artifact ===\n")
    print(result["idea"])


if __name__ == "__main__":
    asyncio.run(main())
