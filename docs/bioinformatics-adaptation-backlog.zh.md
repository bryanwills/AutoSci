# OmegaWiki — 生物信息学适配 Backlog

> 本文件汇总 OmegaWiki 中影响生物信息学使用的 CS 化设计，以及 2026-05-02 由 `/exp-design ptm-aware-degrader-target-nomination` 生成的 8 个实验的可行性审计。每条目带优先级：P0（阻塞 bio 工作或产生误导性输出）、P1（明显摩擦）、P2（锦上添花）。
>
> 逐条验证、逐条改造，每条目独立可处理。
>
> **覆盖范围**：A-G 节是基于一次 protein / PTM / drug-design 的 `/exp-design` 运行总结的，对该垂直方向覆盖较好，但**对生物信息学其他子领域覆盖不足** —— DNA 测序、转录组、表观基因组、单细胞、宏基因组、临床基因组、群体 / 统计遗传、系统发生组学。**H 节**（2026-05-02 新增）从通用 bio 实践推断这些子领域所需条目，但与 A-G 不同，H **尚未由 wiki 实际失败案例验证**。每条 H 项目应在 wiki 首次在该子领域 ingest 论文或跑 `/exp-design` 时重新验证；预期部分条目会被发现不需要或形状不同。
>
> **保持不变的部分**：9 类页面骨架、wikilink 语法、双向反向链接规则、log/index 约定、graph 必须经 tool 操作的纪律。生物信息学相关的适配是**增量**而非替换。
>
> **同步约定**：本文档与 `bioinformatics-adaptation-backlog.en.md` 互为镜像，任一改动需同步另一份。

---

## A 节 — Schema 扩展（页面模板与 frontmatter）

### A1 — [P0] 新增 `datasets/` 一类首位实体类型

**证据**：本次 `/exp-design` 全程频繁引用 **TernaryDB**、**PROTAC-DB**、**DegronMD**、**AlphaFold-DB**、**PhosphoSitePlus**、**dbPTM**、**UniProt**、**PDB**、**PROTAC-DB CRBN+VHL subset**，全部以纯文本形式出现，没有任何能 wikilink 的目标。后续在该领域生成的 idea 会一遍遍重新引入这些数据集，没有任何规范的位置去记录：(a) 数据集是什么、(b) 用了哪个版本、(c) 访问限制如何、(d) 在哪些 paper 中出现。

**修复**：新增 `wiki/datasets/{slug}.md`，frontmatter 草案：

```yaml
---
title: ""
slug: ""
aliases: []
tags: []
maturity: stable          # stable | active | emerging | deprecated
access: public            # public | registration | restricted | wet-lab-derived
versions: []              # 列表 {version, released, url, n_entries, notes}
canonical_url: ""
license: ""
key_papers: []            # 由 papers 反向链接而来
key_concepts: []
date_updated: YYYY-MM-DD
---
```

**影响**：`/ingest` 应自动检测数据集提及；`/exp-design` 应将 `setup.dataset` 自动指向 wikilink。

**验证**：把 **TernaryDB** 作为试点迁移；在邻近的 idea 上重跑 `/exp-design`；确认 dataset 引用变成 wikilink。

---

### A2 — [P1] 新增 `proteins/`（或扩展 `concepts/`）以承载 UniProt 锚定的实体

**证据**：本次引用的 **p53**、**CRBN**、**VHL**、**MDM2**、**IAP**、**EZH2**、**BTK**、**ABL1**、**BCL-XL**、**BRCA1**、**HIF1α**、**14-3-3**、**PCNA**、**FOXO3a**、**Pol-η**、**HER2** 都没有实体页。它们不是"概念"，而是有 UniProt 编号、序列、已知 PTM、结构、配体的具体基因产物。当前只在 paper / claim 正文里以纯文本出现。

**轻量修复**：在 `concepts/` 模板加可选字段 `gene_symbol`、`uniprot_id`、`pdb_ids`、`species`；如填写则 lint 检验格式。

**重型修复**：新建 `proteins/{uniprot-id}.md` 实体类型，使 `[[p53]]` 或 `[[P04637]]` 直接解析为 wikilink。

**建议**：先轻量。一旦蛋白引用突破 50 条且需要图查询（如"靶向激酶 X 的药物"），再升级到独立类型。

---

### A3 — [P0] `papers/` frontmatter 加入 bio 原生标识符

**证据**：当前 `papers/` 模板的规范标识符是 `arxiv: ""`。本 wiki 11 篇 paper 中，bio 相关的 6 篇（Drug Design、Ubiquitin Ligases、AlphaFold-DB 2024、Towards Proteome-Scale、MusiteDeep、From Data to Cure）**没有 arXiv ID**，但都有 DOI 或 PMID。当前模板的 CS 化标识符体系与 bio 错配。

**修复**：扩展 frontmatter：

```yaml
arxiv: ""                  # 保留（部分 bio paper 也走 bioRxiv → arXiv）
doi: ""                    # 新增 — bio 主标识符
pmid: ""                   # 新增 — PubMed ID
biorxiv: ""                # 新增 — bioRxiv DOI 后缀
pdb_ids: []                # 新增 — paper 引入的结构
uniprot_ids: []            # 新增 — paper 表征的蛋白
nct_ids: []                # 新增 — 提及的临床试验
gene_symbols: []           # 新增 — HGNC 符号
species: []                # 新增 — 模式生物
```

`/ingest` 应从 CrossRef/PubMed/EuropePMC 填这些字段，而不仅是 Semantic Scholar。

---

### A4 — [P1] `domain` 字段需要 bio 分类法

**证据**：`runtime-page-templates.en.md` 给出的 domain 示例值是 `NLP / CV / ML Systems / Robotics`。当前本 wiki 一半页面写的是 `Computational Drug Design / Chemical Biology`、`Cancer biology / Molecular oncology`、`Structural Bioinformatics`、`Computational Biology / ML for Science`。字符串字段是个权宜，没有受控词表，所以一致性会漂移。

**修复**：定义一个小型 bio 受控词表（建议：`structural-bio`、`chembio`、`comp-drug-discovery`、`cancer-bio`、`systems-bio`、`bioinformatics`、`clinical-translation`，加上现有 CS 槽位）。允许自由覆盖但 lint 对未在表的值发 warning，鼓励收敛。`/check` 已对 status 字段做 enum 检查，复用同一机制即可。

---

### A5 — [P0] `experiments/` 的 setup 块需要 bio 字段

**证据**：刚写的 8 个实验 setup 块都是 `{model, dataset, hardware, framework}` —— 纯 ML 流水线形状。所有 bio specifics 我都只能写到正文里：
- "AMBER ff14SB + phosaa14SB or equivalent force field"（力场选择）
- "50 ns explicit-solvent"（模拟时长 / 溶剂模型）
- "100-step minimisation + 1 ns NPT equilibration"（协议）
- "Boltz-2 (Jan 2026 weights) with native CCD-PTM tokens"（权重版本与 tokenization）
- 没有 species / cell line / assay type，因为这 8 个全是 in-silico

**修复**：扩展 `setup`，全部可选，skill 在适用时填入：

```yaml
setup:
  # 现有
  model: ""
  dataset: ""
  hardware: ""
  framework: ""
  # bio 扩展
  in_silico_or_wet: in_silico   # in_silico | wet_lab | mixed
  species: []                    # human | mouse | yeast | 等
  cell_line: ""                  # 优先用 Cellosaurus ID
  assay_type: ""                 # Y2H | AP-MS | cryo-EM | NMR | MD | docking | scoring
  force_field: ""                # 仅 MD
  solvent_model: ""              # explicit | implicit | vacuum
  simulation_length: ""          # 仅 MD
  weight_version: ""             # 多版本 ML 模型
  random_seed_protocol: ""       # ranking-shuffle | bootstrap | LOO-CV
```

---

### A6 — [P1] 计算成本估算超越 `estimated_hours`

**证据**：我把 `ablation-boltz2-ptm-vs-md-relaxed-route` 的 `estimated_hours` 写成 12。该实验是 25 个 tuple × 5 个 MD seed × 50 ns 显式溶剂 MD on CRBN-VHL 三元体（约 500 残基）。每次合理 wall-clock 是 24-48 GPU-h，**实际总计约 3000 GPU-h，差 250 倍**。`estimated_hours` 字段的单位与来源都没定义，等于乱猜。

**修复**：换成结构化成本块，用 bio 现实的维度：

```yaml
estimated_cost:
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0      # MD 经常是瓶颈，单独跟踪
  wet_lab_usd: 0             # 抗体、细胞培养、测序
  fte_weeks: 0               # 不可自动化的 postdoc/RA 时间
  dataset_access_lead_time_days: 0   # 注册、MTA、IRB
```

工具：在 `docs/bio-compute-references.md` 维护一个按 assay / MD 体系大小分类的参照表 —— 随经验积累更新。`/exp-design` 直接读它，而不是让模型猜。

---

### A7 — [P1] 证据类型与强度脱离 CS 化

**证据**：claim 的 `evidence` 列表当前 `type: supports | contradicts | tested_by | invalidates`，`strength: weak | moderate | strong`。Bio 证据更细：
- 临床试验阳性结果与单次体外检测不属同一证据等级。
- 机制性生化研究（点突变废活性）和相关性观察是定性不同的。
- GRADE 等级（very low / low / moderate / high）是医学领域的证据强度标准。

**修复**：增加类型 `wet_lab_validated`、`clinical_validated`、`mechanistic_basis`、`correlative`、`predicts`。在 `strength` 旁边加可选 `grade: very-low | low | moderate | high`。保留现有 `strength` 兼容旧数据。

---

### A8 — [P2] 涉及湿实验的实验需要可复现性元数据

**证据**：纯 in-silico 实验有 code commit + checkpoint hash 就够。但只要实验摄取了任何湿实验数据（V1 的 phospho-PROTAC 阳性集来自文献中的 degrader），可复现性就需要 antibody clone ID（RRID）、cell line ID（Cellosaurus）、plasmid ID（Addgene）、批次号等。当前都没追踪。

**修复**：在 `experiments/` 加可选 `reproducibility` 块：

```yaml
reproducibility:
  rrid: []                   # 抗体 / 试剂 RRID
  cellosaurus: []            # 细胞系 CVCL_xxxx
  addgene: []                # 质粒 ID
  pdb_versions: []           # 具体 PDB 条目 + 版本
  dataset_versions: []       # {dataset_slug, version, accessed_date}
```

---

## B 节 — Edge 类型扩展

### B1 — [P1] Bio 关系 edge

**证据**：刚为 8 个实验接 edge 时只用了 `tested_by`。当前 graph 无法表达 "drug X 靶向 protein Y"、"kinase A 磷酸化 substrate B"、"E3 ligase C 泛素化 substrate D" —— 这些都只能放正文。

**修复**：新增 edge 类型（paper / claim / concept / protein → protein）：
- `targets_protein`、`binds`、`inhibits`、`activates`、`degrades`
- `phosphorylates`、`ubiquitinates`、`methylates`、`acetylates`（PTM 专用）
- `is_substrate_of`（上述四个的反向）

应与其他 semantic edge 一样要求 `confidence: high|medium|low`。

---

### B2 — [P1] 验证 / 转化层 edge

**证据**：诸如 "asciminib 已在 CML/Ph+ ALL 获 FDA 批准"、"tazemetostat 已在 epithelioid sarcoma 获 FDA 批准" 等内容只在正文。Graph 无法回答 "哪些 claim 有 FDA 批准的药作为证据"。

**修复**：新增 edge：
- `clinical_trial_for {nct_id, phase}`
- `fda_approved_for {indication, year}`
- `validates_in_species {species}`

---

### B3 — [P2] 实验到数据集版本的来源 edge

**证据**：TernaryDB 总有一天会出 v2，基于 v1 校准的 Phase-0 noise floor 对 v2 不再成立。当前没有 `dataset_version_used` edge。

**修复**：实验引用数据集时同时加 `dataset_version_used {slug, version}`。与 A1（datasets/）和 A6（成本 / 版本追踪）联动。

---

## C 节 — Skill 工作流缺陷

### C1 — [P0] `/ingest` 的形状围绕 arXiv / Semantic Scholar 设计

**证据**：bio paper（本 wiki 中 6 篇）多有 DOI + PMID + journal，但无 arXiv。Semantic Scholar 对 bio 覆盖中等，规范源是 PubMed、EuropePMC、bioRxiv、medRxiv。

**修复**：在 `/ingest` 中：
1. 检测输入是 DOI / PMID / bioRxiv URL / PMC URL，相应路由。
2. 增加 fallback 链：CrossRef API → PubMed E-utilities → EuropePMC → bioRxiv API → DeepXiv → Semantic Scholar。
3. 自动填充 A3 的 bio 标识符字段。
4. 跑一遍 NER（轻量 bio-NER 模型或 LLM-prompt），抽取 gene 符号、protein 名、drug 名、disease 词；预填建议 wikilink。

---

### C2 — [P1] `/discover` 应索引 bio 语料库

**证据**：`session-resume.md` 已记录 "DeepXiv search index is sparse for biology/structure domain — keep WebSearch as primary"。这是已知降级；本 session 没被阻塞但发现质量远不如 CS。

**修复**：`/discover` 应并行查询 PubMed E-utilities、EuropePMC、bioRxiv、Semantic Scholar、DeepXiv，以 DOI/PMID 去重合并。Bio 研究者在 discover 阶段需要召回大于精确。

---

### C3 — [P1] `/ideate` 的 banlist 需要 domain scoping

**证据**：本 wiki banlist 已含 `ptm-site-disorder-predictor`，原因 "saturated by SAPP / PhosAF / GraphPhos / AstraPTM2 / DeepPCT / MTPrompt-PTM"。这些工具饱和了**单 PTM 磷酸预测**子空间，但同一架构家族在植物生物学、微生物 PTM、跨物种迁移中可能并不饱和。当前 banlist 是全局的，没有 `scope` 字段。

**修复**：在 failed idea 元数据中加 `scope`：`species`、`disease_area`、`data_regime`（高数据 / 低数据）。Banlist 仅在 scope 重叠时命中。

---

### C4 — [P0] `/exp-design` 块分类是 ML 流水线形状

**证据**：4 类块（baseline / validation / ablation / robustness）适用于 ML 方法，但本次缺失了 bio 自然的块类型：
- **negative control**（sham / scrambled —— 与 "PTM-blind baseline reproduction" 不同；更像安慰剂组）
- **mechanism / MoA**（预测的因果机制是否真成立？通常通过点突变或化学探针验证）
- **dose-response**（剂量梯度 —— 与超参扫描不同）
- **cross-organism / cross-cell-line generalization**（与 ML 的 "cross-dataset" 类似但失败模式不同）

**修复**：扩展类型枚举为 `negative_control | mechanism | dose_response | cross_context`。在 SKILL.md 中相应地提示。

---

### C5 — [P0] `/exp-design` 不区分湿实验与 in-silico

**证据**：刚设计的 8 个实验全是 in-silico。但源 idea 引用了真实的实验 phospho-PROTAC（phospho-BCL-XL family）作为 held-out 阳性集 —— 这些数据靠湿实验产生。后续在该领域的 idea 不可避免会需要自己的湿实验验证步骤。Skill 从未问过 "这个 idea 是否需要新的湿实验数据"。

**修复**：在 Step 1（Load Context）加湿实验依赖探测：扫描 idea hypothesis 中的 "in cell"、"cellular target engagement"、"in vivo"、"tumor regression"、"binding assay" 等词。命中则提示用户：是否有湿实验访问？有则规划湿实验块；无则把 idea scope 收缩为 retrospective-only 并把约束写进 `conditions`。

---

### C6 — [P1] `/exp-design` 的统计默认值是 ML 形状

**证据**：skill 写 ">= 3 random seeds" for validation/ablation。我的 V1 中 n_test ≈ 50 phospho-PROTAC，多 seed ranking-shuffle 还行；但更大的问题是 bio 测试集常常 n < 20 且类别不平衡。Bio 标准做法是 bootstrap CI + leave-one-out CV + stratified CV —— skill 一字没提。

**修复**：在 skill prompt 中加："若 n_test < 50，默认使用 bootstrap CI（1000 次重抽）+ stratified k-fold（k = min(5, n_positives)）；仅多 seed 不够。" 另加："对湿实验 assay，默认 >= 3 biological × >= 3 technical replicates，并明确指出哪个是哪个。"

---

### C7 — [P1] `/exp-run` 目录布局假设 train.py

**证据**：CLAUDE.md 写 "Experiment code goes in experiments/code/{slug}/: /exp-run writes code to this path (train.py, config.yaml, run.sh, requirements.txt)"。MD 实验自然的文件是 `mdrun.sh`、`system.gro` / `system.pdb`、`system.top`、`mdp/*.mdp`，不是 train.py。湿实验的规范产出是 `protocol.md` 加针对结果 CSV 的 `analysis.ipynb`。

**修复**：扩展 `/exp-run` SKILL.md，根据 setup type（ML / MD / 湿实验 / docking）写出对应的目录布局。模板分别放在 `skills/exp-run/references/templates/{ml,md,wet-lab,docking}/`。

---

### C8 — [P1] `/check` 缺乏 bio 专用 lint

**证据**：`/check` 在本 wiki 跑得干净，但缺以下能抓出真实 bug 的 bio 专用结构检查：
- **PDB ID 格式**（4 字符如 `6XYZ` 或 8 字符扩展）
- **UniProt accession 格式**（regex `^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$`）
- **数据集版本过期**（实验引用的 `dataset_versions` 与 `datasets/{slug}.md` 的 `versions:` 列表对照）
- **物种错配**（实验用 mouse 数据但父 claim 关于 human therapeutics）
- **力场来源**（`assay_type: MD` 的实验必须填 `force_field`）

**修复**：新增 `tools/lint_bio.py` 实现以上检查；`/check` 在出现任何 bio 字段时调用。

---

### C9 — [P1] `/novelty` 应对 bio 类 claim 查询 PubMed

**证据**：`/novelty` 当前用 WebSearch + Semantic Scholar + Review LLM。Bio prior art 绝大部分在 PubMed（>3000 万摘要），Semantic Scholar 只覆盖一部分。缺 PubMed 覆盖意味着 bio 类 prior-art 撞车被 under-report。

**修复**：把 PubMed E-utilities 查询作为并行的 novelty channel；对生物学声明给 PubMed 命中满权重。

---

### C10 — [P2] `/paper-draft` 与 `/paper-plan` 假设 CS paper 结构

**证据**：本次未涉及，但底层假设很重要。ML paper 走 Introduction → Related Work → Method → Experiments → Discussion；bio paper 走 Introduction → Results → Discussion → Methods（Methods 常放最后且弱化；Results 是主骨架）。引文风格：bio 用 Vancouver（按出现顺序的数字）；CS 用 author-year。作者列表：bio 常 20-100 人；CS 极少超 10 人。

**修复**：给 `/paper-plan` 加 `paper_style: cs | bio | clinical` 参数；`/paper-draft` 下游消费。模板放在 `skills/paper-draft/references/templates/{cs,bio,clinical}/`。

---

### C11 — [P2] `/rebuttal` 应跟踪承诺补做的湿实验

**证据**：本次未涉及，但 bio 审稿人例行要求补做湿实验作为接收条件，这些承诺会变成可跟踪的交付物。当前 `/rebuttal` 只产出文字，没有机制为每个承诺的补做实验生成一个新的 `experiments/{slug}.md` 页面。

**修复**：当 rebuttal 承诺新实验时，`/rebuttal` 可选地调用 `/exp-design` 生成实验页脚手架，并带上 `triggered_by_rebuttal: <paper-id>` 来源字段。

---

## D 节 — 约定冲突

### D1 — [P1] Phase-N（bio）vs Stage-N（CS）编号

**证据**：源 idea 用 **Phase-0 / Phase-1 / Phase-2**，是药物发现的标准约定（Phase 0 = 临床前 pilot；Phase 1-3 = 临床试验阶段）。`/exp-design` skill 强制使用 **Stage-0 / Stage-1 / .../ Stage-4**（sanity / baseline / validation / ablation / robustness）。我在报告中不得不互译（"Phase-0 → Stage 2a"），在一个 "Phase 1" 已有固定含义的领域里，这种叠用会引发混淆。

**修复**：把 skill 内部阶段重命名为 **Block-A / Block-B / Block-C / Block-D / Block-E**（或 "Step 1..N"），把 "Phase" 留给用户领域里的原本含义。同步更新 SKILL.md、决策门图、EXPERIMENT_PLAN_REPORT 模板。

---

### D2 — [P2] Maturity 量表需要 bio 等级

**证据**：`concepts/` 的 `maturity: stable | active | emerging | deprecated` 是 ML feature flag 风格。Bio 概念的等级谱不同：一项发现可以是 `consensus`（教科书）、`well-supported`（综述级多研究）、`contested`（争议中）、`hypothesis`（单次原始报道）、`falsified`（已被反驳但仍被引）。"Stable" 不能很好地映射到一个有争议但研究极多的发现。

**修复**：加入 bio 等级可选值；允许 concept 选用 CS 或 bio 任一谱系。lint 在混用时 warn。

---

## E 节 — 我（模型）输出中的 CS 化烙印

这些**不是** skill bug，是模型用 CS 框架推 bio 的局限。值得记录，因为它们会沉淀进 wiki，成为 wiki 风格的一部分：

### E1 — 把成功标准写成百分比

我给 B1 写 "baseline mean abs deviation < 5%"。对 DeepTernary 分数复现合理。但对细胞 assay，±5% 不现实 —— IC50 差 2 倍在大部分 bio 语境里仍算可复现。需要按领域定制成功标准的指引。

### E2 — 把 multi-seed 当作规范的统计重复

Multi-seed 是随机化 ML 训练的属性。对纯确定性的 scorer inference（DeepTernary on a fixed structure），多个 "seed" 不增加分数信息，只是 ranking shuffle 的随机化。我在 V1、A1 等地方写 "5 seeds" 的位置，bootstrap CI 才更恰当。

### E3 — 把 confidence 写成单一 0.0-1.0 数

我把两个新 claim 设成 `confidence: 0.3`。对 bio claim，单数字混淆了：(a) 机制为真的先验概率、(b) 支撑测量的精度、(c) 对患者群体的可推广性。A7 的 evidence-strength 重构能部分解决。

---

## F 节 — 今日设计的 8 个实验的可行性审计

用户因时间无法实跑。以下是每个实验的预飞行风险评估：(a) 计算量是否现实、(b) 科学陷阱、(c) 实跑前应做的修正。

### F1 — `deepternary-baseline-ternarydb-crbn-vhl-reproduction`（Stage 1 baseline）

- **计算量**：4 GPU-h 在 checkpoint + data 公开的前提下现实。✓
- **风险**：TernaryDB test-split 的标签未必与 paper 完全对得上。DeepTernary repo 的 `test/` 目录可能就是 paper 的 split，但要逐 tuple ID 比对 Supplementary Table S2。
- **预修复**：跑前写 `verify_split.py`，断言 repo 中每个 test-tuple ID 都在 paper 的 supplementary 表里出现。失败则 baseline 复现没有意义。

### F2 — `phase0-noise-floor-calibration-deepternary-ptm-perturbations`（Stage 2a，承重门）

- **计算量**：24 GPU-h 对 ~100 POI × 200 次 inference 现实。
- **风险（P0）**：我写了 "≈80 Da, ≈3 Å radius — neutral, no charge, no H-bond donors/acceptors" 作为扰动化学。**真实的磷酸基团在生理 pH 下是二价阴离子，能形成多个氢键。** 化学惰性的 mock 会**低估** noise floor —— scorer 对真实磷酸的响应包含来自电荷 / 氢键 / 特定几何的贡献，mock 不去探针。我设的 Phase-0 会出现假阳性。
- **预修复**：把 "neutral mock" 换成一个真实 PTM 类似物的小型库，放在化学合理的位置（phospho-Ser/Thr/Tyr、methyl-Lys 在随机非修饰 Lys 上）。每对 PTM-position 多次重复。Noise floor 是 "真实 PTM 在随机非修饰位点" 的方差，不是 "mock 在随机表面位置" 的方差。这才匹配我们想要对照的实际 scorer 扰动分布。

### F3 — `calibrated-deltapternary-phospho-protac-ranking`（Stage 2b 主验证）

- **计算量**：16 GPU-h 假设 Boltz-2 inference 主导。约 50 (POI, E3, PROTAC) × 5 seed × {WT, PTM} → 500 次 Boltz-2 推理。每次按 ~30 min 算 CRBN 三元体，**约 250 GPU-h，不是 16，估算差 ~15 倍**。
- **风险（P0）**：我把阳性集描述为 "true experimental phospho-PROTACs (~8-10) + synthetic positives from kinase-substrate phospho-degron pairs (~30-50)"。**把这两个总体混进单个 AUC 在统计上很危险** —— synthetic 阳性容易（kinase-substrate 关系众所周知），真实实验 phospho-PROTAC 困难（要熬过药化优化）。Headline AUC 会被 synthetic 多数派抬高。
- **预修复**：并列报告两个 AUC（仅真实阳性；仅 synthetic 阳性）。Headline 是真实阳性 AUC。Synthetic AUC 仅作 sanity check，证明流程能侦测易例。
- **风险（P1）**："matched negatives" 应在 POI MW + linker 长度 + E3 ligand 化学三个维度匹配。我只指明前两个。E3 ligand 化学错配会泄漏信号。

### F4 — `ablation-uncalibrated-vs-calibrated-deltapternary`（Stage 3）

- **计算量**：4 GPU-h（缓存分数，仅重排），合理。✓
- **风险**：低。自包含；只需 F3 的缓存分数。
- **预修复**：除 F3 自身的修复外无。

### F5 — `ablation-boltz2-ptm-vs-md-relaxed-route`（Stage 3）

- **计算量（P0）**：我写 12 GPU-h。**实际约 3000 GPU-h。** 25 tuple × 5 MD seed × 50 ns 显式溶剂 MD on CRBN-VHL 三元体（~500 残基，~50k 原子含溶剂），每次在常规硬件上 24-48 GPU-h。**差 250 倍。** 当前 scope 在没有大量集群时不可行。
- **预修复方案**：
  1. 缩到 5 tuple × 3 MD seed × 20 ns（仍然不轻：~150-300 GPU-h，可行）。
  2. 用隐式溶剂（GBSA）换 10× 加速，代价是 PTM 区域精度 —— route 比较可接受，主机制声明不行。
  3. 用 Boltz-2 + 仅侧链 repacking 作为 "non-Boltz-2-PTM-token" baseline，绕开 MD 成本。不太忠实于源 idea 但可行。
- **风险（P1）**：50 ns 对捕捉 PTM 诱导的重排来说短，特别是 disorder-to-order 转变的底物（如 14-3-3 结合）。route 可比性的声明可能仅在稳定 / 预成型结合模式下成立。

### F6 — `ablation-deepternary-vs-protac-stan-scorer`（Stage 3）

- **计算量**：16 GPU-h 现实。✓
- **风险（P1）**：PROTAC-STAN 未必有公开 checkpoint，scope 之前先确认。
- **风险（P1）**：每个 scorer 各有自己的 Phase-0 noise floor。"mini-Phase-0"（100 扰动 × ~100 POI）是真实工作量，应单独入预算。
- **预修复**：确认 checkpoint 可用；mini-Phase-0 单独按 +6 GPU-h 入账。

### F7 — `robustness-cross-ptm-type-ubiq-methyl`（Stage 4）

- **计算量**：16 GPU-h 对甲基化 track（小修饰）现实，但**对泛素化 track 不现实**。Mono-Ub 是 ~8.5 kDa —— Boltz-2 接 Ub 再打分的扰动远比源 idea 的 noise-floor 模型设想的大。
- **风险（P0）**：**ΔpTernary-as-noise-perturbation 的框架在泛素化下崩塌。** Ub 是一个 domain，不是侧链修饰。用 ~8.5 kDa "扰动" 做 noise-floor 校准，得到的 null distribution 由 Ub 自身的质量主导；校准后阈值无意义。流程的数学不能迁移。
- **预修复**：把这个实验拆成两个：
  1. **甲基化 track**（≈14-42 Da）：与磷酸同协议，Phase-0 noise floor 按甲基质量缩放。
  2. **泛素化 track**：另立一套验证协议 —— 比如 "Boltz-2 mono-Ub-conjugated POI 结构相比 WT，在 DeepTernary 相关的界面特征上是否多于 mono-Ub 质量本身能解释的差异？"。这是不同的科学问题，可能更适合作为独立 idea，而不是本 idea 下的 robustness。

### F8 — `robustness-mutant-isoform-track-y220c-r175h`（Stage 4）

- **计算量**：12 GPU-h 现实。✓
- **风险（P0）**：**Boltz-2 训练数据泄漏。** p53 突变体 Y220C 与 R175H 研究极广；突变 p53 结构很可能在 PDB 中（也就在 Boltz-2 训练数据里）。"从序列预测突变 POI 结构" 不是预测，是召回。该 track 的 headline AUC 被污染。
- **预修复**：跑前查 Boltz-2 训练数据 manifest（若已发布；未发布则用 PDB 查 `p53` + `Y220C` / `R175H` 的存档日期，与 Boltz-2 权重截止时间交叉对比）。确认泄漏则 pivot 实验：(a) 在突变 track 完全弃用 Boltz-2，改用 AlphaFold2（不同训练截止）；或 (b) 用 Boltz-2 训练截止之后才发布的全新 mutant-isoform PROTAC（集合很小）。
- **风险（P1）**：n=6-10 对可靠 AUC 太小。用 bootstrap CI 至少 1000 次重抽；报点估计旁带 95% CI。

### 总结表

| 实验 | 计算量是否现实 | 最严重风险 | 实跑前动作 |
|------|---------------|------------|------------|
| F1 baseline | OK | split 不一致 | 验证 split ID |
| F2 noise-floor | OK | mock 化学过于温和 | 用真实 PTM 类似物在随机位点 |
| F3 主验证 | **预算差 15×** | 真实与 synthetic 阳性混合 | 报双 AUC，修 matched negatives |
| F4 校准消融 | OK | 低 | 无 |
| F5 MD 路线消融 | **预算差 250×** | 当前 scope 不可行 | 缩 scope 或 implicit solvent |
| F6 scorer 替换 | OK | PROTAC-STAN checkpoint 可得性 | 确认访问；预算 mini-Phase-0 |
| F7 跨 PTM 鲁棒性 | 甲基化 OK，泛素化崩 | Ub 框架失效 | 拆成两个实验 |
| F8 突变体鲁棒性 | OK | Boltz-2 训练数据泄漏 | 泄漏审计；考虑替换为 AF2 |

---

## H 节 — 蛋白 / 药物设计之外的 bio 子领域（外推性，未经验证）

> **注意**：本节条目**未由** wiki 实际失败案例验证，是从通用生物信息学实践外推到 wiki 尚未涉及的子领域。在实际投入前，应在该子领域跑一次 `/ingest` 或 `/exp-design`，再重新校准每条 H 项目。

### H1 — [P0] `experiments/` setup 加测序模态字段

**证据**：A5 给 protein 端实验加了 `species`、`cell_line`、`assay_type`。组学实验对应的字段是测序模态、平台、参考基因组版本、测序深度、样本量、cohort 描述 —— 当前 setup 块都没有位置安放。

**修复**：在 `experiments/` setup 中增加可选 `sequencing` 子块：

```yaml
sequencing:
  modality: ""              # bulk-rna-seq | sc-rna-seq | spatial-rna | wgs | wes | atac-seq | chip-seq | wgbs | hi-c | 16s | shotgun-metagenomics
  platform: ""              # illumina-novaseq | ont | pacbio | 10x-chromium
  reference_genome: ""      # GRCh38 | T2T-CHM13 | mm39 | 等
  read_length: 0
  paired_end: true
  depth: ""                 # 平均覆盖度（WGS）或 reads/cell（scRNA）
  n_samples: 0
  cohort_descriptor: ""     # 人类可读，如 "TCGA-BRCA n=1098"
```

**验证**：首次 `/ingest` 测序论文时，确认这些字段能覆盖论文实际报告的内容。

---

### H2 — [P0] `papers/` / `concepts/` / `claims/` 加基因组学标识符

**证据**：A3 加了 DOI、PMID、PDB、UniProt、NCT、gene 符号、species —— 都锚定在蛋白端。基因组学论文锚在另一套标识符栈上。

**修复**：在 `papers/`、`concepts/`、`claims/` frontmatter 加：

```yaml
genomic_ids:
  ensembl: []        # ENSG... / ENST... / ENSP...
  refseq: []         # NM_... / NP_... / NR_...
  entrez: []         # 数字 Gene ID
  dbsnp: []          # rs... 变异 ID
  hgvs: []           # 标准变异记法（c. / p. / g.）
  clinvar: []        # ClinVar variation ID
  cosmic: []         # COSMIC mutation ID
  go_terms: []       # Gene Ontology ID（GO:NNNNNNN）
  kegg: []           # KEGG pathway / map ID
  reactome: []       # Reactome pathway ID
```

**影响**：使 `/check` 能 lint 标识符格式；使 `/discover` 能按变异 ID 查询；使跨论文聚合可行（如"所有研究 rs334 的论文"）。

---

### H3 — [P0] 测序 cohort 数据集补 `datasets/` 条目

**证据**：A1 已增设 `datasets/` 实体类型。测序方向的规范条目包括 **TCGA**、**GTEx**、**ENCODE**、**Roadmap Epigenomics**、**GEO**、**SRA**、**ENA**、**gnomAD**、**UK Biobank**、**1000 Genomes**、**HCA（Human Cell Atlas）**。每个有不同访问层级（public / 注册 / restricted / IRB 必需）、引用要求、版本节奏。

**修复**：A1 schema 已支持 versioning + access tier，只需填充。首次 ingest 组学论文时预 seed 主要 cohort。

**验证**：确认 `access: restricted` 能正确触发下游 `/exp-design` 标记数据集有 lead time，`/exp-run` 启动前需准备时间。

---

### H4 — [P0] `/exp-design` 加基因组学统计默认

**证据**：C6 为蛋白端小 N 实验加了 bootstrap CI / stratified CV。基因组学有自己应该被 skill 识别的默认值：
- GWAS 全基因组显著性阈值：**p < 5×10⁻⁸**
- 多重检验校正：**Benjamini-Hochberg FDR** 通用；指明 q 值阈值（一般 q < 0.05）
- **功效分析**对任何 cohort 研究都是必需的；n 必须有理由
- 生存终点：**Kaplan-Meier + log-rank**；**Cox proportional hazards** 含 PH 假设违反检查
- 差异表达：log fold-change 阈值（一般 |log2FC| > 1）**与**校正 p 值**并列**报告，不互相替代

**修复**：扩展 C6 的提示："若 `setup.assay_type` 匹配任一基因组学模态（H1 中 `modality` 列出的值），默认使用 BH-FDR 多重校正；GWAS 用 5e-8 阈值并预注册功效分析；生存终点默认用 Cox PH 含违反检查；差异表达必须配 effect size 和校正 p 值。"

---

### H5 — [P0] `/ingest` NER 词表按 bio 子领域不同

**证据**：C1 提议给 `/ingest` 加 bio-NER。bio 内部词表并不统一：药物发现论文抽 protein 名 + drug 名 + PROTAC + kinase + ligand。组学论文抽 cohort 大小 + 校正 p 值 + fold-change + eQTL/sQTL 词 + GO 富集词 + 细胞类型注释。临床论文抽 NCT ID + indication + endpoint + hazard ratio。单一 bio-NER 流水线对所有种类都会 under-extract。

**修复**：`/ingest` 在检测论文子领域后（启发式：abstract 关键词 + venue + journal 分类），选用对应 NER profile：
- `protein-drug` profile（protein 名、drug 名、PROTAC 组件、kinase-substrate 对）
- `omics` profile（gene 符号、cohort 大小、校正 p 值、fold-change、GO/KEGG 词、细胞类型注释）
- `clinical` profile（NCT ID、indication、endpoint、hazard ratio、cohort 大小）
- `microbiome` profile（taxonomy 字符串、OTU/ASV 标识符、alpha/beta diversity 词）

**验证**：ingest 一篇 TCGA 论文，确认 cohort 样本量被抽到 wiki frontmatter，而不是只埋在正文。

---

### H6 — [P1] Domain 分类法扩充（A4 的补丁）

**证据**：A4 提议的受控词表偏 CS 加少量蛋白端 bio。补充：`genomics`、`transcriptomics`、`epigenomics`、`single-cell`、`metagenomics`、`clinical-genomics`、`pharmacogenomics`、`population-genetics`、`phylogenomics`、`functional-genomics`、`cancer-genomics`。

**修复**：附加进 A4 的受控列表；lint 行为相同。

---

### H7 — [P1] `/exp-run` 加工作流管理器目录布局

**证据**：C7 覆盖 ML / MD / 湿实验 / docking。组学流水线几乎一律使用 **snakemake** 或 **nextflow** 作为规范工作流管理器 —— 它们是 bio 的 `train.py` 等价物。当前 skill 没有任何模板。

**修复**：新增模板 `skills/exp-run/references/templates/{snakemake,nextflow}/`：
- Snakemake：`Snakefile` + `config.yaml` + `envs/*.yaml`（conda）+ `scripts/*.py|.R`
- Nextflow：`main.nf` + `nextflow.config` + `modules/*.nf` + `bin/*` +（可选）`nf-core/` 模板

`/exp-run` 通过 `setup.framework`（`snakemake` / `nextflow`）或 H1 的 modality 选模板。

---

### H8 — [P1] 测序成本模型加入 A6 cost 块

**证据**：A6 加了 MD wall-clock + 湿实验 USD。测序成本另有结构：每样本 × 深度 × 平台。NovaSeq lane 美元；10x scRNA 文库构建每样本美元；长读每 Gb 美元。存储也是大头 —— 中等 cohort 的 raw + processed 轻松到多 TB。Alignment CPU-hours 大致与 read 数线性相关。

**修复**：扩展 A6 的 cost 块：

```yaml
estimated_cost:
  # 现有
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0
  wet_lab_usd: 0
  fte_weeks: 0
  dataset_access_lead_time_days: 0
  # 测序新增
  sequencing_usd: 0
  per_sample_sequencing_usd: 0
  storage_tb: 0           # raw + processed
```

---

### H9 — [P1] 变异-疾病、表达-终点关联类 edge

**证据**：B1/B2 加了蛋白端关系与验证 edge。基因组学需要：
- `variant_associated_with_disease {odds_ratio, ci, p_value}`
- `gene_underlies_disease {evidence_level, mode_of_inheritance}`（孟德尔遗传病）
- `expression_correlates_with_outcome {hazard_ratio, ci, cohort}`
- `cell_type_marker_for {ontology_id}`
- `gene_in_pathway {pathway_id, db}`（KEGG / Reactome）
- `transcript_isoform_of {gene_id}`

**修复**：扩展 B1/B2 的 edge type 列表；同样要求 `confidence: high|medium|low`；定量属性带在 edge metadata 上。

---

### H10 — [P2] 细胞类型、组织、疾病 ontology 引用

**证据**：单细胞工作：**Cell Ontology**（CL:NNNNNNN）。组织 / 生物样本：**UBERON**、**BRENDA Tissue Ontology**。疾病分类：**MONDO**、**ICD-10/11**、**MeSH**、表型用 **HPO**（Human Phenotype Ontology）。

**修复**：在 `concepts/`、`claims/`、`datasets/` 加可选 `ontology_refs` 块：

```yaml
ontology_refs:
  cell_type: []        # CL:NNNNNNN
  tissue: []           # UBERON:NNNNNNN
  disease: []          # MONDO / ICD-10 / MeSH
  phenotype: []        # HP:NNNNNNN
```

**影响**：优先级低 —— 这些主要在规模大时才显出价值（跨论文综合、按 ontology 检索）。当 wiki 累积 100+ 组学或临床论文后再做。

---

## G 节 — 推荐推进顺序

按以下顺序处理，每一步会解锁下一步。**H 条目与对应 A/B/C 条目交叉穿插** —— 在同一次改动里同时建蛋白端标识符 schema 字段和基因组学端标识符字段，比分两次做要便宜得多。

1. **A1 + H3（datasets/ 实体，蛋白端与测序 cohort 一并）** —— 牵动每次未来 bio ingest；改造成本最低、杠杆最高。
2. **A3 + H2（papers / concepts / claims 加 bio 标识符，蛋白和基因组两栈）** —— 下游所有改动的 schema 脚手架。
3. **C1 + H5（`/ingest` 接 PubMed/EuropePMC fallback + 按子领域 NER profile）** —— schema 接受 DOI/PMID + 基因组 ID 后，ingest 可按子领域差异化填充。
4. **A5 + H1 + A6 + H8（experiments setup 加测序字段 + cost 块加测序成本模型）** —— 从 schema 层面同时修复 F5 / F3 类（蛋白端）计算盲点 **和**类比的组学成本盲点，赶在 wiki 实际遇到之前。
5. **C4 + C5 + H4（`/exp-design` 块分类 + 湿实验门 + 基因组学统计默认）** —— 系统性解决 F 节所示问题，并预防组学的对应问题。
6. **D1（Phase vs Stage 重命名）** —— 频繁遇到的小困惑，修复成本低。
7. **C8（bio 专用 lint，含 H2 标识符格式）** —— 随 wiki 增长持续受益。
8. **A2 + B1 + H9（proteins/ 实体 + 蛋白关系 edge + 基因组学关系 edge）** —— 蛋白引用累积 30-50 条或组学论文 10-20 篇后再做；下一里程碑回看。
9. **C7 + H7（`/exp-run` 目录布局，含 snakemake/nextflow）** —— 首次非 ML / 非 MD 实验落地时。
10. **H6（domain 分类法扩充）** —— 等 lint 第一次抓到未分类 bio domain 时纳入 A4。
11. **C10（paper-draft bio 模板）** —— 准备好用本 wiki 写 bio paper 时再做。
12. **H10、A8、B2、B3、C9、C11、D2（ontology 引用、湿实验可复现性、验证 edge、数据集版本来源、/novelty PubMed、/rebuttal 跟踪、bio maturity 等级）** —— 长尾；按具体缺口浮现时处理。

---

## 使用方法

每条都有 ID（A1、B1、C1、...）。开工时：

1. 打开本文件，把条目的优先级标签后追加 `**STATUS: in progress (YYYY-MM-DD)**`。
2. Schema 改动（A 节）需同时更新 `i18n/en/CLAUDE.md` 与对应的 `docs/runtime-page-templates.en.md`，再执行 `./setup.sh --lang en` 同步。
3. Skill 改动（C 节）更新该 skill 的 SKILL.md；如有行为变化，在 `wiki/log.md` 加一行说明，便于将来翻历史时知情。
4. F 节项目：是对 `wiki/experiments/` 已存实验的修复。任何 `/exp-run` 之前直接编辑相应页面的 `## Setup` / `## Procedure` / `## Follow-up` 段落。
5. 完成后改成 `**STATUS: done (YYYY-MM-DD)**`，加一行说明验证发现什么。

随新 bio idea 浮现未预料的缺口，本 backlog 可重新调优先级。

---

## 同步约定

- **本文件（zh）** 与 **`bioinformatics-adaptation-backlog.en.md`（en）** 互为镜像。
- 任何对一份的实质性修改（增删条目、修改 STATUS、调优先级、补充验证发现）必须**同时**应用到另一份。
- 仅修订一份的小规模措辞润色无须强制同步，但下次实质性更新时一并处理。
