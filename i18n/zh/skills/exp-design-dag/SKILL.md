---
description: SciDAG增强的实验设计 — 通过多智能体算子DAG（方法候选 + 并行可靠性/测试检查 + 整合）而非单次规划来设计实验套件，然后用与 /exp-design 相同的契约写入实验页面。适用于一次性规划风险较高的复杂设计。
argument-hint: "<idea-slug> [--complexity 1-5] [--dag <name>] [--mock]"
---

# /exp-design-dag

> `/exp-design` 的SciDAG增强版（论文§5）。实验阶段的首要目标是**可靠性** — 实验是成本最高的步骤，
> 因此设计必须合理且可一次性运行。本skill运行来自**实验DAG库**的**可复用算子DAG**，
> 其中 `test`（可行性/逻辑性）算子尤为重要，并在并行分支上出现，从而在消耗任何算力之前对设计进行压力测试。
> 它将结果返回到**与 `/exp-design` 相同的产物契约** — `wiki/experiments/{exp-slug}.md` 页面、
> 主设计文档和 `tested_by` 边 — 因此下游不会发生任何变化。
>
> 本skill是**增量式**的。它**不**修改 `/exp-design`；对标准流程使用 `/exp-design`，
> 当设计足够复杂或代价足够高、值得进行多智能体可靠性检查时使用 `/exp-design-dag`。

## Inputs

- `idea-slug`（必选）：要为其设计实验的idea（`wiki/ideas/{slug}.md`）。
- `--complexity 1-5`（可选）：DAG规模，按设计难度调整。省略时使用**论文图示架构**（`candidate-doubletest-refine`）。
- `--dag <name>`（可选）：从实验库中运行特定架构（覆盖 `--complexity`）。参见 `scidag/templates/experiment/`。
- `--mock`（可选）：离线确定性LLM（仅用于配线测试）。

## Outputs

与 `/exp-design` 完全相同的契约：
- `wiki/experiments/{exp-slug}.md` — 每个实验块一个页面（`status: planned`，`linked_idea` 已设置）
- `experiments/designs/{slug}-master.md` — 主设计文档
- `wiki/graph/edges.jsonl` — `tested_by` 边（idea → 每个experiment）
- `wiki/ideas/{slug}.md` — 更新的 `linked_experiments`
- `wiki/graph/context_brief.md`、`open_questions.md` — 重建
- **DESIGN_REPORT**（终端）— 另加所用的DAG架构

## 与 /exp-design 的关系

`/exp-design` Phase 2（方法候选生成）及其迭代消融循环，正是本skill以DAG形式表达的部分：并行候选设计，每个都由 `test` 把关，由 `refine` 整合（较大架构中消融对比使用 `debate`）。Phase 1（加载上下文）、Phase 3（基准选择）及持久化规则**原封不动地复用**自 `/exp-design`。
请阅读 `/exp-design` SKILL.md 中的"Outputs"、"Wiki Interaction"以及Phase 1–3章节，并原样应用。

## Workflow

**前置条件**：工作目录为wiki项目根目录（包含 `wiki/`、`raw/`、`tools/`、`scidag/`）。

### Phase 1 — 加载上下文（复用 /exp-design Phase 1）

遵循 `/exp-design` Phase 1：读取 `wiki/ideas/{slug}.md`（假设、方法、风险、新颖性），若存在则读取预实验报告，相关 `methods`/`papers` 以及已有实验。从 `/exp-design` Phase 3 补充基准/baseline上下文。
压缩为一份描述idea、其假设、硬件/算力预算和候选方法方向的**任务简报**。这是DAG的任务输入。

### Phase 2 — 运行实验DAG（替代 /exp-design Phase 2 + 消融循环）

1. **选择架构**：
   ```bash
   python3 -m scidag.cli select --stage experiment [--complexity N]
   ```
   若用户指定了 `--dag <name>`，直接使用该名称。较大架构
   （`iterative-ablation`、`full-reliability-suite`）适用于需要消融的因子较多或运行成本较高的设计。

2. **以任务简报运行DAG**：
   ```bash
   python3 -m scidag.cli run --stage experiment --dag <name> \
       --task-file /tmp/expdesign_dag_task.md [--mock] --show-dag
   ```
   从 `===SCIDAG-ARTIFACT-BEGIN/END===` 标记之间提取产物（整合后的实验设计）。该设计枚举了方法候选、基准 + baselines + 指标，以及实验块（主实验、消融、敏感度），每个块附有DAG `test` 算子给出的可行性说明。

### Phase 3 — 基准最终确定（复用 /exp-design Phase 3）

将DAG提出的基准/指标与 `/exp-design` Phase 3 标准进行核对（使用领域标准数据集/指标；验证baselines在wiki中存在）。若DAG选择了非标准基准，则调整设计。

### Phase 4 — 写入wiki（复用 /exp-design 持久化）

将整合后的设计拆分为每块一个 `wiki/experiments/{exp-slug}.md`
（`status: planned`，`linked_idea: {idea-slug}`），遵循
`runtime/templates/experiments.md.tmpl`；写入 `experiments/designs/{slug}-master.md`；
通过 `tools/research_wiki.py add-edge` 添加 `tested_by` 边；更新idea的
`linked_experiments`；重建 `context_brief` / `open_questions`；向
`wiki/log.md` 追加条目，注明 `/exp-design-dag` 所用架构 `<name>`。

### Report

输出标准DESIGN_REPORT，并追加：
`SciDAG: ran experiment architecture <name> (complexity c<N>, <k> LLM calls)`。

## Notes

- 调用 `scidag/` 中的SciDAG引擎；LLM配置与 `llm-review` 相同
  （`.env` 中的 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。
- DAG的 `test` 算子检查设计的**可行性/逻辑性**（无需oracle）；
  它不运行真实实验。实际执行仍由 `/exp-run` 完成。
