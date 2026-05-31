"""Test operator — feasibility / logic stress check (oracle-free). 1 (+<=1 repair) LLM call.

Adapted from MaAS's oracle-free structural Test. MaAS ran candidate *code* in a
subprocess and checked it didn't crash. SciDAG artifacts are research ideas, not
runnable code, so the structural check becomes a **feasibility / internal-logic
check**: the LLM enumerates the idea's most serious feasibility or logic risks
and returns a pass/fail verdict. If it fails (a blocking risk), exactly ONE
repair round revises the idea. Like MaAS, there is no ground-truth oracle — the
check judges only the idea's own coherence and practicality.

Signature (task, idea) -> {"result": bool, "solution": str, "risks": [str]}.
The executor takes `solution` as this node's output (revised idea if repaired,
else the original), matching how MaAS's Test fed `solution` downstream.

Named test_op.py (not test.py) so pytest does not collect it as a test module.
"""
from __future__ import annotations

from typing import List

from .base import Operator, extract_json_object, normalize_risks
from .prompts import FEASIBILITY_CHECK_PROMPT, FEASIBILITY_REPAIR_PROMPT, IDEA_FORMAT


class Test(Operator):
    def __init__(self, llm, name: str = "Test"):
        super().__init__(llm, name)

    async def _check(self, task: str, idea: str) -> tuple[bool, List[str]]:
        """Return (passed, risks). Degrades to pass if the verdict is unparseable."""
        prompt = FEASIBILITY_CHECK_PROMPT.format(task=task, idea=idea, n_lo=2, n_hi=4)
        try:
            raw = await self.llm.aask(prompt, stream=False)
        except Exception:
            return True, []  # cannot check -> treat as structurally fine (MaAS behavior)
        obj = extract_json_object(raw)
        if not obj:
            return True, []
        verdict = str(obj.get("verdict", "pass")).strip().lower()
        risks = normalize_risks(obj.get("risks"))
        return (verdict != "fail"), risks

    async def __call__(self, task: str, idea: str, **_ignore) -> dict:
        if not idea or not idea.strip():
            return {"result": False, "solution": idea, "risks": []}

        passed, risks = await self._check(task, idea)
        if passed:
            return {"result": True, "solution": idea, "risks": risks}

        # exactly one repair round, driven by the blocking risks
        prompt = FEASIBILITY_REPAIR_PROMPT.format(
            task=task, idea=idea, risks="\n".join(f"- {r}" for r in risks),
            idea_format=IDEA_FORMAT,
        )
        revised = await self._ask(prompt)
        revised = revised or idea
        passed_after, _ = await self._check(task, revised)
        return {"result": passed_after, "solution": revised, "risks": risks}
