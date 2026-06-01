"""SciDAG operator library (§1 of the paper's SciDAG method).

The full 9 operators from the paper (Table 5), reframed for research ideas:
generate (+cot/multi), variation, refine, debate, test, review, polish,
ensemble, early-stop. Seven are ported from MaAS; review and polish are the
writing-stage critique→edit pair.
"""
from .base import Operator
from .generate import Generate, GenerateCoT, MultiGenerate
from .variation import Variation
from .refine import Refine
from .debate import Debate
from .test_op import Test
from .review import Review
from .polish import Polish
from .ensemble import Ensemble
from .early_stop import EarlyStop
from .registry import (
    OPERATOR_MAPPING,
    SELECTABLE_OPERATORS,
    PRODUCER_OPERATORS,
    OPERATOR_DESCRIPTIONS,
)

__all__ = [
    "Operator",
    "Generate", "GenerateCoT", "MultiGenerate",
    "Variation", "Refine", "Debate", "Test", "Review", "Polish",
    "Ensemble", "EarlyStop",
    "OPERATOR_MAPPING", "SELECTABLE_OPERATORS",
    "PRODUCER_OPERATORS", "OPERATOR_DESCRIPTIONS",
]
