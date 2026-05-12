---
description: 从 claim 图编译论文大纲：证据图谱 → 叙事结构 → 章节计划 + 图表计划 + 引用计划，强制 Review LLM 审查
argument-hint: <claim-slugs...> --venue <ICLR|NeurIPS|ICML|ACL|CVPR|IEEE|Nature|Science|Cell|NEJM|JAMA|Lancet|...> [--title <working-title>] [--paper-style cs|bio|clinical]
---

<!-- bio-C10: 镜像自 i18n/zh/skills/paper-plan/SKILL.md，加入 C10（paper_style: cs|bio|clinical）草稿。
     真值源：i18n/zh/skills/paper-plan/SKILL.md。本路径不参与运行；要测试请先合回真值源。

     跨节依赖：
       A4 —— bio domain 受控词；`paper_style` 自动检测规则读 `claims[*].domain` 与 venue 列表
       A6 —— `estimated_cost` block 在 bio 论文 Methods 章节的 "Resources" 子节中显式列出
       A7 —— claim evidence type `wet_lab_validated` / `clinical_validated` / `mechanistic_basis`
            决定 bio 模板的 Results 子节形态

     按 style 模板（计划中）位于：
       skills/paper-draft/references/templates/{cs,bio,clinical}/
     模板尚未编写 —— 作为后续工具落地。/paper-plan 仍按下文行内默认开 outline；/paper-draft 在模板落地后从模板生成 LaTeX。 -->

# /paper-plan

> 从 wiki claim 图编译论文大纲。
> 输入目标 claims（status: supported 或 weakly_supported），指定目标 venue，从 wiki 编译证据图谱 → 决定叙事结构 → 生成章节大纲 + 图表计划 + 引用计划。
> Review LLM 审查为强制步骤（充当 area chair 评估 outline 说服力）。
> 输出 PAPER_PLAN.md 到 wiki/outputs/。
>
> 关键区别：大纲是 claim-graph-driven —— 每个章节存在是因为它支撑某个 claim，不是因为论文惯例需要该章节。
>
> <!-- bio-C10 --> 大纲结构取决于 `paper_style`：`cs`（Intro → Related Work → Method → Experiments → Conclusion）；`bio`（Intro → Results → Discussion → Methods，Methods 末位且简化，Results 是主骨架）；`clinical`（Intro → Methods → Results → Discussion，Statistical Analysis 单列、Limitations 显式）。引用风格与作者列表期望按同一 dispatch。

## Inputs

- `claims`：目标 claim slug 列表（空格分隔）
  - 每个 claim 应为 status `supported` 或 `weakly_supported`
  - 若含 `proposed` 或 `challenged` 的 claim 给警告但继续
- `--venue`（必填）：目标 venue，决定页数限制与格式要求
  - cs：`ICLR` / `NeurIPS` / `ICML` / `ACL` / `CVPR` / `IEEE`
  - <!-- bio-C10 --> bio：`Nature` / `Cell` / `Science` / `Nature Methods` / `Nature Biotech` / `Nat. Commun.` / `eLife` / `bioRxiv`
  - <!-- bio-C10 --> clinical：`NEJM` / `JAMA` / `Lancet` / `BMJ` / `Annals` / `medRxiv`
- `--title`（可选）：工作标题；不指定时从目标 claims 生成
- <!-- bio-C10 --> `--paper-style {cs|bio|clinical}`（可选，默认 `auto`）：驱动按 style 的大纲模板、引用规范与 Review LLM area-chair 人格。`auto` 按以下规则挑选：
  - venue → cs（命中上文 cs 列表）、bio（Nature 家族 + bioRxiv）、clinical（NEJM 家族 + medRxiv）
  - 然后 `claims[*].domain`：A4 的 bio 取值（`structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics`）→ bio；`clinical-translation` → clinical；其余 → cs
  - 不一致时：发警告，**优先 venue**（venue 的格式要求不可商量，domain 不一致是内容问题不是结构问题）。用户可通过 `--paper-style` 覆盖。

## Outputs

- `wiki/outputs/paper-plan-{slug}-{date}.md` — 完整论文计划（PAPER_PLAN.md），<!-- bio-C10 --> *metadata block 中记录 `paper_style`*
- `wiki/graph/edges.jsonl` — 新 derived_from edges（plan → 源 claims/papers）
- `wiki/graph/context_brief.md` — 重建
- `wiki/log.md` — 追加日志
- **PAPER_PLAN_REPORT**（输出到终端）— plan 摘要

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — status, confidence, evidence list, conditions of target claims, <!-- bio-C10 --> *与 `evidence[*].type`（A7）+ `.grade` 一同用于 bio Results 子节映射*
- `wiki/experiments/*.md` — 支撑 claim 的实验（results, metrics, key_result），<!-- bio-C10 --> *外加 `setup.in_silico_or_wet`、`estimated_cost.*`、`statistical_protocol` 喂 bio Methods*
- `wiki/papers/*.md` — 证据来源论文（Method, Results, Related）
- `wiki/concepts/*.md` — 涉及的技术概念（支撑 Method 写作）
- `wiki/topics/*.md` — 研究方向上下文（支撑 Introduction 定位）
- `wiki/ideas/*.md` — 原 idea 的 motivation 与 hypothesis
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口（标注 paper limitations）
- `wiki/graph/edges.jsonl` — 关系图（构建叙事逻辑链）
- <!-- bio-C10（依赖 A1）--> `wiki/datasets/*.md` — dataset 访问层级与版本固定，呈现在 bio/clinical Methods
- `.claude/skills/shared-references/academic-writing.md` — 写作原则
- `.claude/skills/shared-references/citation-verification.md` — 引用规范

### Writes
- `wiki/outputs/paper-plan-{slug}-{date}.md` — 论文计划文件
- `wiki/graph/edges.jsonl` — derived_from edges
- `wiki/graph/context_brief.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `derived_from`：paper-plan → claims（计划基于哪些 claim）
- `derived_from`：paper-plan → papers（计划引用哪些 paper）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 加载 claim 图（Load Claim Graph）

1. 读所有目标 claim 的 `wiki/claims/{slug}.md`
2. 对每个 claim 收集 evidence list：
   - 每条 evidence 的来源（paper slug 或 experiment slug）
   - evidence type（supports / contradicts / tested_by / invalidates，<!-- bio-C10 --> *与 A7 的 bio 扩展：`wet_lab_validated` / `clinical_validated` / `mechanistic_basis` / `correlative` / `predicts`*）
   - evidence strength（weak / moderate / strong）<!-- bio-C10 --> *以及可选 `grade`（very-low / low / moderate / high）来自 A7*
3. 读对应 wiki 页：
   - `wiki/experiments/{source}.md` → key_result, metrics, outcome
   - `wiki/papers/{source}.md` → Method, Results
4. 从 `wiki/graph/edges.jsonl` 加载相关 edges 构建 claim 间关系
5. 读 `wiki/graph/context_brief.md` 取全局上下文
6. 读 `wiki/graph/open_questions.md` 标注已知 limitations

**Validation**：
- 任一目标 claim status 为 `proposed`：警告 "claim is unvalidated; paper may lack evidence support"
- 任一 confidence < 0.5：警告 "claim confidence is low; consider running more experiments first"
- 无任何实验证据支撑：报错 "at least one experimental result is required to plan a paper"

<!-- bio-C10 -->

### Step 1b: 解析 `paper_style`

在 Step 3 任何结构性决策之前先解析为 `{cs, bio, clinical}` 之一：

1. 已传 `--paper-style`：用之，结束。
2. 用上文 venue 列表把 `--venue` 映射到 tentative style。
3. 聚合 `claims[*].domain` 取主导 A4 桶：
   - 任一 `structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics` → bio
   - `clinical-translation` → clinical
   - 其他 → cs
4. venue 与 domain 一致：用一致值。不一致：发警告，**优先 venue**（venue 格式要求不可商量；domain 不一致是内容问题不是结构问题）。
5. 把解析后的 `paper_style` 写入 PAPER_PLAN.md 的 metadata block。

### Step 2: 编译证据图谱（Compile Evidence Map）

生成结构化矩阵 claims → evidence → sections：

```markdown
| Claim | Status | Confidence | Evidence Sources | Type/Grade | Strength | Paper Section |   <!-- bio-C10 -->
|-------|--------|-----------|-----------------|------------|----------|---------------|
| [[primary-claim]] | supported | 0.85 | exp-main, paper-A | tested_by / moderate | strong | Method + Exp 5.2 |
| [[supporting-claim-1]] | supported | 0.75 | exp-ablation-1 | wet_lab_validated / high | moderate | Results 3.2 |   <!-- bio-C10 -->
| [[mechanism-claim]] | supported | 0.7 | exp-mechanism | mechanistic_basis / moderate | moderate | Results 3.3 |   <!-- bio-C10 -->
```

按维度映射 claim 到论文结构：
- **Target claim** → 核心贡献，驱动 Abstract + Introduction + Method/Results
- **Decomposition claims** → 因素贡献，驱动 Ablation/Mechanism 子节
- **Contextual claims** → 背景知识，驱动 Related Work + Introduction
- <!-- bio-C10 --> **Mechanism / wet-lab claims**（A7 evidence type）→ bio style 中驱动专门的 Results 子节；cs style 中折入 Experiments

### Step 3: 决定叙事结构

遵循 `shared-references/academic-writing.md` 的沙漏原则：
1. 识别核心 storyline（Gap → Solution → Evidence → Impact）
2. 确定叙事角度（problem-driven vs. method-driven vs. data-driven，<!-- bio-C10 --> *bio 时也可能是 structure / mechanism / discovery / clinical*）
3. 建立 section → claim 映射（无 claim 支撑的章节是 filler，删除或合并）

### Step 4: 生成章节大纲

按 venue 格式要求**与解析后的 `paper_style`** 生成大纲。<!-- bio-C10 --> 每节包含 claims-addressed、paragraph plan、key citations、planned figures/tables。

<!-- bio-C10 -->

#### Style: cs（旧默认）

```markdown
## 1. Introduction (1.5 pages)
## 2. Related Work (1 page)
## 3. Method (2-3 pages)
## 4. Experiments (2-3 pages)
## 5. Conclusion (0.5 page)
```

（按节的 paragraph plan 与旧模板相同 —— 见真值源 SKILL.md。）

#### Style: bio

```markdown
## 1. Introduction (~1 页；4-6 段)
### Claims addressed
- Gap claim
- Contribution claim（target）
### Paragraph plan
1. 广义生物 / 临床上下文（"为什么这事重要"）
2. 具体知识缺口，明确"我们之前不知道什么"
3. 通俗语言描述概念性方法（不要等式）
4. 头条结果预览（1-2 句带最强数字）
5. （可选）Implication / impact
### Key citations
- {3-5 篇建立缺口与所用方法的论文}

---

## 2. Results (3-5 页 —— 主骨架)
### Claims addressed
- Target claim → Section 2.1（headline figure）
- 每个 supporting / decomposition claim → 自己的子节
### Subsection plan（每节一个 claim）
- 2.1 {Headline result} —— 由 [[target-claim]] 驱动；figure-first
- 2.2 {Mechanism / dose-response / cross-context} —— A7 mechanism / dose_response / cross_context evidence
- 2.3 {Ablation / negative-control} —— 由 decomposition claim 驱动
- 2.4 {Wet-lab validation 或 clinical correlate}
- （每子节：1 figure ± 1 table；约 0.5-1 页文字）
### Figures
- Figure 1：headline result + summary statistic + CI / replicate matrix
- Figure 2：mechanism schematic + supporting data
- Figure 3-N：每子节一个 figure
（每个 figure 必须在 caption 中含样本量、生物 vs 技术复制区分（适用时）、统计检验名）

---

## 3. Discussion (~1.5 页)
### Claims addressed
- 综合所有 target / supporting claims
- Limitations（来自 gap_map 与 claim conditions）
- 生物 / 临床相关性
### Paragraph plan
1. 用生物语言重述头条发现
2. 把结果置于先验工作上下文中（这是 bio 论文文献引用密度最高的地方）
3. 提出 mechanism / model
4. 显式 limitations（reviewer 一定会找）
5. Implications 与未来方向

---

## 4. Methods (~2 页，常被弱化；很多 bio venue 允许在 supplementary 写更长的 Methods)
### Claims addressed
- 复现性支撑（不引入新 claim；而是*让* claim 可被检验）
### Subsection plan（每个 assay / 计算 pipeline 一个）
- 4.1 数据与代码可用性（链到 wiki/datasets/{slug} versions[]；A1 依赖）
- 4.2 Wet-lab assay —— 每项：cell line（CVCL ID）、抗体（RRID）、试剂货号、生物 × 技术复制矩阵（C6 statistical_protocol）
- 4.3 计算方法 —— 模型版本、force field、dataset 版本固定、随机种子协议
- 4.4 统计分析 —— bootstrap CI / stratified k-fold / 复制聚合（按 C6）
- 4.5 计算 / 湿实验资源 —— gpu_hours / md_wallclock_hours / wet_lab_usd / fte_weeks（A6）
```

#### Style: clinical

```markdown
## 1. Introduction (0.5-1 页)
- 临床上下文、患病率、当前 SOC
- 本研究回答的具体问题
- 假设（常预注册）与主要终点

## 2. Methods (1.5-2 页 —— 前置，区别于 bio)
- 2.1 研究设计（RCT / 观察 / 回顾 / 前瞻）
- 2.2 受试者 —— 入组/排除标准、招募
- 2.3 干预 / 程序
- 2.4 终点 —— 主要、次要、安全
- 2.5 统计分析 —— 预注册计划、样本量论证、主分析 vs 敏感性分析
- 2.6 伦理与注册 —— IRB 批准、NCT ID（B2 依赖：clinical_trial_for edge metadata.nct_id）

## 3. Results (2-3 页)
- 3.1 受试者流（Figure 1：CONSORT 图）
- 3.2 基线特征（Table 1）
- 3.3 主要终点
- 3.4 次要终点
- 3.5 安全 / 不良事件

## 4. Discussion (1-1.5 页)
- 主要发现
- 与先验证据比较
- 优势与局限（显式；clinical 风格强制）
- 推广性
- 结论 / 启示

## （没有独立的 "Conclusion" 顶层节 —— 折入 Discussion 末段）
```

**页数预算**：按 `--venue` 分配（参 academic-writing.md 的 venue 表）；总章节页数 <= venue 主体 limit。Bio venue 常在页数外另设字数限制；两者都引用。

### Step 5: 图表计划（Figure Plan）

每张图按风格设计：
- **cs**：line plot（scaling 曲线）、table（main comparison + ablation）、架构图。caption 简短。
- <!-- bio-C10 --> **bio**：figure-first 叙事。每张图多面板（a, b, c, ...），头条图承载最强数据。caption 是*叙事性的*（常 4-6 句），含样本量、复制类型（生物 vs 技术）、统计检验名、显著性阈值。Mechanism schematic 通常是 figure 1 或 2。
- <!-- bio-C10 --> **clinical**：Figure 1 几乎一定是 CONSORT 受试者流图。Table 1 是基线特征。森林图 / Kaplan-Meier 曲线常见。caption 点名分析人群（ITT / per-protocol）。

### Step 6: 引用计划（Citation Plan）

引用规范按风格分派：
- **cs**：author-year（如 `\citep{vaswani2017attention}`）；典型论文 30-60 条引用。
- <!-- bio-C10 --> **bio**：Vancouver / 按出现序的数字（如 `\cite{ref}` 渲染为上标 `[1]`）。Nature 主体通常 30-50 条 + supplementary 中扩展引用；Cell 主体可以 80+。
- <!-- bio-C10 --> **clinical**：Vancouver，并显式声明试验注册 ID（NCT）与预注册（如 ClinicalTrials.gov / OSF）。临床试验论文典型 30-40 条引用。

1. 列出大纲中通过 `[[slug]]` 引用的所有 wiki paper
2. 对每篇 pre-fetch BibTeX：
   - DBLP 优先，然后 CrossRef，然后 S2 —— *bio paper 优先 CrossRef + PubMed E-utilities，因为 DBLP 对 bio venue 覆盖稀疏*   <!-- bio-C10 -->
   - 成功：记 BibTeX key + source
   - 失败：标 `[UNCONFIRMED]`
3. 生成引用覆盖报告
4. 对 [UNCONFIRMED] 给手动验证 URL 建议

### Step 7: Review LLM 审查（强制）

Review LLM 人格按 `paper_style` 分派：

```
mcp__llm-review__chat:
  system: |
    {style 特定人格，见下}
  message: |
    ## Paper Outline
    {Step 4 完整大纲}
    ## Resolved style: {paper_style}
    ## Evidence Map
    {Step 2 证据图谱}
    ## Figure/Table Plan
    {Step 5 计划}
    ## Citation Coverage
    {Step 6 报告}
    ## Questions for Review
    {style 特定问题}
```

人格（按 `paper_style` 选）：
- **cs**："You are an area chair at {venue} reviewing a paper outline. Assess: Is the narrative convincing? Does every section serve a clear purpose? Are the experiments sufficient to support the claims? Is the related work coverage adequate? Are there obvious gaps that reviewers will attack?"
- <!-- bio-C10 --> **bio**："You are an editor at {venue} (Nature family / Cell family / eLife) reviewing a paper outline. Assess whether the Results section is figure-first and tells a coherent biological story; whether each Results subsection has the right experimental signature (mechanism via point mutagenesis or chemical probe; dose-response; orthogonal validation; cross-context); whether sample sizes and statistics are reported; whether the Methods section will let an outsider reproduce the work; whether limitations are explicit."
- <!-- bio-C10 --> **clinical**："You are an editor at {venue} (NEJM / JAMA / Lancet) reviewing a clinical paper outline. Assess whether: pre-registration and ethics are clearly cited; primary endpoint is unambiguously defined and analyzed in the pre-registered way; CONSORT diagram is present; baseline characteristics table is comprehensive; analyses are pre-specified; limitations are explicit and not hedged. Reject overpromising or post-hoc reframing."

按 Review LLM 反馈调整大纲（增节、调整页数预算、补图表、修正叙事结构）。

### Step 8: 写入 Wiki

1. **生成 slug**：`python3 tools/research_wiki.py slug "<working-title>"`
2. **写 PAPER_PLAN.md**（包含 metadata 含 **paper_style**、Step 2 证据图谱、Step 4 完整大纲、Step 5 图表计划、Step 6 引用计划、Step 7 Review LLM 摘要）  <!-- bio-C10 -->
3. **添加 graph edges**（同旧）
4. **重建派生数据**（同旧）
5. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "paper-plan | {venue} {paper_style} paper outline for [[{slug}]] | claims: {claim-list} | citations: {verified}/{total}"
   ```
   <!-- bio-C10：log 行带上 paper_style 便于 grep -->
6. **输出 PAPER_PLAN_REPORT 到终端**（同旧 + `Paper style: {cs | bio | clinical}` 行 + Persona 标记）

## Constraints

- **--venue 必填**：页数与格式按 venue 不同显著
- **至少一项实验证据**：纯理论 claim 不足以撑实证论文
- **页数预算必须可行**：总章节页数 <= venue 主体 limit；超时压缩或挪 appendix
- **Review LLM 审查强制**：在大纲阶段抓问题成本最低，不可跳
- **所有引用来自 wiki**：引用计划中每篇 paper 必须存在于 wiki/papers/
- **claim → section 映射必须完整**：每个目标 claim 必须出现在至少一节
- **每节都要有 claim**：无 claim 支撑的节是 filler，删除或合并
- **graph edges 经 tools/research_wiki.py**：不手动改 edges.jsonl
- **引用用 [[slug]]**：大纲中所有引用用 wikilink 语法
- <!-- bio-C10 --> **`paper_style` 一次解析、写入而非 draft 时再推断**：解析后写进 PAPER_PLAN.md metadata，让 `/paper-draft` 直接消费。自动解析仅在 Step 1b 跑一次。
- <!-- bio-C10 --> **bio Methods 节从 A1/A5/A6/A7/C6 拉数据**：不从散文凭空生成 Methods —— 从 `wiki/datasets/` 拉 dataset version、从 `experiments[*].statistical_protocol` 拉复制数、从 `setup` 拉 force-field/cell-line/RRID、从 `estimated_cost` 拉资源。bio Methods 大体是 wiki 驱动的序列化，不是写作任务。
- <!-- bio-C10 --> **Clinical 风格要求 NCT 与预注册**：`paper_style == clinical` 时拒绝完成 plan，除非目标 claim 关联了带 `metadata.nct_id` 的 B2 `clinical_trial_for` edge，**或**用户明确把论文标为 observational（无须 NCT）。

## Error Handling

- 同旧，外加：
- <!-- bio-C10 --> **`paper_style` 解析不一致**：发警告，优先 venue，把两路信号都记入报告。
- <!-- bio-C10 --> **clinical 风格但无 NCT**：报错，除非用户明确传 `--paper-style clinical --observational`。
- <!-- bio-C10 --> **bio venue 但 cs 形态的 claim**（例如投 Nature 但所有证据都是 ML benchmark `tested_by`）：发 🟡 风格警告 venue 多半要求 mechanism / wet-lab / cross-context 证据；不阻塞。

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/fetch_s2.py search "<title>"` — Semantic Scholar 搜索（引用计划 fallback）
- <!-- bio-C10 --> `python3 tools/fetch_crossref.py paper <doi>` — bio paper 的主 BibTeX 来源
- <!-- bio-C10 --> `python3 tools/fetch_pubmed.py paper <pmid>` — bio paper 的 fallback；提供 MeSH 词

### MCP Servers
- `mcp__llm-review__chat` — Step 7 大纲审查（强制；人格按 `paper_style` 分派）

### Claude Code Native
- `Read` — 读 wiki 页
- `Glob` — 找 claims、experiments、papers
- `WebFetch` — DBLP / CrossRef / PubMed BibTeX 抓取（Step 6）

### Shared References
- `.claude/skills/shared-references/academic-writing.md` — 叙事结构与节设计原则
- `.claude/skills/shared-references/citation-verification.md` — 引用抓取与验证规则

### Local References
- <!-- bio-C10 --> `skills/paper-draft/references/templates/cs/`（计划中）
- <!-- bio-C10 --> `skills/paper-draft/references/templates/bio/`（计划中）
- <!-- bio-C10 --> `skills/paper-draft/references/templates/clinical/`（计划中）

### Called by
- `/research` Stage 5（论文写作阶段）
- 用户手动调用
