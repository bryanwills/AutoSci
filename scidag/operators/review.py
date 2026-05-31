"""Review operator — structured critique before final editing. 1 LLM call.

The paper's `review` operator: "critique a candidate before final editing,
focusing on correctness, evidence support, and coherence." Unlike Refine/Debate,
Review does NOT rewrite the idea — it produces an independent, scored critique
(novelty / soundness / feasibility / clarity + strengths / weaknesses /
suggestions + an overall score and verdict).

To fit the single-input DAG executor and pair naturally with Polish, Review
bundles its output: `response` = the original idea with a "## Review feedback"
block appended. A downstream Polish node then reads idea+feedback and applies it.
The parsed `score` / `verdict` are also returned for skills / a future router.

This is the AutoSci analogue of the cross-model `/review` skill; when wired into
SciFlow it can run on the llm-review endpoint for an independent second opinion.

Signature (task, idea) -> {"response": str, "review": str, "score": float|None,
"verdict": str|None}. The executor takes `response`.
"""
from __future__ import annotations

from .base import Operator, extract_score, extract_verdict
from .prompts import REVIEW_PROMPT


class Review(Operator):
    def __init__(self, llm, name: str = "Review"):
        super().__init__(llm, name)

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        if not idea or not idea.strip():
            return {"response": idea, "review": "", "score": None, "verdict": None}

        critique = await self._ask(REVIEW_PROMPT.format(task=task, idea=idea))
        bundled = f"{idea}\n\n## Review feedback\n{critique}"
        return {
            "response": bundled,
            "review": critique,
            "score": extract_score(critique),
            "verdict": extract_verdict(critique),
        }
