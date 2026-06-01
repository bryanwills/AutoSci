#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "i18n" / "zh" / "skills"
EN = ROOT / "i18n" / "en" / "skills"

# Integration tool commands that must be present in BOTH languages of a skill, or neither.
TRACKED_COMMANDS = [
    "research_pipeline.py status",
    "research_pipeline.py validate",
    "research_pipeline.py resume-plan",
    "research_pipeline.py gate",
    "research_pipeline.py feedback",
    "evidence.py verify-claims",
    "research_wiki.py concerns",
    "compile-context wiki/ --entity",
    "consolidate_memory.py propose",
    "consolidate_memory.py apply",
]


def _text(base: Path, name: str) -> str:
    return (base / name / "SKILL.md").read_text(encoding="utf-8")


class TestSkillToolParity(unittest.TestCase):
    def test_zh_en_tracked_command_parity(self):
        zh_skills = {p.parent.name for p in ZH.glob("*/SKILL.md")}
        en_skills = {p.parent.name for p in EN.glob("*/SKILL.md")}
        common = sorted(zh_skills & en_skills)
        self.assertTrue(common, "no skills found in both i18n/zh and i18n/en")

        drift = []
        for name in common:
            zh_text, en_text = _text(ZH, name), _text(EN, name)
            for cmd in TRACKED_COMMANDS:
                in_zh, in_en = cmd in zh_text, cmd in en_text
                if in_zh != in_en:
                    have, miss = ("zh", "en") if in_zh else ("en", "zh")
                    drift.append(f"{name}: '{cmd}' in {have} but missing in {miss}")
        self.assertEqual(drift, [], "zh/en skill tool-command drift:\n" + "\n".join(drift))


if __name__ == "__main__":
    unittest.main()
