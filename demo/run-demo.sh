#!/usr/bin/env bash
# Bio-adaptation demo: run the daily-arxiv pipeline end-to-end on a frozen 9-paper
# sample feed, producing a ranked markdown digest at examples/output/digest.md.
#
# 生信适配 demo：在一份固定的 9 篇论文 sample feed 上端到端跑通 daily-arxiv
# 流水线，最终在 examples/output/digest.md 产出一份排好序的 markdown digest。
#
# What this exercises / 本脚本验证的环节：
#   1) prepare       — dedupe sample feed against the wiki, score signals, build context
#                      去重 + 打信号 + 构造上下文
#   2) recommend-llm — DeepSeek v4-flash ranks candidates (requires LLM_API_KEY + LLM_BASE_URL + LLM_MODEL)
#                      DeepSeek v4-flash 排序（需要 LLM_API_KEY + LLM_BASE_URL + LLM_MODEL）
#   3) finalize      — emit markdown + machine-readable digest
#                      输出 markdown + 机读 JSON digest
#
# No API key? Skip step 2 — finalize will fall back to tool-only ranking and you
# still get a digest (see examples/output/digest-sample.md for what step 2 adds).
# 没设 API key？脚本会自动跳过第 2 步，finalize 退化为 tool-only 排序，仍能拿到
# 一份 digest。第 2 步加上 LLM 之后的效果可对比 examples/output/digest-sample.md。
#
# Pre-rendered output (no API call needed) / 预渲染输出（无需调用 API）:
#   examples/output/digest-sample.md
#
# Run from repo root / 在仓库根目录执行.

set -euo pipefail

cd "$(dirname "$0")/.."

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  PY="python3"
fi

OUT=examples/output
mkdir -p "$OUT"

echo "[1/3] prepare context from demo/sample-feed.json / 从 sample feed 构造上下文"
"$PY" tools/daily_arxiv.py prepare \
  --feed demo/sample-feed.json \
  --no-external \
  --max-recommendations 5 \
  --out "$OUT/context.json"

if [ -n "${LLM_API_KEY:-}" ] || grep -qs '^LLM_API_KEY=' .env ~/.env 2>/dev/null; then
  echo "[2/3] recommend-llm via DeepSeek / 调用 DeepSeek 排序"
  "$PY" tools/daily_arxiv.py recommend-llm \
    --context "$OUT/context.json" \
    --out "$OUT/decisions.json" \
    --limit 9
  DECISIONS_ARG=(--decisions "$OUT/decisions.json")
else
  echo "[2/3] LLM_API_KEY not set — skipping LLM ranking; finalize will use tool signals only / 未设 LLM_API_KEY，跳过 LLM 排序，finalize 退化为 tool-only"
  DECISIONS_ARG=()
fi

echo "[3/3] finalize digest / 落盘 digest"
"$PY" tools/daily_arxiv.py finalize \
  --context "$OUT/context.json" \
  "${DECISIONS_ARG[@]}" \
  --out-md "$OUT/digest.md" \
  --out-json "$OUT/digest.json"

echo
echo "Done. Open $OUT/digest.md to see the ranked digest."
echo "完成。打开 $OUT/digest.md 查看排序后的 digest。"
echo "Reference (pre-rendered LLM-ranked output) / 预渲染的 LLM 排序参考: $OUT/digest-sample.md"
