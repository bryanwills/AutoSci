---
description: 运行或调度 AutoSci 的 agent-first SciEvolve forge 流程：反思工作流信号并应用 proposal-first 的技能补丁
description-zh: 运行或调度 AutoSci 的 agent-first SciEvolve forge 流程：反思工作流信号并应用 proposal-first 的技能补丁
argument-hint: "[setup|status] [wiki-root] [--target-skill <name>] [--dry-run] [--yolo]"
---

# /forge

通过可插拔的策略运行时对 SciEvolve 工作流信号进行反思。`/forge` 是
**workflow** 维度的可审计自演化循环：系统检查有关技能执行的反馈，
判断哪些技能需要补丁，并为 prompt、检查、交接和恢复协议提出具体的、
有证据支撑的更新方案。

策略运行时是 AutoSci agent 的推理层，而非被动 Python 脚本的外部审查器。
Python 工具负责准备工作流证据、验证行/小节目标、应用受保护的补丁，
并写入溯源信息，供后续技能执行使用已变更的协议。这种分离是预期的实现方式：
可替换的推理层加上稳定的验证层，比硬编码的进程内判断器更易审计。

默认模式**直接修改技能文件**。经验证的提案立即应用：
`patch-prompt`、`reorder-steps` 和 `rename-step` 使用唯一行提示或有界小节匹配；
不安全、缺失或存在歧义的补丁会被跳过。`create-skill` 构建骨架。
每次修改同时追加 `SciEvolve Workflow Evolution Note` 并更新 frontmatter 元数据以记录溯源。

使用 `--dry-run` 可在不修改技能文件的前提下预览提案。使用 `--yolo` 可额外允许
破坏性操作（`archive-skill`、`merge-skills`）。

安全姿态：`--dry-run`、证据验证与 `--yolo` 门控是 agent 编辑可执行工作流文本时的
标准部署保障。它们并不削减 `/forge` 的实际自演化能力：默认终结流程可直接应用
经验证的技能补丁，而 `--yolo` 则将应用路径扩展至高置信度的归档/合并操作。

按需查阅以下本地参考文档：

- `references/workflow-operations.md` — patch-prompt、add-check、
  adjust-handoff 和 add-recovery 操作的规范
- `references/evidence-and-boundaries.md` — 证据规则与安全约束
- `references/agent-response-schema.md` — 终结器所需的精确 JSON 结构

在磁盘上的信号/提案契约，请查看 `runtime/schema/scievolve.yaml`。

## Commands

- `/forge`：立即执行一次性工作流演化流程。
- `/forge setup`：验证 `.github/workflows/forge.yml` 是否存在，确认任务 `env:` 中
  暴露了 `LLM_*` 密钥，读取可选的 `config/forge.yml`，运行自动感知，并使用
  与定时 `/dream` 相同的写入边界保护。
- `/forge status`：检查工作流的存在状态、调度情况、策略运行时密钥的可见性，
  以及近期本地 `wiki/outputs/evolution/forge/` 下的产物。

## Inputs

- `wiki-root`（可选）：默认为 `wiki/`
- `--target-skill`（可选）：聚焦于某个特定技能；默认为所有包含 `dimension=workflow` 信号的技能
- `--dry-run`（可选）：写入提案/报告产物，但不修改技能文件
- `--yolo`（可选）：额外允许 archive-skill 和 merge-skills
- `--agent-response`（可选）：/forge agent 返回的严格 JSON 文件路径
- `--run-dir`（可选）：复用已准备好的运行目录，用于确定性终结
- `--use-llm`（可选）：调用 OpenAI 兼容的 LLM 进行 agent 反思
- 定时运行使用 `.github/workflows/forge.yml` 及可选的 `config/forge.yml`
  配置模式、目标技能、信号上限和 `yolo`。

## Outputs

- Forge 运行目录：`wiki/outputs/evolution/forge/<run>/`
- 上下文产物：`forge_context.json`、`forge_context.md`
- Prompt 产物：`forge_agent_prompt.md`
- Agent 响应产物：`forge_agent_response.json`
- 报告产物：`forge_report.md`
- 可选安全应用产物：`forge_apply_report.json`、`forge_apply_report.md`
- 共享 SciEvolve 提案产物位于 `wiki/outputs/evolution/proposals/`

## Wiki Interaction

### Reads

- `wiki/outputs/evolution/signals.jsonl` — `dimension=workflow` 信号
- 过去 30 天内整理出的周期性工作流信号模式
- `i18n/en/skills/<target>/SKILL.md` 与 `.claude/skills/<target>/SKILL.md` —
  目标技能的内容
- `wiki/log.md` — 技能调用频率（信号密度提示）

### Writes

- `wiki/outputs/evolution/forge/<run>/*`
- 终结时写入 `wiki/outputs/evolution/proposals/*`
- 终结时写入 `wiki/outputs/evolution/proposals.jsonl`
- 尝试安全应用时写入 `wiki/outputs/evolution/applications.jsonl`
- 技能文件（`i18n/en/skills/<target>/SKILL.md`、`.claude/skills/<target>/SKILL.md`）
  在 patch-prompt、reorder-steps、rename-step 和 create-skill 时原地修改。
  Frontmatter（`scievolve_forge_notes`、`scievolve_last_forge`）以及
  append-only 的 `## SciEvolve Workflow Evolution Note` 总是与修改一同写入。

## Workflow

**前置条件**：在 AutoSci 项目根目录下运行。一次性解析 `PYTHON_BIN`：

```bash
if   [ -x .venv/bin/python ];         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then PYTHON_BIN=.venv/Scripts/python.exe
else                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

设置 wiki 根目录：

```bash
WIKI_ROOT=wiki
FORGE_TARGET=""
for arg in $ARGUMENTS; do
  case "$arg" in
    --target-skill=*) FORGE_TARGET="${arg#*=}" ;;
    --target-skill)   FORGE_TARGET="${arg}" ;;
    --*) ;;
    *) WIKI_ROOT="$arg" ;;
  esac
done
export WIKI_ROOT FORGE_TARGET
```

### Step 1: 准备 Forge 场景

运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --json
```

读取返回的 `forge_context.md`、`forge_context.json` 和 `forge_agent_prompt.md`。
上下文包含按目标技能分组的工作流信号、周期性信号模式以及技能内容预览。
**将信号视为证据，而非决策。**

### Step 2: 执行 Agentic 工作流反思

使用激活的策略运行时充当 `/forge` 工作流演化 agent。在 slash-command 路径中，
Claude Code 即策略运行时；在无头演示中，`tools/research_wiki.py forge --use-llm`
可调用 OpenAI 兼容模型。

提问以下问题：

1. 哪些技能具有最高的信号密度或周期性模式？
2. 针对根本原因（而非表面症状），具体的补丁方案是什么？
3. 补丁是增量式的（追加检查、添加恢复）还是破坏性的（重写 prompt）？
4. 补丁是否改变了技能的核心目的？若是，则拒绝。
5. 每个提案的支撑证据是什么？引用信号 id 或周期性模式 id，以及技能行提示。
6. 哪些内容因证据不足应保持不变？

优先采用增量式变更。一次良好的 `/forge` 运行通常有 0–3 个提案。

### Step 3: 写入 Agent 响应

读取 `references/agent-response-schema.md`，然后将严格 JSON 写入：

```text
wiki/outputs/evolution/forge/<run>/forge_agent_response.json
```

使用 Step 1 返回的同一运行目录。每个提案必须引用已知证据：上下文中准备好的
信号 id 或周期性模式 id，以及技能文件路径。

### Step 4: 终结并应用

默认行为**将经验证的提案直接应用到技能文件**。运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --agent-response wiki/outputs/evolution/forge/<run>/forge_agent_response.json \
  --json
```

终结器验证引用、写入提案产物，并原地修改技能文件。已应用的操作：
- `patch-prompt` / `reorder-steps` / `rename-step` — 通过唯一 `line_hint`
  或有界标题小节进行内容替换；存在歧义、缺失或破坏 markdown 的补丁会被跳过
- `create-skill` / `add-skill` — 新骨架写入 `i18n/en/skills/<target>/`
- `archive-skill` / `merge-skills` — 仅在 `--yolo` 且 `confidence=high` 时
- 其他操作 — append-only 注记 + frontmatter 元数据

使用 `--dry-run` 可在不触碰技能文件的前提下预览：

```bash
"$PYTHON_BIN" tools/research_wiki.py forge "$WIKI_ROOT" \
  ${FORGE_TARGET:+--target-skill "$FORGE_TARGET"} \
  --agent-response wiki/outputs/evolution/forge/<run>/forge_agent_response.json \
  --dry-run \
  --json
```

若终结器拒绝某个条目，应修改响应 JSON，而非放宽工具的验证条件。

### Step 5: 向用户汇报

汇报内容：

- forge 运行目录
- 已加载的工作流信号数量
- 每个目标技能的信号密度
- 按操作类型统计的提案数量
- 技能修改数量（已应用到技能文件的提案数）
- 被拒绝的 agent 条目（若有）
- 提案产物路径
- 是否应用了技能 frontmatter 或 append-only 注记

## Constraints

- `/forge` 以 agent 为先。确定性扫描负责准备上下文；工作流判断不由扫描做出。
- `/forge` 与策略运行时无关。Claude Code、API 模型、本地模型或提供的响应均可
  充当判断层，只要满足相同的以证据为基础的 JSON 契约即可。
- 展示自演化，而非维护。一个好的提案通过修复真实的失败模式或协调缺口来
  改变未来工作流的执行形态。
- 将保守默认视为安全姿态，而非能力边界。开发契约是闭环：经验证的提案、
  受保护的技能修改、应用账本，以及改变后的未来技能行为。
- 将技能文件视为预期的程序性记忆面。`/forge` 不应重写任意核心运行时代码；
  这类变更属于更高风险的开发路径。
- 默认提案优先。提案在修改前被记录；默认终结流程可应用经验证的技能补丁，
  而 `--dry-run` 保持运行仅供审查。
- 不要将 `/forge` 变成 `/check`。结构性问题（断链、格式错误的 markdown）
  仍属 `/check` 的职责范围。
- 不要改变技能的核心目的。`/forge` 提升健壮性和清晰度；不重新界定技能的范围。
- 保留溯源。每个提案都应使 agent 的工作流组织判断可从产物和账本中追溯。
- 受保护的应用会验证证据并保留溯源。当行提示唯一匹配或小节边界清晰时，
  默认允许 prompt/step 补丁；archive/merge 仍需 `--yolo` 和高置信度。

## Reflection & Signal Recording

forge 运行完成后，反思本次运行是否揭示了值得记录的系统性工作流问题。
如有必要，最多记录 1 条信号。

```bash
python3 tools/scievolve_record.py \
  --wiki-root wiki \
  --source task \
  --dimension workflow \
  --target /forge \
  --kind {review|warning|success} \
  --summary "<concise summary>" \
  --severity {info|low|medium|high|critical} \
  --confidence {low|medium|high}
```

在以下情况记录信号：
- agent 提案的拒绝率较高（>2 倍于接受率）→ `kind=review`
- 某技能累积了超过 5 条工作流信号但未执行过 forge → `kind=warning`
- 运行完成并产生了有意义的提案 → `kind=success`（谨慎使用）

若无值得注意的情况，跳过信号记录。
