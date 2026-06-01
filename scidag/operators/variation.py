"""Variation operator (explore). 1 LLM call.

Ported from MaAS Variation. Reads a parent idea and produces a NEW idea that
deliberately takes a different line of attack, to widen the candidate pool's
diversity for downstream ensemble / debate / vote. Exploration, not refinement.

Signature (task, idea) -> {"response": str}, slot-compatible with refine/debate.
"""
from __future__ import annotations

from .base import Operator
from .prompts import VARIATION_PROMPT, IDEA_FORMAT


class Variation(Operator):
    def __init__(self, llm, name: str = "Variation"):
        super().__init__(llm, name)

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        prompt = VARIATION_PROMPT.format(task=task, idea=idea, idea_format=IDEA_FORMAT)
        return {"response": await self._ask(prompt)}
