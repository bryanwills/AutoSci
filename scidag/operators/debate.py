"""Debate operator (two domain experts, sequential A->B->A->B). 4 LLM calls.

Ported from MaAS Debate. Expert A is a rigorous defender, Expert B a skeptical
challenger. B speaks last and sees one extra round, so B's final idea is taken
as the refined result — matching the paper's `debate` operator ("two experts
debate over multiple rounds to iteratively improve the idea"), no judge.

Signature (task, idea) -> {"response": str}, slot-compatible with refine/variation.
"""
from __future__ import annotations

from .base import Operator
from .prompts import (
    DEBATER_A_INIT_PROMPT,
    DEBATER_B_INIT_PROMPT,
    DEBATER_UPDATE_PROMPT,
    IDEA_FORMAT,
)


class Debate(Operator):
    def __init__(self, llm, name: str = "Debate"):
        super().__init__(llm, name)
        self._traces = None  # smoke runner may set a list to capture rounds

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        # Round 1: A sees the initial idea
        a0 = (await self._ask(
            DEBATER_A_INIT_PROMPT.format(task=task, idea=idea, idea_format=IDEA_FORMAT)
        ))
        # Round 1: B sees idea + A
        b0 = (await self._ask(
            DEBATER_B_INIT_PROMPT.format(
                task=task, idea=idea, response_a=a0, idea_format=IDEA_FORMAT
            )
        ))
        # Round 2: A updates given B
        a1 = (await self._ask(
            DEBATER_UPDATE_PROMPT.format(
                role="A", task=task, own_response=a0, opponent_response=b0,
                idea_format=IDEA_FORMAT,
            )
        ))
        # Round 2: B produces the final idea
        b1 = (await self._ask(
            DEBATER_UPDATE_PROMPT.format(
                role="B", task=task, own_response=b0, opponent_response=a1,
                idea_format=IDEA_FORMAT,
            )
        ))

        if self._traces is not None:
            self._traces.append({"input": idea, "A_0": a0, "B_0": b0, "A_1": a1, "B_1": b1})

        return {"response": b1}
