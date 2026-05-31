#!/usr/bin/env python3
"""Parse and validate wiki/outputs/pipeline-progress.md against runtime/schema/pipeline.yaml.

Shared by tools/lint.py (check_pipeline_progress) and
`research_wiki.py validate-pipeline`. Validation logic lives in
runtime.loader.validate_pipeline; this module handles I/O: parsing the markdown
snapshot and building the (kind, slug) -> status lookup over wiki entity pages.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime import loader  # noqa: E402

PROGRESS_REL = "outputs/pipeline-progress.md"


def _label_to_key() -> dict[str, str]:
    return {l["label"]: l["key"] for l in loader.pipeline_stage_log_lines()}


def parse_progress(path: Path) -> tuple[dict, dict]:
    """Return (frontmatter_dict, {stage_key: state}) for a pipeline-progress.md file."""
    text = Path(path).read_text(encoding="utf-8")
    parts = text.split("---", 2)
    frontmatter = {}
    if len(parts) >= 3:
        loaded = yaml.safe_load(parts[1])
        if isinstance(loaded, dict):
            frontmatter = loaded
    body = parts[2] if len(parts) >= 3 else text

    label_to_key = _label_to_key()
    stage_log: dict[str, str] = {}
    in_log = False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("## "):
            in_log = s == loader.PIPELINE["stage_log"]["section"]
            continue
        if in_log and s.startswith("- ") and ":" in s:
            label, state = s[2:].rsplit(":", 1)
            key = label_to_key.get(label.strip())
            if key:
                stage_log[key] = state.strip()
    return frontmatter, stage_log


def _read_status(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1])
    if isinstance(fm, dict) and fm.get("status") is not None:
        return str(fm["status"])
    return None


def _status_lookup(wiki_dir: Path):
    def lookup(kind: str, slug: str):
        p = Path(wiki_dir) / kind / f"{slug}.md"
        if not p.exists():
            return None
        return _read_status(p)
    return lookup


def validate(wiki_dir) -> list[tuple[str, str]]:
    """Validate the wiki's pipeline-progress.md. Returns [] if the file is absent."""
    wiki_dir = Path(wiki_dir)
    progress = wiki_dir / PROGRESS_REL
    if not progress.exists():
        return []
    frontmatter, stage_log = parse_progress(progress)
    return loader.validate_pipeline(frontmatter, stage_log, entity_status=_status_lookup(wiki_dir))


if __name__ == "__main__":
    import json
    issues = validate(sys.argv[1] if len(sys.argv) > 1 else "wiki")
    print(json.dumps(issues, ensure_ascii=False, indent=2))
