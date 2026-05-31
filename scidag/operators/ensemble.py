"""Ensemble operator (self-consistency vote / synthesis). 1 LLM call.

Ported from MaAS ScEnsemble. Given several candidate ideas, pick the strongest
one. Used as the multi-parent merge vote and the final leaf vote inside the
executor (the paper's `ensemble` operator: "vote over / aggregate multiple
candidate ideas into one"). Position-bias is mitigated by shuffling candidates
before showing them, then mapping the chosen letter back to the original index.

Marked is_aggregator: it is never sampled as a DAG node by a controller; the
executor invokes it directly for merges / final vote.
"""
from __future__ import annotations

import random
from typing import List

from .base import Operator, extract_letter
from .prompts import SC_ENSEMBLE_PROMPT


class Ensemble(Operator):
    is_aggregator = True

    def __init__(self, llm, name: str = "Ensemble"):
        super().__init__(llm, name)

    async def __call__(self, task: str, solutions: List[str], **_ignore) -> dict:
        solutions = [s for s in (solutions or []) if s and s.strip()]
        if not solutions:
            return {"response": ""}
        if len(solutions) == 1:
            return {"response": solutions[0]}

        # shuffle to mitigate position bias; map letter -> original index
        n = len(solutions)
        perm = list(range(n))
        random.shuffle(perm)
        valid = "".join(chr(65 + i) for i in range(n))
        block = ""
        mapping = {}
        for shuf_idx, orig_idx in enumerate(perm):
            letter = chr(65 + shuf_idx)
            mapping[letter] = orig_idx
            block += f"{letter}:\n{solutions[orig_idx]}\n\n\n"

        prompt = SC_ENSEMBLE_PROMPT.format(task=task, solutions=block)
        raw = await self._ask(prompt)
        letter = extract_letter(raw, valid) or "A"
        return {"response": solutions[mapping.get(letter, perm[0])]}
