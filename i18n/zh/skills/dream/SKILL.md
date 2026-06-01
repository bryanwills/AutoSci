---
description: 运行或管理 AutoSci 的 agent-first SciEvolve dream pass：反思 SciMem、编写 proposal-first 自演化产物，并检查定时自动化健康状态
argument-hint: "[setup|status] [wiki-root] [--propose-only] [--yolo]"
---

# /dream

以可插拔的记忆演化策略运行时对 SciMem 进行反思。`/dream`
是记忆的可审计自演化循环：系统审视自身的科学记忆，决定哪些应当淡化、哪些应当重组、哪些潜在关联应当作为未来工作的提案。自主性主张体现在封闭的记忆循环中：SciMem 状态 → 策略判断 → 已验证提案 → 受保护记忆变更 → 下游上下文重建。Claude Code 是默认的用户侧策略运行时，因为 AutoSci 用户本就在此工作；同一底层也可由 OpenAI 兼容 API 调用、本地模型或提供的 JSON 响应驱动。Python 辅助工具负责准备上下文、验证证据、记录产物并应用受保护的记忆更新；它不取代策略判断。

自演化单元是完整的 AutoSci agent 边界，而非单独的 Python CLI。策略运行时在该边界内提供语义判断；确定性工具则使判断有据可查、可审计，并可安全地应用于下游记忆行为。这种分离是预期的实现方式：可替换的推理加上稳定的验证，比硬编码的进程内裁判更易于审计。

按需使用以下本地参考文档：

- `references/memory-operations.md` — 遗忘、整合与关联提案的评判标准
- `references/evidence-and-boundaries.md` — 证据规则、`/check` 边界及安全约束
- `references/agent-response-schema.md` — 终结器所期望的严格 JSON 格式及示例
- `references/automation-scaffold.md` — GitHub Actions 定时任务、密钥、产物及失败行为

打开 `runtime/schema/scievolve.yaml` 查看磁盘上的信号/提案契约。
仅在需要 CLI 示例或自动化细节时打开 `docs/scievolve.md`。

## Commands

- `/dream`：立即执行一次性记忆演化 pass。
- `/dream setup`：验证 `.github/workflows/dream.yml` 是否存在、是否在 job `env:` 中暴露了 `LLM_*`
  密钥、是否读取了可选的 `config/dream.yml`、是否使用了写边界守卫，并说明所需的 Claude Code Action 或
  OpenAI 兼容密钥。
- `/dream status`：检查工作流存在情况、定时计划、策略运行时密钥可用性（可见时），以及近期本地 `wiki/outputs/evolution/dream/`
  产物。
- `scievolve-sense`：定时工作流在上下文准备之前运行此命令，使持久失败状态和应用跳过变为去重后的信号。

## Inputs

- `wiki-root`（可选）：默认为 `wiki/`
- `--propose-only`（可选）：写入已验证的提案产物，但不自动应用变更。不带此选项时，默认的闭环行为是提案后自动应用中/高置信度已验证提案。
- `--yolo`（可选）：高置信度提案可执行不可逆的页面级变更。`consolidation` 将相关页面的正文合并到目标页面并归档源页面；`forgetting` 直接归档目标页面。仅 `high` 置信度提案符合 yolo 条件。该 flag 需显式开启，并产生持久 diff。
- 现有 wiki 页面、graph edges、frontmatter 投影边、引用以及 SciEvolve 记忆信号。
- 定时运行使用 `.github/workflows/dream.yml` 和相同的终结器。它们从 `config/dream.yml` 读取可选的 mode、上下文限制和 `yolo`；手动触发输入会覆盖该配置。它们需要 Claude Code Action 鉴权或 OpenAI 兼容的 `LLM_*` 密钥，运行 `scievolve-sense`，并在确定性终结化之前拒绝生成响应文件之外的 Claude 侧编辑。

安全姿态：`--propose-only` 或默认 `yolo=false` 等保守模式是无人值守 agent 的标准部署保障措施。它们并不降低 `/dream` 实际的自演化能力：默认终结器可自动应用已验证的中/高置信度记忆提案，而显式 `--yolo` 或定时 `yolo=true` 可启用高置信度归档/合并变更。

## Outputs

- Dream 运行目录：`wiki/outputs/evolution/dream/<run>/`
- 上下文产物：`dream_context.json`、`dream_context.md`
- 提示词产物：`dream_agent_prompt.md`
- Agent 响应产物：`dream_agent_response.json`
- 报告产物：`dream_report.md`
- 可选安全应用产物：`dream_apply_report.json`、`dream_apply_report.md`
- 可选的共享 SciEvolve 提案产物，位于 `wiki/outputs/evolution/proposals/` 下

## Wiki Interaction

### Reads

- `wiki/{papers,concepts,topics,people,ideas,experiments,methods,foundations,manuscripts,reviews}/*.md`
- `wiki/graph/edges.jsonl`
- `wiki/graph/citations.jsonl`
- 来自 `runtime/schema/entities.yaml` 的 frontmatter 投影链接
- `wiki/outputs/evolution/signals.jsonl`
- 可选的现有 `/check` 或 lint 报告，仅作为辅助上下文

### Writes

- `wiki/outputs/evolution/dream/<run>/*`
- 仅在使用 `--propose` 终结时写入 `wiki/outputs/evolution/proposals/*`
- 仅在使用 `--propose` 终结时写入 `wiki/outputs/evolution/proposals.jsonl`
- 尝试安全应用时写入 `wiki/outputs/evolution/applications.jsonl`
- 安全应用成功时：实体页面 frontmatter 以及 append-only 的 `SciEvolve Memory Evolution Note`；不重写正文章节
- 安全应用成功后重建 `wiki/graph/context_brief.md`，使下游 skill 能使用演化后的记忆状态。已应用的元数据还会影响未来 `compile-context` 的排名与折叠。

不得从 `/dream` 重写实体页面正文、skill、模板、schema、graph 文件、`index.md` 或 `log.md`。安全应用路径允许的唯一正文变更是 append-only 的 `SciEvolve Memory Evolution Note`。

## Workflow

**前置条件**：在 AutoSci 项目根目录下工作。一次性解析 `PYTHON_BIN`：

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
DREAM_PROPOSE_ONLY=false
for arg in $ARGUMENTS; do
  case "$arg" in
    --propose-only) DREAM_PROPOSE_ONLY=true ;;
    --apply-safe) ;;  # legacy alias; safe auto-apply is now the default
    --*) ;;
    *) WIKI_ROOT="$arg" ;;
  esac
done
export WIKI_ROOT DREAM_PROPOSE_ONLY
```

### Step 1: 准备 Dream 场景

运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" --json
```

读取返回的 `dream_context.md`、`dream_context.json` 和 `dream_agent_prompt.md`。上下文中可能包含确定性候选线索和反复出现的信号模式。**将其视为观测信息；不要机械地将它们复制到提案中。**

### Step 2: 执行 Agentic 记忆反思

使用活跃策略运行时充当 `/dream` 记忆演化 agent。在 slash-command 路径中，Claude Code 是策略运行时；在无头演示中，`tools/research_wiki.py dream --use-llm` 可调用 OpenAI 兼容模型；在测试或本地模型运行中，`--agent-response` 可提供相同的严格 JSON 契约。这些运行时在 `/dream` 边界处可互换：已验证的记忆演化循环独立于策略运行时。在决定提案类型前读取 `references/memory-operations.md`。在接受任何看起来像 lint 修复、删除或不支持科学内容的提案之前，读取 `references/evidence-and-boundaries.md`。

生成少量、高信噪比的提案。一次良好的 `/dream` 运行通常有 0-5 个提案，而非遍历所有微弱线索。

提出以下问题：

1. 哪些记忆正在污染检索或反复出现失败痕迹？
2. 哪些分散页面实际上属于同一个记忆邻域？
3. 哪些不明显的关联在被审查后能帮助未来的研究？
4. wiki 或信号存储中已存在什么证据？
5. 该提案将如何改善下一个研究或检索周期？
6. 哪些内容应当保持不变，因为证据太薄？

### Step 3: 写入 Agent 响应

读取 `references/agent-response-schema.md`，然后将严格 JSON 写入：

```text
wiki/outputs/evolution/dream/<run>/dream_agent_response.json
```

使用 Step 1 返回的相同运行目录。每个提案必须引用已知的上下文证据：来自已准备上下文中的实体 id、候选 id、反复出现模式 id、信号 id 或 edge id。

### Step 4: 通过共享 SciEvolve Store 完成终结

默认的闭环行为是在提供 agent 响应后进行终结**并自动应用**。运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" \
  --agent-response wiki/outputs/evolution/dream/<run>/dream_agent_response.json \
  --json
```

终结器验证引用，写入提案产物，并将中/高置信度提案作为可逆记忆元数据**和可见正文注释**自动应用。这是自演化路径：它同时变更 frontmatter（`scievolve_*`、`tags`、`related_concepts`、`maturity` 等）和页面正文（追加 `SciEvolve Memory Evolution Note` 章节），记录应用事件，重建下游上下文，并将已应用的提案标记为 `applied`。`compile-context` 通过降低降权页面的排名、将整合源折叠到规范目标，以及在 SciEvolve 指导中浮现关联来使用已应用的元数据。

若用户传入了 `--propose-only`（`DREAM_PROPOSE_ONLY=true`），则在写入提案产物后停止，并汇总将要应用的内容：

```bash
"$PYTHON_BIN" tools/research_wiki.py dream "$WIKI_ROOT" \
  --agent-response wiki/outputs/evolution/dream/<run>/dream_agent_response.json \
  --propose-only \
  --json
```

若终结器拒绝某项，应修正响应 JSON，而非放宽工具约束。

### Step 5: 向用户报告

报告内容：

- dream 运行目录
- 读取的候选线索数量
- 按操作类型划分的提案数量
- 安全应用数量（若尝试了安全应用）
- `context_brief.md` 是否已为下游 skill 重建
- 被拒绝的 agent 项目（若有）
- 提案产物路径
- 是否应用了任何记忆元数据或 append-only 正文注释

## Constraints

- `/dream` 是 agent-first 的。确定性扫描准备上下文；它们不做记忆判断。
- `/dream` 与策略运行时无关。只要满足相同的有据可查 JSON 契约，Claude Code、API 模型、本地模型或提供的响应均可提供判断。
- 展示自演化，而非维护。好的提案通过淡化噪声、整合碎片或开启有用的新研究关联来改变记忆的未来形态。
- 将保守默认值视为安全姿态，而非能力边界。开发契约是闭环：已验证提案、受保护变更、应用账本以及下游上下文重建。
- 将安全应用面视为类型化的记忆行为面，而非 `/dream` 应重写任意运行时代码的主张。核心代码变更属于更高风险的开发路径。
- 默认以提案优先。不进行删除、归档或 edge 写入。
- 提供 agent 响应时，闭环自动应用是默认行为。它同时变更 `scievolve_*` 元数据和标准 frontmatter 字段（`tags`、`related_concepts`、`maturity` 等），并向页面正文追加可见的 `SciEvolve Memory Evolution Note`。
- `--yolo` 启用页面级变更：`consolidation` 将相关页面正文合并到目标并归档源；`forgetting` 直接归档目标页面。两者均需要 `high` 置信度。
- 低置信度提案保持仅供审查状态，永不自动应用。
- 不要将 `/dream` 变成 `/check`。断开的链接、格式错误的 graph 行、缺失的必填字段和 xref 不对称仍属于 `/check` 的关注范围。
- 不要捏造科学关联。只有在引用了证据且提案明确标记为待审查时，低置信度才可接受。
- 保留来源可溯性。每个提案都应使 agent 的记忆组织判断可通过产物和账本检查。

## Reflection & Signal Recording

dream 运行完成后，反思此次运行是否揭示了值得记录的系统性记忆问题。如有必要，最多记录 1 条信号。

```bash
python3 tools/scievolve_record.py \\
  --wiki-root wiki \\
  --source task \\
  --dimension memory \\
  --target /dream \\
  --kind {review|warning|success} \\
  --summary "<concise summary>" \\
  --severity {info|low|medium|high|critical} \\
  --confidence {low|medium|high}
```

在以下情况记录信号：
- Agent 提案拒绝率高（>2 倍接受率）→ `kind=review`，汇总拒绝比率
- 尽管有已验证证据，所有提案仍跳过安全应用 → `kind=warning`
- 用户在应用前或应用期间纠正了 dream 提案 → `source=user, kind=correction`
- 运行顺利完成并应用了有意义的变更 → `kind=success`（慎用）

如无值得注意之处，跳过信号记录。
