#!/usr/bin/env python3
"""Smoke tests for the scheduled /morph GitHub Actions workflow."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "morph.yml"
CONFIG_EXAMPLE = REPO / "config" / "morph.yml.example"


class MorphWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_has_weekly_and_manual_triggers(self) -> None:
        self.assertIn("name: Scheduled Morph orchestration evolution", self.text)
        self.assertIn("schedule:", self.text)
        self.assertIn("cron: '13 17 * * 3'", self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("target_template:", self.text)
        self.assertIn("dry-run", self.text)
        self.assertIn("apply", self.text)
        self.assertIn("yolo:", self.text)

    def test_config_controls_scheduled_runs(self) -> None:
        example = CONFIG_EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("config/morph.yml", self.text)
        self.assertIn("yaml.safe_load", self.text)
        self.assertIn('os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"', self.text)
        self.assertIn("MORPH_CONFIG_SOURCE", self.text)
        self.assertIn("mode: dry-run", example)
        self.assertIn('target_template: ""', example)
        self.assertIn("yolo: false", example)

    def test_same_run_finalization_and_write_boundary(self) -> None:
        self.assertIn("Prepare Claude morph context", self.text)
        self.assertIn("Run Claude /morph agent", self.text)
        self.assertIn("Validate Claude write boundary", self.text)
        self.assertIn("Finalize Claude /morph response", self.text)
        self.assertIn('--agent-response "$MORPH_RESPONSE"', self.text)
        self.assertIn('--run-dir "$MORPH_PREPARED_RUN_DIR"', self.text)
        self.assertIn('--allowedTools "Read,Write"', self.text)
        self.assertIn("Claude modified scidag files before deterministic finalization", self.text)
        self.assertIn("prepared-files.sha256", self.text)
        self.assertIn("Claude modified prepared morph context", self.text)
        self.assertIn("Do not finalize the run yourself", self.text)

    def test_sensing_and_fallback_paths_exist(self) -> None:
        self.assertIn("Sense durable SciEvolve signals", self.text)
        self.assertIn("scievolve-sense wiki --json", self.text)
        self.assertIn("Run OpenAI-compatible /morph agent", self.text)
        self.assertIn("--use-llm", self.text)
        self.assertIn("Scheduled /morph needs either Claude Code Action auth", self.text)

    def test_stage_paths_are_finalizer_declared(self) -> None:
        self.assertIn("MORPH_STAGE_PATHS", self.text)
        self.assertIn("wiki/outputs/evolution/signals.jsonl", self.text)
        self.assertIn("wiki/outputs/evolution/proposals.jsonl", self.text)
        self.assertIn("wiki/outputs/evolution/applications.jsonl", self.text)
        self.assertIn('git add --force --all -- "$path"', self.text)
        self.assertNotIn("git add wiki", self.text)
        self.assertNotIn("git add scidag", self.text)

    def test_artifacts_include_template_and_prompt_paths(self) -> None:
        self.assertIn("Upload morph artifacts", self.text)
        self.assertIn("wiki/outputs/evolution/morph/**", self.text)
        self.assertIn("scidag/templates/**", self.text)
        self.assertIn("scidag/operators/prompts.py", self.text)


if __name__ == "__main__":
    unittest.main()
