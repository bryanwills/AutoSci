#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
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


def _wiki() -> Path:
    d = Path(tempfile.mkdtemp())
    for sub in ("graph", "reviews", "manuscripts", "ideas", "methods"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "manuscripts" / "m1.md").write_text(
        "---\nslug: m1\ntitle: M\nstatus: drafting\ntags: []\n---\n# m1\n", encoding="utf-8")
    (d / "ideas" / "my-idea.md").write_text(
        "---\nslug: my-idea\ntitle: I\nstatus: validated\norigin: x\ntags: []\norigin_gaps: []\n---\n# my-idea\n",
        encoding="utf-8")
    (d / "methods" / "my-method.md").write_text(
        "---\nslug: my-method\nname: My Method\ntype: other\ntags: []\nparent_topics: []\n---\n# my-method\n",
        encoding="utf-8")
    (d / "reviews" / "m1-review-1.md").write_text(
        "---\ntitle: R1\nslug: m1-review-1\nfeedback_type: feedback\nresolution_status: open\n"
        "linked_manuscript: m1\nconcerns:\n"
        "  - id: Rv1-C1\n    slug: my-idea\n    source: Reviewer 1\n    severity: major\n"
        "    evidence_status: unchecked\n    response_status: open\n"
        "  - id: Rv1-C2\n    slug: my-method\n    source: Reviewer 1\n    severity: minor\n"
        "    evidence_status: supported\n    response_status: addressed\n"
        "---\n# R1\n## Concerns\n", encoding="utf-8")
    return d


class TestSchema(unittest.TestCase):
    def test_reviews_declares_concerns_list_object(self):
        field = loader.ENTITIES["reviews"]["fields"]["concerns"]
        self.assertEqual(field["type"], "list_object")
        self.assertEqual(field.get("default"), [])
        for k in ("ideas", "methods", "concepts", "experiments"):
            self.assertIn(k, field["to"])
        item = field["item"]
        for sub in ("id", "slug", "source", "severity", "evidence_status", "response_status"):
            self.assertIn(sub, item)
        self.assertEqual(set(item["response_status"]["values"]), {"open", "addressed", "rejected"})


class TestProjection(unittest.TestCase):
    def test_concerns_slug_projects_fm_reviews_concerns_edges(self):
        d = _wiki()
        edges = rw.project_frontmatter_edges(d)
        fm = [e for e in edges if e.get("type") == "fm_reviews_concerns"]
        self.assertEqual({e["to"] for e in fm}, {"ideas/my-idea", "methods/my-method"})
        self.assertTrue(all(e["from"] == "reviews/m1-review-1" for e in fm))


if __name__ == "__main__":
    unittest.main()
