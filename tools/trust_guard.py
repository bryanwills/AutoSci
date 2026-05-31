#!/usr/bin/env python3
"""Trust Guard — gate SciMem writes with a PASS/WARN/BLOCK verdict.

Form validity is deterministic and reuses tools/lint.py. Content validity is an
independent Review-LLM check (tools/trust_content_review.py), injectable for tests.
(Quarantine, event logging, and CLI are added in a later task.)
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import lint
import trust_content_review

PASS, WARN, BLOCK = "PASS", "WARN", "BLOCK"
_RANK = {PASS: 0, WARN: 1, BLOCK: 2}
_LEVEL_TO_STATUS = {"🔴": BLOCK, "🟡": WARN, "🔵": PASS}


@dataclass
class TrustCheck:
    name: str
    status: str
    message: str


@dataclass
class TrustVerdict:
    artifact: str
    status: str
    checks: list[TrustCheck] = field(default_factory=list)

    def to_event(self) -> dict:
        return {
            "artifact": self.artifact,
            "status": self.status,
            "checks": [{"name": c.name, "status": c.status, "message": c.message} for c in self.checks],
        }


def overall_status(checks: list[TrustCheck]) -> str:
    worst = PASS
    for c in checks:
        if _RANK[c.status] > _RANK[worst]:
            worst = c.status
    return worst


def _mk_content_verdict(status: str, message: str):
    """Thin factory for trust_content_review.ContentVerdict (test convenience)."""
    return trust_content_review.ContentVerdict(status=status, message=message, raw=None)


def run_form_checks(wiki_dir: Path, artifact_rel: str) -> list[TrustCheck]:
    """Run deterministic lint over the wiki and keep only issues for `artifact_rel`."""
    issues = [i for i in lint.lint(Path(wiki_dir)) if i.file == artifact_rel]
    if not issues:
        return [TrustCheck("form:pass", PASS, "no deterministic form issues")]
    checks: list[TrustCheck] = []
    for i in issues:
        status = _LEVEL_TO_STATUS.get(i.level, WARN)
        checks.append(TrustCheck(f"form:{i.category}", status, i.message))
    return checks


def _artifact_rel(wiki_dir: Path, artifact_path: Path) -> str:
    try:
        return str(Path(artifact_path).resolve().relative_to(Path(wiki_dir).resolve()))
    except ValueError:
        return str(artifact_path)


def check(wiki_dir: Path, artifact_path: Path, *,
          content_reviewer: Callable[[str, dict], trust_content_review.ContentVerdict | None] | None = None) -> TrustVerdict:
    """Produce a TrustVerdict. `content_reviewer` is a callable
    (text, context) -> ContentVerdict|None; defaults to the real Review-LLM."""
    if content_reviewer is None:
        content_reviewer = lambda text, context: trust_content_review.review_artifact(text, context=context)

    wiki_dir = Path(wiki_dir)
    artifact_path = Path(artifact_path)
    rel = _artifact_rel(wiki_dir, artifact_path)

    if not artifact_path.exists():
        checks = [TrustCheck("form:missing-file", BLOCK, f"{rel} does not exist")]
        return TrustVerdict(artifact=rel, status=overall_status(checks), checks=checks)

    checks = run_form_checks(wiki_dir, rel)

    text = artifact_path.read_text(encoding="utf-8")
    cv = content_reviewer(text, {"neighbors": []})
    if cv is None:
        checks.append(TrustCheck("content:review", PASS, "content-check skipped (Review LLM not configured)"))
    else:
        checks.append(TrustCheck("content:review", cv.status, cv.message))

    return TrustVerdict(artifact=rel, status=overall_status(checks), checks=checks)
