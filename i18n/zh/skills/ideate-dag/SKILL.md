---
description: SciDAG增强的idea生成 — 通过多智能体算子DAG（多样化生成 + 辩论 + 可行性筛查）而非单次脑暴来生成研究idea，然后用与 /ideate 相同的契约将存活的idea写入wiki。适用于一次性脑暴不够充分的复杂或高风险idea生成场景。
argument-hint: "[research-direction-or-topic] [--complexity 1-5] [--dag <name>] [--max-ideas N] [--mock]"
---

# /ideate-dag

> `/ideate` 的SciDAG增强版（论文§5）。本skill不再使用单次双模型脑暴，而是运行来自
> **idea生成DAG库**的**可复用研究算子有向无环图**（generate / variation / debate / refine / test / ensemble），
> 然后将结果返回到**与 `/ideate` 相同的产物契约** — `wiki/ideas/{slug}.md` 页面加上图谱边 —
> 因此下游不会发生任何变化。DAG弥补了线性脑暴所缺失的纠错和迭代机制：idea在写入之前经过探索、辩论和可行性筛查。
>
> 本skill是**增量式**的。它**不**修改 `/ideate`；对标准线性流程使用 `/ideate`，
> 当某个方向足够复杂、值得进行多智能体搜索时使用 `/ideate-dag`。

## Inputs

- `direction`（可选）：研究方向 / 关键词 / 问题描述。
  若省略，则从 `wiki/graph/open_questions.md` 选择最有价值的方向（规则同 `/ideate`）。
- `--complexity 1-5`（可选）：运行的DAG规模，按任务难度调整。省略时使用**论文图示架构**（`explore-debate-test`）。
- `--dag <name>`（可选）：从idea生成库中运行特定架构（覆盖 `--complexity`）。参见 `scidag/templates/ideation/`。
- `--max-ideas N`（可选，默认3）：写入的idea页面数量上限。
- `--mock`（可选）：以离线确定性LLM运行DAG（仅用于配线测试；生成占位idea）。

## Outputs

与 `/ideate` 完全相同的契约：
- `wiki/ideas/{slug}.md` — 每个idea一个页面（`status: proposed`）
- `wiki/graph/edges.jsonl` — `addresses_gap` / `inspired_by` 边
- `wiki/graph/context_brief.md`、`wiki/graph/open_questions.md` — 重建
- **IDEA_REPORT**（终端）— 另加所运行的DAG架构说明

## 与 /ideate 的关系

`/ideate` Phase 2（"双模型脑暴"）是本skill以DAG替代的步骤。Phase 1（景观扫描）、Phase 3（novelty/可行性验证）和Phase 4（写入wiki）**原封不动地复用**：本skill通过DAG产出候选idea，然后遵循 `/ideate` 自身的"写入wiki"规则进行持久化。
请阅读 `/ideate` SKILL.md 中的"Outputs"、"Wiki Interaction"以及Phase 4章节，并原样应用于持久化。

## Workflow

**前置条件**：工作目录为wiki项目根目录（包含 `wiki/`、`raw/`、`tools/`、`scidag/`）。

### Phase 1 — 景观扫描（复用 /ideate Phase 1）

遵循 `/ideate` Phase 1，为目标方向组装上下文：
wiki内部上下文（`context_brief.md`、`open_questions.md`、相关 `papers`/`concepts`/`methods`/`topics`）+ 外部搜索（WebSearch + S2 + DeepXiv）。将其压缩为一份**任务简报** — 几段话，说明方向、已知的知识缺口和最相关的先前工作。此简报是DAG的任务输入。

### Phase 2 — 运行idea生成DAG（替代 /ideate Phase 2）

1. **选择架构**：
   ```bash
   # 默认 = 论文图示架构；或传入 --complexity / --dag
   python3 -m scidag.cli select --stage ideation [--complexity N]
   ```
   若用户传入了 `--dag <name>`，直接使用该名称。否则使用 `select` 的结果（启发式规则：方向越难/越宽泛，DAG越大）。

2. **以Phase 1的任务简报运行DAG**：
   ```bash
   # 将任务简报写入文件以避免shell引号问题
   python3 -m scidag.cli run --stage ideation --dag <name> \
       --task-file /tmp/ideate_dag_task.md [--mock] --show-dag
   ```
   产物（遵循Title / Motivation / Hypothesis / Approach / Why / Risks格式的研究idea）
   打印在 `===SCIDAG-ARTIFACT-BEGIN===` 和 `===SCIDAG-ARTIFACT-END===` 之间。提取它。

3. **当需要多个idea时**（`--max-ideas N > 1`）：运行DAG N次（或运行一次更宽泛的架构，并将每个叶节点候选视为一个idea）。保留最强的N个不同idea。

### Phase 3 — 验证（复用 /ideate Phase 3，可选）

所选DAG已包含可行性 `test` 算子。对于高风险idea，可额外对每个存活的idea执行 `/novelty`（和 `/review`），方式与 `/ideate` Phase 3 完全相同，并淘汰未通过的idea。

### Phase 4 — 写入wiki（复用 /ideate Phase 4）

使用 `/ideate` Phase 4 规则持久化每个存活的idea：将DAG产物的各章节映射到 `runtime/templates/ideas.md.tmpl` + `entities.yaml`，创建 `wiki/ideas/{slug}.md`（`status: proposed`），通过 `tools/research_wiki.py add-edge` 添加 `addresses_gap` / `inspired_by` 边，然后重建 `context_brief` 和 `open_questions`。向 `wiki/log.md` 追加条目，注明ideas由 `/ideate-dag` 以架构 `<name>` 生成。

### Report

输出标准IDEA_REPORT，并追加一行：
`SciDAG: ran ideation architecture <name> (complexity c<N>, <k> LLM calls)`。

## Notes

- 本skill调用 `scidag/` 中的SciDAG引擎（算子 + DAG执行器）。
  该引擎使用与 `llm-review` MCP服务器相同的LLM配置
  （`.env` 中的 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。
- 条件边剪枝和学习型架构控制器尚未实现；架构选择通过 `--complexity` / `--dag` / 论文图示默认值进行。
