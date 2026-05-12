---
description: 解析评审意见 → 原子化为 concern（Rvx-Cy）→ 映射到 wiki claim → 检查 evidence → Review LLM 压力测试 → 生成答辩；可通过 /exp-design 自动 scaffold 后续湿实验
argument-hint: <review-file-or-path> [--paper-slug <slug>] [--venue <venue>] [--stress-test] [--format formal|rich] [--scaffold-followups]
---

<!-- bio-C11: 镜像自 i18n/zh/skills/rebuttal/SKILL.md，加入 C11（追踪承诺的后续湿实验）草稿。
     真值源：i18n/zh/skills/rebuttal/SKILL.md。本路径不参与运行；要测试请先合回真值源。

     跨节依赖：
       /exp-design（C4+C5+C6）—— Strategy B 答复承诺新湿实验时由本 skill 自动 scaffold experiment 页。
            Bio / 临床 venue 的 reviewer 经常把额外湿实验作为接受条件；把那些承诺转成可追踪 deliverable
            能避免 rebuttal commitment 烂尾。
       A5 —— scaffold 出的后续 experiment 自动填 `setup.in_silico_or_wet | assay_type | cell_line | species`，
            让 /check + /exp-status 后续能跟踪。
       C8（lint_bio）—— 新 `triggered_by_rebuttal` 字段把 scaffolded experiment 关回 review thread；
            后续 experiment 上缺该字段是 🟡 lint 候选（不在 C8 v1 但是自然延展）。

     新 flag `--scaffold-followups` 是 opt-in：未传时 /rebuttal 流程不变（Strategy B 仍只产文本承诺）。
     传了的话 Step 4 收集所有 Strategy B commitment，然后每条逐一调 /exp-design，并附
     `--triggered-by-rebuttal` 注明 provenance。 -->

# /rebuttal

> 解析评审意见，把每个 concern 原子化（Rvx-Cy 编号）并映射到 wiki claim，
> 检查 evidence 是否充足（追溯到 wiki experiment），用 Review LLM 模拟 reviewer follow-up 问题（压力测试，1-5 分），
> 生成正式纯文本答辩与富文本答辩。
> 安全检查确保不编造、不空头承诺、覆盖完整。
> <!-- bio-C11 --> 传 `--scaffold-followups` 时，每条 Strategy B 承诺新建一个实验的 commitment 都会通过 `/exp-design` 转化为 `wiki/experiments/{slug}.md` 脚手架，并附 `triggered_by_rebuttal` provenance 字段连回答辩。纯文本答辩仍只送承诺文本；wiki 拿到一个可追踪 deliverable。

## Inputs

- `review`：评审意见来源，以下之一：
  - 文件路径（如 `raw/reviews/reviewer1.txt`、`raw/reviews/meta-review.md`）
  - 多个文件路径（逗号分隔：`raw/reviews/R1.txt,raw/reviews/R2.txt,raw/reviews/R3.txt`）
  - 直接粘贴的评审文本
- `--paper-slug`（可选）：关联论文在 wiki/outputs/ 的 slug，用于定位 PAPER_PLAN
- `--venue`（可选）：目标会议/期刊（ICLR / NeurIPS / ICML / ACL / CVPR / Nature / Cell / NEJM / JAMA / Lancet）；影响答辩格式与字数限制
- `--stress-test`（可选，默认启用）：Review LLM 模拟 reviewer follow-up；用 `--no-stress-test` 关闭
- `--format`（可选，默认 `formal`）：输出格式
  - `formal`：正式纯文本答辩（适合直接粘贴投稿系统）
  - `rich`：富文本版（带 wiki [[links]]、详细分析、改进计划）
- <!-- bio-C11 --> `--scaffold-followups`（可选，默认关闭）：对每条承诺新建实验的 Strategy B commitment，通过 `/exp-design` 自动 scaffold 一个 `wiki/experiments/{slug}.md` 页（每条 commitment 一次调用）。每个 scaffold 出的 experiment 都带 `triggered_by_rebuttal: <paper-slug>` provenance 字段。**默认关闭**因为旧流程是纯文本；opt-in 保后向兼容，且用户通常想在自动产生 3+ 个新"已规划"实验前显式确认。

## Outputs

- **wiki/outputs/rebuttal-{slug}.md** — 富文本答辩（带 [[wikilinks]]、evidence trace、分析表）
- **wiki/outputs/rebuttal-{slug}.txt** — 正式答辩（纯文本，适合粘贴投稿系统）
- **wiki/claims/*.md** — 若某 concern 暴露 evidence gap，向 `## Open questions` 追加建议
- <!-- bio-C11 --> **wiki/experiments/{follow-up-slug}.md** — 传了 `--scaffold-followups` 时每条 Strategy B commitment 一个 scaffold experiment 页，带 `triggered_by_rebuttal: <paper-slug>` 与 `status: planned`
- **wiki/log.md** — 追加日志

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — 把 concern 映射到 claim，检查 evidence 充足性
- `wiki/experiments/*.md` — 找支撑 claim 的实验结果
- `wiki/papers/*.md` — 找引用上下文
- `wiki/concepts/*.md` — 理解方法相关 concern 的概念背景
- `wiki/ideas/*.md` — 找 idea 的 motivation 与 pilot results
- `wiki/outputs/PAPER_PLAN.md` — 理解论文结构（来自 /paper-plan，传了 --paper-slug 时）
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/edges.jsonl` — claim-experiment-paper 关系
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM 压力测试独立性

### Writes
- `wiki/outputs/rebuttal-{slug}.md` — 富文本版
- `wiki/outputs/rebuttal-{slug}.txt` — 正式纯文本版
- `wiki/claims/*.md` — 把 reviewer 识别的 gap 追加到 `## Open questions`（不直接改 confidence/status；只加建议）
- <!-- bio-C11 --> `wiki/experiments/{follow-up-slug}.md` — scaffold 出的后续 experiment（仅传 `--scaffold-followups` 时；通过 `/exp-design` 创建）
- `wiki/log.md` — 追加日志

### Graph edges created
- 直接无。<!-- bio-C11 --> `--scaffold-followups` 触发 `/exp-design` 时，那个 skill 按其契约在 scaffold 的 experiment 与其 `target_claim` 之间建 `tested_by` 边；`/rebuttal` 自身不直接写 graph 边。

## Workflow

**前置**：
1. 确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/`）
2. 读 `cross-model-review.md` 确认压力测试独立性原则
3. 生成 slug：`python3 tools/research_wiki.py slug "{paper-slug}-rebuttal"`

### Step 1: 解析评审意见

（同旧：读评审文件 / 粘贴文本；提取每位 reviewer 的总分、summary、Strengths、Weaknesses、questions；输出结构化意见。）

### Step 2: 原子化 concern

（同旧：把每条 weakness/question 拆为 Rvx-Cy 原子 concern；分类为 evidence/method/missing/clarity/scope/novelty/minor；评估 severity。）

### Step 3: 把 concern 映射到 wiki claim

（同旧：搜 claim 与 edge 找关联 claim；检查 Evidence Status 为 sufficient/partial/insufficient/contradicted；选 Strategy A/B/C/D。）

### Step 4: 起草答辩

按 strategy 起草每条 concern 的回应：

**Strategy A — 证据充足（直接回应）**：
- 引用具体实验结果与数据（标来源，确保可追溯到 wiki/experiments/）
- 指向 wiki 中的 evidence（转化为论文引用）
- concern 基于误解：礼貌澄清，指向论文相关 Section

**Strategy B — 证据不足（承认 + 具体方案）**：
- 诚实承认当前证据不足
- 提出具体的补充实验方案（具体到 assay type、cell line / species / data、复制数、统计分析、预期时间线）
- 给具体时间线与资源需求
- 不用模糊承诺；只承诺具体可执行的补充实验
- <!-- bio-C11 --> **把 commitment 记录为结构化记录**让其能成为可追踪 deliverable。每条 Strategy B 答复记：
  ```yaml
  commitment_id: Rvx-Cy
  proposed_title: "<short experiment title>"
  target_claim: "<existing claim slug if mapped, or 'unmapped'>"
  setup_hint:
    in_silico_or_wet: wet | in_silico | hybrid
    assay_type: ""             # 例如 CETSA | nanoBRET | RNA-seq | docking | MD
    species: ""
    cell_line: ""              # 优先填 CVCL ID
  estimated_cost_hint:         # 从承诺文本中粗解析的数字，喂给 /exp-design
    gpu_hours: 0
    md_wallclock_hours: 0
    wet_lab_usd: 0
    fte_weeks: 0
  rationale: "<why this experiment addresses the concern>"
  ```
  这些记录留在内存中直到 Step 6e —— 默认仅作为富文本答辩的 "Suggested Experiments" 出现，传 `--scaffold-followups` 时喂给 `/exp-design` 转化为 scaffold experiment 页。

**Strategy C — clarity 问题（承诺修订）**：
（同旧：承认表述不清；提供改进描述（在答辩中直接显示修订后文字）；列具体 Paper Edit 计划。）

**Strategy D — scope/novelty 挑战（论辩）**：
（同旧：突出与现有工作的本质差异；引用 novelty-check 结果；点出 reviewer 可能漏看的差别。）

**每条回应格式**：
```markdown
**[Rvx-Cy]** {concern summary}

{response text, 2-5 sentences, annotated sources for traceability}
```

**安全检查（每条回应）**：
- [ ] 不编造：不捏造数据或实验结果
- [ ] 不空头承诺：只承诺具体可执行的补充实验
- [ ] 引用的数据已在 wiki/experiments/ 中
- [ ] 若 claim 是 challenged/deprecated，不假装它已被支持
- <!-- bio-C11 --> [ ] Strategy B 承诺含足够具体的 setup hint（湿实验非空 `assay_type`，动物/细胞实验非空 `species` 与 `cell_line`），让 `/exp-design` 能 scaffold 而无须用户进一步输入。承诺过于含糊时在报告中发 🟡，请用户细化后再 scaffold。

### Step 5: Review LLM 压力测试

（同旧：Review LLM 1-5 分；reviewer 推回弱回应；评分 ≤2 重写；最多 2 轮；<!-- bio-C11 --> *压力测试 prompt 更新以特别检查 Strategy B commitment 是否具体到能 scaffold 成真实 experiment 页 —— 含糊承诺现在打更低分*。）

```
mcp__llm-review__chat:
  system: "You are a critical reviewer who has just read a rebuttal to your review
           comments. You are skeptical and will push back on weak responses.
           For each rebuttal response, assess on a scale of 1-5:
           1 = unconvincing (deflection or fabrication suspected)
           2 = weak (vague, no concrete evidence; for Strategy B: too vague to scaffold)   <!-- bio-C11 -->
           3 = acceptable (addresses concern but could be stronger)
           4 = strong (concrete evidence, clear reasoning; for Strategy B: scaffoldable)   <!-- bio-C11 -->
           5 = fully convincing (compelling evidence, thorough response)
           Also check for overpromise: are commitments specific and feasible?
           When the response is Strategy B (commits to a new experiment),
           explicitly check whether the commitment names: assay type, system
           (cell line / species / dataset), readout, replicate counts,
           and a specific timeline. Generic 'we will run experiments' must
           score 1-2. A response that names CETSA on HEK293 cells, n=3 biological,
           with a 4-week timeline scores 4-5.   <!-- bio-C11 -->
           Provide a follow-up question for any response scoring <= 3."
  message: |
    ## Original Review Concerns
    {atomic concerns list with Rvx-Cy IDs}

    ## Author Rebuttal
    {drafted rebuttal responses}

    ## Please assess each response (score 1-5) and provide follow-up questions.
```

### Step 6: 格式化输出 + 安全检查

**6a. 格式化正式 rebuttal-{slug}.txt**（纯文本，适合投稿系统）：

（同旧结构。）

**6b. 格式化富文本 rebuttal-{slug}.md**：

```markdown
# Rebuttal Analysis: {paper title}

## Coverage Summary
{表格同旧}

## Responses
### Reviewer 1
**[Rv1-C1]** ...
**[Rv1-C2]** ...

## Evidence Gap Analysis
{同旧}

## Action Items

### Paper Edits
{同旧}

### Wiki Updates
{同旧}

### Suggested Experiments       <!-- bio-C11 -->
| Experiment | Target Claim | Suggested by | Setup Hint | Cost Hint | Scaffolded? |
|-----------|-------------|--------------|------------|-----------|-------------|
| ablation-dataset-x | [[claim-slug]] | Rv1-C2 | wet, CETSA, HEK293, n=3×3 | $8k wet-lab, 4 fte_weeks | ✅ wiki/experiments/ablation-dataset-x.md |
| mechanism-mutagenesis-y | [[claim-slug]] | Rv2-C3 | wet, point mutagenesis, HEK293, n=3×3 | $5k wet-lab, 3 fte_weeks | ❌ (--scaffold-followups not set) |

→ Run `/exp-design ablation-dataset-x` to refine the scaffolded experiment

## Review LLM Stress-Test Summary
{同旧}

## Safety Checklist
- [x] No fabrication: all cited data exists in wiki/experiments
- [x] No overpromise: all committed experiments are specific and feasible
- [x] Full coverage: {N}/{N} concerns addressed (no omissions)
- [x] Challenged claims not presented as supported
- [x] Strategy B commitments are scaffoldable (concrete assay/system/replicates)   <!-- bio-C11 -->
```

**6c. 最终安全检查**：
（同旧。）

<!-- bio-C11 -->

**6d. 可选 follow-up scaffolding**（传 `--scaffold-followups` 时）：

对 Step 4 收集的每条 Strategy B commitment 记录：

1. **预飞检查**：确认 commitment 结构化记录有非空 `proposed_title`、`target_claim`（或 "unmapped"）、`setup_hint.in_silico_or_wet`。任一必填缺则跳过该条并在报告中发 🟡。

2. **生成 slug**：
   ```bash
   python3 tools/research_wiki.py slug "{commitment.proposed_title}"
   ```

3. **调 `/exp-design`**：
   ```
   Skill: exp-design
   Args: "<proposed_title and rationale>" \
         --triggered-by-rebuttal {paper-slug} \
         --commitment-id {Rvx-Cy} \
         --setup-hint {parsed setup_hint as flags} \
         --auto
   ```

   注：`/exp-design` 当前未文档化 `--triggered-by-rebuttal`、`--commitment-id`、`--setup-hint` 这些用户面 flag —— 它们是 bio-C11 对 `/exp-design` SKILL.md 的后续添加（与 C11 一同列为 planned tooling）。这些 flag 落地之前，`/rebuttal` 退化为不带它们调 `/exp-design`，事后用 `tools/research_wiki.py set-meta` 把 `triggered_by_rebuttal` 字段写入 experiment 页。两条路径产出相同最终状态。

4. **验证 scaffold**：确认 `wiki/experiments/{slug}.md` 已建，含：
   - `status: planned`
   - `target_claim: <commitment.target_claim>`（或为空，若 "unmapped"）
   - `triggered_by_rebuttal: <paper-slug>`（provenance 字段；必填）
   - `triggered_by_concern: <Rvx-Cy>`（provenance 字段；必填）
   - `setup` 由 `commitment.setup_hint` 填
   - `estimated_cost` 由 `commitment.estimated_cost_hint` 填

5. **更新富文本答辩**：在 "Suggested Experiments" 表中把对应行 `Scaffolded?` 列标为新页的 wikilink。

**6e. 更新 wiki**：
- 对带 evidence gap 的 claim：把 reviewer 识别的 gap 追加到 `wiki/claims/{slug}.md` 的 `## Open questions`
- 追加日志：
  ```bash
  python3 tools/research_wiki.py log wiki/ \
    "rebuttal | {N} concerns addressed | {M} evidence gaps | {S} stress-test avg | {F} follow-ups scaffolded"
  ```
  <!-- bio-C11：log 行末尾加 follow-ups-scaffolded 数 -->

## Constraints

- **不编造**：永不捏造实验数据或结果。引用的每个数字必须可追溯到 wiki/experiments/ 并标来源
- **不空头承诺**：只承诺具体可执行的补充实验。用 "we will run ablation on X with setup Y" 而非 "we will investigate"
- **覆盖完整**：每条 reviewer concern（Rvx-Cy）必须有回应；遗漏阻塞输出
- **evidence 可追溯**：回应中引用的每条 evidence 必须可追溯到 wiki 页并标 source slug
- **不直接改 wiki claims**：rebuttal 仅向 claim 的 Open questions 追加建议；不改 confidence/status
- **Review LLM 独立性**：压力测试中遵循 cross-model-review.md；不向 Review LLM 透露答辩策略
- **concern ID 格式**：严格用 Rvx-Cy（Rv1-C1, Rv1-C2, Rv2-C1）确保可追溯
- **承诺具体**：所有修订承诺与实验计划必须具体（具体 Section、具体 dataset、明确 metric）
- **输出到 wiki/outputs/**：rebuttal 文件统一存到 wiki/outputs/ 目录
- <!-- bio-C11 --> **Strategy B 承诺必须可 scaffold**：承诺新实验时，散文中必须含足够细节（assay type / system / 复制数）以填一个 `experiments/{slug}.md` 页。Review LLM 压力测试强制此条。
- <!-- bio-C11 --> **scaffold 出的后续带 `triggered_by_rebuttal` provenance**：通过 `--scaffold-followups` 创建的每个 experiment 都必须在 frontmatter 含 `triggered_by_rebuttal: <paper-slug>` 与 `triggered_by_concern: <Rvx-Cy>`。未来 `/check` 可用此检测未兑现的 rebuttal commitment（列入 "C8 future extensions" —— 不在 C8 v1）。
- <!-- bio-C11 --> **`--scaffold-followups` opt-in**：即便 bio reviewer 显式要求后续实验，用户也必须主动启用。从 rebuttal 文本静默生成 experiment 页是高代价惊喜（用户醒来发现 5 个新"已规划"实验却记不起为什么）。

## Error Handling

- **review 文件找不到**：报错，列 raw/reviews/ 下可用文件
- **review 格式无法解析**：退化为纯文本处理；用 LLM 抽 concern；报告中标注
- **concern 无法映射到 claim（unmapped）**：标 "unmapped"；仍回应（基于论文内容而非 wiki claim）。<!-- bio-C11 --> *传了 --scaffold-followups 而 Strategy B commitment 是 unmapped 时，仍 scaffold experiment 但 `target_claim: ""` 并发 🟡 提示请之后填上*
- **Review LLM 压力测试不可用**：跳 Step 5；报告中标 "stress-test skipped: Review LLM unavailable"
- **evidence 严重不足**：>50% concern evidence 不足时警告用户并建议先补实验
- **wiki 为空**：警告 wiki 知识库为空；建议先 /ingest 补 claim 与 experiment
- **Review LLM 全部回应打 1-2**：halt 输出，报告需要重新分析，建议先补实验
- <!-- bio-C11 --> **scaffold 阶段 `/exp-design` 调用失败**：报告中发 🔴；rebuttal 输出退化为纯文本（旧行为）；用户可手动跑 `/exp-design <slug>` 用 commitment 结构化记录补
- <!-- bio-C11 --> **Strategy B commitment 即便压力测试推回后仍太含糊**：发 🟡 而非 scaffold；富文本答辩 "Suggested Experiments" 行的 `Scaffolded?` 列标为 `❌ (commitment not concrete enough)` 并提示用户细化

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "{title}"` — 生成 rebuttal slug + scaffold experiment slug
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- <!-- bio-C11 --> `python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md triggered_by_rebuttal {paper-slug}` — `/exp-design` 尚不支持 `--triggered-by-rebuttal` 时的 fallback

### Skills（via Skill tool）
- <!-- bio-C11 --> `/exp-design` — 传 `--scaffold-followups` 时对每条 Strategy B commitment 调一次；把解析后的 commitment 记录作为输入

### MCP Servers
- `mcp__llm-review__chat` — Step 5 压力测试首轮
- `mcp__llm-review__chat-reply` — Step 5 压力测试后续轮

### Claude Code Native
- `Read` — 读评审意见、wiki 页、shared references
- `Write` — 写 rebuttal-{slug}.md、rebuttal-{slug}.txt
- `Glob` — 找 claim、experiment
- `Grep` — 在 wiki 中搜 concern 关键词

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM 压力测试独立性原则

### 建议后续 skill
- `/exp-design` — 为证据不足的 concern 设计补充实验（也是 `--scaffold-followups` 内部调用）
- `/paper-draft` — 准备修订论文（基于 Paper Edits 清单）
