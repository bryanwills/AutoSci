#!/usr/bin/env python3
"""Smoke tests for the agent-first /morph SciEvolve stage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "research_wiki.py"
sys.path.insert(0, str(REPO))

from tools import research_wiki


class SciEvolveMorphTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )

    def seed_wiki(self, wiki: Path) -> None:
        self.run_tool("init", str(wiki))
        # Seed an orchestration signal
        self.run_tool(
            "scievolve-record-signal", str(wiki),
            "--source", "task",
            "--dimension", "orchestration",
            "--target", "explore-debate-test",
            "--kind", "cost",
            "--summary", "Debate operator consumes too many LLM calls",
            "--confidence", "medium",
            "--severity", "medium",
        )

    def test_morph_prepares_context(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            self.seed_wiki(wiki)
            result = self.run_tool("morph", str(wiki), "--json")
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertIn("morph_context.json", data["context_path"])
            self.assertIn("morph_agent_prompt.md", data["prompt_path"])
            self.assertTrue(Path(wiki, data["context_path"]).exists())
            self.assertTrue(Path(wiki, data["prompt_path"]).exists())

    def test_morph_dry_run_no_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            self.seed_wiki(wiki)
            # Capture a template file content before
            template = REPO / "scidag" / "templates" / "ideation" / "4-explore-debate-test.yaml"
            before = template.read_text(encoding="utf-8")
            result = self.run_tool("morph", str(wiki), "--dry-run", "--json")
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            # No mutation should happen in dry-run
            after = template.read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_morph_finalizes_agent_response(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            self.seed_wiki(wiki)
            # Prepare context
            prep = self.run_tool("morph", str(wiki), "--json")
            prep_data = json.loads(prep.stdout)
            run_dir = Path(prep_data["run_dir"])

            agent_response = {
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "Debate",
                        "title": "Shorten debate rounds",
                        "proposed_action": "Shorten debate to 1 round.",
                        "rationale": "Reduce LLM calls.",
                        "confidence": "medium",
                        "line_hint": "Expert Debate",
                        "evidence": [
                            {"source": prep_data["signal_count"], "summary": "cost signal"}
                        ],
                    }
                ]
            }
            resp_path = run_dir / "morph_agent_response.json"
            resp_path.write_text(json.dumps(agent_response), encoding="utf-8")

            result = self.run_tool(
                "morph", str(wiki),
                "--agent-response", str(resp_path),
                "--dry-run", "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertGreaterEqual(data["proposal_count"], 0)

    def test_morph_signal_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            self.seed_wiki(wiki)
            result = self.run_tool("morph", str(wiki), "--json")
            data = json.loads(result.stdout)
            self.assertEqual(data["signal_count"], 1)


if __name__ == "__main__":
    unittest.main()
