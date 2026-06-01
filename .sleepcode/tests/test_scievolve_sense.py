#!/usr/bin/env python3
"""Tests for automatic SciEvolve signal sensing."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "research_wiki.py"


class SciEvolveSenseTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_empty_input_writes_no_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            result = self.run_tool("scievolve-sense", str(wiki), "--json")
            data = json.loads(result.stdout)
            self.assertEqual(data["sensed_events"], 0)
            self.assertEqual(data["signals_written"], 0)
            self.assertFalse((wiki / "outputs" / "evolution" / "signals.jsonl").exists())

    def test_failed_entity_sensing_is_deduped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            idea = wiki / "ideas" / "dead-end.md"
            idea.parent.mkdir(parents=True)
            idea.write_text(
                """---
title: Dead End
status: failed
failure_reason: Pilot contradicted the premise.
---

Body.
""",
                encoding="utf-8",
            )

            first = json.loads(self.run_tool("scievolve-sense", str(wiki), "--json").stdout)
            second = json.loads(self.run_tool("scievolve-sense", str(wiki), "--json").stdout)

            self.assertEqual(first["sensed_events"], 1)
            self.assertEqual(first["signals_written"], 1)
            self.assertEqual(second["sensed_events"], 1)
            self.assertEqual(second["signals_written"], 0)
            self.assertEqual(second["signals_skipped"], 1)

            signals = [
                json.loads(line)
                for line in (wiki / "outputs" / "evolution" / "signals.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(signals), 1)
            self.assertEqual(signals[0]["dimension"], "memory")
            self.assertEqual(signals[0]["target"], "ideas/dead-end")
            self.assertIn("dedupe_key", signals[0])

    def test_log_and_apply_skip_sensing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir(parents=True)
            (wiki / "log.md").write_text(
                "- /discover failed with timeout while fetching S2.\n",
                encoding="utf-8",
            )
            report = wiki / "outputs" / "evolution" / "forge" / "run-1" / "forge_apply_report.json"
            report.parent.mkdir(parents=True)
            report.write_text(
                json.dumps({
                    "skipped": [
                        {"proposal_id": "prop-1", "reason": "line_hint matched multiple locations"}
                    ]
                }),
                encoding="utf-8",
            )

            data = json.loads(self.run_tool("scievolve-sense", str(wiki), "--json").stdout)

            self.assertEqual(data["signals_written"], 2)
            signals = [
                json.loads(line)
                for line in (wiki / "outputs" / "evolution" / "signals.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            targets = sorted(signal["target"] for signal in signals)
            self.assertEqual(targets, ["discover", "forge"])
            self.assertTrue(all(signal["dimension"] == "workflow" for signal in signals))


if __name__ == "__main__":
    unittest.main()
