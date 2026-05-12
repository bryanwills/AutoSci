---
description: Claim-driven 实验设计：界定目标 claims → 设计实验块（baseline/validation/ablation/robustness/negative-control/mechanism/dose-response/cross-context）→ 构建执行顺序 → 可选 Review LLM review → 写入 wiki
argument-hint: <idea-slug-or-hypothesis> [--review] [--budget <gpu-hours>] [--wet-lab yes|no|skip]
---

<!-- bio-C4+C5+C6: 镜像自 i18n/zh/skills/exp-design/SKILL.md，加入 C4/C5/C6 三项 bio 修订草稿。
     真值源：i18n/zh/skills/exp-design/SKILL.md。本路径不参与运行；要测试请先合回真值源。

     Section C-1（Batch 收尾）—— 三项打包修订，全部落在这一份 SKILL.md：
       C4 [P0] 块类型扩展：negative_control | mechanism | dose_response | cross_context
       C5 [P0] Step 1 wet-lab vs in-silico 路由（关键词扫描 → 三分支用户提示；非交互默认 skip+flag）
       C6 [P1] bio 统计默认值：n_test < 50 时改用 bootstrap CI + stratified k-fold；wet-lab assay 用 biological×technical 复制矩阵
     跨节依赖：A1（datasets/）、A5（experiments setup 增加 bio 字段）、A6（estimated_cost block）、
       A7（claim evidence type/grade）、B1（bio relation edges —— 仅在 Step 5 review prompt 中提及）。 -->

# /exp-design

> 根据一个 idea（或自由文本假设），设计完整的实验计划。
> 以 claims 为核心：从 Target / Decomposition / Threats 三个维度界定要验证的 claims。
> 设计四种基础实验块：baseline（基线复现）、validation（核心验证）、ablation（因素隔离）、robustness（鲁棒性）；当 idea 涉及生物系统时，再额外引入四种生物原生块：negative_control（sham/scrambled 安慰剂臂）、mechanism（点突变 / 化学探针验证因果机制）、dose_response（剂量梯度）、cross_context（跨物种 / 跨细胞系泛化）。<!-- bio-C4 -->
> 实验按依赖关系排序，阶段间设决策门（sanity fail → 提前停止）。
> 可选 Review LLM review 检查实验完整性。所有实验写入 wiki/experiments/ 并添加 graph edges。

## Inputs

- `idea`：以下之一：
  - wiki/ideas/ 中的 slug（如 `sparse-lora-for-edge-devices`）
  - 自由文本假设描述（直接提供实验目标）
- `--review`（可选）：启用 Review LLM review 审查实验计划完整性
- `--budget <gpu-hours>`（可选）：总计算预算上限（GPU 小时），影响 robustness 实验规模
- <!-- bio-C5 --> `--wet-lab yes|no|skip`（可选）：以非交互方式预先回答 Step 1 的 wet-lab probe。`yes` = 关键词命中时新增 wet-lab 块；`no` = 把 idea 的范围收窄为 retrospective / 仅 in-silico，并把约束写入 `conditions`；`skip` = 不改范围、在报告中标 flag。**未传且交互模式**：弹出提示询问用户。**非交互模式默认值**（如 `/research` 编排时）：`skip` + 报告 flag。

## Outputs

- `wiki/experiments/{slug}.md` — 每个实验块一个页面（status: planned）
- `wiki/graph/edges.jsonl` — 新增 experiment → claim 的 tested_by 边
- `wiki/ideas/{slug}.md` — 更新 linked_experiments 字段
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加日志
- **EXPERIMENT_PLAN_REPORT**（输出到终端）— 实验块总览、执行顺序、计算预算，<!-- bio-C5 --> wet-lab 路由决策与任何 retrospective-only 范围降级，<!-- bio-C6 --> 每块实际选用的统计协议（multi-seed vs bootstrap-CI vs stratified-k-fold vs replicate matrix）

## Wiki Interaction

### Reads
- `wiki/ideas/{slug}.md` — 获取 idea 的 hypothesis、approach、risks、origin_gaps
- `wiki/claims/*.md` — 目标 claims 的当前状态、已有 evidence、confidence
- `wiki/experiments/*.md` — 已有实验（避免重复设计、参考 setup 配置）
- `wiki/papers/*.md` — 相关论文的 baselines 和实验设置
- `wiki/concepts/*.md` — 涉及的技术概念（指导实验设计）
- <!-- bio-C5（依赖 A1）--> `wiki/datasets/*.md` — 已有 dataset 页面：用于解析 `setup.dataset` 的 wikilink，以及挑选与 idea 数据形态匹配的 `versions[]`
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口（指导实验优先级）

### Writes
- `wiki/experiments/{slug}.md` — 创建实验页面（每个实验块一个）
- `wiki/ideas/{slug}.md` — 更新 linked_experiments 字段
- `wiki/graph/edges.jsonl` — 添加 tested_by 边
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `tested_by`：claim → experiment（claim 被该实验验证）

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 加载上下文

1. **解析 idea 输入**：
   - 若为 slug：读取 `wiki/ideas/{slug}.md`，提取 `## Motivation`、`## Hypothesis`、`## Approach sketch`、`## Risks`，以及 frontmatter 字段 `origin_gaps`、`tags`、`domain`、`priority`（遵循 CLAUDE.md 的 ideas template）
   - 若为自由文本：直接作为假设描述使用
2. **加载相关 wiki 上下文**：
   - 读取 `wiki/graph/context_brief.md`（全局上下文）
   - 读取 `wiki/graph/open_questions.md`（知识缺口）
   - 从 idea 的 `origin_gaps` 读取对应的 `wiki/claims/*.md`（目标 claims）
   - 从每个目标 claim 的 `source_papers` 字段读取对应的 `wiki/papers/*.md`，获取 baseline setup 和已有实验协议 —— 这是 idea → claim → paper 的规范路径（ideas **不带** `linked_papers` 字段，改用 `origin_gaps` → `source_papers`）
   - 读取已有 `wiki/experiments/*.md`，检查是否已有类似实验
3. **若 idea 无 origin_gaps**：从假设描述中提取隐含的 claims，在 wiki/claims/ 中查找或标注需要新建
4. <!-- bio-C5 --> **Wet-lab 依赖性 probe**（idea 的 `domain` 明显是 CS —— `NLP|CV|ML Systems|Robotics` —— 时跳过本子步骤）：
   - **关键词扫描**：在 `## Hypothesis` + `## Approach sketch` + `## Risks`（或自由文本假设）拼接出的文本中搜索以下锚点；命中即视为 idea 终将需要新的 wet-lab 数据：
     - **基于细胞**：`in cell`、`in cellulo`、`cellular target engagement`、`CETSA`、`nanoBRET`、`viability`、`apoptosis`、`proliferation`
     - **动物 / 临床**：`in vivo`、`xenograft`、`tumor regression`、`PK/PD`、`pharmacokinetic`、`mouse model`、`clinical trial`
     - **生物物理**：`binding assay`、`IC50`、`EC50`、`Kd`、`ITC`、`SPR`、`BLI`、`thermal shift`、`DSF`
     - **结构**：`cryo-EM`、`crystal structure`、`NMR`（用作主要 readout 时；用作起始模型不算）
     - **互作组**：`Y2H`、`AP-MS`、`co-IP`、`BioID`、`proximity labeling`
     - **基因组学 readout**：`RNA-seq`、`ChIP-seq`、`CRISPR screen`、`MPRA`
   - **分支**：
     - 若已传 `--wet-lab`：直接走对应分支，不再询问。
     - 若交互模式且命中 ≥1 个关键词：用 `AskUserQuestion` 列出命中的关键词，给出三选一：
       - `yes` → 在 Step 3 新增一个 wet-lab 实验块（type 为 `validation`，`setup.in_silico_or_wet: wet`，填 `setup.assay_type` / `setup.cell_line` / `setup.species`；记录对应的 `estimated_cost.wet_lab_usd` 和 `estimated_cost.dataset_access_lead_time_days`）
       - `no` → 收窄范围为 retrospective / 仅 in-silico。在实验页面 `## Setup` 末尾追加一句"scoped to retrospective in-silico evaluation; no new wet-lab generation"（idea 来自 wiki 时也写入 idea 的 `conditions`），并在最终报告中显示。
       - `skip` → 不改范围，但在报告中记一行"wet-lab probe deferred"，方便之后重跑 `/exp-design` 或 `/check` 重新捡起。
     - 若非交互模式且命中 ≥1 个关键词：默认 `skip` + 报告 flag。
     - 若 0 个命中：什么也不做，按默认 in-silico 处理。
   - **本子步骤的输出**（带入 Step 3）：`wet_lab_decision ∈ {plan|retrospective_only|deferred|none}` + 命中关键词列表。

### Step 2: 界定 Claims（Scope Claims）

从三个维度界定本次实验计划涉及的 claims。对于每个维度，先在 wiki/claims/ 中查找已有 claim；若不存在，创建新 claim（status: proposed, confidence: 0.3）。

1. **Target**（验证什么）：
   - idea 的核心假设对应的 claim —— 本次实验计划要直接验证的目标
   - 通常 1 个，最多 2 个
2. **Decomposition**（拆解什么）：
   - 方法中各独立因素各自的贡献 claim
   - 每个因素对应一个 claim，用于设计隔离验证实验
3. **Threats**（什么会推翻我们）：
   - 已知的风险、替代解释、边界条件
   - 来源：wiki 中的 counter-evidence、papers 的 limitations、claim 的 open questions
   - 指导鲁棒性实验的设计

输出：界定的 claims 清单（slug 列表 + 维度标注 + 每个 claim 的当前 status/confidence）

### Step 3: 设计实验块（Design Experiment Blocks）

为每个界定的 claim 设计实验块。**基础四种**对所有计划都适用；**生物原生四种**仅在 idea 具备生物属性时启用 —— 即 `domain` 落入 A4 的 bio 词表（`structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics | clinical-translation`）**或** Step 1 子步骤 4 有任何关键词命中。<!-- bio-C4 -->

**A. Baseline 实验（基线复现）**：
- 目的：确认问题存在、基线可复现
- 复现最相关论文的核心实验
- 成功标准：基线结果与论文报告的差异 < 5%（此阈值与下方 Stage 1 decision gate 一致 —— 不要在别处使用不同的数字）
- 计算量：通常最小

**B. Validation 实验（验证 Target claim）**：
- 目的：在基线之上验证核心贡献
- 指标：比 baseline 有统计显著提升
- <!-- bio-C6 --> **统计协议**（按样本量挑默认）：当 `n_test >= 50` 且实验是 in-silico 时沿用旧 ML 默认 —— **>= 3 random seeds** + 与 baseline 的配对检验。当 `n_test < 50`（bio held-out 集的常态）**或** `domain` 属于 A4 的 bio 词表时，默认升级到 **bootstrap CI（1000 次 resample）** + **stratified k-fold（k = min(5, n_positives)）**；只跑 multi-seed 不够，必须显式标记。Wet-lab 实验（`setup.in_silico_or_wet: wet`）：默认 **>= 3 个 biological replicates × >= 3 个 technical replicates**，并在 `## Setup` 中写清哪一维是哪一种；单复制是例外，必须在正文中说明理由。
- 计算量：中等

**C. Ablation 实验（验证 Decomposition claims）**：
- 目的：隔离各独立因素的贡献
- 每个 ablation 移除一个因素，验证性能下降
- N 个因素 → N 个 ablation 实验
- <!-- bio-C6 --> 统计协议选择规则与 validation 一致：bio 小样本升级到 bootstrap CI + stratified k-fold；wet-lab ablation 必须给出 biological×technical 复制矩阵。
- 计算量：与 validation 类似 × N

**D. Robustness 实验（排除 Threats）**：
- 目的：排除已知风险和替代解释，验证方法在不同条件下仍然有效
- 变化维度：模型大小、数据集、超参数、domain
- 至少测试 2 个变化维度
- 计算量：取决于 --budget

<!-- bio-C4: 生物原生块 E–H，仅在 bio 域或 wet-lab 关键词命中时启用。 -->

**E. Negative-control 实验（sham / scrambled 安慰剂臂）**：
- 目的：把真实效应与非特异 / 批次伪影区分开。**与"PTM-blind baseline 复现"不同**：baseline 是去掉新因素去复现先前结果；negative_control 是在新因素位置上换一个明显失活的版本（sham PTM 位点、scrambled 序列、错配 ligand、无转染孔、纯溶剂剂量），并测同一个 readout。
- 何时加：任何 wet-lab 块；任何对比关键依赖于单一新特征、效应可能仅由结构先验解释的 in-silico 块（例如同一 scaffold 上 PTM-conditioned 打分 vs PTM-blind 打分）。
- 成功标准：negative-control 臂复现 baseline 的零分布（效应大小落在噪声楼层内）；非零的 negative control 直接让 validation 块的结论作废，必须先定位伪影。
- 计算量：通常等同 1 个 validation 块。

**F. Mechanism 实验（预测的 MoA 是否成立）**：
- 目的：检验 idea 主张的*因果*机制本身，而不只是末端 readout。对应 A7 的 `mechanistic_basis` 证据类型。
- 标准设计：在预测的催化 / 结合 / PTM 残基上做点突变（loss-of-function 应消除效应；WT rescue 应恢复）；化学探针（抑制预测的上游节点应表型表型化 loss-of-function）；正交扰动（RNAi vs CRISPR、两种结构上不同的 ligand）以排除 off-target。
- 成功标准：至少两个正交扰动给出方向一致的效应。
- 计算量：通常是 validation 块的 1–2 倍；性价比高 —— 砍预算时优先砍 robustness、保 mechanism。

**G. Dose-response 实验（剂量梯度）**：
- 目的：刻画扰动幅度与效应的关系；**与超参数 sweep 不同** —— 超参数是模型旋钮，dose-response 是连续的生物变量（药物浓度、表达量、修饰位点 stoichiometry、模拟时长）。
- 标准设计：≥ 6 个剂量、log 尺度上跨 ≥ 3 个数量级；拟合 4 参数 Hill 曲线（或合适替代）；报告 EC50 / IC50 + 95% CI。
- 成功标准：剂量-效应单调，Hill 系数与 EC50/IC50 落在预注册区间内；预测变量上 dose-response 平坦本身就是一个有信息量的反证。
- 计算量：单条件大约 6–10 倍 validation 单点。

**H. Cross-context 实验（跨物种 / 跨细胞系泛化）**：
- 目的：检验效应是否在训练上下文之外仍然成立。精神上接近 ML 的"cross-dataset"，但失败模式是生物上下文特异的（物种特异 PTM 酶、paralogue 冗余、细胞系特异 co-factor 表达、肿瘤 vs 正常 proteome 差异）。
- 何时加：idea 隐含一个物种 / 细胞系约束、但 wet-lab 计划只覆盖一个上下文（例如训练在 HEK293、应用目标却是原代 T 细胞）。
- 成功标准：预注册一个效应保留阈值（如 ≥ 50% 的同上下文效应大小）；至少一个跨上下文失败不应作废同上下文 claim —— 但要降级该 claim 的适用范围。
- 计算量：每个上下文与一个 validation 块相当；按政策相关度选 1–2 个上下文。

每个实验块包含：
- `title`：描述性标题
- `target_claim`：对应的 claim slug
- `hypothesis`：实验验证的具体假设
- `type`：<!-- bio-C4 --> `baseline | validation | ablation | robustness | negative_control | mechanism | dose_response | cross_context`
- `setup`：model、dataset、hardware、framework <!-- bio-C5（经 A5）--> 以及在合适场景下填的 bio 字段：`in_silico_or_wet`、`species`、`cell_line`、`assay_type`、`force_field`、`solvent_model`、`simulation_length`、`weight_version`、`random_seed_protocol`
- `metrics`：评估指标列表
- `baseline`：对比基线（negative-control 块用*安慰剂*臂；mechanism 块用 WT/vehicle 臂；dose_response 用零剂量；cross_context 用同上下文效应大小）<!-- bio-C4 -->
- `success_criterion`：明确的成功/失败标准
- <!-- bio-C6 --> `statistical_protocol`：恰好填一项 —— `seeds_only`（旧 ML 默认；n_test ≥ 50 且 in-silico）| `bootstrap_ci`（1000 resample；in-silico 小样本）| `stratified_kfold`（k = min(5, n_positives)；类不平衡）| `replicate_matrix_BxT`（生物 × 技术复制；wet-lab）
- `estimated_gpu_hours`：旧字段，保留以做向后兼容
- <!-- bio-C5（经 A6）--> `estimated_cost`：当本块涉及 MD 或 wet-lab 时填的结构化 block（只在适用维度上填非零）：`gpu_hours`、`cpu_hours`、`md_wallclock_hours`、`wet_lab_usd`、`fte_weeks`、`dataset_access_lead_time_days`
- `seeds`：随机种子数（仅当 `statistical_protocol == seeds_only` 时有意义；建议 >= 3）

### Step 4: 构建执行顺序（Build Run Order）

按依赖关系排序实验，设置决策门：

```
Stage 0: Sanity check
  └── 小规模运行（1 epoch / 100 steps）验证代码无 bug、数据可加载、GPU 可用
  └── 门：若 sanity 失败 → 停止，修复代码

Stage 1: Baseline（基线复现）
  └── 复现基线结果
  └── 门：若基线偏差 > 5% → 停止，检查实现（与 Step 3 成功标准同阈值）

Stage 2: Validation（核心验证）
  └── 在基线之上验证核心方法
  └── 任何已规划的 negative-control 块与 validation 块在同一 Stage 2 并行执行  <!-- bio-C4 -->
  └── 门：若无提升 → 停止，分析原因（可能是 idea 不成立）
  └── 门：negative control 出现非零效应 → 停止，validation 结果不可解读  <!-- bio-C4 -->

Stage 3: Ablation（因素隔离） + Mechanism（因果 MoA）  <!-- bio-C4 -->
  └── 多个 ablation 可并行执行
  └── Mechanism 块排在此处（依赖 Stage 2 通过；与 ablation 正交）
  └── 门：若某因素 ablation 无影响 → 记录，但继续其他 ablation
  └── 门：两个正交 mechanism 扰动都没给出预期方向的效应 → 把 target claim 的 mechanistic_basis 证据降级为 correlative；带 flag 继续 robustness  <!-- bio-C4 -->

Stage 4: Robustness（鲁棒性验证） + Dose-response + Cross-context  <!-- bio-C4 -->
  └── 仅在 Stage 2 成功后执行
  └── 范围由 --budget 剩余额度决定；预算紧张时按以下顺序砍：cross_context → robustness → dose_response（dose_response 最后砍 —— 它单位成本上产出的可量化 claim 最多）
```

输出：
- 有序实验列表（含依赖关系）
- 每阶段的决策门条件
- 总计算预算估算（若超过 --budget 则调整 Stage 4 范围）

### Step 5: 可选 Review LLM Review（--review）

若指定 `--review`：

```
mcp__llm-review__chat:
  system: "You are a senior researcher reviewing an experiment plan. The plan
           may include both ML-style blocks (baseline/validation/ablation/
           robustness) and bio-natural blocks (negative_control/mechanism/
           dose_response/cross_context).
           Focus on: missing baselines, missing ablations, unfair comparisons,
           statistical rigor (sample size, replicates, seeds vs bootstrap CI
           vs stratified k-fold), dataset selection and version pinning, and
           — for bio plans — whether negative controls are present where the
           contrast hinges on a single feature, whether mechanism blocks use
           ≥2 orthogonal perturbations, whether dose-response covers ≥3
           orders of magnitude, and whether cross-context blocks pre-register
           effect-size retention thresholds.
           For every issue found, suggest a concrete fix."  <!-- bio-C4+C6 -->
  message: |
    ## Experiment Plan
    {complete experiment plan: claims, blocks, run order, budgets, statistical_protocol per block}

    ## Context
    {target claims with current status, related papers' experiment setups, wet-lab decision from Step 1}

    ## Review Questions
    1. Are any critical experiments missing?
    2. Are the baselines fair and comprehensive?
    3. Is the ablation design sufficient to isolate each contribution?
    4. Are the success criteria well-defined and reasonable?
    5. Any statistical concerns (sample size, variance, seeds vs bootstrap CI vs stratified k-fold; wet-lab replicate matrix)?  <!-- bio-C6 -->
    6. <!-- bio-C4 --> For bio plans: is a negative-control block present wherever the contrast hinges on a single feature? Do mechanism blocks use ≥2 orthogonal perturbations? Does dose-response span ≥3 orders of magnitude? Are cross-context retention thresholds pre-registered?
    7. <!-- bio-C5 --> Did the wet-lab decision (`plan|retrospective_only|deferred|none`) match the idea's actual data dependencies? Any keyword hits the probe missed?
```

根据 Review LLM 反馈调整实验计划（添加遗漏的实验、修正不合理的标准、补齐缺失的 negative_control / mechanism / dose_response / cross_context 块）。

### Step 6: 写入 Wiki

1. **创建实验页面**：
   对每个实验块：
   ```bash
   python3 tools/research_wiki.py slug "<experiment-title>"
   ```
   创建 `wiki/experiments/{slug}.md`，**严格遵循 CLAUDE.md experiments template** —— 下方所有字段都必须存在（即使为空），因为 `/exp-run` 稍后会用 `tools/research_wiki.py set-meta` 来更新它们，而 `set-meta` 拒绝创建 frontmatter 中不存在的字段（它只更新已存在的 key）：
   ```yaml
   ---
   title: ""
   slug: ""
   status: planned
   target_claim: ""          # claim slug
   hypothesis: ""
   tags: []
   domain: ""
   setup:
     model: ""
     dataset: ""               # 当 dataset 已在 wiki 中时填 [[datasets/{slug}]] wikilink（依赖 A1）
     hardware: ""
     framework: ""
     # bio-C5（经 A5）：可选 bio 字段 —— 仅在适用时填
     in_silico_or_wet: ""      # "" | in_silico | wet | hybrid
     species: ""
     cell_line: ""             # 优先填 CVCL_xxxx 的 Cellosaurus ID
     assay_type: ""            # 例如 CETSA | nanoBRET | RNA-seq | docking | MD | binding-affinity-prediction
     force_field: ""           # 仅 MD 块
     solvent_model: ""         # 仅 MD 块
     simulation_length: ""     # 仅 MD 块（如 100ns）
     weight_version: ""        # ML 权重 provenance，例如 boltz-2.1.0
     random_seed_protocol: ""  # 描述 seed 选取方式的文本
   metrics: []
   baseline: ""
   # bio-C4：扩展的 type 枚举
   # type: baseline | validation | ablation | robustness
   #     | negative_control | mechanism | dose_response | cross_context
   # bio-C6：显式统计协议（必填）
   statistical_protocol: ""    # seeds_only | bootstrap_ci | stratified_kfold | replicate_matrix_BxT
   outcome: ""                 # 留空，由 /exp-run Phase 4 填写 — succeeded | failed | inconclusive
   key_result: ""              # 留空，由 /exp-run Phase 4 填写
   linked_idea: "{idea-slug}"  # 必填：源 idea slug（与 wiki/ideas/{idea-slug}.md 的 linked_experiments 互为双向链接）
   date_planned: YYYY-MM-DD
   date_completed: ""          # 留空，由 /exp-run Phase 4 填写
   run_log: ""                 # 留空，由 /exp-run Phase 2 填写
   started: ""                 # 留空，由 /exp-run Phase 2 填写（ISO 时间戳，通过 set-meta）
   estimated_hours: 0          # 旧字段，保留以做向后兼容（A6 已弃用）
   # bio-C5（经 A6）：结构化 cost block —— 只在适用维度上填非零
   estimated_cost:
     gpu_hours: 0
     cpu_hours: 0
     md_wallclock_hours: 0
     wet_lab_usd: 0
     fte_weeks: 0
     dataset_access_lead_time_days: 0
   remote:                     # 完整 block 必须存在，以便 /exp-run --env remote 通过 Edit 填充子字段
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ---

   ## Objective
   {what this experiment proves}

   ## Setup
   {detailed setup: model, dataset, hardware, hyperparameters}
   {bio-C5：当 Step 1 选择 retrospective_only 分支时，在末尾追加一句
    "scoped to retrospective in-silico evaluation; no new wet-lab generation."}
   {bio-C6：当 statistical_protocol == replicate_matrix_BxT 时，明确写哪一维是 biological
    replicates、哪一维是 technical replicates，以及各自数量。}

   ## Procedure
   {step-by-step execution plan}

   ## Results
   (to be filled after /exp-run)

   ## Analysis
   (to be filled after /exp-run)

   ## Claim updates
   (to be filled after /exp-eval)

   ## Follow-up
   {contingency plans: what to do if success / failure}
   ```

2. **创建新 claims（若 Step 2 中发现缺失的 claims）**：
   ```bash
   python3 tools/research_wiki.py slug "<claim-title>"
   ```
   创建 `wiki/claims/{slug}.md`（status: proposed, confidence: 0.3）

3. **添加 graph edges**：
   ```bash
   # 对每个实验 → 目标 claim
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "claims/{target-claim}" --to "experiments/{slug}" \
     --type tested_by --evidence "Designed by /exp-design"
   ```

4. **更新 idea 页面**（若 idea 来自 wiki）：
   - 在 `wiki/ideas/{idea-slug}.md` 的 `linked_experiments` 追加所有新建实验的 slugs
   - 若 idea status 为 `proposed`，更新为 `in_progress`
   - <!-- bio-C5 --> 若 wet-lab 决策为 `retrospective_only`，在 `conditions` 也追加一行记录范围降级（如 "scoped to retrospective in-silico evaluation per /exp-design 2026-MM-DD"）

5. **更新 index.md**：在 experiments 和 claims（若新建）类别下追加条目

6. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

7. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-design | {N} experiments designed for idea {slug} | claims: {claim-list} | wet_lab_decision: {plan|retrospective_only|deferred|none}"
   ```
   <!-- bio-C5：log 行末尾增加 wet_lab_decision，方便 grep -->

8. **输出 EXPERIMENT_PLAN_REPORT 到终端**：
   ```markdown
   # Experiment Plan Report

   ## Target Idea
   - Idea: [[idea-slug]]
   - Hypothesis: {hypothesis}
   - Wet-lab decision: {plan | retrospective_only | deferred | none}    <!-- bio-C5 -->
   - Matched wet-lab keywords: {comma-separated list, or "—"}            <!-- bio-C5 -->

   ## Scoped Claims
   | Claim | Current status | Confidence | Dimension |
   |-------|---------------|------------|-----------|
   | [[claim-slug]] | proposed | 0.3 | target |
   | [[claim-slug]] | weakly_supported | 0.5 | decomposition |

   ## Experiment Blocks
   | # | Experiment | Type | Claim | Stat protocol | Cost (primary dim) | Stage |
   |---|-----------|------|-------|---------------|--------------------|-------|
   | 1 | [[baseline-slug]]       | baseline         | —              | seeds_only         | 2 GPU-h           | 1 |
   | 2 | [[validation-slug]]     | validation       | target         | bootstrap_ci       | 8 GPU-h           | 2 |
   | 3 | [[neg-ctrl-slug]]       | negative_control | target         | bootstrap_ci       | 8 GPU-h           | 2 |
   | 4 | [[ablation-1-slug]]     | ablation         | decomposition-1| stratified_kfold   | 8 GPU-h           | 3 |
   | 5 | [[mechanism-slug]]      | mechanism        | target         | replicate_matrix_BxT| $12k wet-lab     | 3 |
   | 6 | [[dose-response-slug]]  | dose_response    | target         | replicate_matrix_BxT| $8k wet-lab      | 4 |
   | 7 | [[cross-context-slug]]  | cross_context    | target         | bootstrap_ci       | 16 GPU-h          | 4 |

   ## Run Order
   Stage 0: Sanity → Stage 1: Baseline → Stage 2: Validation + Negative-Control → Stage 3: Ablation + Mechanism → Stage 4: Robustness + Dose-response + Cross-context
   每阶段边界设决策门，包括 Stage 2 的 negative-control 门 与 Stage 3 的正交扰动门。   <!-- bio-C4 -->

   ## Budget
   - Total estimated: {N} GPU-hours; {N} MD wall-clock hours; {USD} wet-lab; {N} FTE-weeks; {N} days dataset access lead time   <!-- bio-C5（经 A6） -->
   - Budget limit: {--budget or "unlimited"}

   ## Next Steps
   - Run `/exp-run [[baseline-slug]]` to start Stage 1
   - After each stage, run `/exp-eval` to update wiki
   ```

## Constraints

- **每个实验必须关联 claim**：`target_claim` 不能为空（baseline 实验可关联 Target claim）
- **实验不可重复**：创建前检查 wiki/experiments/ 中是否已存在相同 target_claim + hypothesis 的实验
- **claims 界定后不修改**：Step 2 界定的 claims 在本次计划中不修改 status/confidence，只有 /exp-eval 可以修改
- **success criterion 必须量化**：每个实验块的成功标准必须包含具体数值（如 "> 2% accuracy improvement"）
- <!-- bio-C6 --> **`statistical_protocol` 必填**：每个实验块都要明确填入 `seeds_only | bootstrap_ci | stratified_kfold | replicate_matrix_BxT` 之一。挑选方式按 Step 3 的默认；偏离默认必须在 `## Setup` 中给出理由。
- <!-- bio-C6 --> **>= 3 seeds 或等价的替代协议**：`statistical_protocol == seeds_only` 时必须 >= 3 个 random seeds。bootstrap_ci 时声明 resample 数（默认 1000）；stratified_kfold 时声明 k（默认 min(5, n_positives)）；replicate_matrix_BxT 时声明 biological × technical 数量（默认 >= 3 × >= 3）。
- <!-- bio-C5 --> **wet-lab 决策必须落到记录里、不静默丢失**：跑了 Step 1 子步骤 4 的所有计划都必须在报告与日志行中记录 `wet_lab_decision`，即便取值是 `none`。`retrospective_only` 计划还要把约束写入 `## Setup`（idea 来自 wiki 时同时写入 idea 的 `conditions`）。
- <!-- bio-C4 --> **negative-control 门强制生效**：当规划了 negative-control 块时，非零的 negative-control 结果让 validation 块的结论作废，与 validation 自身的成败无关 —— 必须在 `## Follow-up` 中写明这条规则。
- **graph edges 使用 tools/research_wiki.py**：不手动编辑 edges.jsonl
- **idea status 只能前进**：proposed → in_progress，不可逆
- **slug 唯一性**：创建前检查是否存在相同 slug

## Error Handling

- **idea 找不到**：提示用户检查 slug，列出 wiki/ideas/ 中的候选
- **目标 claim 不存在**：自动创建新 claim 页面（status: proposed, confidence: 0.3），在报告中标注
- **已有相似实验**：列出已有实验，询问用户是继续追加还是跳过
- **Review LLM 不可用**（--review 模式）：跳过 Step 5，在报告中标注「unreviewed — Review LLM unavailable」
- **budget 不足**：按 Step 4 给出的优先级削减 Stage 4 范围（先砍 `cross_context` → 再砍 `robustness` → 最后砍 `dose_response`），在报告中标注实际预算分配   <!-- bio-C4 -->
- **slug 冲突**：追加数字后缀（如 `sparse-lora-ablation-v2`）
- **wiki 为空**：正常执行但 baseline 实验无法参考已有结果，在报告中建议先 /ingest 相关论文
- <!-- bio-C5 --> **wet-lab probe 在非交互模式下命中关键词**：未传 `--wet-lab` 且无人交互（如 `/research` 编排）时默认 `skip`，并在报告中显示一行清晰提示 "wet-lab probe deferred —— 重跑 /exp-design 并加 --wet-lab 以解析"。
- <!-- bio-C6 --> **从 dataset metadata 拿不到 `n_test`**：发出 warning，默认按 `bootstrap_ci` 处理，并请用户回填 `wiki/datasets/{slug}.versions[*].n_test`，以便后续运行能自动选对协议。

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建 gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志

### MCP Servers
- `mcp__llm-review__chat` — Step 5 实验计划审查（可选）

### Claude Code Native
- `Read` — 读取 wiki 页面
- `Glob` — 查找已有实验和 claims
- `AskUserQuestion` — Step 1 子步骤 4 的 wet-lab probe 交互分支（已传 `--wet-lab` 或非交互会话时跳过）   <!-- bio-C5 -->

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Step 5 Review LLM 审查独立性（若启用）

### Called by
- `/research` Stage 2（实验设计阶段）
- 用户手动调用
