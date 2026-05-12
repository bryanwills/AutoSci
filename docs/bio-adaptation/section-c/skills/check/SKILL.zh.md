---
description: 扫描全 wiki 发现健康问题，生成修复建议报告（覆盖全 10 种 entity + graph 一致性，可选 bio-lint pass）
---

<!-- bio-C8: 镜像自 i18n/zh/skills/check/SKILL.md，加入 C8 bio-lint pass 草稿。
     真值源：i18n/zh/skills/check/SKILL.md。本路径不参与运行；要测试请先合回真值源。
     新增工具引用（`tools/lint_bio.py`）**尚未存在**，仅在 Dependencies 列为待办。该工具落地之前
     bio pass 静默跳过（既有 `tools/lint.py` 照常运行）。跨节依赖：
       A1（datasets/）—— 版本漂移检查的锚点是 datasets/{slug}.versions[]
       A3（papers/ bio identifiers）—— DOI/PMID/PDB/UniProt 格式校验
       A5（experiments setup bio fields）—— MD 实验的 force-field 校验、物种不一致校验
       A8（reproducibility.dataset_versions）—— 版本漂移检查的同源依赖
       B3（dataset_version_used edge）—— 与 datasets/{slug}.versions[] 的对照完整性
       C4（statistical_protocol enum）—— 字段值完整性
       C6（statistical_protocol selector）—— 同字段，作为非确定性建议时降级
     -->

# /check

> 扫描全 wiki，发现结构、链接、字段、graph 的健康问题，生成分级修复建议。
> 覆盖所有 10 种 entity 类型 <!-- bio-C8（依赖 A1）-->，包括 claims confidence 合理性、idea 失败原因完整性、experiment-claim 链接有效性、graph edges 一致性，以及 —— 当 bio 字段存在时 —— 一个 bio-lint pass 检查 identifier 格式、dataset 版本漂移、MD 实验的 force-field provenance、物种 / 范围一致性。

## Inputs

- 全 wiki 目录（默认 `wiki/`）
- 可选：`--json` 标志（通过 tools/lint.py 输出 JSON 格式）
- 可选：`--fix` 标志（自动修复确定性问题）
- 可选：`--fix --dry-run`（预览修复但不执行）
- 可选：`--suggest` 标志（显示非自动修复问题的建议）
- <!-- bio-C8 --> 可选：`--bio` 标志（即便未检测到 bio 字段也强制运行 bio-lint pass）；默认行为：当 `papers/*.md doi|pmid|pdb_ids|uniprot_ids`、`experiments/*.md setup.in_silico_or_wet|setup.assay_type|setup.force_field` 或 `datasets/*.md` 任一非空时自动启用。
- <!-- bio-C8 --> 可选：`--no-bio` 标志（即便检测到 bio 字段也强制跳过 bio-lint pass）；用于 CS 改动的迭代场景。

## Outputs

- Lint report（直接报告给用户）
- 可选写入文件：`wiki/outputs/lint-report-{date}.md`

## Wiki Interaction

### Reads
- `wiki/papers/*.md` — 论文页面字段和链接
- `wiki/concepts/*.md` — 概念页面字段和链接
- `wiki/topics/*.md` — 方向页面字段和链接
- `wiki/people/*.md` — 人物页面字段和链接
- `wiki/ideas/*.md` — idea 状态、failure_reason、origin_gaps
- `wiki/experiments/*.md` — experiment 状态、target_claim、outcome
- `wiki/claims/*.md` — claim confidence、status、evidence、source_papers
- `wiki/Summary/*.md` — 综述页面字段
- <!-- bio-C8（依赖 A1）--> `wiki/datasets/*.md` — dataset 页面字段、`versions[]`、`access`、`key_papers`
- `wiki/graph/edges.jsonl` — semantic graph edge 一致性检查
- `wiki/graph/citations.jsonl` — bibliographic citation 一致性检查
- `wiki/index.md` — 对照页面完整性

### Writes
- 不直接修改 wiki 内容（只报告不修复）
- `wiki/log.md` — 通过 `tools/research_wiki.py log` 记录 lint 结果摘要

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。
设 `WIKI_ROOT=wiki/`。

### Step 1: 运行自动化 lint 工具

**默认模式（只报告）**：
```bash
python3 tools/lint.py --wiki-dir wiki/ --json
```

**自动修复模式**（用户指定 `--fix` 时）：
```bash
python3 tools/lint.py --wiki-dir wiki/ --fix --json
```
自动修复确定性问题（xref 反向链接补全、缺失字段填默认值），输出修复报告。

**预览模式**（用户指定 `--fix --dry-run` 时）：
```bash
python3 tools/lint.py --wiki-dir wiki/ --fix --dry-run --json
```
预览会修复什么，不实际执行。

解析 JSON 输出，获取所有自动检测到的 issues（及修复结果）。

### Step 2: 结构完整性（自动化覆盖）

自动化工具检查以下项目：

1. **Broken wikilinks**：`[[slug]]` 目标文件不存在
2. **Orphan pages**：无任何入链的页面
3. **必填字段缺失**（全 10 种 entity）<!-- bio-C8 -->：
   - papers: title, slug, tags, importance
   - concepts: title, tags, maturity, key_papers
   - topics: title, tags
   - people: name, tags
   - Summary: title, scope, key_topics
   - ideas: title, slug, status, origin, tags, priority
   - experiments: title, slug, status, target_claim, hypothesis, tags
   - claims: title, slug, status, confidence, tags, source_papers, evidence
   - <!-- bio-C8（依赖 A1）--> datasets: title, slug, tags, maturity, access, versions, date_updated

### Step 3: 字段值验证（自动化覆盖）

1. **Enum 值检查**：
   - papers.importance ∈ {1,2,3,4,5}
   - concepts.maturity ∈ {stable, active, emerging, deprecated}
   - ideas.status ∈ {proposed, in_progress, tested, validated, failed}
   - ideas.priority ∈ {1,2,3,4,5}
   - experiments.status ∈ {planned, running, completed, abandoned}
   - experiments.outcome ∈ {succeeded, failed, inconclusive}
   - <!-- bio-C8（依赖 C4）--> experiments.type ∈ {baseline, validation, ablation, robustness, negative_control, mechanism, dose_response, cross_context}
   - <!-- bio-C8（依赖 C6）--> experiments.statistical_protocol ∈ {seeds_only, bootstrap_ci, stratified_kfold, replicate_matrix_BxT}
   - claims.status ∈ {proposed, weakly_supported, supported, challenged, deprecated}
   - <!-- bio-C8（依赖 A7）--> claims.evidence[*].type ∈ 基础集合 ∪ bio 扩展集合；存在时 claims.evidence[*].grade ∈ {very-low, low, moderate, high}
   - <!-- bio-C8（依赖 A1）--> datasets.maturity ∈ {stable, active, emerging, deprecated}；datasets.access ∈ {public, registration, restricted, wet-lab-derived}
2. **Claim confidence** ∈ [0.0, 1.0]
3. **Idea failure_reason**：status=failed 时必须非空（anti-repetition memory）
4. **Experiment target_claim**：引用的 claim 必须存在

### Step 4: Cross Reference 对称性（自动化覆盖）

检查所有 CLAUDE.md 中定义的双向链接规则：

| 正向链接 | 检查的反向链接 |
|----------|---------------|
| concepts.key_papers → papers | papers.Related 含 concept 链接 |
| papers → people (wikilink) | people.Key papers 含 paper |
| claims.source_papers → papers | papers.Related 含 claim 链接 |
| ideas.origin_gaps → claims | claims.Linked ideas 含 idea |
| experiments.target_claim → claims | claims.evidence 含 experiment |
| <!-- bio-C8（依赖 A1）--> papers → datasets（正文 wikilink 或 frontmatter `[[ternarydb]]` 类） | datasets.key_papers 含 paper |
| <!-- bio-C8（依赖 A1）--> experiments.setup.dataset → datasets | datasets `## Used by experiments` 含 experiment |

### Step 5: Graph Edge 一致性（自动化覆盖）

1. **JSON 格式有效性**：每行都是合法 JSON
2. **必填字段**：每条 edge 有 from, to, type
3. **Edge type 合法性**：semantic edges 使用当前 endpoint-aware type set；旧 paper-paper / paper-concept 类型给出迁移 warning
4. **Edge confidence**：`/ingest` 写出的 paper-paper 与 paper-concept semantic edges 使用 `confidence: high|medium|low`
5. <!-- bio-C8（依赖 B1/B2/B3）--> **bio edge metadata 完整性**：B1 bio-relation edge 必须带 `confidence`；B2（`clinical_trial_for {nct_id, phase}`、`fda_approved_for {indication, year}`、`validates_in_species {species}`）与 B3（`dataset_version_used {slug, version}`）必须带 `tools/_schemas.py::EDGE_METADATA_REQUIRED` 中声明的 typed `metadata` 键。缺失必填键 → 🔴。
6. **Citation layer**：`graph/citations.jsonl` 使用 `type: cites`、合法 source/date、paper endpoints，且不写 confidence 字段
7. **Dangling nodes**：from/to 引用的 wiki 页面必须存在

### Step 6: 内容质量（LLM 辅助）

自动化工具可检测的：
1. importance=5 的论文无 concept 页引用
2. maturity=stable 的 concept 只有 1 篇 key_paper
3. topics 的 Open problems 为空

LLM 额外判断（需要阅读内容）：
1. **Concept 近似重复检测**：扫描所有 concept 页面的 title + aliases，判断是否有语义相同/高度相似的概念对（如 "attention mechanism" 和 "self-attention"）。对疑似重复对输出合并建议。
2. 矛盾表述检测（不同页面对同一事实的描述不一致）
3. SOTA 记录超过 6 个月未更新
4. people 的 Recent work 超过 6 个月未更新
5. claim confidence 与 evidence 数量/强度不匹配
6. 高 priority idea 长期停留在 proposed 状态

<!-- bio-C8 -->

### Step 6b: Bio-Lint pass（自动检测，或通过 --bio / --no-bio 强制）

未传 `--bio` 且 `papers/*.md`、`experiments/*.md`、`datasets/*.md` 都不带任何 bio 字段时跳过；或传了 `--no-bio`。否则：

```bash
python3 tools/lint_bio.py --wiki-dir wiki/ --json
```

bio-lint 工具发出与 `tools/lint.py` 相同形状的 JSON（每行一个 issue：`severity ∈ {🔴, 🟡, 🔵}`、`file`、`field`、`message`、`fix-rule`），让 Step 7 的报告生成器无须改动即可消费。分类如下：

1. **identifier 格式校验**（确定性，硬违例 🔴，貌似但非规范 🟡）：
   - **DOI**（`papers.doi`、citations 行）：正则 `^10\.\d{4,9}/[-._;()/:A-Z0-9]+$`（不分大小写）。空或畸形拒绝。
   - **PMID**（`papers.pmid`）：纯数字 1–9 位。拒绝补 0 与字段值中带 `PMID:` 前缀（前缀仅是 UI 修饰）。
   - **bioRxiv DOI**（`papers.biorxiv`）：正则 `^10\.1101/\d{4}\.\d{2}\.\d{2}\.\d{6}$`。medRxiv 共享前缀 `10.1101/`，但日期范围从 2019 中开始；2013 之前的 bioRxiv DOI 给 warn（不报错）。
   - **PDB ID**（`papers.pdb_ids[*]`、`experiments.setup.pdb_versions`）：4 字符短形 `^[0-9][A-Za-z0-9]{3}$` 或 8 字符扩展 `^pdb_[0-9a-z]{8}$`。
   - **UniProt accession**（`papers.uniprot_ids[*]`、`concepts.uniprot_id`）：正则 `^[OPQ][0-9][A-Z0-9]{3}[0-9]$` 或 `^[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}$`。
   - **NCT ID**（`papers.nct_ids[*]`、`clinical_trial_for.metadata.nct_id`）：正则 `^NCT[0-9]{8}$`。
   - **Cellosaurus ID**（`experiments.setup.cell_line`）：正则 `^CVCL_[A-Z0-9]{4}$`。纯文本 cell line 名给 🟡 "建议升级到 CVCL"，非错误。
   - **HGNC gene symbol**（`papers.gene_symbols[*]`、`concepts.gene_symbol`）：正则 `^[A-Z][A-Z0-9]{0,9}(-[A-Z0-9]{1,4})?$`。保守放过 `HLA-DRB1`、`BRCA2` 等，但拒小写或带空白。

2. **dataset 版本漂移**（确定性，缺边 🔴，版本过期 🟡）：
   - 对每个 `setup.dataset` 解析为 `[[datasets/{slug}]]` 链接的 `experiments/*.md`，校验 `graph/edges.jsonl` 中存在出边 `dataset_version_used`（B3 依赖）。
   - 对每条已有 `dataset_version_used` 边，校验 `metadata.version` 在目标 `datasets/{slug}.versions[*].version` 列表中。不在 → 🟡 "stale or unknown version pinned"。
   - 当 `experiments.reproducibility.dataset_versions[*].version` 设值时与同一 `versions[]` 列表交叉校验。不在列表 → 🟡。

3. **MD 实验的 force-field provenance**（确定性，🔴）：
   - 当 `experiments.setup.assay_type == 'MD'`（不分大小写）时，要求 `setup.force_field` 非空。`setup.solvent_model` 与 `setup.simulation_length` 同规则。
   - 当 `setup.force_field` 非空但 `setup.assay_type` 为空或非 MD 时，发 🔵 提醒："force_field set on a non-MD experiment — confirm assay_type"。

4. **物种-范围一致性**（LLM 辅助，🟡）：
   - 对每个 `setup.species` 非空的 `experiments/*.md`，沿 `target_claim` 找父 claim，判断 claim 文本或 `evidence[*].grade` 是否暗示不同的转化范围。
   - 启发式：claim 提到 "human"、"patient"、"clinical"、"therapeutic" 但实验 `setup.species` 是 `mouse`/`rat`/`zebrafish` → 发 🟡 "species-claim scope mismatch — explicit cross-context block (C4) recommended"。
   - 此项故意是 LLM 辅助提示而非硬错误，因为跨物种证据常常正是人类 claim 的*正确*基底 —— 目标是揭示未声明的范围漂移。

5. **statistical_protocol 完整性**（确定性，🟡）：
   - 对 C6 落地之后写的 `experiments/*.md`（启发式：`date_planned >= 2026-05-04`），`statistical_protocol` 必填四值之一。空 → 🟡 "statistical_protocol unset; default selector documented in /exp-design Step 3"。
   - 对 C6 之前的实验（`date_planned < 2026-05-04`），`statistical_protocol` 为空视为 🔵 迁移提示；`--fix` 的确定性填充仅在 `seeds >= 3` 且无 bio domain 标记时填 `seeds_only`，其余留空、由用户选择。

6. **domain 词汇一致性**（确定性，🔵）：
   - 出现旧 CS 词汇 `domain` 字符串（`Computational Drug Design / Chemical Biology`、`Cancer biology / Molecular oncology`、`Structural Bioinformatics`…）时，建议最接近的 A4 受控词。仅给建议 —— `/check` 不自动重写自由文本 domain 值。

### Step 7: 生成报告

按优先级排序输出：

```
## Lint Report — YYYY-MM-DD

**Summary**: N 🔴, M 🟡, K 🔵
{bio-lint 跑了：} **Bio-lint**: N_bio 🔴, M_bio 🟡, K_bio 🔵 (在上方总数中)   <!-- bio-C8 -->

### 🔴 需立即修复
1. [file] — {issue description}

### 🟡 建议修复
1. [file] — {issue description}

### 🔵 可选优化
1. [file] — {issue description}
```

分类标准：
- **🔴 需立即修复**：broken links、missing required fields、invalid enum values、failed idea without failure_reason、invalid JSON in edges、confidence out of range、<!-- bio-C8 --> identifier 格式硬违例、缺失 B2/B3 边的必填 metadata、缺失 `dataset_version_used` 边、MD 实验缺 force_field
- **🟡 建议修复**：xref asymmetry、dangling graph edges、broken claim references、unknown edge types、<!-- bio-C8 --> dataset 版本过期、物种-claim 范围不一致、C6 之后写的实验缺 `statistical_protocol`
- **🔵 可选优化**：orphan pages、quality suggestions、empty sections、<!-- bio-C8 --> CS 词汇 `domain` 值、纯文本 cell line 名缺 CVCL ID

记录日志：
```bash
python3 tools/research_wiki.py log wiki/ "check | report: N 🔴, M 🟡, K 🔵 | bio-lint: {ran|skipped}"
```
<!-- bio-C8：log 行末尾记录 bio pass 是否运行 -->

## Constraints

- **默认只报告**：不带 `--fix` 时只报告不修复
- **`--fix` 仅修复确定性问题**：xref 反向链接补全、缺失字段填安全默认值。不确定的问题输出建议（`--suggest`），由用户手动批准
- **raw/ 只读**：不修改 `raw/` 下的文件
- **graph/ 只读**：lint 不修改 graph 文件，仅检查一致性
- **LLM 判断标注来源**：自动化检查和 LLM 判断在报告中明确区分
- **幂等**：多次运行产生相同结果（除非 wiki 内容变化）
- <!-- bio-C8 --> **bio-lint 自动检测**：bio pass 仅在存在 bio 字段或传 `--bio` 时运行；从不改变非 bio 行为。`tools/lint.py`（跨节结构）与 `tools/lint_bio.py`（bio 专属）边界严格 —— 不共享状态、发同形 JSON。
- <!-- bio-C8 --> **identifier 格式不自动修**：即便带 `--fix`，bio-lint 也绝不重写畸形的 DOI/PMID/PDB/UniProt —— 这些是用户提供的 ground truth，"修复" 会静默腐蚀 provenance。

## Error Handling

- **wiki/ 不存在**：报错并建议运行 `/init`
- **graph 文件不存在**：跳过缺失 graph 文件的检查，在报告中注明
- **部分目录缺失**：跳过缺失目录的检查，在报告中列出缺失目录
- <!-- bio-C8 --> **`tools/lint_bio.py` 不存在**（当前状态，直至 Batch C-2 后续工具落地）：在报告中注明 "bio-lint pass skipped — tools/lint_bio.py not installed"，`/check` 其余照常运行。
- <!-- bio-C8 --> **`datasets/` 目录为空但 papers/experiments 中存在 bio 字段**：发 🟡 "datasets/ schema is live but no entries authored — TernaryDB pilot recommended; see CHANGELOG entry 2026-05-04 for the wiring procedure"。

## Dependencies

### Tools（via Bash）
- `python3 tools/lint.py --wiki-dir wiki/ [--json] [--fix] [--dry-run] [--suggest]` — 自动化结构检查 + 修复（核心依赖）
- <!-- bio-C8 --> `python3 tools/lint_bio.py --wiki-dir wiki/ [--json]` — bio-lint pass（计划中后续工具，尚未实现）
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/research_wiki.py stats wiki/` — 获取统计信息（可选，用于报告）

<!-- bio-C8：计划中后续工具设计

`tools/lint_bio.py` 应：
- 复用 `tools/_env.py` 解析仓库根
- 遍历 `wiki/papers/`、`wiki/experiments/`、`wiki/datasets/`、`wiki/concepts/`、`wiki/claims/`，按以下形状每 issue 一行 JSON：
    {"severity": "🔴|🟡|🔵",
     "file": "wiki/...",
     "field": "frontmatter.<dotted-path>" 或 "body",
     "message": "<one-line>",
     "fix-rule": "deterministic|suggestion|none"}
- 实现 Step 6b 列出的六类检查
- 接受 `--wiki-dir` 与 `--json`（与 tools/lint.py CLI 对齐）
- 退出码与 `tools/lint.py` 一致：**有任一 🔴 issue 时退出 1，否则退出 0**。`/check` 消费 JSON 输出而非退出码，因此非零退出不阻塞其余检查 —— 这条是给直接 shell 调用 linter 的 CI pipeline 用的，让它能在硬违例上 fail。
- 校验 B2/B3 metadata 时引用 `tools/_schemas.py::EDGE_METADATA_REQUIRED`
- 加法式：`tools/lint.py` 不调 `lint_bio.py`；`/check` 编排两者
-->
