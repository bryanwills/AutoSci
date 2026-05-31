#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("wiki_events", TOOLS / "wiki_events.py")
assert spec and spec.loader
we = importlib.util.module_from_spec(spec)
sys.modules["wiki_events"] = we
spec.loader.exec_module(we)


class WikiEventsTests(unittest.TestCase):
    def _wiki(self) -> Path:
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_writes_jsonl_line_with_ts(self) -> None:
        wiki = self._wiki()
        we.append_event(str(wiki), "pipeline_events", {"kind": "gate", "decision": "PASS"})
        rows = [json.loads(line) for line in (wiki / "graph" / "pipeline_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "gate")
        self.assertIn("ts", rows[0])

    def test_appends_not_overwrites(self) -> None:
        wiki = self._wiki()
        we.append_event(str(wiki), "pipeline_events", {"n": 1})
        we.append_event(str(wiki), "pipeline_events", {"n": 2})
        rows = [json.loads(line) for line in (wiki / "graph" / "pipeline_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual([r["n"] for r in rows], [1, 2])

    def test_rejects_unknown_stream(self) -> None:
        with self.assertRaises(ValueError):
            we.append_event(str(self._wiki()), "random_stream", {"x": 1})

    def test_preserves_caller_ts(self) -> None:
        wiki = self._wiki()
        we.append_event(str(wiki), "trust_events", {"n": 1, "ts": "2020-01-01T00:00:00+00:00"})
        rows = [json.loads(line) for line in (wiki / "graph" / "trust_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(rows[0]["ts"], "2020-01-01T00:00:00+00:00")

    def test_accepts_pipeline_feedback_stream(self) -> None:
        wiki = self._wiki()
        we.append_event(str(wiki), "pipeline_feedback",
                        {"kind": "feedback", "category": "evidence_gap", "action": "manual_gate"})
        rows = [json.loads(line) for line in (wiki / "graph" / "pipeline_feedback.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(rows[0]["category"], "evidence_gap")


if __name__ == "__main__":
    unittest.main()
