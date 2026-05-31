#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime import loader  # noqa: E402


def _ok_fm() -> dict:
    return {
        "slug": "p1", "direction": "d", "status": "running",
        "current_stage": "stage1", "started": "2026-05-31", "mode": "interactive",
        "idea_slug": "", "experiment_slugs": [], "linked_idea_slugs": [],
    }


def _ok_log() -> dict:
    return {"stage0": "skipped", "stage1": "pending", "gate1": "pending",
            "stage2": "pending", "stage3a": "pending", "stage3b": "pending",
            "stage3c": "pending", "stage4": "pending", "gate2": "pending", "stage5": "pending"}


def _sevs(issues):
    return [s for s, _ in issues]


class ValidatePipelineTests(unittest.TestCase):
    def test_clean_initial_snapshot_passes(self) -> None:
        self.assertEqual(loader.validate_pipeline(_ok_fm(), _ok_log()), [])

    def test_missing_required_field_blocks(self) -> None:
        fm = _ok_fm(); del fm["direction"]
        issues = loader.validate_pipeline(fm, _ok_log())
        self.assertIn("BLOCK", _sevs(issues))
        self.assertTrue(any("direction" in m for _, m in issues))

    def test_bad_enum_blocks(self) -> None:
        fm = _ok_fm(); fm["current_stage"] = "stage9"
        issues = loader.validate_pipeline(fm, _ok_log())
        self.assertTrue(any(s == "BLOCK" and "current_stage" in m for s, m in issues))

    def test_bad_stage_log_state_blocks(self) -> None:
        log = _ok_log(); log["stage1"] = "frobnicated"
        issues = loader.validate_pipeline(_ok_fm(), log)
        self.assertTrue(any(s == "BLOCK" and "stage1" in m for s, m in issues))

    def test_monotonicity_violation_blocks(self) -> None:
        log = _ok_log(); log["stage5"] = "completed"
        issues = loader.validate_pipeline(_ok_fm(), log)
        self.assertTrue(any(s == "BLOCK" and "completed" in m for s, m in issues))

    def test_current_stage_coherence_blocks(self) -> None:
        fm = _ok_fm(); fm["current_stage"] = "stage4"
        issues = loader.validate_pipeline(fm, _ok_log())
        self.assertTrue(any(s == "BLOCK" and "stage2" in m for s, m in issues))

    def test_cross_entity_dangling_idea_blocks(self) -> None:
        fm = _ok_fm(); fm["idea_slug"] = "ghost"
        issues = loader.validate_pipeline(fm, _ok_log(), entity_status=lambda k, s: None)
        self.assertTrue(any(s == "BLOCK" and "ghost" in m for s, m in issues))

    def test_stage4_with_running_experiment_blocks(self) -> None:
        fm = _ok_fm()
        fm["current_stage"] = "stage4"
        fm["experiment_slugs"] = ["e1"]
        fm["idea_slug"] = "i1"
        log = _ok_log()
        for k in ("stage1", "gate1", "stage2", "stage3a", "stage3b", "stage3c"):
            log[k] = "completed"
        log["stage4"] = "running"

        def status(kind, slug):
            return {"experiments:e1": "running", "ideas:i1": "tested"}.get(f"{kind}:{slug}")

        issues = loader.validate_pipeline(fm, log, entity_status=status)
        self.assertTrue(any(s == "BLOCK" and "e1" in m and "running" in m for s, m in issues))

    def test_stage5_completed_requires_status_completed(self) -> None:
        fm = _ok_fm(); fm["current_stage"] = "stage5"; fm["status"] = "running"
        log = _ok_log()
        for k in ("stage1", "gate1", "stage2", "stage3a", "stage3b", "stage3c", "stage4", "gate2"):
            log[k] = "completed"
        log["stage5"] = "completed"
        issues = loader.validate_pipeline(fm, log)
        self.assertTrue(any(s == "BLOCK" and "status" in m for s, m in issues))

    def test_stale_running_snapshot_warns(self) -> None:
        fm = _ok_fm(); fm["status"] = "running"
        log = _ok_log()
        for line in loader.pipeline_stage_log_lines():
            log[line["key"]] = "completed"
        issues = loader.validate_pipeline(fm, log)
        self.assertIn("WARN", _sevs(issues))

    def test_dangling_linked_idea_blocks(self) -> None:
        fm = _ok_fm(); fm["linked_idea_slugs"] = ["ghostlink"]
        issues = loader.validate_pipeline(fm, _ok_log(), entity_status=lambda k, s: None)
        self.assertTrue(any(s == "BLOCK" and "ghostlink" in m for s, m in issues))

    def test_current_stage_later_line_not_pending_blocks(self) -> None:
        log = _ok_log(); log["stage4"] = "running"  # later stage not pending while current_stage=stage1
        issues = loader.validate_pipeline(_ok_fm(), log)
        self.assertTrue(any(s == "BLOCK" and "stage4" in m and "later" in m for s, m in issues))

    def test_stage3_await_snapshot_passes(self) -> None:
        # the real /research Stage-3b await state: experiments running, idea in_progress
        fm = _ok_fm()
        fm["current_stage"] = "stage3-await"
        fm["experiment_slugs"] = ["e1"]
        fm["idea_slug"] = "i1"
        log = _ok_log()
        for k in ("stage1", "gate1", "stage2", "stage3a"):
            log[k] = "completed"
        log["stage3b"] = "running"

        def status(kind, slug):
            return {"experiments:e1": "running", "ideas:i1": "in_progress"}.get(f"{kind}:{slug}")

        self.assertEqual(loader.validate_pipeline(fm, log, entity_status=status), [])

    def test_at_verdict_via_stage4_completed_path(self) -> None:
        fm = _ok_fm(); fm["current_stage"] = "stage3"; fm["experiment_slugs"] = ["e1"]
        log = _ok_log()
        for k in ("stage1", "gate1", "stage2", "stage3a", "stage3b", "stage3c"):
            log[k] = "completed"
        log["stage4"] = "completed"

        def status(kind, slug):
            return {"experiments:e1": "planned"}.get(f"{kind}:{slug}")

        issues = loader.validate_pipeline(fm, log, entity_status=status)
        self.assertTrue(any(s == "BLOCK" and "e1" in m and "planned" in m for s, m in issues))


if __name__ == "__main__":
    unittest.main()
