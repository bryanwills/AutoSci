#!/usr/bin/env python3
"""Tests for SciEvolve recurring pattern detection."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "research_wiki.py"
sys.path.insert(0, str(REPO))

from tools import research_wiki


class SciEvolvePatternTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )

    def record_signal(self, wiki: Path, *, dimension: str, target: str, severity: str) -> str:
        result = self.run_tool(
            "scievolve-record-signal",
            str(wiki),
            "--source", "task",
            "--dimension", dimension,
            "--target", target,
            "--kind", "failure",
            "--summary", f"{target} failed with {severity} severity",
            "--severity", severity,
            "--confidence", "high",
        )
        return json.loads(result.stdout)["signal_id"]

    def test_medium_threshold_patterns_enter_dream_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            self.run_tool("init", str(wiki))
            for idx in range(3):
                self.record_signal(
                    wiki,
                    dimension="memory",
                    target="concepts/cache",
                    severity="medium",
                )
            result = json.loads(self.run_tool("dream", str(wiki), "--json").stdout)
            context = json.loads(Path(result["context_path"]).read_text(encoding="utf-8"))

            self.assertEqual(context["stats"]["recurring_patterns"], 1)
            pattern = context["recurring_patterns"][0]
            self.assertEqual(pattern["target"], "concepts/cache")
            self.assertEqual(pattern["medium_plus_count"], 3)

    def test_high_threshold_patterns_enter_forge_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            for idx in range(2):
                self.record_signal(
                    wiki,
                    dimension="workflow",
                    target="discover",
                    severity="high",
                )
            result = json.loads(self.run_tool("forge", str(wiki), "--json").stdout)
            context = json.loads(Path(result["context_path"]).read_text(encoding="utf-8"))

            self.assertEqual(context["stats"]["recurring_patterns"], 1)
            pattern = context["recurring_patterns"][0]
            self.assertEqual(pattern["target"], "discover")
            self.assertEqual(pattern["high_plus_count"], 2)

    def test_time_window_filters_old_signals(self) -> None:
        now = datetime.now(timezone.utc)
        old = (now - timedelta(days=45)).isoformat().replace("+00:00", "Z")
        recent = now.isoformat().replace("+00:00", "Z")
        signals = [
            {
                "id": f"sig-{idx}",
                "timestamp": old if idx == 0 else recent,
                "dimension": "workflow",
                "target": "discover",
                "kind": "failure",
                "severity": "medium",
            }
            for idx in range(3)
        ]

        patterns = research_wiki._scievolve_recurring_patterns(
            signals,
            dimension="workflow",
            window_days=30,
        )

        self.assertEqual(patterns, [])


if __name__ == "__main__":
    unittest.main()
