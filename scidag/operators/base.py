"""Operator base class + lightweight output parsing.

Replaces MaAS's `Operator` + ActionNode/pydantic machinery. Because SciDAG
artifacts are free-form research text (not code), most operators just return
the model's text. Only `ensemble` and `test` need to parse structured fields,
handled by the small helpers below (tolerant of markdown fences and reasoning
preambles, like the MaAS parsers were).
"""
from __future__ import annotations

import json
import re
from typing import List, Optional

from .prompts import RESEARCH_SYSTEM


class Operator:
    """Base operator. Holds the shared LLM client and a name.

    Subclasses implement `async def __call__(...)`. The constructor signature
    `(llm, name)` matches MaAS so the registry can build every operator the
    same way: `operator_mapping[name](llm)`.
    """

    #: operators that produce an artifact without reading parents (layer-0 only)
    is_producer = False
    #: operators never sampled as a node; used only for merge / final vote
    is_aggregator = False
    #: pure control signal, no LLM call
    is_control = False

    def __init__(self, llm, name: str):
        self.llm = llm
        self.name = name

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _ask(self, prompt: str, temperature: Optional[float] = None) -> str:
        return await self.llm.aask(prompt, system=RESEARCH_SYSTEM, temperature=temperature)


# ---------------- parsing helpers ----------------

def extract_letter(raw: str, valid: str) -> Optional[str]:
    """Pull a single choice letter (A, B, C, ...) from an ensemble response.

    Looks for an explicit `solution_letter` field first (JSON or `key: value`),
    then falls back to the first standalone valid letter. Returns None if none
    found, so the caller can default safely.
    """
    if not raw:
        return None
    valid_set = set(valid)
    # JSON-ish: "solution_letter": "B"
    m = re.search(r'"?solution_letter"?\s*[:=]\s*"?([A-Za-z])"?', raw)
    if m and m.group(1).upper() in valid_set:
        return m.group(1).upper()
    # last resort: first standalone valid letter
    for ch in re.findall(r"\b([A-Za-z])\b", raw):
        if ch.upper() in valid_set:
            return ch.upper()
    return None


def extract_json_object(raw: str) -> Optional[dict]:
    """Grab the outermost {...} and json-load it; tolerant of fences/prose."""
    if not raw:
        return None
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def normalize_risks(risks) -> List[str]:
    if isinstance(risks, list):
        return [str(r).strip() for r in risks if str(r).strip()]
    if isinstance(risks, str) and risks.strip():
        return [risks.strip()]
    return []


def extract_score(raw: str, lo: float = 1, hi: float = 10) -> Optional[float]:
    """Pull an overall review score from a review response.

    Looks for `Score: N/10` first, then a bare `Score: N`. Returns None if no
    in-range number is found, so the caller can treat the score as unknown.
    """
    if not raw:
        return None
    for pat in (r"score\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10",
                r"score\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)"):
        m = re.search(pat, raw, re.IGNORECASE)
        if m:
            try:
                v = float(m.group(1))
            except ValueError:
                continue
            if lo <= v <= hi:
                return v
    return None


def extract_verdict(raw: str) -> Optional[str]:
    """Pull a review verdict (accept / revise / reject) from a review response."""
    if not raw:
        return None
    m = re.search(r"verdict\s*[:=]?\s*(accept|revise|reject)", raw, re.IGNORECASE)
    return m.group(1).lower() if m else None
