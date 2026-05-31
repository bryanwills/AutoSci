"""Polish operator — review-guided final editing. 1 LLM call.

The paper's `polish` operator: "improve presentation, wording, formatting, or
local organization according to review feedback." Polish edits expression, not
substance: it tightens wording and structure and addresses presentational
review suggestions, while preserving the hypothesis, approach, and risks.

Polish is the consumer half of the review→polish pair. If its input idea carries
a "## Review feedback" block (from an upstream Review node), Polish acts on the
actionable parts of that feedback and strips the block from its output; if not,
it simply produces a clean, well-organized version of the idea.

Signature (task, idea) -> {"response": str}, slot-compatible with the other
consumers in the DAG executor.
"""
from __future__ import annotations

from .base import Operator
from .prompts import POLISH_PROMPT, IDEA_FORMAT


class Polish(Operator):
    def __init__(self, llm, name: str = "Polish"):
        super().__init__(llm, name)

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        if not idea or not idea.strip():
            return {"response": idea}
        prompt = POLISH_PROMPT.format(task=task, idea=idea, idea_format=IDEA_FORMAT)
        return {"response": await self._ask(prompt)}
