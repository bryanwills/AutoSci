#!/usr/bin/env python3
"""Sanctioned writer for wiki/graph/*.jsonl event logs (per hard-rule 2).

Shared by tools/research_wiki.py (re-export + `append-event` CLI) and the
pipeline tools (Trust Guard events, pipeline gate/feedback events). Keeping the
writer here lets multiple tools emit events without coupling to research_wiki.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

GRAPH_DIRNAME = "graph"  # intentionally duplicates research_wiki.DERIVED_DIR (kept local to avoid an import cycle)
ALLOWED_EVENT_STREAMS = {"trust_events", "pipeline_events", "jobs", "consolidation_events"}


def append_event(wiki_root: str, stream: str, record: dict[str, object]) -> None:
    """Append one JSON record to wiki/graph/<stream>.jsonl. A UTC `ts` is stamped
    if the caller did not provide one."""
    if stream not in ALLOWED_EVENT_STREAMS:
        raise ValueError(
            f"unknown event stream {stream!r}; allowed: {sorted(ALLOWED_EVENT_STREAMS)}"
        )
    graph_dir = Path(wiki_root) / GRAPH_DIRNAME
    graph_dir.mkdir(parents=True, exist_ok=True)
    row = dict(record)
    row.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    path = graph_dir / f"{stream}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
