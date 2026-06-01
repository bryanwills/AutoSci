---
description: 运行或调度 AutoSci 的 agent-first SciEvolve morph pass：反思 SciDAG 编排信号并演化算子图与阶段模板
argument-hint: "[setup|status] [wiki-root] [--target-template <name>] [--dry-run] [--apply] [--yolo]"
---

# /morph

通过可插拔策略运行时对 SciDAG 编排信号进行反思。
`/morph` 是 **orchestration** 维度的可审计自演化循环：系统检查
关于 DAG 执行、算子性能和模板适用性的反馈，然后对算子提示词、
图结构、验证节点及阶段专属模板提出具体变更方案。

策略运行时是 AutoSci agent 边界内的编排推理层。确定性工具提供传感器
和效应器：它们汇编信号/模板上下文、验证提议的 patch 目标、仅在启用
时对类型化的 DAG 表面执行变更，并将结果记入账本供后续 SciDAG 执行使用。
这种分离是既定的实现方式：可替换的推理层加上稳定的验证层，比硬编码的
进程内判断器更易审计。

默认模式为 **dry-run/提案优先**。经验证的提案以可检查的 artifact 形式写出；
使用 `--apply` 可额外对模板 YAML 和算子提示词文件执行变更。使用 `--yolo`
允许破坏性模板操作（archive-template、merge-templates）。

安全策略：`--dry-run` 和 `--yolo` 门控是针对编辑可执行编排文本的 agent
的标准部署保障。它们不会削减 `/morph` 实际的自演化能力：默认最终化在
传入 `--apply` 时可直接对经验证的模板 patch 执行变更，而 `--dry-run`
则让运行保持仅供审阅的状态。

打开 `runtime/schema/scievolve.yaml` 查看磁盘上的信号/提案契约及
精确的操作评分规则。

## Commands

- `/morph`：立即执行一次性编排演化 pass。
- `/morph setup`：验证 `.github/workflows/morph.yml` 是否存在，
  检查 job `env:` 中是否暴露了 `LLM_*` secrets，读取可选的
  `config/morph.yml`，执行自动感知，并使用与定时 `/dream` 相同的
  写边界保护。
- `/morph status`：检查工作流存在情况、调度、可见时的策略运行时 secret
  可用性，以及最近的本地 `wiki/outputs/evolution/morph/` artifact。

## Inputs

- `wiki-root`（可选）：默认 `wiki/`
- `--target-template`（可选）：聚焦于某个特定模板；默认为所有具有
  `dimension=orchestration` 信号的模板
- `--dry-run`（可选）：写出提案/报告 artifact，但不修改模板或提示词文件。
  这是默认行为。
- `--apply`（可选）：直接应用经验证的模板/提示词 patch
- `--yolo`（可选）：额外允许破坏性操作：archive-template、merge-templates
- `--agent-response`（可选）：指向 /morph agent 返回的严格 JSON 的路径
- `--run-dir`（可选）：复用已准备好的运行目录以实现确定性最终化
- `--use-llm`（可选）：调用与 OpenAI 兼容的 LLM 执行 agent 反思
- 定时运行使用 `.github/workflows/morph.yml` 和可选的 `config/morph.yml`
  来配置模式、目标模板、信号限制和 `yolo`。

## Outputs

- Morph 运行目录：`wiki/outputs/evolution/morph/<run>/`
- 上下文 artifact：`morph_context.json`、`morph_context.md`
- 提示词 artifact：`morph_agent_prompt.md`
- Agent 响应 artifact：`morph_agent_response.json`
- 报告 artifact：`morph_report.md`
- 可选的应用 artifact：`morph_apply_report.json`、`morph_apply_report.md`
- 共享 SciEvolve 提案 artifact，位于 `wiki/outputs/evolution/proposals/`

## Wiki Interaction

### Reads

- `wiki/outputs/evolution/signals.jsonl` — `dimension=orchestration` 信号
- 过去 30 天内准备的周期性编排信号模式
- `scidag/templates/<stage>/*.yaml` — DAG 模板库
- `scidag/operators/prompts.py` — 算子提示词文本
- `scidag/operators/registry.py` — 算子描述与能力
- `wiki/log.md` — DAG 调用频率（信号密度参考）

### Writes

- `wiki/outputs/evolution/morph/<run>/*`
- 最终化时写入 `wiki/outputs/evolution/proposals/*`
- 最终化时写入 `wiki/outputs/evolution/proposals.jsonl`
- 尝试应用时写入 `wiki/outputs/evolution/applications.jsonl`
- 传入 `--apply` 时，模板 YAML（`scidag/templates/<stage>/<name>.yaml`）
  将就地变更，支持 patch-template、add-verification-node、prune-branch
  和 specialize-template。
- 传入 `--apply` 时，算子提示词文件（`scidag/operators/prompts.py`）
  将就地变更，支持 patch-prompt。
- frontmatter（`scievolve_morph_notes`、`scievolve_last_morph`）与
  append-only `## SciEvolve Orchestration Evolution Note` 始终与
  变更同步写入。

## Workflow

**前置条件**：在 AutoSci 项目根目录下执行。首先解析 `PYTHON_BIN`：

```bash
if   [ -x .venv/bin/python ];         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then PYTHON_BIN=.venv/Scripts/python.exe
else                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

设置 wiki 根目录和可选目标模板：

```bash
set -- $ARGUMENTS
WIKI_ROOT=wiki
MORPH_TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --target-template=*) MORPH_TARGET="${1#*=}"; shift ;;
    --target-template)   MORPH_TARGET="$2"; shift 2 ;;
    --*) shift ;;
    *) WIKI_ROOT="$1"; shift ;;
  esac
done
export WIKI_ROOT MORPH_TARGET
```

### Step 1: 准备 Morph 场景

运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --json
```

读取返回的 `morph_context.md`、`morph_context.json` 和
`morph_agent_prompt.md`。上下文包含按目标模板分组的编排信号、
周期性信号模式、模板库摘要及算子提示词预览。**将信号视为证据，而非决策。**

### Step 2: 执行 Agent 编排反思

使用当前活跃的策略运行时担任 `/morph` 编排演化 agent。在
slash-command 路径下，Claude Code 是策略运行时；在无头演示模式下，
`tools/research_wiki.py morph --use-llm` 可调用与 OpenAI 兼容的模型。

思考以下问题：

1. 在信号证据中，哪些算子表现出稳定的性能不足？
2. 哪些图结构反复失败或浪费调用次数（如未测试的分支）？
3. 什么具体 patch 能解决根本原因：提示词修改、新增节点、
   剪除分支，还是模板特化？
4. 该 patch 是增量式的（新增验证节点、强化提示词）还是破坏性的
   （剪除分支、移除算子）？
5. 该 patch 是否改变了阶段的核心目的？若是，则拒绝。
6. 每条提案有哪些证据支撑？引用信号 id、模板名称和算子名称。
7. 哪些内容因证据太薄应保持不变？

优先选择增量式变更。一次良好的 `/morph` 运行通常产生 0–3 条提案。

### Step 3: 写入 Agent 响应

读取 `morph_agent_prompt.md`（Step 1 准备）中的 agent 响应 schema，
然后将严格 JSON 写入：

```text
wiki/outputs/evolution/morph/<run>/morph_agent_response.json
```

使用 Step 1 返回的同一运行目录。每条提案必须引用已知证据：
来自准备好的上下文的信号 id、周期性模式 id、模板文件路径和算子名称。

### Step 4: 最终化并应用

默认行为为 **dry-run**：写出提案/报告 artifact，不修改文件。运行：

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --json
```

若要直接应用经验证的模板/提示词 patch，添加 `--apply`：

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --apply \
  --json
```

最终化器验证引用，写出提案 artifact，并在传入 `--apply` 时就地变更文件。
支持的操作：
- `patch-template` — 通过安全文本 patch 对 YAML 节点列表进行修改
- `patch-prompt` — 通过有界区段匹配修改算子提示词
- `add-verification-node` — 向模板追加一个 `Test` 或 `Review` 节点
- `prune-branch` — 从模板中移除弱分支
- `specialize-template` — 为某阶段/问题类型复制并适配模板
- `create-template` — 向 `scidag/templates/<stage>/` 写入新模板骨架
- `archive-template` / `merge-templates` — 仅在 `--yolo` 且 `confidence=high` 时可用
- 其他操作 — 追加 append-only 注释 + frontmatter 元数据

使用 `--dry-run` 在不触碰文件的情况下审阅：

```bash
"$PYTHON_BIN" tools/research_wiki.py morph "$WIKI_ROOT" \
  ${MORPH_TARGET:+--target-template "$MORPH_TARGET"} \
  --agent-response wiki/outputs/evolution/morph/<run>/morph_agent_response.json \
  --dry-run \
  --json
```

若最终化器拒绝某一条目，请修改响应 JSON，而非放宽工具限制。

### Step 5: 向用户汇报

汇报内容：

- morph 运行目录
- 已加载的编排信号数量
- 每个目标模板的信号密度
- 按操作类型统计的提案数量
- 文件变更数量（已应用至模板/提示词的提案）
- 被拒绝的 agent 条目（若有）
- 提案 artifact 路径
- 是否有模板或提示词文件被实际修改

## Constraints

- `/morph` 以 agent 为核心。确定性扫描用于准备上下文；它们不做
  编排判断。
- `/morph` 对策略运行时不作假设。Claude Code、API 模型、本地模型
  或外部提供的响应均可提供判断，只要满足同样以证据为基础的 JSON 契约。
- 展示自演化，而非维护。一条好的提案通过修复真实的算子弱点或
  图低效问题来改变 DAG 未来执行的形态。
- 将保守默认值视为安全策略，而非能力边界。开发契约是闭环：
  经验证的提案、受保护的模板/提示词变更、应用账本，以及改变后的
  未来 DAG 行为。
- 将模板和算子提示词视为预期的编排行为表面。`/morph` 不应改写
  任意的核心运行时代码；那些变更属于风险更高的开发路径。
- 默认提案优先。提案在变更前先被记录；`--apply` 可应用经验证的
  patch，而 `--dry-run` 让运行保持仅供审阅的状态。
- 不要把 `/morph` 变成 `/check`。结构性问题（损坏的 YAML、畸形的
  图）仍属 `/check` 的职责范围。
- 不要改变阶段的核心目的。`/morph` 提升算子鲁棒性和图效率；
  它不重新划定阶段的范围。
- 保留溯源信息。每条提案都应使 agent 的编排组织判断可从 artifact
  和账本中检查。
- 受保护的应用验证证据并保留溯源信息。当行提示唯一匹配或区段边界
  清晰时，模板/提示词 patch 在传入 `--apply` 后被允许；archive/merge
  仍需 `--yolo` 且置信度为 high。

## Reflection & Signal Recording

morph 运行完成后，反思本次运行是否揭示了值得记录的系统性编排问题。
若有必要，最多记录 1 条信号。

```bash
python3 tools/scievolve_record.py \
  --wiki-root wiki \
  --source task \
  --dimension orchestration \
  --target /morph \
  --kind {review|warning|success} \
  --summary "<concise summary>" \
  --severity {info|low|medium|high|critical} \
  --confidence {low|medium|high}
```

以下情况记录信号：
- agent 提案拒绝率高（>2 倍于接受数）→ `kind=review`
- 某模板积累了 >5 个编排信号但尚未执行 morph 运行 → `kind=warning`
- 运行完成并产生了有意义的提案 → `kind=success`（谨慎使用）
- `/dream` 或 `/forge` 的变更表明 DAG 结构应当适配 → 跨 skill
  级联信号，使用 `dimension=orchestration`

若无值得记录的内容，跳过信号记录。

## Cross-Skill Cascade

`/morph` 有意不孤立运行。当 `/dream` 整合记忆或 `/forge` 修订 skill
的方式改变了预期的 DAG 输入/输出契约时，这些阶段应记录一个
`orchestration` 信号，以便 `/morph` 能提议相应的模板变更。反之，
当 `/morph` 为新问题类型特化一个模板时，它应记录一个 `memory` 信号，
以便 `/dream` 可以创建或更新对应的 Topic/Method 实体。

三个演化维度形成闭环：
- `/dream`（memory）→ `compile-context` 排序 → skill 输入 → DAG 执行
- `/forge`（workflow）→ skill 协议 → DAG 调用模式
- `/morph`（orchestration）→ 模板/算子 → 执行轨迹 → 信号
