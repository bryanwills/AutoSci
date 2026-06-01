#!/usr/bin/env python3
"""Tests for the /forge Stage 2 workflow evolution."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "research_wiki.py"
RECORD_TOOL = REPO / "tools" / "scievolve_record.py"


class SciEvolveForgeTests(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )

    def run_record(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RECORD_TOOL), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        )

    def _make_skill(self, wiki: Path, name: str, body_extra: str = "") -> Path:
        """Create a minimal skill file in both i18n and .claude trees."""
        for base in ("i18n/en/skills", ".claude/skills"):
            d = wiki.parent / base / name
            d.mkdir(parents=True, exist_ok=True)
            f = d / "SKILL.md"
            f.write_text(
                f"---\ndescription: test skill {name}\n---\n\n"
                f"# /{name}\n\nSome workflow text.\n{body_extra}\n",
                encoding="utf-8",
            )
        return wiki.parent / "i18n" / "en" / "skills" / name / "SKILL.md"

    def test_forge_empty_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            result = self.run_tool("forge", str(wiki), "--json")
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["signal_count"], 0)
            self.assertEqual(data["proposal_count"], 0)
            self.assertTrue(Path(data["report_path"]).exists())

    def test_forge_signal_to_proposal_and_apply(self) -> None:
        """Default mode auto-applies to skill files (not just proposals)."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            self._make_skill(wiki, "discover")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "S2 timeout causes empty shortlist",
                "--severity", "medium",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "add-recovery",
                        "target": "discover",
                        "title": "Add S2 timeout recovery",
                        "proposed_action": "Add timeout check and DeepXiv fallback in Step 2.",
                        "rationale": "Task signals show S2 timeout causes empty shortlists.",
                        "confidence": "high",
                        "skill_path": "i18n/en/skills/discover/SKILL.md",
                        "evidence": [
                            {"source": signal_id, "summary": "S2 timeout"}
                        ],
                    }
                ]
            }), encoding="utf-8")

            result = self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["signal_count"], 1)
            self.assertEqual(data["accepted_agent_proposals"], 1)
            self.assertEqual(data["proposal_count"], 1)
            # Default auto-apply: skill file gets the note appended
            self.assertGreaterEqual(data["safe_application_count"], 1)

            # Verify skill file actually mutated
            skill_file = wiki.parent / "i18n" / "en" / "skills" / "discover" / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("SciEvolve Workflow Evolution Note", content)
            self.assertIn("scievolve_last_forge", content)

            # Proposal artifact still exists
            proposals = data.get("proposals", [])
            self.assertEqual(len(proposals), 1)
            self.assertTrue((wiki / proposals[0]["output_path"]).exists())

    def test_forge_rejects_fabricated_skill_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Test signal",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "add-check",
                        "target": "nonexistent-skill",
                        "title": "Fake",
                        "proposed_action": "Add check.",
                        "rationale": "Signal shows issue.",
                        "confidence": "high",
                    }
                ]
            }), encoding="utf-8")

            result = self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["accepted_agent_proposals"], 0)
            self.assertEqual(data["rejected_agent_items"], 1)
            self.assertEqual(data["proposal_count"], 0)

    def test_forge_dry_run_no_apply(self) -> None:
        """--dry-run produces proposals but does not touch skill files."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            skill_file = self._make_skill(wiki, "discover")
            original_content = skill_file.read_text(encoding="utf-8")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Test signal",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "add-recovery",
                        "target": "discover",
                        "title": "Recovery",
                        "proposed_action": "Add recovery.",
                        "rationale": "Signal.",
                        "confidence": "high",
                        "evidence": [{"source": signal_id, "summary": "Test signal"}],
                    }
                ]
            }), encoding="utf-8")

            result = self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--dry-run",
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["safe_application_count"], 0)
            self.assertEqual(len(data.get("safe_applications", [])), 0)
            # Skill file untouched
            self.assertEqual(skill_file.read_text(encoding="utf-8"), original_content)

    def test_forge_patch_prompt_mutates_skill(self) -> None:
        """patch-prompt is applied by default (no --yolo needed)."""
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            skill_file = self._make_skill(wiki, "discover")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "S2 timeout causes empty shortlist",
                "--severity", "medium",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "discover",
                        "title": "Fix S2 fallback wording",
                        "proposed_action": "Always pass --wiki-root so dedup works.",
                        "rationale": "Old wording misses --wiki-root flag.",
                        "confidence": "high",
                        "line_hint": "Some workflow text.",
                        "evidence": [
                            {"source": signal_id, "summary": "S2 timeout"}
                        ],
                    }
                ]
            }), encoding="utf-8")

            result = self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["safe_application_count"], 1)

            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("Always pass --wiki-root so dedup works.", content)
            self.assertNotIn("Some workflow text.", content)
            # Note still appended
            self.assertIn("SciEvolve Workflow Evolution Note", content)

    def test_forge_patch_rejects_multiple_line_hint_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            skill_file = self._make_skill(wiki, "discover", "Some workflow text.\n")
            original = skill_file.read_text(encoding="utf-8")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Repeated prompt line is ambiguous",
                "--severity", "high",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "discover",
                        "title": "Ambiguous patch",
                        "proposed_action": "Use only one replacement.",
                        "rationale": "The signal points at the duplicated line.",
                        "confidence": "high",
                        "line_hint": "Some workflow text.",
                        "evidence": [{"source": signal_id, "summary": "Ambiguous duplicate"}],
                    }
                ]
            }), encoding="utf-8")

            data = json.loads(self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            ).stdout)

            self.assertEqual(data["safe_application_count"], 0)
            self.assertIn("multiple locations", data["safe_application_skips"][0]["reason"])
            self.assertEqual(skill_file.read_text(encoding="utf-8"), original)

    def test_forge_patch_rejects_missing_line_hint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            skill_file = self._make_skill(wiki, "discover")
            original = skill_file.read_text(encoding="utf-8")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Missing hint",
                "--severity", "high",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "discover",
                        "title": "Missing patch target",
                        "proposed_action": "Replacement text.",
                        "rationale": "The signal asks for a change.",
                        "confidence": "high",
                        "line_hint": "Line not in the skill.",
                        "evidence": [{"source": signal_id, "summary": "Missing hint"}],
                    }
                ]
            }), encoding="utf-8")

            data = json.loads(self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            ).stdout)

            self.assertEqual(data["safe_application_count"], 0)
            self.assertIn("line_hint not found", data["safe_application_skips"][0]["reason"])
            self.assertEqual(skill_file.read_text(encoding="utf-8"), original)

    def test_forge_patch_rejects_markdown_structure_break(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            skill_file = self._make_skill(wiki, "discover")
            original = skill_file.read_text(encoding="utf-8")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Bad markdown patch",
                "--severity", "high",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "discover",
                        "title": "Bad markdown",
                        "proposed_action": "```python\nprint('unterminated')",
                        "rationale": "The signal asks for a change.",
                        "confidence": "high",
                        "line_hint": "Some workflow text.",
                        "evidence": [{"source": signal_id, "summary": "Bad patch"}],
                    }
                ]
            }), encoding="utf-8")

            data = json.loads(self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--json",
            ).stdout)

            self.assertEqual(data["safe_application_count"], 0)
            self.assertIn("break markdown structure", data["safe_application_skips"][0]["reason"])
            self.assertEqual(skill_file.read_text(encoding="utf-8"), original)

    def test_forge_finalize_reuses_prepared_run_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            self._make_skill(wiki, "discover")
            signal = self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Prepared forge context",
                "--severity", "high",
                "--confidence", "high",
            )
            signal_id = json.loads(signal.stdout)["signal_id"]

            prepare = json.loads(self.run_tool("forge", str(wiki), "--dry-run", "--json").stdout)
            response_path = wiki / "forge_response.json"
            response_path.write_text(json.dumps({
                "proposals": [
                    {
                        "operation": "patch-prompt",
                        "target": "discover",
                        "title": "Reuse prepared context",
                        "proposed_action": "Prepared replacement.",
                        "rationale": "The same prepared context should be finalized.",
                        "confidence": "high",
                        "line_hint": "Some workflow text.",
                        "evidence": [{"source": signal_id, "summary": "Prepared context"}],
                    }
                ]
            }), encoding="utf-8")

            data = json.loads(self.run_tool(
                "forge", str(wiki),
                "--agent-response", str(response_path),
                "--run-dir", prepare["run_dir"],
                "--json",
            ).stdout)

            self.assertEqual(data["run_dir"], prepare["run_dir"])
            self.assertEqual(data["context_path"], prepare["context_path"])
            self.assertEqual(data["safe_application_count"], 1)

    def test_forge_target_skill_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "discover",
                "--kind", "failure",
                "--summary", "Discover issue",
            )
            self.run_record(
                "--wiki-root", str(wiki),
                "--source", "task",
                "--dimension", "workflow",
                "--target", "ideate",
                "--kind", "failure",
                "--summary", "Ideate issue",
            )
            result = self.run_tool(
                "forge", str(wiki),
                "--target-skill", "discover",
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["signal_count"], 1)


if __name__ == "__main__":
    unittest.main()
