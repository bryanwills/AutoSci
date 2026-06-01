"""DAG executor for SciDAG.

Adapted from MaAS `.../MBPP/train/graph.py` (the `Workflow` class). Runs a
SampledDAG in topological order and returns one research idea, so a calling
SciFlow skill keeps its artifact contract. Carries over the MaAS execution
mechanics, reframed from code to research ideas:

  - **Lane mechanism**: a node's output is a list of candidate ideas (lanes).
    MultiGenerate emits N lanes; lanes broadcast/propagate to children. A 1-lane
    parent broadcasts to every lane of a wider child.
  - **Multi-parent merge**: when a consumer has several parents (or several
    lanes feeding one lane slot), their ideas are voted by Ensemble into one
    before the operator runs.
  - **Final aggregation**: ideas across all leaves are voted by Ensemble into a
    single delivered idea (single leaf -> passthrough, no extra call).

Producers ignore parent inputs; consumers (Variation / Refine / Debate / Test)
share the (task, idea) -> {"response"|"solution": str} shape. Conditional-edge
routing / early-stop pruning is a later step; this executor runs the full
sampled graph.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .dag import SampledDAG
from .operators.registry import OPERATOR_MAPPING, PRODUCER_OPERATORS


class DAGExecutor:
    def __init__(self, llm, operator_mapping: Optional[dict] = None):
        self.llm = llm
        mapping = operator_mapping or OPERATOR_MAPPING
        # one shared instance per operator name (built as cls(llm), MaAS style)
        self.operators = {name: cls(llm) for name, cls in mapping.items()}
        self.ensemble = self.operators["Ensemble"]  # merge / final vote aggregator

    async def run(self, dag: SampledDAG, task: str) -> dict:
        """Execute the DAG for `task`. Returns a result dict:

        {"idea": str, "n_calls": int, "node_outputs": {nid: [idea, ...]}}.
        """
        dag.finalize_leaves()
        node_outputs: Dict[int, List[str]] = {}
        calls_before = self.llm.n_calls

        for nid in dag.topological_order():
            node = dag.nodes[nid]
            if node.is_root:
                node_outputs[nid] = []
                continue
            try:
                node_outputs[nid] = await self._execute_node(node, dag, task, node_outputs)
            except Exception:  # noqa: BLE001 — a dead node should not kill the graph
                node_outputs[nid] = []

        leaf_outputs: List[str] = []
        for leaf_id in dag.leaves():
            leaf_outputs.extend(node_outputs.get(leaf_id, []))
        final_idea = await self._aggregate(leaf_outputs, task)

        return {
            "idea": final_idea,
            "n_calls": self.llm.n_calls - calls_before,
            "node_outputs": node_outputs,
        }

    async def _aggregate(self, ideas: List[str], task: str) -> str:
        """Final leaf vote: single -> passthrough, >=2 -> Ensemble."""
        ideas = [i for i in ideas if i and i.strip()]
        if not ideas:
            return ""
        if len(ideas) == 1:
            return ideas[0]
        return (await self.ensemble(task=task, solutions=ideas)).get("response", "")

    async def _vote_lane_inputs(self, lane_inputs: List[str], task: str) -> str:
        """Collapse several parent ideas feeding one lane slot into one idea."""
        lane_inputs = [i for i in lane_inputs if i and i.strip()]
        if not lane_inputs:
            return ""
        if len(lane_inputs) == 1:
            return lane_inputs[0]
        return (await self.ensemble(task=task, solutions=lane_inputs)).get("response", "")

    async def _execute_node(self, node, dag: SampledDAG, task: str, node_outputs) -> List[str]:
        op_name = node.op_name
        op = self.operators[op_name]

        # MultiGenerate: producer, ignores parents, 1 logical op -> N lanes.
        if op_name == "MultiGenerate":
            result = await op(task=task)
            resp = result.get("response", [])
            return [r for r in resp] if isinstance(resp, list) else [resp]

        # Other producers ignore parents -> single lane.
        if op_name in PRODUCER_OPERATORS:
            return [(await op(task=task)).get("response", "")]

        # Consumers: gather parent lanes (skip virtual root).
        parent_outputs = [
            node_outputs.get(pid, [])
            for pid in node.parent_ids
            if not dag.nodes[pid].is_root
        ]
        lane_count = max([len(po) for po in parent_outputs] + [1])

        outputs: List[str] = []
        for k in range(lane_count):
            lane_inputs: List[str] = []
            for po in parent_outputs:
                if not po:
                    continue
                lane_inputs.append(po[k] if len(po) >= lane_count else po[0])  # broadcast 1-lane
            idea_in = await self._vote_lane_inputs(lane_inputs, task)

            if op_name == "Test":
                # Test returns {"result", "solution", ...}; downstream takes the idea.
                outputs.append((await op(task=task, idea=idea_in)).get("solution", ""))
            else:
                # Variation / Refine / Debate / Review / Polish all share
                # (task, idea) -> {"response": str}. (Review also carries
                # score/verdict, but the idea+feedback bundle is in "response".)
                outputs.append((await op(task=task, idea=idea_in)).get("response", ""))

        return outputs
