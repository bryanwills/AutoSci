#!/usr/bin/env python3
"""Smoke tests for the scheduled /dream GitHub Actions workflow."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "dream.yml"
CONFIG_EXAMPLE = REPO / "config" / "dream.yml.example"


class DreamWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_has_scheduled_and_manual_triggers(self) -> None:
        self.assertIn("name: Scheduled Dream memory evolution", self.text)
        self.assertIn("schedule:", self.text)
        self.assertIn("cron: '43 18 * * *'", self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("mode:", self.text)
        self.assertIn("propose-only", self.text)
        self.assertIn("yolo:", self.text)

    def test_scheduled_yolo_is_user_configurable(self) -> None:
        example = CONFIG_EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("config/dream.yml", self.text)
        self.assertIn("yaml.safe_load", self.text)
        self.assertIn('os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"', self.text)
        self.assertIn("DREAM_CONFIG_SOURCE", self.text)
        self.assertIn("yolo: false", example)
        self.assertNotIn('github.event_name }}" != "workflow_dispatch"', self.text)
        self.assertNotIn("yolo=false", self.text)
        self.assertNotIn("explicit workflow_dispatch", self.text)
        self.assertNotIn("yolo mode requires Claude Code Action auth", self.text)

    def test_policy_runtime_secrets_are_exposed_and_gated(self) -> None:
        self.assertIn("HAS_CLAUDE_CODE_AUTH", self.text)
        self.assertIn("HAS_REVIEW_LLM", self.text)
        self.assertIn("LLM_API_KEY: ${{ secrets.LLM_API_KEY }}", self.text)
        self.assertIn("LLM_BASE_URL: ${{ secrets.LLM_BASE_URL }}", self.text)
        self.assertIn("LLM_MODEL: ${{ secrets.LLM_MODEL }}", self.text)
        self.assertIn("Validate policy runtime", self.text)
        self.assertIn("Scheduled /dream needs either Claude Code Action auth", self.text)

    def test_claude_path_prepares_then_finalizes_same_run_deterministically(self) -> None:
        self.assertIn("Prepare Claude dream context", self.text)
        self.assertIn("Run Claude /dream agent", self.text)
        self.assertIn("Validate Claude write boundary", self.text)
        self.assertIn("Finalize Claude /dream response", self.text)
        self.assertIn("--agent-response \"$DREAM_RESPONSE\"", self.text)
        self.assertIn("--run-dir \"$DREAM_PREPARED_RUN_DIR\"", self.text)
        self.assertIn("--allowedTools \"Read,Write\"", self.text)
        self.assertIn("Do not finalize the run yourself", self.text)
        self.assertIn("Claude modified wiki files before deterministic finalization", self.text)
        self.assertIn("prepared-files.sha256", self.text)
        self.assertIn("Claude modified prepared dream context", self.text)

    def test_fallback_path_uses_openai_compatible_llm(self) -> None:
        self.assertIn("Run OpenAI-compatible /dream agent", self.text)
        self.assertIn("--use-llm", self.text)
        self.assertIn("> \"$DREAM_FINALIZE\"", self.text)

    def test_artifacts_and_writeback_are_reviewer_visible(self) -> None:
        self.assertIn("Upload dream artifacts", self.text)
        self.assertIn("wiki/outputs/evolution/dream/**", self.text)
        self.assertIn("wiki/outputs/evolution/proposals.jsonl", self.text)
        self.assertIn("wiki/outputs/evolution/applications.jsonl", self.text)
        self.assertIn("wiki/graph/context_brief.md", self.text)
        self.assertIn("Commit dream evolution changes", self.text)
        self.assertIn("DREAM_STAGE_PATHS", self.text)
        self.assertIn("git add --force --all -- \"$path\"", self.text)
        self.assertNotIn("git add wiki", self.text)

    def test_does_not_copy_daily_arxiv_external_api_secrets(self) -> None:
        self.assertNotIn("SEMANTIC_SCHOLAR_API_KEY", self.text)
        self.assertNotIn("DEEPXIV_TOKEN", self.text)


if __name__ == "__main__":
    unittest.main()
