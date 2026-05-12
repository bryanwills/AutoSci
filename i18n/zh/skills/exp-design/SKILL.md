---
description: Idea-driven 实验设计：界定 idea 的 hypothesis → 设计实验块（baseline/validation/ablation/robustness）→ 构建执行顺序 → 可选 Review LLM review → 写入 wiki
argument-hint: <idea-slug-or-hypothesis> [--linked-idea <idea-slug>] [--review] [--budget <gpu-hours>]
---

# /exp-design

> 根据一个 idea（或自由文本假设），设计完整的实验计划。
> 以 idea 为核心：从 Target / Decomposition / Threats 三个维度界定 idea 的 hypothesis。
> 设计 baseline（基线复现）、validation（核心验证）、ablation（因素隔离）、robustness（鲁棒性）四种实验块。
> 实验按依赖关系排序，阶段间设决策门（sanity fail → 提前停止）。
> 可选 Review LLM review 检查实验完整性。所有实验写入 `wiki/experiments/`，并通过 frontmatter `linked_idea` 字段反链回 idea。

## Inputs

- `idea`：以下之一：
  - wiki/ideas/ 中的 slug（如 `sparse-lora-for-edge-devices`）—— 推荐路径
  - 自由文本假设描述（可接受；将创建或引用 idea 页面）
- `--linked-idea <idea-slug>`（可选）：当位置参数是自由文本，但用户已有想要绑定的 idea 页面时显式指定。等价于把该 slug 作为位置参数传入；提供该 flag 是为了让 SPA 可以从 idea 阅读页直接调用 `/exp-design --linked-idea <slug>`。
- `--review`（可选）：启用 Review LLM review 审查实验计划完整性
- `--budget <gpu-hours>`（可选）：总计算预算上限（GPU 小时），影响 robustness 实验规模

## Outputs

- `wiki/experiments/{slug}.md` — 每个实验块一个页面（status: planned，已设置 `linked_idea`）
- `wiki/graph/edges.jsonl` — 新增 idea → experiment 的 `tested_by` 边
- `wiki/ideas/{slug}.md` — 更新 `linked_experiments` 字段
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加日志
- **EXPERIMENT_PLAN_REPORT**（输出到终端）— 实验块总览、执行顺序、计算预算

## Wiki Interaction

### Reads
- `wiki/ideas/{slug}.md` — idea 的 hypothesis、approach、risks、novelty argument、`origin_gaps`
- `wiki/concepts/*.md` 与 `wiki/topics/*.md` — 通过 idea 的 `origin_gaps` 引用（idea 关闭的 concept/topic）
- `wiki/methods/*.md` — idea 借用的可复用 method（来自 idea 的 `## Approach sketch` 引用）
- `wiki/papers/*.md` — 通过 `concepts.key_papers` / `methods.source_papers` 路径回溯，获取 baseline setup 与已有实验协议
- `wiki/experiments/*.md` — 已有实验（避免重复设计、参考 setup 配置）
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口（指导实验优先级）

### Writes
- `wiki/experiments/{slug}.md` — 创建实验页面（每个实验块一个）；每页都带非空 `linked_idea` frontmatter 字段
- `wiki/ideas/{slug}.md` — 在 `linked_experiments` 追加新实验 slugs；如可，把 status 从 `proposed` 推进到 `in_progress`
- `wiki/graph/edges.jsonl` — 添加 `tested_by` 边（idea → experiment）
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `tested_by`：idea → experiment（idea 正在被该实验验证）。反向方向通过 experiment 的 `linked_idea` frontmatter 字段表达，由 `xref.yaml` 反向写入 idea 的 `linked_experiments` 列表。

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 加载上下文

1. **解析 idea 输入**：
   - 若是 slug（或传入了 `--linked-idea`）：读取 `wiki/ideas/{slug}.md`，提取 `## Motivation`、`## Hypothesis`、`## Approach sketch`、`## Novelty argument`、`## Risks`，以及 frontmatter 字段 `origin_gaps`、`tags`、`target_venue`、`priority`、`novelty_score`。
   - 若是自由文本：直接作为假设描述，并提示尚未绑定 idea 页面；用户应传入 `--linked-idea`，否则每个实验都缺 `linked_idea` slug。新 schema 要求每个实验都有 `linked_idea`，因此在没有 idea slug 时直接报错退出。
2. **加载相关 wiki 上下文**：
   - 读取 `wiki/graph/context_brief.md`（全局上下文）
   - 读取 `wiki/graph/open_questions.md`（知识缺口）
   - 从 idea 的 `origin_gaps` 读取每个 `wiki/concepts/{slug}.md` 或 `wiki/topics/{slug}.md`。再从它们的 `key_papers`（concept）/ `## Seminal works` + `## SOTA tracker`（topic）回溯到相关的 `wiki/papers/*.md` 用于 baseline setup。
   - 从 `## Approach sketch` 中的 wikilink 读取被引用的 `wiki/methods/{slug}.md` 页面 —— 这些告诉你 idea 继承了哪些可复用技术，决定了 ablation 因子。
   - 读取已有 `wiki/experiments/*.md` 中 `linked_idea` 与本 idea 一致的实验（避免重复先前设计）。
3. **探测湿实验依赖**（bio-C5 minimal pilot 2026-05-12 合并）：
   - 扫描 idea 的 `## Hypothesis`、`## Risks`、`## Approach sketch`（以及任何自由文本输入），匹配湿实验信号词：`in cell`、`cellular target engagement`、`in vivo`、`tumor regression`、`binding assay`、`ELISA`、`Western blot`、`co-IP`、`cryo-EM`、`point mutation`、`knockdown`、`knockout`、`IC50`、`Kd`。
   - 若命中任一词：向用户一次性展示命中清单，并询问项目是否具备湿实验访问条件。把回答记为 `wet_lab_planned: true | false`。
     - `true` → Step 3 规划一个或多个 `setup.in_silico_or_wet: wet_lab`（或 `mixed` —— 适合 in-silico 预测 + 湿实验验证的混合块）的实验块。湿实验块在 `## Procedure` 中写协议，用 `setup.assay_type` / `setup.cell_line` / `setup.species` 锚定可复现性。
     - `false` → 把范围收紧为 retrospective-only（全部块 `setup.in_silico_or_wet: in_silico`），并在每个实验页的 `## Procedure` 节记录约束："Retrospective-only —— 湿实验后续不在本轮范围内,留待具备湿实验访问的未来周期。"
   - 若无命中：静默跳过。纯 ML / 纯 in-silico 设计不必询问。

### Step 2: 界定 Hypothesis（Scope the Hypothesis）

把 idea 的 `## Hypothesis` 拆解到三个维度。本步骤的产物是一张表格式 scope sheet，**不**新建 wiki 页面 —— `/exp-design` 不创建 concept 或 method。（如发现缺少某个 concept，正确做法是 `/edit` 或 `/ingest`，不要在此处静默新建。）

1. **Target 维度** —— idea 的核心命题，重写为一个可检验的命题。通常 1 个，至多 2 个。
2. **Decomposition 维度** —— 列出方法中各独立因子。每个因子一行；这是 ablation 主干。
3. **Threats 维度** —— 已知风险、替代解释、边界条件。来源：idea 的 `## Risks`、源论文的 `## Limitations`，以及任何相关 concept/topic 的 `## Open problems` 条目。这是 robustness 主干。

输出：含 `dimension | proposition | source (idea section / concept / method / paper)` 列的 markdown 表。

### Step 3: 设计实验块（Design Experiment Blocks）

为 scope sheet 的每一行设计实验块，4 种类型：

**A. Baseline 实验（基线复现）**：
- 目的：确认问题存在、基线可复现
- 复现最相关论文的核心实验（通过 `origin_gaps → concept.key_papers` 或 `## Approach sketch → method.source_papers` 解析）
- 成功标准：基线结果与论文报告的差异 < 5%（此阈值与下方 Stage 1 decision gate 一致 —— 不要在别处使用不同的数字）
- 计算量：通常最小

**B. Validation 实验（验证 Target）**：
- 目的：在基线之上验证 idea 的核心命题
- 指标：比 baseline 有统计显著提升
- 统计默认值：见下方 "Statistical defaults" 子节 —— `>= 3 seeds` 仅在 `n_test >= 50` 时足够;小样本 bio 集合需 bootstrap CI + stratified k-fold。
- 计算量：中等

**C. Ablation 实验（验证 Decomposition 因子）**：
- 目的：隔离各独立因子的贡献
- 每个 ablation 移除一个因子，验证性能下降
- N 个因子 → N 个 ablation 实验
- 计算量：与 validation 类似 × N

**D. Robustness 实验（排除 Threats）**：
- 目的：排除已知风险和替代解释，验证方法在不同条件下仍然有效
- 变化维度：模型大小、数据集、超参数、domain
- 至少测试 2 个变化维度
- 计算量：取决于 --budget

**Bio 专用块类型**（bio-C4 minimal pilot 2026-05-12 合并）：idea 具有 bio 形态时，在 A–D 之外加用这些。它们与 A–D 独立 —— 一个实验可同时携带 A–D 和 bio 两个 tag（例如 `tags: [validation, mechanism]`）。块类型作为 tag 记录而非 frontmatter 枚举。

- **E. negative_control** —— 假对照 / 乱序对照 / 安慰剂。与 A 类基线复现不同：basline 复现已发表方法的报告数值；negative_control 排除"无功能对照也能产生的混淆信号"（如乱序 PROTAC、催化失活酶、仅载体处理）。当核心声明可能是非特异效应时使用。
- **F. mechanism** —— 验证预测的因果机制而非仅看结果。典型形态：点突变预测的活性位点 / PTM 位点 / 结合残基，检查预测效应是否消失；或用化学探针特异性阻断所提出的机制。与 B 类 validation 区别：validation 测"头条数字是否提升"；mechanism 测"提升是否真的由我们说的原因引起"。
- **G. dose_response** —— 剂量梯度设计，自变量是有生物学意义的连续量（配体浓度、暴露时长、表达量）。与超参扫描区别：梯度是生物学的而非算法的，预期形状（sigmoidal IC50/EC50、激素效应、阈值）本身就含机制信息。
- **H. cross_context** —— 跨物种 / 跨细胞系 / 跨组织的泛化。与 D 类 ML 跨数据集 robustness 区别：失败模式不同（PTM 底物 motif 的物种漂移、不同实验室的批次效应、细胞系特异的辅因子表达）。当声明指向人体临床转化时，至少需要一个针对目标临床物种 / 组织的 cross_context 块。

**Statistical defaults**（bio-C6 minimal pilot 2026-05-12 合并）：按测试集大小与 assay 类型选复制策略，并把结果记入 `setup.random_seed_protocol`（A5 full 字段）。小样本 bio 集合仅靠多 seed 通常不够。

| 形态 | 测试集大小 | 默认协议 | 记入 `random_seed_protocol` |
|---|---|---|---|
| ML 大样本 | `n_test >= 50` | `>= 3 random seeds` 足够 —— 报告跨 seed 的均值 ± 标准差 | `ranking-shuffle`（或 `multi-seed`） |
| Bio 小样本 | `n_test < 50` | **bootstrap CI**（≥ 1000 次重抽）头条指标 + **stratified k-fold** `k = min(5, n_positives)` 避免类不平衡偏差。叠多 seed 可以,不可替代以上。 | `bootstrap`（bootstrap CI 主导时）或 `stratified-k-fold`（CV 主导时） |
| Bio 极小样本 | `n_test < 10` | **leave-one-out CV** 替代 k-fold（k = n_test）;头条指标仍报 bootstrap CI | `LOO-CV` |
| Wet-lab assay | 任意 | `>= 3 biological replicates × >= 3 technical replicates`。在 `## Procedure` 中显式标哪个是哪个;biological replicate 是独立样本,technical replicate 是同一样本重复读 —— 二者答不同问题。 | 在 `## Procedure` 文档 bio×tech 拆分;若与 in-silico 重抽混合再填 `random_seed_protocol` |

类不平衡检查：二分类任务若 `min(n_positives, n_negatives) < 20`,k-fold 按类分层 AND 报告逐类指标,不仅是头条 AUC。在不平衡 bio 集上只报 AUC 经常掩盖少数类的大幅下降。

每个实验块包含：
- `title`：描述性标题
- `linked_idea`：源 idea slug（必填；schema 要求字段，写入时校验）
- `hypothesis`：实验验证的具体假设
- `type`：baseline / validation / ablation / robustness —— 对 bio 设计可额外加 negative_control / mechanism / dose_response / cross_context 之一或多个。作为 tag 记录而非 frontmatter 枚举（experiments schema 没有 `type` 字段）。
- `setup`：model、dataset、hardware、framework
- `metrics`：评估指标列表
- `baseline`：对比基线
- `success_criterion`：明确的成功/失败标准（写在实验页面的 `## Procedure` 节）
- `estimated_gpu_hours`：预估计算时间
- `seeds`：随机种子数量（`n_test >= 50` 时 >= 3;小样本 bio 集合按上方 Statistical defaults 表用 bootstrap / stratified-k-fold / LOO-CV —— 把选择记入 `setup.random_seed_protocol`）

### Step 4: 构建执行顺序（Build Run Order）

**Vocabulary disambiguation**（bio-D1 minimal pilot 2026-05-12 合并）：本 skill 用 **Stage 0..4** 表示运行顺序位置。**不**用 "Phase" 表此意 —— "Phase" 留给用户领域的本义。药物发现里 "Phase 0" = 临床前 pilot,"Phase 1–3" = 临床试验阶段;部分 bio idea 页面的 "Phase-0 noise-floor calibration" 或 "Phase-1 dose escalation" 带的是领域含义而非 skill 工作流含义。输出时一律说 "Stage N" 指 skill 的运行顺序步。解析 idea 页面遇到 "Phase-N" 时视为领域词汇,**不**静默重映射为 Stage-N —— 把 bio 含义反映到实验的 `## Procedure` 文本即可。单页确需两者同存时（"Stage 2b 跑 Phase-0 noise-floor calibration 子协议"）,两者并存,读者上下文消歧。

按依赖关系排序实验，设置决策门：

```
Stage 0: Sanity check
  └── 小规模运行（1 epoch / 100 steps）验证代码无 bug、数据可加载、GPU 可用
  └── 门：若 sanity 失败 → 停止，修复代码

Stage 1: Baseline（基线复现）
  └── 复现基线结果
  └── 门：若基线偏差 > 5% → 停止，检查实现（与 Step 3 成功标准同阈值）

Stage 2: Validation（核心验证）
  └── 在基线之上验证 idea 的核心命题
  └── 门：若无提升 → 停止，分析原因（可能是 idea 不成立）

Stage 3: Ablation（因素隔离）
  └── 可并行执行多个 ablation
  └── 门：若某因素 ablation 无影响 → 记录，但继续其他 ablation

Stage 4: Robustness（鲁棒性验证）
  └── 仅在 Stage 2 成功后执行
  └── 范围由 --budget 剩余额度决定
```

输出：
- 有序实验列表（含依赖关系）
- 每阶段的决策门条件
- 总计算预算估算（若超过 --budget 则调整 Stage 4 范围）

### Step 5: 可选 Review LLM Review（--review）

若指定 `--review`：

```
mcp__llm-review__chat:
  system: "You are a senior ML researcher reviewing an experiment plan.
           Focus on: missing baselines, missing ablations, unfair comparisons,
           statistical rigor (enough seeds?), and dataset selection.
           For every issue found, suggest a concrete fix."
  message: |
    ## Idea
    {idea title, hypothesis, novelty argument}

    ## Experiment Plan
    {complete experiment plan: scope sheet, blocks, run order, budgets}

    ## Context
    {related papers' experiment setups, concepts/methods the idea inherits}

    ## Review Questions
    1. Are any critical experiments missing?
    2. Are the baselines fair and comprehensive?
    3. Is the ablation design sufficient to isolate each contribution?
    4. Are the success criteria well-defined and reasonable?
    5. Any statistical concerns (sample size, variance, seeds)? For small-n bio sets (n_test < 50), is the protocol bootstrap CI + stratified k-fold (or LOO-CV when n_test < 10), or does it still rely on multi-seed only? For wet-lab assays, are biological vs technical replicates explicitly labelled?
```

根据 Review LLM 反馈调整实验计划（添加遗漏的实验、修正不合理的标准）。

### Step 6: 写入 Wiki

1. **创建实验页面**：
   对每个实验块：
   ```bash
   python3 tools/research_wiki.py slug "<experiment-title>"
   ```
   创建 `wiki/experiments/{slug}.md`，严格遵循 `runtime/schema/entities.yaml::experiments` 与 `runtime/templates/experiments.md.tmpl` —— 下方所有 frontmatter 字段都必须存在（即使为空），因为 `/exp-run` 稍后会用 `tools/research_wiki.py set-meta` 来更新它们，而 `set-meta` 拒绝创建 frontmatter 中不存在的字段：
   ```yaml
   ---
   title: ""
   slug: ""
   status: planned
   linked_idea: "{idea-slug}"   # 必填（schema 要求）。通过 xref.yaml 反向链回 wiki/ideas/{idea-slug}.md::linked_experiments。
   hypothesis: ""
   tags: []                     # 把类型 tag 放在这里：["baseline"]、["validation"]、["ablation"] 或 ["robustness"]；bio 设计可叠加 ["mechanism"]、["dose_response"]、["negative_control"]、["cross_context"]
   setup:
     model: ""
     dataset: ""
     hardware: ""
     framework: ""
     # bio-A5 full（2026-05-12 pilot merge）：可选的 bio 形态 setup 字段。纯 ML 设计留空仍合法。
     # in_silico_or_wet 由 Step 1 湿实验依赖探测驱动；force_field / solvent_model / simulation_length
     # 仅 MD 流水线；species / cell_line / assay_type 覆盖湿实验与 cross_context；weight_version
     # 捕获多版本 ML 模型；random_seed_protocol 记录实际复制策略。
     in_silico_or_wet: ""         # in_silico | wet_lab | mixed
     species: []                  # ["human"] | ["mouse", "human"] | …
     cell_line: ""                # 优先 Cellosaurus ID（如 HEK293T 是 CVCL_0023）
     assay_type: ""               # MD | docking | scoring | Y2H | AP-MS | cryo-EM | NMR | binding_assay | …
     force_field: ""              # 仅 MD（如 "AMBER ff14SB + phosaa14SB"）
     solvent_model: ""            # 仅 MD（explicit | implicit | vacuum）
     simulation_length: ""        # 仅 MD（如 "50 ns"）
     weight_version: ""           # 多版本 ML 模型（如 "Boltz-2 Jan 2026 weights"）
     random_seed_protocol: ""     # ranking-shuffle | bootstrap | stratified-k-fold | LOO-CV
   metrics: []
   baseline: ""
   outcome: ""                  # 留空，由 /exp-run Phase 4 填写 — succeeded | failed | inconclusive
   key_result: ""               # 留空，由 /exp-run Phase 4 填写
   date_planned: YYYY-MM-DD
   date_completed: ""           # 留空，由 /exp-run Phase 4 填写
   run_log: ""                  # 留空，由 /exp-run Phase 2 填写
   started: ""                  # 留空，由 /exp-run Phase 2 填写（ISO 时间戳，通过 set-meta）
   estimated_hours: 0           # bio-A6：legacy 单数字预算 —— 向后兼容保留
   # bio-C2（2026-05-11 minimal pilot merge）：根据 Step 3 / Step 4 的预算拆分填充结构化
   # estimated_cost 块。用真实的逐实验数字；子字段对该实验不适用时填 0（例如纯算力流水线
   # wet_lab_usd: 0；公开数据集如 [[ternarydb]] 时 dataset_access_lead_time_days: 0）。保留
   # estimated_hours 作为 GPU 时数的粗合计供 legacy 消费者使用；estimated_cost.gpu_hours
   # 通常应等于 estimated_hours。完整 C2（自动检测湿实验 / MD 墙钟时）延后 —— 最小 pilot
   # 阶段，从 setup.framework 和 setup.hardware 字段推断拆分。
   estimated_cost:
     gpu_hours: 0
     cpu_hours: 0
     md_wallclock_hours: 0      # > 0 仅适用于显式 MD 流水线（如 AMBER、GROMACS、OpenMM）
     wet_lab_usd: 0             # > 0 仅当实验含湿实验交接
     fte_weeks: 0               # 研究者时间估计（小/中/大粗粒度）
     dataset_access_lead_time_days: 0   # > 0 当 setup.dataset 需要注册 / DUA 时
   # bio-A8（2026-05-12 pilot merge）：reproducibility 块。实验摄取外部试剂 / 结构 / 数据集
   # 版本时填充非空子字段。纯 in-silico 无外部数据时块可留空。lint_bio 会 cross-check
   # dataset_versions[*] 与 datasets/{slug}.md::versions —— setup.dataset wikilink 到含版本
   # 条目的外部 [[dataset]] 页时填此字段（如 dataset_versions: [{dataset_slug: ternarydb,
   # version: v1, accessed_date: 2026-05-02}]）。
   reproducibility:
     rrid: []                   # 抗体 / 试剂 RRID（如 ["AB_12345"]）
     cellosaurus: []            # 细胞系 Cellosaurus ID（如 ["CVCL_0023"]）
     addgene: []                # Addgene 质粒 ID（如 ["#12345"]）
     pdb_versions: []           # ["{PDB_ID}@{version-or-date}"]（如 ["6XYZ@2024-03-15"]）
     dataset_versions: []       # {dataset_slug, version, accessed_date} 列表
   remote:                      # 完整 block 必须存在，以便 /exp-run --env remote 通过 Edit 填充子字段
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ---

   ## Objective
   {该实验为 linked idea 验证什么}

   ## Setup
   {detailed setup: model, dataset, hardware, hyperparameters}

   ## Procedure
   {step-by-step execution plan, including the explicit success criterion}

   ## Results
   (to be filled after /exp-run)

   ## Analysis
   (to be filled after /exp-run)

   ## Idea updates
   (to be filled after /exp-eval — 记录 linked idea 的 status / pilot_result 变化)

   ## Follow-up
   {contingency plans: what to do if success / failure}
   ```

2. **添加 graph edges**：
   ```bash
   # 对每个实验：idea → experiment
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "ideas/{idea-slug}" --to "experiments/{slug}" \
     --type tested_by --evidence "Designed by /exp-design"
   ```

3. **更新 idea 页面**：
   - 在 `wiki/ideas/{idea-slug}.md` 的 `linked_experiments` 追加所有新建实验的 slugs
   - 若 idea status 为 `proposed`，通过 `tools/research_wiki.py transition` 推进到 `in_progress`

4. **更新 index.md**：在 experiments 类别下追加条目。

5. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

6. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-design | {N} experiments designed for idea {slug} | linked_idea: {slug}"
   ```

7. **输出 EXPERIMENT_PLAN_REPORT 到终端**：
   ```markdown
   # Experiment Plan Report

   ## Target Idea
   - Idea: [[idea-slug]]
   - Hypothesis: {hypothesis}
   - Novelty score: N/5（未评分时填 "—"）

   ## Scoped Hypothesis
   | Dimension | Proposition | Source |
   |-----------|-------------|--------|
   | target | {target proposition} | idea ## Hypothesis |
   | decomposition | {factor 1} | method [[method-slug]] |
   | decomposition | {factor 2} | method [[method-slug]] |
   | threat | {known risk} | idea ## Risks / concept ## Open problems |

   ## Experiment Blocks
   | # | Experiment | Type | Linked idea | GPU-hrs | Stage |
   |---|-----------|------|-------------|---------|-------|
   | 1 | [[baseline-slug]] | baseline | idea-slug | 2 | 1 |
   | 2 | [[validation-slug]] | validation | idea-slug | 8 | 2 |
   | 3 | [[ablation-1-slug]] | ablation | idea-slug | 8 | 3 |
   | 4 | [[robustness-slug]] | robustness | idea-slug | 16 | 4 |

   ## Run Order
   Stage 0: Sanity → Stage 1: Baseline → Stage 2: Validation → Stage 3: Ablation → Stage 4: Robustness
   Decision gates at each stage boundary.

   ## Budget
   - Total estimated: {N} GPU-hours
   - Budget limit: {--budget or "unlimited"}

   ## Next Steps
   - Run `/exp-run [[baseline-slug]]` to start Stage 1
   - After each stage, run `/exp-eval` to update the linked idea's status / pilot_result
   ```

## Constraints

- **每个实验必须关联 idea**：`linked_idea` 是 schema 要求字段，也是本 skill 合同要求。若没有 idea 页面，拒绝设计实验 —— 让用户先跑 `/ideate` 或自行写一份 idea 页面。
- **实验不可重复**：创建前扫描 `wiki/experiments/*.md` 中是否已存在相同 `linked_idea` + `hypothesis` 的实验。
- **scope sheet 不持久化**：Step 2 的维度表是规划产物，不写入 wiki。`/exp-design` 不得创建新的 concept/method/topic 页面。
- **success criterion 必须量化**：每个实验块的成功标准必须包含具体数值（如 "> 2% accuracy improvement"），写在 `## Procedure` 正文章节。
- **统计可靠性**：需要统计可靠性的实验（validation、ablation）必须按 Step 3 Statistical defaults 表指定协议。`n_test >= 50`：>= 3 random seeds。`n_test < 50`：bootstrap CI + stratified k-fold（`n_test < 10` 改 LOO-CV）。Wet-lab assay：>= 3 biological × >= 3 technical replicates 并显式标注。
- **graph edges 使用 tools/research_wiki.py**：不手动编辑 `edges.jsonl`。
- **idea status 只能前进**：`proposed → in_progress`，不可逆（受 `entities.yaml::ideas.lifecycle` 约束）。
- **slug 唯一性**：创建前检查是否存在相同 slug。

## Error Handling

- **idea 找不到**：提示用户检查 slug，列出 `wiki/ideas/` 中的候选。
- **自由文本输入但未传 `--linked-idea`**：拒绝继续 —— 引导用户先跑 `/ideate` 或显式传 `--linked-idea`。
- **已有相似实验**：列出已有实验，询问用户是继续追加还是跳过。
- **Review LLM 不可用**（`--review` 模式）：跳过 Step 5，在报告中标注「unreviewed — Review LLM unavailable」。
- **budget 不足**：削减 Stage 4 robustness 实验范围，在报告中标注实际预算分配。
- **slug 冲突**：追加数字后缀（如 `sparse-lora-ablation-v2`）。
- **wiki 为空**：正常执行但 baseline 实验无法参考已有结果，在报告中建议先 `/ingest` 相关论文。

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py transition wiki/ideas/{slug}.md --to in_progress` — 推进 idea 生命周期
- `python3 tools/research_wiki.py set-meta wiki/ideas/{slug}.md linked_experiments [<slug>] --append` — 更新 idea 的 linked_experiments
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建 gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志

### MCP Servers
- `mcp__llm-review__chat` — Step 5 实验计划审查（可选）

### Claude Code Native
- `Read` — 读取 wiki 页面
- `Glob` — 查找已有实验

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Step 5 Review LLM 审查独立性（若启用）

### Called by
- `/research` Stage 2（实验设计阶段）
- 用户直接调用
- SPA 中 idea 阅读页的动作按钮（`/exp-design --linked-idea <idea-slug>`，由 `tools/serve.py` 调度）
