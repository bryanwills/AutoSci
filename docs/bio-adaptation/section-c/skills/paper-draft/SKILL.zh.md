---
description: 从 PAPER_PLAN 起草 LaTeX 论文：按节从 wiki 取材 + 生成 figures/tables + BibTeX 验证 + de-AI polish
argument-hint: <paper-plan-path> [--review] [--sections <section-numbers>]
---

<!-- bio-C10: 镜像自 i18n/zh/skills/paper-draft/SKILL.md，加入 C10（paper_style: cs|bio|clinical 模板与规范）草稿。
     真值源：i18n/zh/skills/paper-draft/SKILL.md。本路径不参与运行；要测试请先合回真值源。

     跨节依赖：
       /paper-plan（本批次同伴镜像）—— `paper_style` 从 PAPER_PLAN.md metadata 读
       A6 —— `estimated_cost` block 喂 bio Methods 的 "Resources" 子节
       A7 —— claim evidence type 决定 /paper-draft 写哪种 Results 子节文本
       A8 —— `reproducibility.dataset_versions` 与 RRID 喂 bio Methods 子节

     按 style 模板（计划中）位于：
       skills/paper-draft/references/templates/{cs,bio,clinical}/
     模板尚未编写；落地之前 /paper-draft 用下文行内默认生成 LaTeX，不匹配模板时写占位。 -->

# /paper-draft

> 从 /paper-plan 生成的 PAPER_PLAN.md 起草完整 LaTeX 论文。
> 按节写：每节从 wiki claims/experiments/papers/concepts 取材，生成 LaTeX + 图 + 表。BibTeX 从 DBLP/CrossRef <!-- bio-C10 --> *（bio/clinical 用 CrossRef/PubMed）* 抓（遵循 citation-verification）。
> 完成后做 de-AI polish（遵循 academic-writing）。
> 可选每节 Review LLM 审查。输出可编译的 paper/ 目录。
> <!-- bio-C10 --> 本 skill 从 PAPER_PLAN.md metadata 读 `paper_style`（cs / bio / clinical）；节序、figure 规范、引用风格、Review LLM 人格均按之分派。

## Inputs

- `plan`：PAPER_PLAN.md 路径（如 `wiki/outputs/paper-plan-sparse-lora-2026-04-08.md`）
- `--review`（可选）：启用每节 Review LLM 审查
- `--sections`（可选）：仅写指定节（如 `--sections 3,4` 只写 Method + Experiments）；用于增量写作

## Outputs

- `paper/` 目录（在 wiki 项目根下）：
  - `paper/main.tex` — 主文件（include 各节）
  - `paper/sections/{section-files}.tex` — 每节内容。<!-- bio-C10 --> *节文件名取决于 `paper_style`：*
    - **cs**：`introduction.tex`, `related_work.tex`, `method.tex`, `experiments.tex`, `conclusion.tex`
    - **bio**：`introduction.tex`, `results.tex`, `discussion.tex`, `methods.tex`（注意 Results 在前、Methods 末位）
    - **clinical**：`introduction.tex`, `methods.tex`, `results.tex`, `discussion.tex`（Methods 前置）
  - `paper/sections/appendix.tex`（如适用）
  - `paper/figures/` — 生成的图（PDF/PNG）
  - `paper/tables/` — 独立 table 文件（可选）
  - `paper/math_commands.tex` — 共享数学符号定义
  - `paper/references.bib` — 已验证 BibTeX 条目
- `wiki/log.md` — 追加日志

## Wiki Interaction

### Reads
- `wiki/outputs/paper-plan-*.md` — PAPER_PLAN（节大纲、证据图谱、figure plan、citation plan、**paper_style metadata**）<!-- bio-C10 -->
- `wiki/claims/*.md` — Statement, Evidence summary, Conditions of target claims, <!-- bio-C10 --> *与 `evidence[*].type` + `.grade` 用于 bio Results 子节文本*
- `wiki/experiments/*.md` — Results, Analysis, key_result, metrics 数据, <!-- bio-C10 --> *与 `setup.in_silico_or_wet`、`setup.cell_line`、`setup.force_field`、`statistical_protocol`、`estimated_cost.*` 用于 bio Methods 子节*
- `wiki/papers/*.md` — Method, Results, Related（作引用内容与 baseline 参考）
- `wiki/concepts/*.md` — Definition, Formal notation, Variants（支撑 Method 写作）
- `wiki/topics/*.md` — Overview, Timeline, SOTA tracker（支撑 Introduction 上下文）
- `wiki/ideas/*.md` — Motivation, Hypothesis（支撑 Introduction 中 gap 叙事）
- `wiki/people/*.md` — 作者姓名与机构（引用格式化）
- <!-- bio-C10（依赖 A1）--> `wiki/datasets/*.md` — dataset 名、版本、访问层级、license —— 直接序列化进 bio Methods 的 "Datasets and code availability" 子节
- `wiki/graph/edges.jsonl` — 关系图（构建论证逻辑链）
- `wiki/graph/open_questions.md` — 已知 limitations（写 Limitations 与 Future Work）
- `.claude/skills/shared-references/academic-writing.md` — 写作标准
- `.claude/skills/shared-references/citation-verification.md` — 引用规范

### Writes
- `paper/` 目录（所有文件）
- `wiki/log.md` — 追加操作日志

### Graph edges created
- 无（paper-plan 已建 derived_from edges）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/`）。

### Step 1: 初始化 paper 目录

1. 读 PAPER_PLAN.md，提取 venue、title、节列表、**`paper_style`**（从 metadata block —— 缺失则报错）。<!-- bio-C10 -->
2. 若 `paper/` 目录已存在：备份为 `paper.bak-{timestamp}/`；提示用户确认覆盖。
3. 创建目录结构：`paper/`、`paper/sections/`、`paper/figures/`，加上 `main.tex` / `math_commands.tex` / `references.bib` 占位。
4. 复制 venue 模板（如存在）：
   - `templates/{venue}.sty` 或 `templates/{venue}/`
   - <!-- bio-C10 --> 按 style 的内容模板从 `skills/paper-draft/references/templates/{paper_style}/` 复制（落地后）。落地前：终端报告中发 🟡 风格警告"模板未安装"，沿用下文行内默认。
   - 无模板：用通用 article class，在 main.tex 中标注须替换正式模板。
5. 生成 `math_commands.tex`：从 wiki/concepts/ 收集 Formal notation；统一向量、矩阵、集合、常用算子的符号定义。
6. 按 style 分派生成 `main.tex` 骨架：<!-- bio-C10 -->

   **cs**：（同 EN 镜像中的 cs 骨架，使用 `\bibliographystyle{plainnat}` 即 author-year）
   ```latex
   \documentclass{article}
   \input{math_commands}
   \usepackage{booktabs,graphicx,amsmath,hyperref,natbib}
   \title{<title>}
   \author{}
   \begin{document}
   \maketitle
   \begin{abstract}\end{abstract}
   \input{sections/introduction}
   \input{sections/related_work}
   \input{sections/method}
   \input{sections/experiments}
   \input{sections/conclusion}
   \bibliography{references}
   \bibliographystyle{plainnat}  % author-year
   \end{document}
   ```

   **bio**：<!-- bio-C10 --> 节序 Intro → Results → Discussion → Methods，使用 `naturemag` Vancouver 数字风
   ```latex
   \documentclass{article}
   \input{math_commands}
   \usepackage{booktabs,graphicx,amsmath,hyperref}
   \usepackage[numbers,super,sort&compress]{natbib}
   \title{<title>}
   \author{}
   \begin{document}
   \maketitle
   \begin{abstract}\end{abstract}
   \input{sections/introduction}
   \input{sections/results}
   \input{sections/discussion}
   \input{sections/methods}
   \bibliography{references}
   \bibliographystyle{naturemag}  % Nature numeric Vancouver
   \end{document}
   ```

   **clinical**：<!-- bio-C10 --> Methods 前置（NEJM/JAMA/Lancet 惯例），使用 `vancouver` style
   ```latex
   \documentclass{article}
   \input{math_commands}
   \usepackage{booktabs,graphicx,amsmath,hyperref}
   \usepackage[numbers,sort&compress]{natbib}
   \title{<title>}
   \author{}
   \begin{document}
   \maketitle
   \begin{abstract}\end{abstract}
   \input{sections/introduction}
   \input{sections/methods}    % Methods 前置（clinical 惯例）
   \input{sections/results}
   \input{sections/discussion}
   \bibliography{references}
   \bibliographystyle{vancouver}  % NEJM/JAMA/Lancet
   \end{document}
   ```

### Step 2: 生成图与表

按 PAPER_PLAN 的 Figure Plan 一项项处理：

1. **Diagram type**（架构图、机制 schematic）：
   - cs：TikZ / pgfplots；太复杂改 matplotlib 脚本
   - <!-- bio-C10 --> bio：BioRender 风格 mechanism schematic 通常用 Inkscape / Adobe Illustrator 起，PDF 导入；纯程序化 diagram 用 Inkscape SVG → PDF
   - <!-- bio-C10 --> clinical：CONSORT 图惯例（Enrolled / Allocated / Followed-up / Analyzed 各阶段方框）；用 TikZ 或导入 SVG

2. **Plot type**：
   - cs：线图（scaling）、条形图（ablation）、散点（定性）；caption 简短
   - <!-- bio-C10 --> bio：多面板（a, b, c, ...）+ **叙事性 caption**，含：
     - 每面板样本量
     - 复制类型（生物 vs 技术，从 `experiments.statistical_protocol == replicate_matrix_BxT`）
     - 统计检验名 + 显著性阈值（如 "n=4 biological replicates × 3 technical replicates; two-sided t-test, *P<0.05, **P<0.01"）
     - error bar 定义（SD vs SEM vs 95% CI）
   - <!-- bio-C10 --> clinical：森林图（亚组分析）、Kaplan-Meier 曲线（生存）、漏斗图（meta-analysis）；caption 点名分析人群（intent-to-treat / per-protocol）

3. **Table type**：
   - 用 booktabs 风（toprule, midrule, bottomrule）
   - cs：最优结果加粗，次优下划线
   - <!-- bio-C10 --> clinical：Table 1 **永远是**基线特征；列 = 治疗组 + Total + P-value；行 = 人口学 + 临床协变量，用合适的描述统计（连续变量 mean ± SD 或 median [IQR]；分类变量 n (%)）

### Step 3: 写各节

按 PAPER_PLAN 的**按 style** 大纲序写；指定 `--sections` 时仅写指定节。

**3a. 收集材料**（按 style 分派）

按节定义抽取 claims、wiki 页清单、planned figures/tables、citation list。读相关部分：

- **cs Introduction** → `wiki/ideas/{idea}.md#Motivation` + `wiki/topics/{topic}.md#Overview`
- **cs Related Work** → `wiki/papers/*.md#Related` + `wiki/concepts/*.md#Comparison`
- **cs Method** → `wiki/concepts/*.md#Formal_notation` + `wiki/claims/{claim}.md#Statement`
- **cs Experiments** → `wiki/experiments/*.md#Results` + `wiki/experiments/*.md#Analysis`
- **cs Conclusion** → `wiki/graph/open_questions.md` + `wiki/claims/*.md#Open_questions`

<!-- bio-C10 -->
- **bio Introduction** → wiki/ideas/{idea}.md#Motivation，但用**生物语言**（无等式）；从 `claims[*].evidence[*].type == clinical_validated` 找一个亮眼开篇事实
- **bio Results** → wiki/experiments/*.md#Results —— 每 claim 一个子节。按 `experiments[*].type`：
  - `validation` → 头条结果子节
  - `mechanism` → "We tested whether the predicted mechanism holds" 子节（通常用点突变或化学探针数据）
  - `dose_response` → 滴定子节带 EC50/IC50
  - `cross_context` → 泛化子节
  - `negative_control` → 折入 validation 子节的 caption（"a non-null negative control rules out X artefact"）
- **bio Discussion** → 头条发现 → 文献上下文 → 机制解读 → 显式 limitations（从 `wiki/graph/open_questions.md` 与 `wiki/claims/*.md#Conditions` 拉）
- **bio Methods** → **wiki 驱动的序列化，不是写作任务**：
  - Datasets 子节：序列化每个 `wiki/datasets/{slug}.md` 含 `versions[*].version`、`access`、`license`、`canonical_url`（A1）
  - Wet-lab assay 子节：从 `wiki/experiments/{slug}.md setup.cell_line`（CVCL ID）、正文中的 antibody RRID、`statistical_protocol == replicate_matrix_BxT` 的生物 × 技术复制数读
  - 计算子节：序列化 `setup.weight_version`、`setup.force_field`、`setup.solvent_model`、`setup.simulation_length`、`setup.random_seed_protocol`
  - 统计分析子节：序列化 `statistical_protocol` 取值与参数（bootstrap_ci 1000 resample、stratified_kfold k = min(5, n_positives) 等）
  - Resources 子节：序列化 `estimated_cost.*`（A6）—— gpu_hours、md_wallclock_hours、wet_lab_usd、fte_weeks、dataset_access_lead_time_days

<!-- bio-C10 -->
- **clinical Methods** → 类似的 wiki 驱动序列化，但前置；明确引用 NCT ID 与预注册来源（B2 `clinical_trial_for.metadata.nct_id`）
- **clinical Results** → 3.1 受试者流（Figure 1 CONSORT）、3.2 基线（Table 1）、3.3 主要终点、3.4 次要终点、3.5 安全
- **clinical Discussion** → 主要发现 → 与先验证据比较 → 优势与**限制（强制、显式）**→ 推广性 → 结论

**3b. 写 LaTeX**

遵循 `shared-references/academic-writing.md`：
- 按节的 paragraph plan 写
- 插入 `\cite{key}`（key 由 citation plan 映射）
- <!-- bio-C10 --> 引用按 `\bibliographystyle` 渲染：cs 用 `\citep{...}` author-year；bio/clinical 用纯 `\cite{...}` Vancouver 数字
- 插入 `\ref{fig:name}` / `\ref{tab:name}` 引用图表
- 用 `math_commands.tex` 中定义的符号
- 段落以主题句起
- cs Experiments：claim-first（"We claim X. To verify, we..."）
- <!-- bio-C10 --> bio Results：result-first 内嵌统计（"In ABC cells, treatment with the phospho-PROTAC reduced target abundance by 78% (Fig. 2a; n=4 biological replicates, two-sided t-test, P<0.001)"）。Figure 引用、样本量、统计常住同一句。

**3c. de-AI polish**

同旧。<!-- bio-C10 --> bio/clinical 论文尤其受益于去除 AI 风格 hedging —— bio 编辑对 "we delve into" / "this comprehensive analysis" 这类散文反应强烈。

**3d. 可选 Review LLM 审查（--review）**

启用时每节按 style 分派人格：

```
mcp__llm-review__chat:
  system: |
    {style 特定人格，见下}
  message: |
    ## Section: {section name}
    {LaTeX content}
    ## Paper style: {paper_style}                             <!-- bio-C10 -->
    ## Claims this section should support
    {claims from matrix}
    ## Review questions: {style 特定}
```

人格：
- **cs**："You are a senior ML researcher reviewing one section of a paper draft. Focus on: clarity, logical flow, claim-evidence alignment, notation consistency. Point out any remaining AI-sounding language patterns. Suggest specific rewrites for unclear passages."
- <!-- bio-C10 --> **bio**："You are a senior bio researcher reviewing one section of a paper draft for {Nature / Cell / eLife}. For Results: confirm result-first structure, sample sizes in-line with claims, statistical test named in captions, biological vs technical replicate distinction maintained. For Methods: confirm cell line CVCL IDs, antibody RRIDs, dataset version pinning, replicate matrix declaration. For Discussion: confirm explicit limitations and biological mechanism interpretation."
- <!-- bio-C10 --> **clinical**："You are a senior clinical reviewer for {NEJM / JAMA / Lancet}. For Methods: confirm NCT ID, pre-registration, primary endpoint definition, sample-size justification, pre-specified analyses. For Results: confirm CONSORT diagram, baseline table, ITT/per-protocol distinction, multiple comparisons handling. For Discussion: confirm explicit limitations (no hedging), generalizability statement."

按反馈做行内修订（不重写整节）。

### Step 4: 构建 bibliography

遵循 `shared-references/citation-verification.md`：
1. 收集各节的 `\cite{key}`
2. 按 PAPER_PLAN 的 citation plan 取 BibTeX
3. 排除未使用条目（不要 `\nocite{*}`）
4. 校验 BibTeX 格式
5. <!-- bio-C10 --> bio/clinical 论文还要校验 PMID 与/或 DOI 在 BibTeX 条目中存在 —— Vancouver 风格引用通常都要显示。两者皆缺 → 🟡 提示。
6. 输出统计：`references.bib: {N} entries, {M} verified, {K} [UNCONFIRMED]`

### Step 5: 全文交叉审查

完成后做 Review LLM 全文审查（人格按 style 分派，与 Step 3d 同；问题是论文级）：
- **cs**：Intro→Conclusion 故事一致；claim-evidence 串通；符号一致；图表引用；冗余
- <!-- bio-C10 --> **bio**：Results-first 叙事是否成立；mechanism 是否有 ≥2 个正交扰动支撑；适用时 dose-response 是否覆盖 ≥3 数量级；cross-context retention 阈值是否预注册；Methods 是否可复现（CVCL、RRID、版本固定）；Discussion limitations 是否显式
- <!-- bio-C10 --> **clinical**：预注册是否引用；主要终点是否按预注册方式分析；CONSORT 是否在；基线表是否完整；多重比较处理；limitations 是否显式

### Step 6: 收尾

1. 确认 `paper/` 下所有文件已写
2. 验证完整性：
   - `\input{sections/X}` 引用的文件存在
   - `\includegraphics{figures/X}` 引用的文件存在
   - 所有 `\cite{key}` 在 references.bib 中有对应条目
   - 所有 `\ref{label}` 有对应 `\label{label}`
3. <!-- bio-C10 --> **bio/clinical 专属完整性检查**：
   - bio Methods 序列化使用的 dataset 版本必须存在于对应 `wiki/datasets/{slug}.versions[]`（与 C8 lint 逻辑交叉对照）
   - clinical 论文的 NCT ID 必须匹配 `wiki/graph/edges.jsonl` 中的 B2 `clinical_trial_for` edge
4. 追加日志：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "paper-draft | {paper_style} {venue} '{title}' | {N} sections, {M} figures, {K} citations ({V} verified)"
   ```
   <!-- bio-C10：log 行带 paper_style 便于 grep -->
5. 终端输出：与旧同形，外加 `## Status` 下加一行 `Paper style: {cs | bio | clinical}`

## Constraints

- **每节从 wiki 取材**：不凭空生成；每条技术声明都要追溯到 wiki 页
- **BibTeX 遵循 citation-verification.md**：从 DBLP/CrossRef/S2 抓；不要从 LLM 记忆生成
- <!-- bio-C10 --> **bio/clinical BibTeX 优先 CrossRef + PubMed 而非 DBLP**：DBLP 对 bio venue 覆盖稀疏，DBLP-first 浪费时间。
- **de-AI polish 强制**：每节写完都要 polish，不可跳
- **figure 遵循 academic-writing.md**：色盲安全、字号 ≥ 8pt、向量格式优先
- <!-- bio-C10 --> **bio figure caption 含样本量 + 统计检验名**；clinical figure caption 点名分析人群
- **匿名投稿**：不写作者姓名、机构、致谢（按 venue 匿名要求）
- **禁 \nocite{*}**：只引用确实使用的条目
- **符号一致**：所有节用 math_commands.tex 中统一符号
- **覆盖前先备份 paper/**：不要直接覆盖
- **Wikilink → \cite 转换**：PAPER_PLAN 中的 [[slug]] 在 LaTeX 中转为 \cite{key}
- **table 用 booktabs**：无竖线或全格网
- <!-- bio-C10 --> **bio Methods 是 wiki 驱动序列化，不是写作任务**：cell line（CVCL）、抗体（RRID）、dataset 版本、force field、复制数、成本直接从 `wiki/` 拉。不要换说或编造。
- <!-- bio-C10 --> **`paper_style` 从 PAPER_PLAN.md 读，不再推断**：metadata block 缺该字段则报错并提示用户重跑 /paper-plan。

## Error Handling

- **PAPER_PLAN 找不到**：报错；建议先跑 /paper-plan
- **PAPER_PLAN 格式不完整**：列出缺失节；建议重跑 /paper-plan
- <!-- bio-C10 --> **PAPER_PLAN 缺 `paper_style` metadata**：报错并提示 "PAPER_PLAN was generated before C10 landed; rerun /paper-plan with --paper-style to regenerate, or manually add `paper_style: cs|bio|clinical` to the metadata block"
- **wiki 页找不到**（plan 中引用的 claim/experiment/paper 不存在）：警告并跳过该引用；标为 missing
- **figure 生成失败**（matplotlib 报错）：写占位 `% TODO: generate figure {name}`；继续其他节
- **所有 BibTeX 抓取失败**：用 [UNCONFIRMED] 占位；终端报告手动处理数量
- **Review LLM 不可用**（--review 模式）：跳过节级与全文审查；标 "unreviewed"
- **venue 模板找不到**：用通用 article class；在 main.tex 中标注
- **节超长**（超出 plan 页数预算）：警告；建议挪 appendix 或压缩
- <!-- bio-C10 --> **bio Methods 序列化时某 wiki/datasets/{slug}.md 不存在**：终端报告发 🔴 风格提示，并在该节写 `% TODO: dataset entry missing — author wiki/datasets/{slug}.md` 占位。不阻塞起草完成。
- <!-- bio-C10 --> **clinical 论文的 NCT ID 不在 edges.jsonl 中**：发 🔴 风格提示；写占位引用。用户必须在投稿前补 B2 边。

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/fetch_s2.py search "<title>"` — BibTeX fallback（S2 搜索）
- <!-- bio-C10 --> `python3 tools/fetch_crossref.py paper <doi>` — bio/clinical 论文的主 BibTeX 来源
- <!-- bio-C10 --> `python3 tools/fetch_pubmed.py paper <pmid>` — PubMed BibTeX（部分 venue 用 MeSH 词）
- `python3` — 跑 matplotlib figure 脚本

### MCP Servers
- `mcp__llm-review__chat` — 节级审查（可选 `--review`）+ Step 5 全文交叉审查；人格按 `paper_style` 分派 <!-- bio-C10 -->

### Claude Code Native
- `Read` — 读 wiki 页与 PAPER_PLAN
- `Glob` — 找 wiki 页
- `Write` — 写 paper/ 下文件
- `Bash` — 跑 figure 脚本，建目录
- `WebFetch` — DBLP / CrossRef / PubMed BibTeX 抓取

### Shared References
- `.claude/skills/shared-references/academic-writing.md` — 写作标准 + de-AI polish 规则 + figure 设计
- `.claude/skills/shared-references/citation-verification.md` — BibTeX 抓取流程 + [UNCONFIRMED] 协议

### Local References
- <!-- bio-C10 --> `skills/paper-draft/references/templates/cs/`（既有的隐式模式）
- <!-- bio-C10 --> `skills/paper-draft/references/templates/bio/`（计划中）
- <!-- bio-C10 --> `skills/paper-draft/references/templates/clinical/`（计划中）

### Called by
- `/research` Stage 5（论文写作阶段）
- 用户手动调用
