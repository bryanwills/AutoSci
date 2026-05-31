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

spec = importlib.util.spec_from_file_location("research_wiki", TOOLS / "research_wiki.py")
assert spec and spec.loader
research_wiki = importlib.util.module_from_spec(spec)
sys.modules["research_wiki"] = research_wiki
spec.loader.exec_module(research_wiki)


class AppendEventTests(unittest.TestCase):
    def _wiki(self) -> Path:
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "graph").mkdir(parents=True, exist_ok=True)
        return d

    def test_append_event_writes_jsonl_line_with_ts(self) -> None:
        wiki = self._wiki()
        research_wiki.append_event(str(wiki), "trust_events", {"artifact": "papers/foo.md", "status": "PASS"})
        path = wiki / "graph" / "trust_events.jsonl"
        self.assertTrue(path.exists())
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["artifact"], "papers/foo.md")
        self.assertEqual(rows[0]["status"], "PASS")
        self.assertIn("ts", rows[0])

    def test_append_event_appends_not_overwrites(self) -> None:
        wiki = self._wiki()
        research_wiki.append_event(str(wiki), "trust_events", {"n": 1})
        research_wiki.append_event(str(wiki), "trust_events", {"n": 2})
        rows = [json.loads(line) for line in (wiki / "graph" / "trust_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual([r["n"] for r in rows], [1, 2])

    def test_append_event_rejects_unknown_stream(self) -> None:
        wiki = self._wiki()
        with self.assertRaises(ValueError):
            research_wiki.append_event(str(wiki), "random_stream", {"x": 1})

    def test_append_event_preserves_caller_ts(self) -> None:
        wiki = self._wiki()
        research_wiki.append_event(str(wiki), "trust_events", {"n": 1, "ts": "2020-01-01T00:00:00+00:00"})
        rows = [json.loads(line) for line in (wiki / "graph" / "trust_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(rows[0]["ts"], "2020-01-01T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
