"""Generate operators (producers).

Ported from MaAS Generate / GenerateCoT / MultiGenerateCoT. Producers ignore
parent inputs and emit a fresh research idea from the task. MultiGenerate runs
N independent generations to seed `N` parallel lanes downstream (diversity for
ensemble / debate / final vote), mirroring MaAS's MultiGenerateCoT 3-lane fan-out.
"""
from __future__ import annotations

from typing import List

from .base import Operator
from .prompts import GENERATE_PROMPT, GENERATE_COT_PROMPT, IDEA_FORMAT


class Generate(Operator):
    """Single-shot idea generation from the task (1 LLM call)."""

    is_producer = True

    def __init__(self, llm, name: str = "Generate"):
        super().__init__(llm, name)

    async def __call__(self, task: str, **_ignore) -> dict:
        prompt = GENERATE_PROMPT.format(task=task, idea_format=IDEA_FORMAT)
        return {"response": await self._ask(prompt)}


class GenerateCoT(Operator):
    """Chain-of-thought idea generation (1 LLM call).

    Surveys obvious approaches and gaps before committing to one idea. Per the
    paper's writing-stage emphasis on CoT, this is the reasoning-heavy producer.
    """

    is_producer = True

    def __init__(self, llm, name: str = "GenerateCoT"):
        super().__init__(llm, name)

    async def __call__(self, task: str, **_ignore) -> dict:
        prompt = GENERATE_COT_PROMPT.format(task=task, idea_format=IDEA_FORMAT)
        return {"response": await self._ask(prompt)}


class MultiGenerate(Operator):
    """N independent generations -> N lanes (default 3). Cost = N LLM calls.

    Returns {"response": [idea1, idea2, ...]}. The executor reads the list as
    parallel lanes that propagate downstream (the MaAS lane mechanism).
    """

    is_producer = True

    def __init__(self, llm, name: str = "MultiGenerate", n: int = 3):
        super().__init__(llm, name)
        self.n = n

    async def __call__(self, task: str, **_ignore) -> dict:
        prompt = GENERATE_COT_PROMPT.format(task=task, idea_format=IDEA_FORMAT)
        ideas: List[str] = []
        for _ in range(self.n):
            ideas.append(await self._ask(prompt))
        return {"response": ideas}
