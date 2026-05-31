"""DAG data structure for SciDAG.

Adapted from MaAS `maas/ext/maas/models/dag.py`. The graph algorithms
(add_node / topological_order / get_children / get_ancestors / leaves) are
kept verbatim in spirit; the torch dependency is removed so the executor runs
without a learned controller. `LayerDecision` keeps the per-parent
credit-assignment slots (log_prob / entropy / value) as plain optional floats,
so a controller can be bolted on later without changing this module.

A node names an operator; a directed edge means "information flows from parent
to child". Conditional edges are not stored here — they are realized at run
time by a router over execution state (see executor.py / routing, later step).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DAGNode:
    node_id: int
    op_name: str
    layer_idx: int
    parent_ids: List[int] = field(default_factory=list)
    is_root: bool = False
    is_leaf: bool = False


@dataclass
class LayerDecision:
    """One per-parent sampling decision (atomic credit-assignment unit).

    Covers the K children spawned for one parent at one layer; those children
    share this decision's log_prob / entropy / value. Filled by a controller;
    left as None on hand-built / controller-less DAGs.
    """
    layer_idx: int
    parent_id: int
    op_names: List[str]
    log_prob: Optional[float] = None
    entropy: Optional[float] = None
    value: Optional[float] = None


@dataclass
class SampledDAG:
    nodes: Dict[int, DAGNode] = field(default_factory=dict)
    decisions: List[LayerDecision] = field(default_factory=list)
    truncated_decisions: int = 0  # merge nodes dropped due to max_nodes cap
    root_id: int = -1

    # ---- construction ---------------------------------------------------

    def add_root(self, op_name: str = "ROOT") -> int:
        """Add the virtual root (layer -1). Producers attach to it at layer 0."""
        nid = len(self.nodes)
        self.nodes[nid] = DAGNode(node_id=nid, op_name=op_name, layer_idx=-1, is_root=True)
        self.root_id = nid
        return nid

    def add_node(self, op_name: str, layer_idx: int, parent_ids: List[int]) -> int:
        nid = len(self.nodes)
        self.nodes[nid] = DAGNode(
            node_id=nid, op_name=op_name, layer_idx=layer_idx, parent_ids=list(parent_ids)
        )
        return nid

    def add_decision(
        self,
        layer_idx: int,
        parent_id: int,
        op_names: List[str],
        log_prob: Optional[float] = None,
        entropy: Optional[float] = None,
        value: Optional[float] = None,
    ) -> None:
        self.decisions.append(
            LayerDecision(layer_idx, parent_id, list(op_names), log_prob, entropy, value)
        )

    # ---- queries --------------------------------------------------------

    def get_children(self, node_id: int) -> List[int]:
        return [n.node_id for n in self.nodes.values() if node_id in n.parent_ids]

    def get_ancestors(self, node_id: int) -> Set[int]:
        result: Set[int] = set()
        stack = list(self.nodes[node_id].parent_ids)
        while stack:
            cur = stack.pop()
            if cur in result:
                continue
            result.add(cur)
            stack.extend(self.nodes[cur].parent_ids)
        return result

    def has_ancestor_with_name(self, node_id: int, op_name: str) -> bool:
        return any(self.nodes[aid].op_name == op_name for aid in self.get_ancestors(node_id))

    def topological_order(self) -> List[int]:
        """Kahn's algorithm over parent_ids. Returns node ids in execution order."""
        in_degree = {nid: len(node.parent_ids) for nid, node in self.nodes.items()}
        queue = [nid for nid, d in in_degree.items() if d == 0]
        order: List[int] = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for cid in self.get_children(nid):
                in_degree[cid] -= 1
                if in_degree[cid] == 0:
                    queue.append(cid)
        return order

    def finalize_leaves(self) -> None:
        for nid, node in self.nodes.items():
            if node.is_root:
                continue
            if len(self.get_children(nid)) == 0:
                node.is_leaf = True

    def leaves(self) -> List[int]:
        return [nid for nid, n in self.nodes.items() if n.is_leaf]

    def nodes_by_layer(self) -> Dict[int, List[int]]:
        out: Dict[int, List[int]] = {}
        for nid, node in self.nodes.items():
            if node.is_root:
                continue
            out.setdefault(node.layer_idx, []).append(nid)
        return out

    # ---- debug ----------------------------------------------------------

    def pretty_print(self) -> str:
        lines = [f"SampledDAG ({len(self.nodes)} nodes incl. root)"]
        for nid in self.topological_order():
            n = self.nodes[nid]
            tags = " ".join(t for t, on in (("ROOT", n.is_root), ("LEAF", n.is_leaf)) if on)
            parents = ",".join(str(p) for p in n.parent_ids) if n.parent_ids else "-"
            lines.append(
                f"  #{nid:>2d}  L{n.layer_idx:>2d}  {n.op_name:<16s}  parents=[{parents:<8s}] {tags}"
            )
        return "\n".join(lines)
