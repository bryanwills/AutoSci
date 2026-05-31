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
    (d / "graph").mkdir(parents=True, exist_ok=True)
    (d / "ideas").mkdir(exist_ok=True)
    (d / "methods").mkdir(exist_ok=True)
    (d / "experiments").mkdir(exist_ok=True)
    (d / "ideas" / "i1.md").write_text(
        "---\nslug: i1\ntitle: Idea One\nstatus: in_progress\norigin: x\ntags: []\n"
        "linked_experiments: [e1]\n---\n# i1\n", encoding="utf-8")
    (d / "methods" / "m1.md").write_text(
        "---\nslug: m1\nname: Method One\ntype: other\ntags: []\n---\n# m1\n", encoding="utf-8")
    (d / "experiments" / "e1.md").write_text(
        "---\nslug: e1\ntitle: Exp One\nstatus: completed\noutcome: succeeded\n"
        "linked_idea: i1\nhypothesis: h\ntags: []\n---\n# e1\n", encoding="utf-8")
    (d / "graph" / "edges.jsonl").write_text(
        '{"from": "ideas/i1", "to": "methods/m1", "type": "applies_method"}\n', encoding="utf-8")
    return d


class GraphNeighborsTests(unittest.TestCase):
    def test_explicit_edge_only(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ids = {n["id"] for n in rw.graph_neighbors(str(d), "ideas/i1", depth=1, include_projected=False)}
        self.assertIn("methods/m1", ids)
        self.assertNotIn("experiments/e1", ids)

    def test_includes_projected_frontmatter_edge(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        ids = {n["id"] for n in rw.graph_neighbors(str(d), "ideas/i1", depth=1, include_projected=True)}
        self.assertIn("methods/m1", ids)
        self.assertIn("experiments/e1", ids)  # ideas.linked_experiments projected

    def test_returns_list_not_none(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        out = rw.graph_neighbors(str(d), "ideas/nonexistent", depth=2, include_projected=True)
        self.assertEqual(out, [])

    def test_neighbors_cli_unchanged(self) -> None:
        d = _wiki()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        r = subprocess.run([sys.executable, str(TOOLS / "research_wiki.py"), "neighbors",
                            str(d), "ideas/i1", "--depth", "1"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        payload = json.loads(r.stdout)
        ids = {n["id"] for n in payload["nodes"]}
        self.assertIn("methods/m1", ids)
        self.assertNotIn("experiments/e1", ids)  # CLI keeps include_projected=False


if __name__ == "__main__":
    unittest.main()
