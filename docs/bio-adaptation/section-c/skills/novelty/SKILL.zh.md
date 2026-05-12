---
description: 多源 novelty 验证：WebSearch + Semantic Scholar + PubMed + EuropePMC + wiki + Review LLM cross-verify，输出 novelty 评分与建议
argument-hint: <idea-description-or-slug> [--quick] [--verbose] [--bio-channels {auto|on|off}]
---

<!-- bio-C9: 镜像自 i18n/zh/skills/novelty/SKILL.md，加入 C9（PubMed 并行通道；EuropePMC 补充）草稿。
     真值源：i18n/zh/skills/novelty/SKILL.md。本路径不参与运行；要测试请先合回真值源。
     跨节依赖：
       C1 —— bio fetcher 工具（tools/fetch_pubmed.py、tools/fetch_europepmc.py）已在 runnable 目录存在。
       C2 —— 与 /discover 相同的通道集合规则；两个 skill 应当对同一输入解析出相同的 auto，避免意外。
       A4 —— auto 检测器使用的 domain 受控词。
     `tools/fetch_s2.py`、`tools/fetch_deepxiv.py` 不变；PubMed/EuropePMC 在 Step 2 Source B 旁
     作为并行通道（为清晰起见单列为 Source B-bio）。 -->

# /novelty

> 对一个研究想法或方法进行多源 novelty 验证。搜索 WebSearch、Semantic Scholar、<!-- bio-C9 --> PubMed（bio 通道激活时）、EuropePMC、wiki 内已有工作和 arXiv 最新预印本，然后由 Review LLM 交叉验证，输出 novelty 评分（1-5）、最相似已有工作、差异化要点和下一步建议。
> 可独立使用，也被 /ideate Phase 4 调用。

## Inputs

- `target`：以下之一：
  - idea 的自由文本描述（一段话或几句话）
  - wiki 中 ideas/ 页面的 slug（如 `sparse-lora-for-edge-devices`）
  - 论文标题或 arXiv URL（检查该论文方法的 novelty）
  - <!-- bio-C9 --> DOI / PMID / bioRxiv URL（在其所在的 bio 先验中检查 novelty）
- `--quick`：快速模式，跳过 Review LLM cross-verify（Step 3），仅做搜索
- `--verbose`：输出完整搜索结果，不仅是摘要
- <!-- bio-C9 --> `--bio-channels {auto|on|off}`（可选，默认 `auto`）：强开/强关 PubMed + EuropePMC 通道。`auto` 在以下任一成立时启用：(a) target 是 DOI / PMID / bioRxiv URL；(b) target slug 的 `domain` 命中 A4 的 bio 词表；(c) 自由文本含任一 bio 锚名（gene symbol、药名、MeSH 风格描述符如 "kinase"、"PROTAC"、"phospho-degron"）。auto 规则与 `/discover` 镜像 —— 同输入两 skill 解析一致。

## Outputs

- **Novelty Report**（输出到终端，不写入 wiki）：
  - Novelty Score（1-5）
  - 最相似的已有工作列表（top 3-5）
  - 与每个已有工作的差异化要点
  - Review LLM 交叉验证意见（除非 --quick）
  - 推荐行动：proceed / modify / abandon
  - <!-- bio-C9 --> bio 通道运行时：每来源拆分 —— 多少候选来自 S2 / PubMed / EuropePMC / DeepXiv / WebSearch —— 让用户能判断 prior-art 覆盖到底广不广。
- 该 skill 是**只读查询**，不修改 wiki 任何内容

## Wiki Interaction

### Reads
- `wiki/papers/*.md` — 搜索已有论文中是否有类似方法
- `wiki/concepts/*.md` — 检查概念重叠
- `wiki/ideas/*.md` — 检查是否与已有 idea 重复（特别是 failed ideas 的 failure_reason）
- `wiki/claims/*.md` — 检查 idea 所依赖的 claims 当前状态
- `wiki/graph/context_brief.md` — 获取全局上下文辅助搜索
- <!-- bio-C9 --> `wiki/papers/*.md` frontmatter `domain`、`gene_symbols`、`pdb_ids`、`uniprot_ids`、`doi`、`pmid` —— `auto` 通道检测器与外部候选的 bio 侧 dedup 使用

### Writes
- **无**。Novelty check 是纯查询操作，不修改 wiki。

### Graph edges created
- **无**。

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

### Step 1: 提取方法签名

1. **若 target 是 slug**：读取 `wiki/ideas/{slug}.md`，提取 title、Hypothesis、Approach sketch
2. **若 target 是自由文本**：直接使用
3. **若 target 是 arXiv URL**：下载摘要，提取方法描述
4. <!-- bio-C9 --> **若 target 是 DOI / PMID / bioRxiv URL**：通过 `tools/fetch_crossref.py paper <doi>` 或 `tools/fetch_pubmed.py paper <pmid>` 解析获取 title + abstract + MeSH terms；提取方法描述与 bio 锚实体。
5. 从 target 中提取「方法签名」——方法的核心要素：
   - **What**：做什么（任务/目标）
   - **How**：用什么方法（技术路线）
   - **Why novel**：声称的创新点
6. 生成 3-5 个核心关键词用于后续搜索
7. <!-- bio-C9 --> target 偏 bio 时同时生成 2–4 个 bio 锚词（gene symbol、药名、PDB ID、MeSH 描述符）供 PubMed / EuropePMC 通道使用。这些词逐字喂给 PubMed 的 MeSH-aware 搜索，常常能命中关键词搜索遗漏的 prior art。

### Step 2: 多源搜索

并行执行以下搜索（使用 Agent tool 并发）：

**Source A — Web Search（5+ 查询）：**
1. 直接查询：`"<method-name>" + "<task>"` 精确短语搜索
2. 组件查询：`<component-1> + <component-2> + <domain>` 组件组合搜索
3. Survey 查询：`"survey" OR "review" + <task-area> + 2024 2025`
4. 竞品查询：`<alternative-approach> + <same-task>`
5. 最新查询：`<method-keywords> + arXiv + 2025 2026`

**Source B — Semantic Scholar + DeepXiv：**
```bash
python3 tools/fetch_s2.py search "<method-keywords>" --limit 20
python3 tools/fetch_deepxiv.py search "<method-keywords>" --mode hybrid --limit 20
```
合并两个来源的结果（按 arxiv_id 去重）。DeepXiv 的混合语义搜索能发现 S2 关键词搜索遗漏的语义相似工作。
- 对 top 5 结果获取详情和 TLDR：
```bash
python3 tools/fetch_s2.py paper <s2_id>
python3 tools/fetch_deepxiv.py brief <arxiv_id>
```
使用 DeepXiv brief 的 TLDR 辅助快速判断方法相似度。
**若 DeepXiv 不可用**：仅使用 S2 搜索（回退到原有行为）。

<!-- bio-C9 -->

**Source B-bio — PubMed + EuropePMC**（`--bio-channels` 解析为 `on` 时启用）：

```bash
# PubMed：关键词 + MeSH 扩展。返回最多 50 个 PMID，按相关度排序。
python3 tools/fetch_pubmed.py search "<method-keywords>" --limit 50

# 可选 MeSH-aware 收窄（gene symbol、药名等 bio 锚词）：
python3 tools/fetch_pubmed.py search "<bio-anchor>[MeSH]" --limit 30

# EuropePMC：全文 + 摘要索引，单次调用返回更丰富的 metadata。
python3 tools/fetch_europepmc.py search "<method-keywords>" --limit 50
```

合并 PubMed + EuropePMC 结果，按 DOI > PMID > 标题模糊去重。bio 先验绝大多数在 PubMed（>30M 摘要，S2 仅部分索引）；漏掉这条通道会让 bio prior-art 撞车被低报，让用户在已有的方法上继续。给 bio claim 打分时把 PubMed 命中按全权重计 —— 不要相对 S2 降权。

对该通道的 top 5 候选拉详情/摘要：
```bash
python3 tools/fetch_pubmed.py paper <pmid>            # abstract + MeSH + author list
python3 tools/fetch_europepmc.py annotations <id>     # 实体级 annotations：UniProt、GO、ChEBI URI
```

EuropePMC 的 `annotations` endpoint 让 `/novelty` 廉价地判断 "这个候选是不是在我 idea 同样的 protein / 药 / pathway 上做"——它在摘要旁返回实体 URI。bio target 的相似度信号优先采它，而不是只用 abstract bag-of-words。

**若 PubMed 不可用**：仅用 EuropePMC 继续；在报告中注明 degraded。**若 PubMed 与 EuropePMC 都不可用**：发出硬警告，提示 bio prior-art 覆盖严重退化，建议至少一个通道恢复后再重试。**不要**默默 fall through 到 "S2 only" —— 已知 S2 单独跑 bio prior-art 不全。

**Source C — Wiki 内部搜索：**
1. 扫描 `wiki/papers/` 所有页面的 Key idea 和 Method 段落
2. 扫描 `wiki/concepts/` 的 Definition 和 Variants 段落
3. 扫描 `wiki/ideas/` 的全部内容，特别关注：
   - status = failed 的 ideas 及其 failure_reason（anti-repetition）
   - status = proposed/in_progress 的 ideas（避免内部重复）
4. 读取 `wiki/graph/context_brief.md` 获取全局视角

**Source D — arXiv 近期预印本：**
- 使用 WebSearch 查询 `site:arxiv.org <method-keywords> 2025 2026`
- <!-- bio-C9 --> bio 通道激活时同时跑 `site:biorxiv.org <method-keywords> 2025 2026` 与 `site:medrxiv.org <method-keywords> 2025 2026`，覆盖 bio fetcher 难以全覆盖的 preprint 区。

### Step 3: Review LLM 交叉验证

（若 `--quick` 则跳过此步）

将以下信息提交 Review LLM 进行独立判断：

```
mcp__llm-review__chat:
  system: "You are a senior researcher assessing the novelty of a proposed method.
           Be rigorous: if the method is essentially a recombination of known techniques
           with minor changes, score it low. Only score 4-5 if there is a genuinely new
           insight or formulation.
           When the method is bio-anchored, weight PubMed / EuropePMC hits at full
           strength — those corpora cover bio prior art that arXiv / S2 alone miss."   <!-- bio-C9 -->
  message: |
    ## Proposed Method
    {method signature from Step 1}

    ## Existing Similar Work Found
    {top 5 similar works from Step 2, with title + one-line summary, source-tagged: S2 / DeepXiv / PubMed / EuropePMC / WebSearch}   <!-- bio-C9 -->

    ## Questions
    1. Is this method genuinely novel, or a minor variation of existing work?
    2. What is the closest existing work and what's the real difference?
    3. Novelty score 1-5 with justification.
    4. If score <= 2, what modification could increase novelty?
    5. <!-- bio-C9 --> If the method is bio-anchored: are there clinical-validation or wet-lab-validation precedents that the search missed but should have surfaced? Name them by DOI/PMID.
```

### Step 4: 生成 Novelty Report

综合 Step 2 搜索结果和 Step 3 Review LLM 意见，生成结构化报告：

```markdown
# Novelty Report: {idea title}

## Score: {1-5}/5 — {label}

| Score | Label | 含义 |
|-------|-------|------|
| 1 | Published | 已有高度相似的发表工作 |
| 2 | Very Similar | 存在非常相似的方法，仅细节差异 |
| 3 | Incremental | 在已有工作基础上有明确的增量贡献 |
| 4 | Novel Combination | 创新性地组合已有技术，产生新 insight |
| 5 | Fundamentally New | 提出全新范式或 formulation |

## Search Coverage   <!-- bio-C9 -->
| Source | Hits | 用于 top-5 |
|--------|------|------------|
| Semantic Scholar | {N} | {n} |
| DeepXiv | {N} | {n} |
| PubMed | {N} | {n} |
| EuropePMC | {N} | {n} |
| WebSearch | {N} | {n} |
| Wiki internal | {N} | {n} |

## Closest Prior Work

1. **{title}** ({year}) — {一句话描述相似之处}
   - Source: {S2 | DeepXiv | PubMed | EuropePMC | WebSearch}    <!-- bio-C9 -->
   - Identifier: {arxiv | doi | pmid | biorxiv}                  <!-- bio-C9 -->
   - 差异：{本方法与之的关键区别}
   - Wiki 链接：[[slug]]（若存在）
2. ...

## Review LLM Assessment
{Review LLM 的独立判断摘要}

## Anti-repetition Check
- Wiki 中已有 failed ideas：{列出相关 failed ideas 及 failure_reason}
- Wiki 中已有 in_progress ideas：{列出可能重叠的 ideas}

## Recommendation
- **{proceed / modify / abandon}**
- 理由：{一段话}
- 若 modify：建议的差异化方向：{具体建议}
```

**评分规则（综合判断）：**
- Claude 搜索结果 和 Review LLM 意见取较低分（保守原则）
- 若 wiki 中存在 failed idea 且 failure_reason 与本 idea 相关 → 降 1 分
- 若 wiki 中存在 in_progress idea 高度重叠 → 标记为 abandon（内部重复）
- <!-- bio-C9 --> bio 通道激活且 PubMed 命中 ≥1 篇方法重合、protein target 相同、≤5 年的工作时，无论 S2 结果如何视为 1（Published）—— 对 bio claim，bio prior-art 凌驾偏 CS 的 S2 corpus。

## Constraints

- **不修改 wiki**：novelty check 是纯查询操作，所有结果仅输出到终端
- **保守评分**：宁可低估 novelty 也不高估，避免在已有工作上浪费精力
- **必须检查 failed ideas**：wiki/ideas/ 中 status=failed 的 ideas 是重要的 anti-repetition 信号
- **搜索覆盖面**：至少 5 个不同的 WebSearch 查询 + Semantic Scholar + wiki 内部搜索；<!-- bio-C9 --> bio 通道激活时再加至少 2 次 PubMed 查询（一次关键词、一次 MeSH 收窄）+ 1 次 EuropePMC 查询
- **Review LLM 独立性**：提交给 Review LLM 时不包含 Claude 自己的 novelty 判断，让 Review LLM 独立评估
- **引用真实来源**：报告中列出的所有 prior work 必须是真实存在的（WebSearch/S2/<!-- bio-C9 --> PubMed/EuropePMC 返回的），不得编造
- <!-- bio-C9 --> **bio 通道不替代 wiki 内部搜索**：PubMed 覆盖虽广，但不包含 wiki 的 claim/idea 图。即便 bio 通道返回大量候选也要跑 wiki 内部搜索。

## Error Handling

- **WebSearch 不可用**：跳过 Source A 和 D，仅依赖 S2 + wiki 搜索，在报告中注明覆盖面不足
- **Semantic Scholar API 不可用**：跳过 S2 部分，依赖 DeepXiv + WebSearch 补偿
- **DeepXiv API 不可用**：跳过 DeepXiv 部分，依赖 S2 + WebSearch（回退到原有行为）
- <!-- bio-C9 --> **PubMed 不可用**：跳过 PubMed 子通道；仅用 EuropePMC 继续。注明 bio prior-art 覆盖部分。
- <!-- bio-C9 --> **PubMed 与 EuropePMC 都不可用**（auto 或 `on`）：报告顶部硬警告 —— "Bio prior-art coverage is severely degraded; consider retrying when at least one bio channel is reachable" —— 在用户允许下才用 S2-only 继续。不要在 bio target 上未经 bio 通道确认就静默给出自信的 novelty 分。
- **Review LLM 不可用**：跳过 Step 3，报告标注「Review LLM cross-verify unavailable, single-model assessment only」
- **Wiki 为空**：正常执行外部搜索，wiki 内部搜索部分标注「wiki empty」
- **idea slug 不存在**：提示用户检查 slug，列出 wiki/ideas/ 中的可用 slugs
- <!-- bio-C9 --> **DOI / PMID 全通道未命中**：target 无法解析；明确报错而非凭空猜测。

## Dependencies

### Tools（via Bash）
- `python3 tools/fetch_s2.py search "<query>" --limit 20` — Semantic Scholar 关键词搜索
- `python3 tools/fetch_s2.py paper <s2_id>` — 获取论文详情
- `python3 tools/fetch_deepxiv.py search "<query>" --mode hybrid --limit 20` — DeepXiv 语义搜索
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — 获取论文 TLDR 辅助相似度判断
- <!-- bio-C9 --> `python3 tools/fetch_pubmed.py search "<query>" --limit <N>` — PubMed E-utilities 搜索；支持 MeSH 标签查询
- <!-- bio-C9 --> `python3 tools/fetch_pubmed.py paper <pmid>` — 获取 abstract + MeSH terms + author list
- <!-- bio-C9 --> `python3 tools/fetch_europepmc.py search "<query>" --limit <N>` — EuropePMC 搜索
- <!-- bio-C9 --> `python3 tools/fetch_europepmc.py annotations <pmid-or-doi>` — 实体级 annotations（UniProt / GO / ChEBI URI）
- <!-- bio-C9 --> `python3 tools/fetch_crossref.py paper <doi>` — bio target 自由文本时把 DOI 解析到 title + abstract

### MCP Servers
- `mcp__llm-review__chat` — Review LLM 交叉验证（Step 3）

### Claude Code Native
- `WebSearch` — 多查询 web 搜索（Step 2 Source A + D）
- `Agent` tool — 并行执行多源搜索（Step 2）

### Shared References
- `.claude/skills/shared-references/cross-model-review.md`（Phase 2 创建，Review LLM 独立性原则）
