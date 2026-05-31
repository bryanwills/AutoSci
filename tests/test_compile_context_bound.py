#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("research_wiki", TOOLS / "research_wiki.py")
assert spec and spec.loader
rw = importlib.util.module_from_spec(spec)
sys.modules["research_wiki"] = rw
spec.loader.exec_module(rw)


def _wiki() -> Path:
    d = Path(tempfile.mkdtemp())
    for sub in ("graph", "ideas", "experiments", "methods", "papers"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "ideas" / "i1.md").write_text(
        "---\nslug: i1\ntitle: Idea One\nstatus: in_progress\norigin: x\ntags: []\n"
        "linked_experiments: [e1, e2]\n---\n# i1\n", encoding="utf-8")
    (d / "experiments" / "e1.md").write_text(
        "---\nslug: e1\ntitle: Exp One\nstatus: completed\noutcome: succeeded\n"
        "linked_idea: i1\nhypothesis: h\ntags: []\n---\n# e1\n", encoding="utf-8")
    (d / "experiments" / "e2.md").write_text(
        "---\nslug: e2\ntitle: Exp Two\nstatus: completed\noutcome: failed\n"
        "linked_idea: i1\nhypothesis: h\ntags: []\nkey_result: regressed\n---\n# e2\n", encoding="utf-8")
    return d


def _run(*args):
    return subprocess.run([sys.executable, str(TOOLS / "research_wiki.py"), "compile-context", *args],
                          capture_output=True, text=True)


class CompileContextBoundTests(unittest.TestCase):
    def test_stage_resolves_purpose(self) -> None:
        self.assertEqual(rw.STAGE_PURPOSE["stage5"], "writing")
        self.assertEqual(rw.STAGE_PURPOSE["stage1"], "ideation")

    def test_entity_pack_written_with_focus_and_neighbors(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _run(str(d), "--entity", "ideas/i1", "--include-neighbors-depth", "1")
        self.assertEqual(r.returncode, 0)
        status = json.loads(r.stdout)
        self.assertEqual(status["entity"], "ideas/i1")
        pack = (d / "graph" / "context_pack.md").read_text(encoding="utf-8")
        self.assertIn("## Focus: ideas/i1", pack)
        self.assertIn("### Graph neighborhood", pack)
        self.assertIn("experiments/e1", pack)
        self.assertIn("Related prior failures", pack)
        self.assertIn("e2", pack)
        self.assertFalse((d / "graph" / "context_brief.md").exists())

    def test_entity_emits_context_event(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _run(str(d), "--entity", "ideas/i1")
        events = d / "graph" / "pipeline_events.jsonl"
        self.assertTrue(events.exists())
        rows = [json.loads(line) for line in events.read_text(encoding="utf-8").splitlines() if line.strip()]
        ctx = [row for row in rows if row.get("kind") == "context"]
        self.assertTrue(ctx)
        self.assertEqual(ctx[0]["entity"], "ideas/i1")

    def test_unbound_for_backward_compat(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _run(str(d), "--for", "review")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["purpose"], "review")
        self.assertTrue((d / "graph" / "context_brief.md").exists())
        self.assertFalse((d / "graph" / "context_pack.md").exists())
        self.assertFalse((d / "graph" / "pipeline_events.jsonl").exists())

    def test_stage_flag_sets_purpose(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _run(str(d), "--stage", "stage5")
        self.assertEqual(json.loads(r.stdout)["purpose"], "writing")

    def test_entity_and_stage_combined(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _run(str(d), "--entity", "ideas/i1", "--stage", "stage3")
        self.assertEqual(r.returncode, 0)
        status = json.loads(r.stdout)
        self.assertEqual(status["entity"], "ideas/i1")
        self.assertEqual(status["stage"], "stage3")
        self.assertEqual(status["purpose"], "experiment")
        rows = [json.loads(line) for line in (d / "graph" / "pipeline_events.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        ctx = [row for row in rows if row.get("kind") == "context"]
        self.assertEqual(ctx[0]["stage"], "stage3")
        self.assertEqual(ctx[0]["purpose"], "experiment")

    def test_bare_entity_rejected(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = _run(str(d), "--entity", "ideas")  # no slash
        self.assertEqual(r.returncode, 2)

    def test_failures_appear_before_neighborhood(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _run(str(d), "--entity", "ideas/i1")
        pack = (d / "graph" / "context_pack.md").read_text(encoding="utf-8")
        self.assertIn("Related prior failures", pack)
        self.assertIn("Graph neighborhood", pack)
        self.assertLess(pack.index("Related prior failures"), pack.index("Graph neighborhood"))


if __name__ == "__main__":
    unittest.main()
