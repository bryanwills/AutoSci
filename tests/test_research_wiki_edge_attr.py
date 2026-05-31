#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT))

from runtime import loader  # noqa: E402

_spec = importlib.util.spec_from_file_location("research_wiki", TOOLS / "research_wiki.py")
assert _spec and _spec.loader
rw = importlib.util.module_from_spec(_spec)
sys.modules["research_wiki"] = rw
_spec.loader.exec_module(rw)

STRUCTURED = ("source_path", "source_span", "metric_name", "metric_value", "artifact_hash")
EVIDENCE_EDGES = ("supports", "contradicts", "tested_by", "invalidates")


def _wiki() -> Path:
    d = Path(tempfile.mkdtemp())
    for sub in ("graph", "ideas", "experiments"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "ideas" / "i-val.md").write_text(
        "---\nslug: i-val\ntitle: V\nstatus: validated\norigin: x\ntags: []\norigin_gaps: []\n---\n# i-val\n",
        encoding="utf-8")
    (d / "experiments" / "e1.md").write_text(
        "---\nslug: e1\ntitle: E\nstatus: completed\noutcome: succeeded\nkey_result: r\n"
        "linked_idea: i-val\nhypothesis: h\ntags: []\n---\n# e1\n", encoding="utf-8")
    return d


class TestSchema(unittest.TestCase):
    def test_evidence_edges_declare_structured_attrs(self):
        for et in EVIDENCE_EDGES:
            attrs = loader.EDGES[et]["attributes"]
            for a in STRUCTURED:
                self.assertIn(a, attrs, f"{et} missing {a}")
                self.assertEqual(attrs[a]["type"], "str")

    def test_validate_edge_attributes_accepts_structured(self):
        errs = loader.validate_edge_attributes(
            "tested_by", {"metric_value": "94.2 ± 0.3", "source_path": "results/e1/metrics.json"})
        self.assertEqual(errs, [])


class TestAddEdgeAttr(unittest.TestCase):
    def test_add_edge_writes_attrs(self):
        d = _wiki()
        rw.add_edge(str(d), "ideas/i-val", "experiments/e1", "tested_by",
                    evidence="exp tested it",
                    attrs={"metric_value": "94.2 ± 0.3",
                           "source_path": "results/e1/metrics.json"})
        edges = rw.load_edges(str(d))
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["metric_value"], "94.2 ± 0.3")
        self.assertEqual(edges[0]["source_path"], "results/e1/metrics.json")

    def test_unknown_attr_key_errors(self):
        d = _wiki()
        with self.assertRaises(SystemExit):
            rw.add_edge(str(d), "ideas/i-val", "experiments/e1", "tested_by",
                        attrs={"bogus": "x"})


if __name__ == "__main__":
    unittest.main()
