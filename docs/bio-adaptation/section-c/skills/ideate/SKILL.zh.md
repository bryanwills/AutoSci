---
description: 多阶段研究 idea 生成管道：景观扫描 → 双模型脑暴 → 初筛 → 深度验证 → 写入 wiki
argument-hint: "[research-direction-or-topic] [--max-ideas N] [--skip-validation] [--auto] [--scope species=...|disease_area=...|data_regime=...]"
---

<!-- bio-C3: 镜像自 i18n/zh/skills/ideate/SKILL.md，加入 C3（failed-idea banlist 增 scope: species / disease_area / data_regime）草稿。
     真值源：i18n/zh/skills/ideate/SKILL.md。本路径不参与运行；要测试请先合回真值源。

     跨节依赖：
       A4 —— bio domain 受控词；新 `scope.disease_area` 在合适处复用 A4 取值
       A1 —— `scope.data_regime` 区分 high-data（如 PROTAC-DB 规模）与 low-data（如一次性 phospho-PROTAC 队列）；
            配合 `wiki/datasets/{slug}.versions[*].n_test` 时，banlist 匹配能用真实数字而非猜测

     `scope` 字段是 `wiki/ideas/{slug}.md` frontmatter 上的纯加法 —— C3 之前的 ideas 不带它就走旧的"全局 banlist"语义，
     既有 wiki 行为不变。 -->

# /ideate

> 基于 wiki 知识库和外部搜索，通过 5 阶段管道生成高质量研究 idea。
> Phase 1 扫描研究景观（wiki + WebSearch + S2），Phase 2 双模型脑暴（Claude + Review LLM 独立生成），
> Phase 3 初步筛选（可行性 + 快速 novelty），Phase 4 深度验证（调用 /novelty + /review），
> Phase 5 写入 wiki（ideas/ + graph edges），包括被淘汰的 ideas（记录原因作为 anti-repetition 记忆）。
> <!-- bio-C3 --> 失败 idea 匹配是**带 scope 的**：在 `species: human, data_regime: high-data` 上被禁的 idea，不会阻塞同一架构家族在 `species: plant` 或 low-data 场景的探索。Scope 是每个 idea 上的可选元数据；缺省时表示"全局"（旧行为）。

## Inputs

- `direction`（可选）：研究方向、关键词或具体问题描述。若不指定，则从 open_questions.md 自动选择最有价值的方向。
- `--max-ideas N`（可选，默认 3）：最终写入 wiki 的 idea 数量上限
- `--skip-validation`：跳过 Phase 4 深度验证（快速模式，仅做 Phase 1-3 + Phase 5）
- `--auto`：全自动模式，不暂停等待用户确认（用于 /research 调用）
- <!-- bio-C3 --> `--scope species=<value>|disease_area=<value>|data_regime=<value>`（可选，可重复，逗号或空格分隔的 `key=value`）：本次运行所瞄准的 bio 轴 scope。新 idea 继承该 scope；banlist 匹配仅在失败 idea 的 `scope` 与之有重叠时触发。CS 方向缺 `--scope` 没事 —— banlist 退回 global。Bio 方向缺 `--scope` 允许，但会在 IDEA_REPORT 中发 🟡 风格提示（"scope unset on a bio direction; banlist will treat all failed ideas as global"）。v1 允许键集合开放；A4 的 bio 词表是 `disease_area` 的推荐受控列表。

## Outputs

- `wiki/ideas/{slug}.md` — 每个 idea 一个页面（status: proposed），包含 top ideas 和被淘汰的 ideas
- `wiki/graph/edges.jsonl` — 新增 idea → claim/gap 的关系边
- `wiki/graph/context_brief.md` — 重建后的压缩上下文
- `wiki/graph/open_questions.md` — 重建后的知识缺口图
- **IDEA_REPORT**（输出到终端）— 管道执行摘要、排名结果、novelty 评分，<!-- bio-C3 --> scope 决策与按 scope-overlap 拆分的 banlist 命中

## Wiki Interaction

### Reads
- `wiki/graph/context_brief.md` — 全局上下文
- `wiki/graph/open_questions.md` — 知识缺口，驱动 idea 方向
- `wiki/ideas/*.md` — 已有 ideas，特别是 status=failed 的 ideas 及 failure_reason（banlist），<!-- bio-C3 --> *以及当存在时它们的 `scope` block*
- `wiki/claims/*.md` — 当前 claims 状态，识别 weakly_supported 和 challenged claims
- `wiki/papers/*.md` — 已有论文方法和结果
- `wiki/concepts/*.md` — 技术概念，寻找跨领域组合机会
- `wiki/topics/*.md` — 研究方向地图，SOTA 和 open problems
- `wiki/experiments/*.md` — 已有实验结果，避免重复
- <!-- bio-C3（依赖 A1）--> `wiki/datasets/*.md` — `versions[*].n_test` 决定 `data_regime` scope 取值（high-data ≥ 1000 条目，low-data < 1000）

### Writes
- `wiki/ideas/{slug}.md` — 创建新 idea 页面
- `wiki/graph/edges.jsonl` — 添加 idea → claim/gap 的关系边（addresses_gap, inspired_by）
- `wiki/graph/context_brief.md` — 重建
- `wiki/graph/open_questions.md` — 重建
- `wiki/log.md` — 追加操作日志

### Graph edges created
- `addresses_gap`：idea → claim/topic（idea 针对的知识缺口）
- `inspired_by`：idea → paper/concept（idea 的灵感来源）

## Workflow

**前置**：
1. 确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）
2. **检查 wiki 成熟度**：
   ```bash
   python3 tools/research_wiki.py maturity wiki/ --json
   ```
   根据 maturity level 调整后续行为：
   - **cold**：Phase 1 外部搜索扩展（WebSearch 查询从 5 增至 8，S2/DeepXiv limit 从 20 增至 30），跳过 wiki 内部上下文加载（为空，无价值），标注 "cold-start mode: heavier external search"
   - **warm**：标准行为（当前默认）
   - **hot**：Phase 1 外部搜索收窄（WebSearch 查询从 5 减至 2，S2/DeepXiv limit 从 20 减至 10），Phase 3 gap_alignment_bonus 从 +2 增至 +3，优先解决 wiki 中已存在的弱 claims
3. **快照 wiki 状态**（用于结尾的 Growth Report）：将 maturity 返回的 JSON 存入内存变量 `maturity_before`
4. <!-- bio-C3 --> **解析当前 scope**（direction 明显是 CS —— `domain` 命中 `NLP|CV|ML Systems|Robotics` —— 时跳过）：
   - 已传 `--scope`：解析 `key=value` 对存为 `current_scope`
   - 否则从 `direction` 推断：抽取 gene symbol / disease 名 / dataset 名；映射到 `species` / `disease_area`（A4 词表）/ `data_regime`
   - 推断在 bio 方向上得到空 scope：发上文提到的 warning；本次 banlist 匹配按 global 处理

### Phase 1: 景观扫描（Landscape Scan）

目标：建立目标领域的全面视图，包括已有工作、知识缺口、最新进展。

1. **加载 wiki 内部上下文**：
   - 读 `wiki/graph/context_brief.md`（全局压缩上下文）
   - 读 `wiki/graph/open_questions.md`（知识缺口列表）
   - 读所有 `wiki/ideas/*.md`，提取：
     - status=failed → **banlist**（含 failure_reason，<!-- bio-C3 --> *与存在时的 `scope` block*）
     - status=proposed/in_progress → **active list**（避免重复）
   - 读 `wiki/claims/*.md`，找 status=weakly_supported / challenged 的 claims → **weak claims list**
   - 若指定了 `direction`，过滤到相关子集
   - <!-- bio-C3 --> **Banlist scope 过滤器**：每条 banlist 项目附 `scope_overlap` 注释 —— 失败 idea 没 `scope` block 时为 `True`（旧 global ban）；与解析出的 `current_scope` 至少有一个键重叠时为 `True`；否则 `False`。Phase 2/3 仅把 `scope_overlap == True` 的项视为硬阻塞；其余在报告中显示为"out-of-scope precedent — informational"。

2. **外部搜索**（用 Agent 工具并行）：
   - **WebSearch**：搜索目标方向最近 6 个月的论文与进展（3-5 个查询）
   - **Semantic Scholar**：
     ```bash
     python3 tools/fetch_s2.py search "<direction-keywords>" --limit 20
     ```
     拉 top 5 高被引论文详情
   - **DeepXiv 语义搜索**：
     ```bash
     python3 tools/fetch_deepxiv.py search "<direction-keywords>" --mode hybrid --limit 20
     ```
     对 top 5 最相关结果取 TLDR 与关键词：
     ```bash
     python3 tools/fetch_deepxiv.py brief <arxiv_id>
     ```
     语义搜索补 S2 关键词搜索可能漏掉的概念相似论文。
   - **DeepXiv trending**：
     ```bash
     python3 tools/fetch_deepxiv.py trending --days 14
     ```
     trending 表示社区关注热点，对发现 trend-driven gap 有用。
   - **arXiv latest**：`site:arxiv.org <direction> 2025 2026`
   - **若 DeepXiv 不可用**：跳过 DeepXiv 搜索与 trending，仅依赖 S2 + WebSearch（回退到旧行为）。

3. **编写 landscape 报告**（仅内部使用，不写 wiki）：
   - 当前 SOTA 方法与表现
   - 已知的 open problems / 未解决挑战
   - 最新趋势与热点
   - wiki 中的知识缺口（来自 gap_map）
   - 禁止方向（来自 banlist），<!-- bio-C3 --> *每项旁附 scope-overlap 状态*

### Phase 2: 双模型脑暴（Dual-Model Brainstorm）

目标：让 Claude 与 Review LLM 独立生成 ideas，利用模型视角差异获取多样性。

**遵循 `shared-references/cross-model-review.md`**：Claude 与 Review LLM 互不见对方输出。

1. **Claude 生成 6-10 个 ideas**：
   - 输入：landscape 报告 + wiki gaps + weak claims + banlist <!-- bio-C3 --> *（仅 in-scope 子集；out-of-scope 部分单列为信息性 precedent）*
   - 策略：
     - 跨领域组合（topic A 的方法 + topic B 的问题）
     - 填补 gap_map 缺口
     - 强化 weakly_supported claims
     - 给 challenged claims 出反假说
     - 已知 SOTA 局限 → 改进方向
     - <!-- bio-C3 --> **out-of-scope precedent 翻译**：失败 idea 被标 out-of-scope 时，考虑同样的架构是否能合法地应用到当前 scope（例如 "single-PTM phospho predictor saturated in human / high-data" 不阻碍 "same backbone in plant / low-data" —— precedent 的价值是它告诉你哪里已经拥挤，而不是一刀切的禁令）
   - 每个 idea 包含：title、hypothesis（1-2 句）、approach sketch（3-5 句）、target claims、可行性估计（high/medium/low），<!-- bio-C3 --> *以及一个 `scope` block 提案（默认继承 `current_scope`；仅在 idea 故意改 scope 时偏离）*

2. **Review LLM 独立生成 4-6 个 ideas**（并行）：
   ```
   mcp__llm-review__chat:
     system: "You are a creative ML researcher brainstorming research ideas.
              Generate novel, concrete, and feasible ideas based on the given context.
              For each idea, provide: title, hypothesis (1-2 sentences),
              approach sketch (3-5 sentences), and feasibility assessment.
              When the run is bio-scoped (species / disease_area / data_regime
              are provided), prefer ideas that fit that scope; out-of-scope
              banned precedents are informational, not hard blockers."   <!-- bio-C3 -->
     message: |
       ## Research Landscape
       {landscape report from Phase 1 — gaps, SOTA, trends}

       ## Current Scope                                                 <!-- bio-C3 -->
       {current_scope key=value list, or "global / unset"}

       ## Knowledge Gaps
       {gap_map entries}

       ## Banlist (DO NOT revisit these)
       {failed ideas with failure_reason — IN-SCOPE OVERLAPS ONLY}      <!-- bio-C3 -->

       ## Out-of-scope Precedent (informational)                        <!-- bio-C3 -->
       {failed ideas whose scope does not overlap current_scope — these
        are not bans; they tell you what's already saturated elsewhere}

       ## Active Ideas (avoid duplicating)
       {proposed/in_progress ideas}

       Generate 4-6 novel research ideas that address the gaps above.
       Focus on ideas that are: (1) genuinely novel, (2) feasible within 3-6 months,
       (3) directly address a knowledge gap.
   ```

3. **合并去重**：
   - 合并 Claude 与 Review LLM 的 ideas（10-16 候选）
   - 删除高度相似的 ideas（同核心方法的合并，保更具体的版本）
   - 删除与 **in-scope** banlist 重叠的 ideas <!-- bio-C3 -->
   - 删除与 active list 大量重复的 ideas
   - 输出：8-12 候选 ideas

### Phase 3: 初筛（First-Pass Filter）

目标：快速淘汰明显不可行或新颖性不足的 ideas。

对每个候选 idea 跑：

1. **可行性检查**：GPU/计算预算合理吗？数据可用？实现复杂度？打 high/medium/low。
2. **快速 novelty 筛**（每 idea 2-3 个 WebSearch 查询）：精确短语 + 组件组合 + 找到高度相似的发表工作 → 淘汰或标记。
3. **wiki 对齐检查**：是否针对 gap_map 的缺口？是否针对 weakly_supported claim？是否构建在已有 wiki 知识上？（+score）
4. **过滤决策**：
   - 淘汰：feasibility=low 且快速 novelty 找到相似发表工作
   - 淘汰：与 banlist 中 `scope_overlap == True` 的 failure_reason 高度相关 <!-- bio-C3 -->
   - 保留：feasibility >= medium 且未被淘汰
   - 输出：4-6 幸存 idea（已排序）

### Phase 4: 深度验证（Deep Validation）

（若 `--skip-validation` 设置则跳过，直接进入 Phase 5。）

对 Phase 3 的 top 3 ideas 跑：
1. **/novelty**（逐个）
2. **/review**（top 2）
3. **复合排名**：Final score = novelty_score × 2 + review_score + gap_alignment_bonus；novelty_score <= 2 → "modify needed"；review_score <= 4 → "major issues"
4. 若 `--auto` 未设：终端展示排名，等用户确认或调整

### Phase 5: 写入 Wiki

把验证后的 ideas 写入 wiki（淘汰的也写，记录原因）。

1. **写 top ideas**（status: proposed）：
   ```bash
   python3 tools/research_wiki.py slug "<idea-title>"
   ```
   严格按 CLAUDE.md ideas 模板创建 `wiki/ideas/{slug}.md`：
   ```yaml
   ---
   title: "<idea title>"
   slug: "<idea-slug>"
   status: proposed
   origin: "ideate: <short description>"
   origin_gaps: []
   tags: []
   domain: ""
   priority: 3
   pilot_result: ""
   failure_reason: ""
   linked_experiments: []
   date_proposed: YYYY-MM-DD
   date_resolved: ""
   # bio-C3：可选 scope block；默认继承 current_scope。C3 之前的 idea 不带这块退回 "global" 语义。
   scope:
     species: ""              # human | mouse | plant | microbial 等；空 = global
     disease_area: ""         # cancer-bio | structural-bio（A4 词表）等；空 = global
     data_regime: ""          # high-data | low-data | unknown；空 = global
   ---
   ```

   **Priority 计算**（把 Phase 4 信号映射到 1-5）：
   - `--skip-validation`：默认 `priority = 3`
   - 否则从 `novelty_score`（1-5）起算
   - `gap_alignment_bonus > 0` → `+1`
   - `review_score <= 4` → `-1`
   - clamp 到 `[1, 5]`

   正文 sections（严格匹配 CLAUDE.md 模板，不要改名）：`## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results`（留空）/ `## Lessons learned`（留空）。

2. **写淘汰的 ideas**（status: failed）：
   - `status: failed`
   - `priority: 1`
   - `date_resolved: YYYY-MM-DD`
   - `failure_reason: "[filter] <具体原因>"`
   - <!-- bio-C3 --> `scope:` 填该淘汰 idea **意图覆盖的 scope**（不是 global ban）—— 这让后续在另一 scope 跑的运行能正确绕过本条。淘汰原因若确实与 scope 无关（例如 "core math is wrong"），明确把三个子字段全留空 **并且**在 failure_reason 里点明这是 global ban（如 `"[filter] global: core derivation is incorrect"`）。
   - `## Motivation` 与 `## Hypothesis` 必填（让未来 banlist 匹配有内容）
   - 这些 failed ideas 成为未来 ideate 运行的 banlist

3. **添加 graph edges**：
   ```bash
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "ideas/{slug}" --to "claims/{target-claim}" \
     --type addresses_gap --evidence "Generated by ideate"

   python3 tools/research_wiki.py add-edge wiki/ \
     --from "ideas/{slug}" --to "papers/{source-paper}" \
     --type inspired_by --evidence "Inspired by method in {paper-title}"
   ```

4. **重建派生数据**：
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

5. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "ideate | {N} ideas proposed, {M} ideas filtered out | direction: {direction} | scope: {scope_summary}"
   ```
   <!-- bio-C3：log 行尾巴附解析后的 scope summary，便于 grep -->

6. **输出 IDEA_REPORT 到终端**：
   ```markdown
   # Idea Generation Report

   ## Pipeline Summary
   - Direction: {direction}
   - Scope: {current_scope or "global / unset"}                          <!-- bio-C3 -->
   - Phase 1: Scanned {N} external papers, {M} wiki gaps identified, {B} banlist entries (in-scope: {B_in}, out-of-scope precedent: {B_out})   <!-- bio-C3 -->
   - Phase 2: Generated {X} candidates (Claude: {a}, Review LLM: {b})
   - Phase 3: {Y} survived initial filter (from {X})
   - Phase 4: Deep validation on top {Z}
   - Phase 5: {K} ideas written to wiki

   ## Top Ideas (ranked)

   | Rank | Idea | Scope | Novelty | Review | Gap Align | Status |   <!-- bio-C3 -->
   |------|------|-------|---------|--------|-----------|--------|
   | 1 | [[slug]] | human / cancer-bio / high-data | 4/5 | 7/10 | +2 | proposed |
   | 2 | [[slug]] | (inherits current) | 3/5 | 6/10 | +0 | proposed |

   ## Filtered Out
   | Idea | Scope | Reason | Status |   <!-- bio-C3 -->
   |------|-------|--------|--------|
   | [[slug]] | (intended scope) | Similar published work exists | failed |
   | [[slug]] | global | Core derivation is incorrect | failed |

   ## Banlist Trace                                                    <!-- bio-C3 -->
   In-scope hits ({B_in}):
   - [[failed-slug]] → blocks "{candidate-title}" (overlap: species=human, data_regime=high-data)
   Out-of-scope precedents ({B_out}, informational only):
   - [[failed-slug]] (scope: human / high-data) — current scope is plant / low-data; not blocked but worth knowing

   ## Suggested Next Steps
   - Run `/exp-design {top-idea-slug}` to design experiments
   - Run `/novelty` on any idea before investing time

   ## Wiki Growth
   | Metric | Before | After | Delta |
   |--------|--------|-------|-------|
   | Papers | {before} | {after} | +{delta} |
   | Claims | {before} | {after} | +{delta} |
   | Ideas | {before} | {after} | +{delta} |
   | Edges | {before} | {after} | +{delta} |
   | Maturity | {before_level} | {after_level} | {unchanged/upgraded} |
   ```

## Constraints

- **wiki cold 时自动切换 cold-start 模式**：扩展外部搜索（WebSearch 8 个查询、S2/DeepXiv limit 30），不阻塞执行
- **每个 idea 必须有 wiki 锚点**：每条 idea 至少引用 2 个 wiki 页面（paper/concept/claim）
- **必须加载 banlist**：Phase 1 必须读 failed ideas 的 failure_reason；Phase 2/3 必须检查重叠
- <!-- bio-C3 --> **banlist 匹配带 scope**：失败 idea 阻塞候选仅当其 `scope` 与本次运行的 `current_scope` 至少一个键重叠，**或**失败 idea 没有 `scope` block（旧 global ban）。Out-of-scope precedent 必须在报告中可见但不阻塞。
- <!-- bio-C3 --> **失败 idea 应记录其自身 scope，不是当前运行的 scope**：写淘汰 idea 时 `scope` 填该 idea **意图覆盖的** scope，不是当前运行的 scope。例外：淘汰原因可证明与 scope 无关时把 `scope` 留空，**并**在 failure_reason 前缀加 `[filter] global:`。
- **Review LLM 独立性**：Phase 2 中 Review LLM 看不到 Claude 的 idea 列表（cross-model-review.md）
- **淘汰的 ideas 也写入 wiki**：status=failed + failure_reason，作为 anti-repetition 记忆
- **不编造**：所有 idea 必须从 wiki 已有知识或外部搜索结果衍生；不发明不存在的论文或方法
- **slug 唯一性**：创建前检查 wiki/ideas/ 中是否已存在同 slug
- **graph edges 经 tools/research_wiki.py**：不手动改 edges.jsonl

## Error Handling

- **wiki 为空**：用外部搜索（Phase 1 sources B/C/D），跳过 wiki 内部上下文；提示用户先建知识库
- **WebSearch 不可用**：跳过外部搜索，仅从 wiki 内部知识生成 idea（降级模式，报告中标注）
- **Semantic Scholar API 不可用**：跳过 S2 搜索，依赖 DeepXiv + WebSearch 补偿
- **DeepXiv API 不可用**：跳过 DeepXiv 搜索与 trending，回退到 S2 + WebSearch（旧行为）
- **Review LLM 不可用**：Phase 2 仅用 Claude（无双模型多样性，报告中标注）
- **/novelty 失败**：单 idea 在 Phase 4 失败时标 "novelty unverified" 后继续
- **/review 失败**：Phase 4 失败时标 "unreviewed" 后继续；建议用户手动 /review
- **slug 冲突**：在 wiki/ideas/ 已存在同 slug 时附数字后缀（如 `sparse-lora-v2`）
- **所有 idea 都被淘汰**：仍写入 wiki（status: failed）；报告建议用户拓宽搜索方向或 /ingest 更多论文
- <!-- bio-C3 --> **`--scope` 解析后键未知**（不在 `species|disease_area|data_regime`）：发警告，丢弃该未知键，用其余有效键继续。不要静默把未知键当作"匹配任意"。
- <!-- bio-C3 --> **bio 方向但 scope 为空**：在前置步骤 4 发警告；banlist 匹配回退到 global。IDEA_REPORT 显示 "scope: global / unset (warning)"。

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py maturity wiki/ --json` — 检查 wiki 成熟度 + Growth Report
- `python3 tools/research_wiki.py slug "<title>"` — 生成 slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — 添加 graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — 重建 query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — 重建 gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/fetch_s2.py search "<query>" --limit 20` — Semantic Scholar 搜索
- `python3 tools/fetch_deepxiv.py search "<query>" --mode hybrid --limit 20` — DeepXiv 语义搜索
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — 获取论文 TLDR
- `python3 tools/fetch_deepxiv.py trending --days 14` — trending 趋势

### Skills（via Skill tool）
- `/novelty` — Phase 4 深度 novelty 验证
- `/review` — Phase 4 跨模型审查

### MCP Servers
- `mcp__llm-review__chat` — Phase 2 Review LLM 独立脑暴

### Claude Code Native
- `WebSearch` — Phase 1 外部搜索、Phase 3 快速 novelty 筛
- `Agent` 工具 — Phase 1 并行搜索、Phase 2 并行脑暴

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Phase 2 Review LLM 独立性原则
