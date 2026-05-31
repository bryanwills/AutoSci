"""EarlyStop operator — control signal, 0 LLM calls.

Ported from MaAS EarlyStop. When a controller selects EarlyStop for a parent,
that parent's branch is terminated (no child node is created), so EarlyStop
never executes as a real node. It exists as a selectable control action and as
the conceptual basis for the paper's conditional-edge pruning ("cut a branch
once it has converged or the node budget is reached"). The executor never calls
it; it is handled at sampling / routing time.
"""
from __future__ import annotations

from .base import Operator


class EarlyStop(Operator):
    is_control = True

    def __init__(self, llm=None, name: str = "EarlyStop"):
        super().__init__(llm, name)

    async def __call__(self, *args, **kwargs):
        # Control signal only; should never be executed as a node.
        raise RuntimeError("EarlyStop is a control signal and must not be executed")
