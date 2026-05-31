"""Refine operator (self-refine). 1 LLM call.

Ported from MaAS SelfRefine. Reads a parent idea and produces an improved
version: sharpens the hypothesis, makes the approach concrete, removes vague
mechanisms and hidden assumptions. Improvement, not exploration.

Signature (task, idea) -> {"response": str}, slot-compatible with variation/debate.
"""
from __future__ import annotations

from .base import Operator
from .prompts import REFINE_PROMPT, IDEA_FORMAT


class Refine(Operator):
    def __init__(self, llm, name: str = "Refine"):
        super().__init__(llm, name)

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        prompt = REFINE_PROMPT.format(task=task, idea=idea, idea_format=IDEA_FORMAT)
        return {"response": await self._ask(prompt)}
