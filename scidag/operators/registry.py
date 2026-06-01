"""Operator registry for SciDAG.

`OPERATOR_MAPPING`: name -> Operator class, all built as `cls(llm)` by the
executor. `SELECTABLE_OPERATORS`: the operators a controller may place as DAG
nodes, in a fixed order (a future policy head's logits align to this order).

Following MaAS: Ensemble is NOT selectable (used only for merge / final vote),
and EarlyStop is excluded from the selectable list (handled as a control signal
at sampling / routing time). `OPERATOR_DESCRIPTIONS` seeds operator text
embeddings for the learned controller added in a later step.

This is the full 9-operator library from the paper (Table 5): the 7 ported from
MaAS plus `review` and `polish` (the writing-stage critique→edit pair).
"""
from __future__ import annotations

from .generate import Generate, GenerateCoT, MultiGenerate
from .variation import Variation
from .refine import Refine
from .debate import Debate
from .test_op import Test
from .ensemble import Ensemble
from .early_stop import EarlyStop
from .review import Review
from .polish import Polish

OPERATOR_MAPPING = {
    "Generate": Generate,
    "GenerateCoT": GenerateCoT,
    "MultiGenerate": MultiGenerate,
    "Variation": Variation,
    "Refine": Refine,
    "Debate": Debate,
    "Test": Test,
    "Review": Review,
    "Polish": Polish,
    "Ensemble": Ensemble,
    "EarlyStop": EarlyStop,
}

# Operators a controller may sample as nodes (Ensemble / EarlyStop excluded).
SELECTABLE_OPERATORS = [
    "Generate",
    "GenerateCoT",
    "MultiGenerate",
    "Variation",
    "Refine",
    "Debate",
    "Test",
    "Review",
    "Polish",
]

PRODUCER_OPERATORS = {"Generate", "GenerateCoT", "MultiGenerate"}

# Short natural-language descriptions to initialize operator embeddings for the
# learned controller (paper §3 architecture-layer selection; added later).
OPERATOR_DESCRIPTIONS = {
    "Generate": "Produce one concrete research idea directly from the task.",
    "GenerateCoT": "Reason step by step about gaps, then produce one research idea.",
    "MultiGenerate": "Produce several independent research ideas as parallel lanes.",
    "Variation": "Given an idea, produce a different idea via a new line of attack (explore).",
    "Refine": "Given an idea, sharpen its hypothesis and make the approach concrete (improve).",
    "Debate": "Two domain experts debate an idea over rounds and return the refined idea.",
    "Test": "Stress-test an idea's feasibility and logic; repair one blocking flaw.",
    "Review": "Independently critique an idea (novelty/soundness/feasibility/clarity) and score it.",
    "Polish": "Edit an idea's presentation per review feedback without changing its substance.",
    "Ensemble": "Vote over multiple candidate ideas and return the strongest one.",
    "EarlyStop": "Terminate a branch that has converged or hit the node budget.",
}
