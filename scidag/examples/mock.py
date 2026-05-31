"""Shared deterministic mock LLM responder for offline smoke tests.

Returns short, distinguishable canned text per operator, and well-formed
structured replies for Ensemble (a choice letter), Test (a JSON verdict), and
Review (a scored critique with `Score:` / `Verdict:` lines), so every operator's
parser exercises a real path without any network call.
"""
from __future__ import annotations


def mock_responder(prompt: str, system=None) -> str:
    p = prompt.lower()
    # Ensemble: pick a candidate letter
    if "selecting the single strongest" in p:
        return '{"thought": "A is sharpest", "solution_letter": "A"}'
    # Test: feasibility verdict as JSON
    if "stress-test a research idea" in p or '"verdict"' in p and "feasibility" in p:
        return '{"verdict": "pass", "risks": ["compute cost"]}'
    # Review: scored critique
    if "independent, rigorous peer reviewer" in p:
        return (
            "Novelty: 7/10 — fresh angle.\n"
            "Soundness: 6/10 — mechanism mostly holds.\n"
            "Feasibility: 8/10 — runnable.\n"
            "Clarity: 5/10 — approach is vague.\n"
            "Strengths: clear hypothesis.\n"
            "Weaknesses: approach under-specified.\n"
            "Concrete suggestions: spell out the steps.\n"
            "Score: 7/10\nVerdict: revise"
        )
    # Polish
    if "final, polished version" in p:
        return "Title: Polished idea\nHypothesis: H (sharpened).\nApproach: step 1, step 2.\nRisks: R."
    # Debate
    if "expert a" in p and "expert b" not in p:
        return "Title: Expert-A idea\nHypothesis: H.\nApproach: do X.\nRisks: R."
    if "expert b" in p or "final round of a debate" in p:
        return "Title: Expert-B idea\nHypothesis: H'.\nApproach: do Y.\nRisks: R."
    # Variation
    if "different line of attack" in p:
        return "Title: Variation idea\nHypothesis: alt.\nApproach: do Z.\nRisks: R."
    # Refine
    if "refine a research idea" in p:
        return "Title: Refined idea\nHypothesis: H (tighter).\nApproach: do X+.\nRisks: R."
    # Feasibility repair (Test repair round)
    if "blocking feasibility" in p:
        return "Title: Repaired idea\nHypothesis: H.\nApproach: do X (fixed).\nRisks: R."
    # Generators (Generate / GenerateCoT / MultiGenerate)
    return "Title: Generated idea\nHypothesis: base.\nApproach: do base.\nRisks: R."
