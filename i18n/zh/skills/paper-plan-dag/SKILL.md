---
description: SciDAG增强的论文规划 — 通过多智能体算子DAG（起草 + 审查 + 精炼 + 润色）而非单次规划来编译论文大纲，然后用与 /paper-plan 相同的契约写入PAPER_PLAN。适用于一次性起草不够充分的复杂或高风险大纲。
argument-hint: "<idea-slugs...> --venue <ICLR|NeurIPS|ICML|ACL|CVPR|IEEE> [--complexity 1-5] [--dag <name>] [--title <t>] [--mock]"
---

# /paper-plan-dag

> `/paper-plan` 的SciDAG增强版（论文§5）。写作阶段的首要目标是**证据保真度与精炼**：
> 大纲必须忠实地表达idea及其证据。本skill运行来自**写作DAG库**的**可复用算子DAG**，
> 围绕 **review→polish** 组合构建（起草稿独立经过审查和并行精炼，然后润色），
> 在大纲定稿前捕捉无据声明和结构性缺陷。它将结果返回到**与 `/paper-plan` 相同的产物契约** —
> `wiki/outputs/` 中的 `PAPER_PLAN.md`、manuscript记录和 `derived_from` 边 — 因此下游不会发生任何变化。
>
> 本skill是**增量式**的。它**不**修改 `/paper-plan`；对标准流程使用 `/paper-plan`，
> 当大纲足够复杂或风险足够高、值得进行多智能体审查时使用 `/paper-plan-dag`。

## Inputs

- `ideas`（必选）：目标idea的slug列表（空格分隔）；资格规则与 `/paper-plan` 相同（`validated`，或 `in_progress` 且有一个succeeded的实验）。
- `--venue`（必选）：目标会议/期刊（ICLR / NeurIPS / ICML / ACL / CVPR / IEEE）。
- `--complexity 1-5`（可选）：DAG规模。省略时使用**论文图示架构**（`review-polish`）。
- `--dag <name>`（可选）：从写作库中运行特定架构（覆盖 `--complexity`）。参见 `scidag/templates/writing/`。
- `--title <t>`（可选）：工作标题。
- `--mock`（可选）：离线确定性LLM（仅用于配线测试）。

## Outputs

与 `/paper-plan` 完全相同的契约：
- `wiki/outputs/paper-plan-{slug}-{date}.md` — PAPER_PLAN
- `wiki/manuscripts/{slug}.md` — manuscript记录（`status: drafting`）
- `wiki/graph/edges.jsonl` — `derived_from` 边（plan → ideas/papers）
- `wiki/graph/context_brief.md` — 重建
- **PAPER_PLAN_REPORT**（终端）— 另加所用的DAG架构

## 与 /paper-plan 的关系

`/paper-plan` 将Review LLM审查设为**必选**；本skill将审查提升为一等DAG算子，并与refine + polish配对。DAG产出大纲核心（叙事结构 + 章节计划）；`/paper-plan` 的Step 1（加载idea图谱）、Step 2（证据映射）、图表/引用规划以及持久化规则**原封不动地复用**。
请阅读 `/paper-plan` SKILL.md 中的"Outputs"、"Wiki Interaction"以及Step 1–2章节，并原样应用。

## Workflow

**前置条件**：工作目录为wiki项目根目录（包含 `wiki/`、`raw/`、`tools/`、`scidag/`）。

### Phase 1 — 加载idea图谱 + 证据映射（复用 /paper-plan Step 1–2）

遵循 `/paper-plan` Step 1（读取目标idea、其 `linked_experiments`、`origin_gaps` 中的concepts/topics、Approach sketch中引用的methods/papers）和Step 2（编译证据映射：idea → 证据 → 章节）。将其压缩为一份包含会议 + 页数限制、证据映射和候选叙事主线的**任务简报**。这是DAG的任务输入。

### Phase 2 — 运行写作DAG（替代 /paper-plan 起草 + 审查）

1. **选择架构**：
   ```bash
   python3 -m scidag.cli select --stage writing [--complexity N]
   ```
   若用户指定了 `--dag <name>`，直接使用该名称。较大架构
   （`full-review-suite`）适用于需要多角度审查的多idea论文。

2. **以任务简报运行DAG**：
   ```bash
   python3 -m scidag.cli run --stage writing --dag <name> \
       --task-file /tmp/paperplan_dag_task.md [--mock] --show-dag
   ```
   从 `===SCIDAG-ARTIFACT-BEGIN/END===` 标记之间提取产物（大纲：叙事结构 + 章节计划，已经过审查和润色）。

### Phase 3 — 图表 + 引用计划（复用 /paper-plan）

DAG产出叙事 + 章节；按照 `/paper-plan` 补充**图表计划**和**引用计划**（每个章节 → 所需的图表/表格；每个声明 → wiki证据 + 已验证的BibTeX）。保留 `/paper-plan` 的引用规范（`citation-verification.md`）。

### Phase 4 — 写入PAPER_PLAN（复用 /paper-plan 持久化）

组装完整的PAPER_PLAN.md（来自DAG的叙事 + 章节，加上图表和引用计划）并写入 `wiki/outputs/paper-plan-{slug}-{date}.md`；创建/更新 `wiki/manuscripts/{slug}.md`（`status: drafting`）；通过 `tools/research_wiki.py add-edge` 添加 `derived_from` 边；重建 `context_brief`；向 `wiki/log.md` 追加条目，注明 `/paper-plan-dag` 所用架构 `<name>`。

### Report

输出标准PAPER_PLAN_REPORT，并追加：
`SciDAG: ran writing architecture <name> (complexity c<N>, <k> LLM calls)`。

## Notes

- 调用 `scidag/` 中的SciDAG引擎；LLM配置与 `llm-review` 相同
  （`.env` 中的 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。DAG的 `review` 算子是 `/paper-plan` 必选Review LLM步骤在引擎内的对应物。
