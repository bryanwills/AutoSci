---
description: 把一篇论文 ingest 进 wiki —— 建立 papers + concepts + people + claims 页面，并完成所有双向交叉引用与 graph edge。当用户说 "ingest"、"加入这篇论文"、丢 `.pdf` / `.tex` / arXiv URL / DOI / PMID / bioRxiv URL / PMC URL 或要求把论文折叠进知识库时触发。
argument-hint: <local-path-or-arXiv-URL-or-DOI-or-PMID-or-bioRxiv-URL-or-PMC-URL> [--discover]
---

<!-- bio-C1: 镜像自 i18n/zh/skills/ingest/SKILL.md，加入 C1（PubMed/EuropePMC/bioRxiv 路由 + bio NER 预扫描）草稿。
     真值源：i18n/zh/skills/ingest/SKILL.md。本路径不参与运行；要测试请先合回真值源。
     新增工具（`fetch_crossref.py`、`fetch_pubmed.py`、`fetch_europepmc.py`、`fetch_biorxiv.py`、`extract_bio_ner.py`）
     **尚未存在**，仅在 Dependencies 中作为待办列出。这些工具落地之前，bio fallback 链优雅降级到现有 S2 路径。 -->

# /ingest

把一篇论文转化成一组正确链接的 wiki 页面。`/ingest` 的职责是写出 well-shaped 的实体与正确的双向链接；语义层面的审计（反向链接对称性、dangling node、字段取值合规）留给 `/check`。

按需打开下列本地参考文件：

- `references/pdf-preprocessing.md` —— 直接 PDF 输入时的 arXiv-ID 恢复、tex 抓取、prepare-paper 交接流程
- `references/dedup-policy.md` —— concept / claim 的合并与新建决策规则，以及 `/ingest` 形状检查与 `/check` 语义审计的边界
- `references/cross-references.md` —— 正向/反向链接矩阵与 paper-to-paper edge 类型选择
- `references/init-mode.md` —— `/init` 的 manifest 交接与并行安全约束
- `references/error-handling.md` —— 来源解析、API 与 slug 冲突的 fallback

在撰写任何 wiki 页面 frontmatter 或正文章节前，先打开 `docs/runtime-page-templates.zh.md`；需要 `index.md`、`log.md` 或 `graph/` 格式时，打开 `docs/runtime-support-files.zh.md`。

## Inputs

<!-- bio-C1: source 枚举扩到 DOI / PMID / bioRxiv / PMC。 -->
- `source`：以下之一 ——
  - arXiv URL（例如 `https://arxiv.org/abs/2106.09685`）
  - **bio-C1**: DOI（例如 `10.1038/s41586-021-03819-2`）
  - **bio-C1**: PubMed ID（例如 `PMID:34265844` 或纯数字 `34265844`）
  - **bio-C1**: bioRxiv / medRxiv URL（例如 `https://www.biorxiv.org/content/10.1101/2024.03.01.582944v1`）
  - **bio-C1**: PubMed Central URL（例如 `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8316889/`）
  - 本地 `.tex`
  - 本地 `.pdf`
  - 或 `/init` 通过 `.checkpoints/init-sources.json` 交接的 `canonical_ingest_path`（见 `references/init-mode.md`）
- `--discover`（可选，默认 **关闭**）：在最终 report 之后调用 `/discover --anchor <this-paper's-arxiv-id>`，把 shortlist 作为 "接下来可能想 ingest 的相关论文" 附在 report 里。从不自动 ingest 推荐结果。INIT MODE 下自动跳过。视为用户可见参数：不得仅根据仓库状态擅自开启。

## Outputs

- 一篇完整链接的论文页面及其关联实体（concepts、claims、people）
- 通过 `tools/research_wiki.py` 追加的 graph edges 与 citations
- 终端汇总报告（新增页面数、建议后续 ingest 的论文）

## Wiki Interaction

### Reads

- `wiki/index.md`，用于获取所有已存在 slug 与 tag
- `wiki/papers/*.md`，用于识别已 ingest 过的论文
- `wiki/concepts/*.md`、`wiki/foundations/*.md`，用于 dedup 匹配
- `wiki/claims/*.md`，用于 dedup 匹配
- `wiki/people/*.md`，用于识别已有作者
- `wiki/topics/*.md`，用于将论文归入已有 topic
- `wiki/graph/open_questions.md`，用于识别论文是否填补了已知 gap
- <!-- bio-C1 --> `wiki/datasets/*.md`，用于检测数据集提及并把纯文本提升为 wikilink（依赖 A1）

### Writes

- `wiki/papers/{slug}.md` —— CREATE
- `wiki/concepts/{slug}.md` —— CREATE（新建）或 EDIT（追加 `key_papers`、aliases、variants）
- `wiki/claims/{slug}.md` —— CREATE（新建）或 EDIT（追加 `evidence` 条目）
- `wiki/people/{slug}.md` —— CREATE（仅当 importance ≥ 4）或 EDIT（追加 `Key papers`）
- `wiki/topics/{slug}.md` —— 只允许 EDIT，`/ingest` 不得 CREATE 新 topic
- <!-- bio-C1 --> `wiki/datasets/{slug}.md` —— 仅当数据集页面已存在时 EDIT；仅当 NER 高置信度发现一个新数据集且本论文引入它（importance ≥ 4）时 CREATE。否则把数据集页创建留给 `/edit`。依赖 A1。
- `wiki/graph/edges.jsonl` —— 通过工具 APPEND
- `wiki/graph/citations.jsonl` —— 通过工具 APPEND
- `wiki/graph/context_brief.md` —— REBUILD（INIT MODE 下跳过）
- `wiki/graph/open_questions.md` —— REBUILD（INIT MODE 下跳过）
- `wiki/index.md` —— APPEND
- `wiki/log.md` —— 通过工具 APPEND

### 会新增的 Graph edges

- `paper → concept`：`introduces_concept` / `uses_concept` / `extends_concept` / `critiques_concept`，并写 `confidence`
- `paper → foundation`：`derived_from`（foundation 是终端节点，无反向链接）
- `paper → claim`：`supports` / `contradicts`
- `paper → paper`：`same_problem_as` / `similar_method_to` / `complementary_to` / `builds_on` / `compares_against` / `improves_on` / `challenges` / `surveys`，并写 `confidence`
- bibliographic `paper → paper`：`graph/citations.jsonl` 中的 `cites`
- <!-- bio-C1（依赖 B1） --> `paper → concept`（蛋白）bio 关系 edge，仅当 NER + 正文分析给出清晰信号：`targets_protein`、`binds`、`inhibits`、`activates`、`degrades`、`phosphorylates`、`ubiquitinates`、`methylates`、`acetylates`、`is_substrate_of` —— 全部带 `confidence`。保守倾向：仅在原文给出清晰线索时才发出。

`tools/research_wiki.py add-edge` 会拒绝缺少 confidence/evidence 的
paper-paper 与 paper-concept semantic edge，也会拒绝新写入 legacy
paper-to-concept 或 paper-to-paper 类型。

## Workflow

**前置条件**：工作目录下同时存在 `wiki/`、`raw/`、`tools/`。先解析一次 Python interpreter 并复用：

```bash
GIT_COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || true)
PROJECT_ROOT=""
if [ -n "$GIT_COMMON_DIR" ]; then
  PROJECT_ROOT=$(cd "$(dirname "$GIT_COMMON_DIR")" 2>/dev/null && pwd)
fi
if   [ -x "$PROJECT_ROOT/.venv/bin/python" ];         then PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
elif [ -x "$PROJECT_ROOT/.venv/Scripts/python.exe" ]; then PYTHON_BIN="$PROJECT_ROOT/.venv/Scripts/python.exe"
elif [ -x .venv/bin/python ];                         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ];                 then PYTHON_BIN=.venv/Scripts/python.exe
else                                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Step 1: 解析来源

1. 如果 `/init` 交接了 `canonical_ingest_path`，进入 **INIT MODE** 并原样消费该路径，不要重新扫描 `raw/`。详见 `references/init-mode.md`。
2. 如果来源是 arXiv URL，先提取 arXiv ID；可用时通过 `"$PYTHON_BIN" tools/fetch_s2.py paper <arxiv-id>` 恢复标题，然后运行 `"$PYTHON_BIN" tools/init_discovery.py download --raw-root raw --arxiv-id <arxiv-id> --title "<title-or-arxiv-id>"`。后续从返回的 `canonical_ingest_path` 继续。该 helper 会先尝试 arXiv source，再 fallback 到 PDF；不要用 `fetch_arxiv.py` 处理单篇论文，因为它只用于 RSS。
3. <!-- bio-C1 --> **bio 标识符路由。** 如果来源是 DOI、PMID、bioRxiv URL 或 PMC URL，按以下分类与路由处理。每条路由最终在 `raw/discovered/` 下解析出 `canonical_ingest_path`（PDF 或全文 XML），然后进入后续流程。
   - **DOI**（`10.NNNN/...`）：用 CrossRef 拿规范元数据；若 DOI 解析为 bioRxiv/medRxiv preprint，从出版方镜像下载全文 PDF；否则下载出版方 PDF（受许可限制 —— 非公开 DOI 可能降级为仅摘要 ingest，并在 report 中标注）。
   - **PMID**（`PMID:NNNNNNNN` 或纯数字 ≥ 7 位）：用 PubMed E-utilities（`efetch`）拿元数据 + 摘要，再用 EuropePMC（`fullTextXML`）拿开放获取全文。无全文则仅摘要 ingest 并在 report 标注。
   - **bioRxiv / medRxiv URL**：抽 DOI 后缀（`10.1101/...`），用 bioRxiv content API（`/details/biorxiv/<doi>`）拿元数据，再从版本固定 URL 下载 PDF。
   - **PMC URL**（`PMC<id>`）：直接调 EuropePMC `fullTextXML`（PMC ID 可干净映射），fallback 到 PMC OAI-PMH 拿开放获取 XML。
   - 上述四种情况下：`source_type: pdf`（JATS XML 流水线落地后改为 `xml`），在 report 记录所选通道，并把文件持久化到 `raw/discovered/`。
4. 如果来源是本地 `.tex`，直接使用。
5. 如果来源是本地 `.pdf`，先走 `references/pdf-preprocessing.md` 的预处理流程，在 `raw/tmp/` 下生成 prepared `.tex`，再继续。

raw 持久化规则：已经在 `raw/discovered/`、`raw/tmp/`、`raw/papers/` 中的文件，不得被复制或重写到别的 raw 子目录。

### Step 2: 论文身份与 enrichment

1. 生成 paper slug：

   ```bash
   "$PYTHON_BIN" tools/research_wiki.py slug "<paper-title>"
   ```

2. 冲突检查：若 `wiki/papers/{slug}.md` 已存在且 arXiv ID **或 DOI / PMID / bioRxiv DOI** <!-- bio-C1 --> 或标题一致，报告并退出；若不一致，按 `references/error-handling.md` 处理冲突。
3. <!-- bio-C1 --> **元数据 fallback 链。** 按优先级依次尝试，第一个返回可用记录的源胜出。后续调用仅做最佳努力的 enrichment —— 不要重复请求前一源已填充的字段。
   - **存在 bio 锚点**（DOI / PMID / bioRxiv）：`CrossRef → PubMed E-utilities → EuropePMC → bioRxiv API → DeepXiv → Semantic Scholar`
   - **仅有 arXiv 锚点**（CS 路径）：`Semantic Scholar → DeepXiv → CrossRef`（CrossRef 是 arXiv 论文若获期刊 DOI 的 fallback）
   - 链路在 `title`、`venue`/`journal`、`year`、（如适用）`doi`/`pmid` 都填充后立即停止；后续调用仅追加 citation count / `s2_id` / DeepXiv brief。

   ```bash
   # CS 路径（已有，不变）：
   "$PYTHON_BIN" tools/fetch_s2.py paper <arxiv-id>

   # bio-C1 —— bio 路径（新工具，待落地，见 Dependencies）：
   "$PYTHON_BIN" tools/fetch_crossref.py paper <doi>
   "$PYTHON_BIN" tools/fetch_pubmed.py paper <pmid>
   "$PYTHON_BIN" tools/fetch_europepmc.py paper <pmid-or-pmcid>
   "$PYTHON_BIN" tools/fetch_biorxiv.py paper <biorxiv-doi>
   ```

   合并结果用于填写 `venue`、`year`、`doi`、`pmid`、`biorxiv`、`s2_id`、citation count，以及 `importance`（1-5）的评估依据。
4. <!-- bio-C1 --> **bio 标识符抽取。** 当元数据源暴露结构化 bio 注解（CrossRef abstract subjects、PubMed MeSH、EuropePMC annotations API），预填 A3 frontmatter 字段 `pdb_ids`、`uniprot_ids`、`nct_ids`、`gene_symbols`、`species`。这些是**待 Step 4 NER 通道确认或覆盖的建议值** —— 暂不写入页面。
5. 可选 DeepXiv enrichment，失败则静默跳过：

   ```bash
   "$PYTHON_BIN" tools/fetch_deepxiv.py brief <arxiv-id>
   "$PYTHON_BIN" tools/fetch_deepxiv.py head <arxiv-id>
   "$PYTHON_BIN" tools/fetch_deepxiv.py social <arxiv-id>
   ```

   `brief` 用于 seed Key idea；`head` 用于对照 tex 解析的章节结构；`social` 作为 importance 的辅助信号。**bio-C1**：无 arXiv ID 的 bio 论文 DeepXiv brief 不可用；Key idea seed 改用 PubMed E-utilities 或 CrossRef 返回的摘要做 fallback。

### Step 3: 写 paper 页面

打开 `docs/runtime-page-templates.zh.md` 中的 paper 模板。填写全部必需 frontmatter 字段；`cited_by` 本步骤留空，Step 5 再回填。<!-- bio-C1：A3 字段填充时也写入：doi / pmid / biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species。 -->

写入前对即将输出的 frontmatter 做一次**形状检查** —— 仅限以下范围：

- 每个必需字段都存在且非空
- `importance` ∈ {1,2,3,4,5}；claim 的 `status` 在合法集合内；concept 的 `maturity` 在合法集合内；claim 的 `confidence` ∈ [0,1]
- YAML 可解析
- <!-- bio-C1 + bio-C8 --> 当 `doi`、`pmid`、`pdb_ids`、`uniprot_ids` 填充时，格式匹配预期 regex（完整标识符格式 lint 在 `/check` C8；这里只做"看起来合理"的检查）

形状检查刻意保持狭窄：反向链接对称性、dangling node、跨实体一致性是 `/check` 的工作，不是本 skill 的。

正文章节：Problem、Key idea、Method、Results、Limitations、Open questions、My take、Related。

### Step 4: concept / claim / people

按 `references/dedup-policy.md` 执行。简要步骤：

1. <!-- bio-C1 --> **bio NER 预扫描。** 在 per-candidate dedup loop 之前，用 `tools/extract_bio_ner.py`（待建工具，见 Dependencies）对预处理过的正文跑一次 NER 预扫描。默认 NER profile 是 `protein-drug`；C1 的完整设计中 `/ingest` 会按论文选不同 profile（genomics / clinical / microbiome 见 H5）。预扫描输出：候选基因符号、蛋白名、药物名、数据集名、疾病词，以及它们的字符 span 和置信度分。NER 预扫描输出**增强**而非**取代** dedup-policy 决策；每个候选仍走现有 `find-similar-concept` / `find-similar-claim` 流程。
2. 每个 concept / claim 候选都先调用对应的 `find-similar-*` 工具。
3. 默认合并到 top 结果。只有在工具返回无可用候选、且论文 importance 确实证明新建合理时，才新建页面。
4. 每写一条正向链接，同一 turn 内写入其反向链接。义务矩阵见 `references/cross-references.md`。
5. 仅当 importance ≥ 4 才允许新建 `wiki/people/{slug}.md`；否则只允许向已有作者页面追加。
6. <!-- bio-C1 --> **数据集 wikilink 提升。** 当 NER 预扫描发现某数据集名（如 "TernaryDB"、"AlphaFold-DB"）能解析到已存在的 `wiki/datasets/{slug}.md`（依 A1），把正文中纯文本提及替换为 wikilink。新数据集页创建保持保守 —— 仅当本论文引入该数据集且 importance ≥ 4 时；否则在 report 中标注，留给 `/edit`。
7. <!-- bio-C1（依赖 B1） --> **bio 关系 edge 抽取。** 当预处理正文给出明确功能线索（"X 抑制 Y"、"激酶 A 磷酸化底物 B"）时，通过 `tools/research_wiki.py add-edge` 写入一条 B1 bio 关系 edge，`confidence: medium`（仅当线索无歧义且两端蛋白都已是 wiki 实体时才用 `high`）。当关系是隐喻或推测时跳过。

### Step 5: paper-to-paper edge 与 `cited_by`

INIT MODE 下整步跳过 —— 由上层 `/init` 在 fan-in 时统一处理。

```bash
"$PYTHON_BIN" tools/fetch_s2.py references <arxiv-id>
"$PYTHON_BIN" tools/fetch_s2.py citations <arxiv-id>
```

<!-- bio-C1 --> 走 bio 路径 ingest 的论文（无 arXiv ID）references / citations 改用 CrossRef + PubMed E-utilities + EuropePMC。dedup 逻辑相同；JSON shape 由 `tools/fetch_pubmed.py references|citations` 与 `tools/fetch_crossref.py references`（待建）规整。

- 对于 references 中 arXiv ID、**DOI 或 PMID** <!-- bio-C1 --> 能解析到 `wiki/papers/{slug}.md` 的条目，在 `graph/citations.jsonl` 写一条 bibliographic `cites` 记录。
- 只有当原文给出清晰信号时，才在 `graph/edges.jsonl` 写 semantic paper-to-paper edge。选型规则见 `references/cross-references.md`。若没有能干净对应的语义关系，只保留 `cites` 记录。
- 对于 citations 中已在 wiki 的引用者，在本论文的 `cited_by` 追加引用者 slug。
- 在最终报告中列出未匹配的高引用 references，供用户决定是否后续 `/ingest`。

### Step 6: topic 与 index

1. 将论文的 domain 与 tags 对 `wiki/topics/*.md` 做匹配。对每个命中 topic：
   - importance ≥ 4 → 追加到 `## Seminal works`
   - importance < 4 → 按年份追加到 `## SOTA tracker` 或 `## Recent work`
   - 若论文直接回应了 topic 中列出的 open problem，在对应行上标注
2. `/ingest` 不得新建 topic 页面 —— topic 创建属于 `/init` 与 `/edit`。
3. 在 `wiki/index.md` 对应分类下追加新增或编辑过的条目。格式见 `docs/runtime-support-files.zh.md`。<!-- bio-C1（依赖 A1 follow-up） --> A1 的 index.md schema 后续条目落地后，包含 `datasets:` 段。

### Step 7: 日志与 rebuild

```bash
"$PYTHON_BIN" tools/research_wiki.py log wiki/ "ingest | added papers/<slug> | updated: <list>"
```

非 INIT MODE 下再执行：

```bash
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/
```

### Step 8: 汇报

输出一个紧凑 summary：新建的页面、编辑的页面、新增的 graph edge、发现的 contradiction（如有）、尚未 ingest 的高引用 references（后续 `/ingest` 建议）。<!-- bio-C1 --> 同时上浮：fallback 链中胜出的元数据通道（如 `metadata: PubMed E-utilities`）、bio NER 候选合并 vs 新建数量、留作纯文本的数据集提及（延后到 `/edit`）、降级为仅摘要 ingest 的访问受限 DOI。末尾一行：

```
Wiki: +1 paper, +{N} claims, +{M} concepts, +{K} edges
```

### Step 9: 可选的 discovery（仅当 `--discover` 显式开启）

如果用户没有显式传 `--discover`，跳过本步骤。INIT MODE 下也一律跳过 —— 是否在 fan-in 之后跑 discovery，是 `/init` 父流程的决定，不是单个子代理的决定。

开启时，用刚 ingest 论文作为单 anchor 调用 `/discover`：

```bash
"$PYTHON_BIN" tools/discover.py from-anchors \
  --id <arxiv-id-of-this-paper> \
  --wiki-root wiki \
  --limit 10 \
  --output-checkpoint .checkpoints/ \
  --markdown
```

<!-- bio-C1 --> bio 路径论文改用 `--doi <doi>` 或 `--pmid <pmid>` 锚定；`tools/discover.py` 接受任一 anchor key（C2 扩展计划；C2 落地前 fallback 到基于标题的搜索）。

把 markdown 输出附在 report 下一个 "接下来可能想 ingest 的相关论文" 小节里。**不要**自动 ingest 列表里的任何东西 —— 由用户挑选。若 discovery 失败（S2 故障、所有通道返回空），在 report 里一行说明并继续 —— discovery 失败不应让一次成功的 `/ingest` 也算失败。

## Constraints

- `raw/papers/`、`raw/notes/`、`raw/web/` 归用户所有且只读。直接本地 `/ingest` 可在 `raw/tmp/` 下新增 prepared sidecar；直接 arXiv ingest 可把源归档写到 `raw/discovered/`。<!-- bio-C1 --> 走 bio 路径的 ingest（DOI / PMID / bioRxiv / PMC）同样把抓取的产物持久化到 `raw/discovered/`。INIT MODE 下 `raw/` 全部只读。
- `wiki/graph/` 由工具维护。仅通过 `tools/research_wiki.py` 修改。
- slug 始终来自 `tools/research_wiki.py slug`，不得手写。
- 每一条正向链接必须在同一 turn 内写入其反向链接 —— 这是 wiki 的双向链接不变量。唯一例外是指向 `wiki/foundations/` 的链接，foundations 是终端节点。
- 在 INIT MODE 下，不要向已有页面（由 sibling worktree 或 scaffold 创建的）写入反向链接。只通过 `tools/research_wiki.py add-edge` 记录关系；上层 `/init` 在 fan-in 时统一回填反向链接。
- 来源优先级：`.tex` > `.pdf` > vision API fallback。只要有可用 `.tex`，就不从 PDF ingest。<!-- bio-C1 --> 走 bio 路径以 JATS XML（EuropePMC fullTextXML）输入时，把 XML 等价于解析后的 `.tex` 用于正文抽取 —— XML > PDF > vision API。
- ingest 对新实体保守：
  - importance < 4：每篇论文最多 **1** 个新 concept、**1** 个新 claim
  - importance ≥ 4：每篇论文最多 **3** 个新 concept、**2** 个新 claim
  - 超出上限的候选，必须合并到最接近的 `find-similar-*` 结果，或整体跳过交给 `/check` 标记。规则与理由：`references/dedup-policy.md`。
- <!-- bio-C1 --> **bio NER 候选受同一 per-paper cap 限制**：NER 预扫描可能给出几十个 gene/protein 提及，但页面创建仍按上面 importance 分层的 concept/claim 上限。超出的候选作为 "NER suggestions not adopted" 出现在 report，便于 `/edit` 后续提升。
- `/ingest` 只对自己写出的内容做形状检查（必需字段、枚举取值、YAML 可解析），到此为止。反向链接对称性、dangling node、完整语义审计属于 `/check`，不要在本 skill 内重复实现。
- 必须假设有其他 `/ingest` 在并行 worktree 中同时运行 —— 批量 ingest 已在路线图上。所有对共享文件（`graph/edges.jsonl`、`graph/citations.jsonl`、`index.md`、`log.md`）的写入必须经过 `tools/research_wiki.py` 或采用 append-only 语义。详见 `references/init-mode.md`。
- INIT MODE 下跳过 `fetch_s2.py citations`、`fetch_s2.py references`，以及 `rebuild-*` 命令 —— 由上层 `/init` 在 fan-in 后统一运行。

## Error Handling

详见 `references/error-handling.md`。要点：来源解析按 tex → PDF → vision API → 报告用户的顺序 fallback；S2 不可用时 `importance` 默认取 3 并跳过 citation 回填；DeepXiv 不可用时静默跳过 enrichment；slug 冲突追加数字后缀。

<!-- bio-C1 --> bio 路径补充：
- **CrossRef / PubMed / EuropePMC / bioRxiv 故障**：沿 fallback 链降级。bio 锚点输入的最终 fallback 是已有的 S2+RSS 路径；若 S2 也故障，仅以摘要 + 元数据 ingest，并在 report 标注。
- **许可受限 DOI**：当出版方门控 PDF 且 EuropePMC 无全文，仅以摘要 + 元数据 ingest；frontmatter 与从摘要派生的 Key idea 都填上；report 中清晰提示，便于用户在有访问权时手动补 `.pdf`。
- **bio NER 工具不可用**（`tools/extract_bio_ner.py` 未建或模型加载失败）：跳过 Step 4 NER 预扫描；现有 dedup loop 仍照常处理候选。Report 标注 "bio NER pre-pass skipped"。

## Dependencies

### Tools（via Bash）

- `"$PYTHON_BIN" tools/research_wiki.py slug "<title>"`
- `"$PYTHON_BIN" tools/research_wiki.py find-similar-concept wiki/ "<title>" --aliases "<a,b,c>"`
- `"$PYTHON_BIN" tools/research_wiki.py find-similar-claim wiki/ "<title>" --tags "<a,b,c>"`
- `"$PYTHON_BIN" tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>" [--confidence high|medium|low]`
  - paper-paper 与 paper-concept semantic edge **以及 B1 bio 关系 edge** 必须带 `--confidence high|medium|low`。<!-- bio-C1 -->
- `"$PYTHON_BIN" tools/research_wiki.py add-citation wiki/ --from papers/<citing> --to papers/<cited> --source semantic_scholar`
  - <!-- bio-C1 --> `--source` 枚举扩展：`semantic_scholar | parsed_bib | manual | crossref | pubmed | europepmc | biorxiv`
- `"$PYTHON_BIN" tools/research_wiki.py log wiki/ "<message>"`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/`
- `"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"] [--arxiv-id "<recovered-arxiv-id>"]`
- `"$PYTHON_BIN" tools/init_discovery.py download --raw-root raw --arxiv-id <id> --title "<title-or-id>"` —— 单篇论文下载到 `raw/discovered/`，优先 arXiv source，fallback 到 PDF
- `"$PYTHON_BIN" tools/fetch_s2.py paper|citations|references <arxiv-id>`
- `"$PYTHON_BIN" tools/fetch_deepxiv.py brief|head|social <arxiv-id>`
- `"$PYTHON_BIN" tools/discover.py from-anchors --id <arxiv-id> --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown` —— 仅当 `--discover` 开启

<!-- bio-C1 —— 待建新工具（尚不存在；落地前 bio 路径降级到 S2+RSS） -->
**待建 bio fetcher 工具（C1 后续实现工作）**：
- `"$PYTHON_BIN" tools/fetch_crossref.py paper|references <doi>` —— CrossRef 元数据 + reference 列表
- `"$PYTHON_BIN" tools/fetch_pubmed.py paper|references|citations <pmid>` —— PubMed E-utilities（`efetch`/`elink`）
- `"$PYTHON_BIN" tools/fetch_europepmc.py paper|fulltext <pmid-or-pmcid>` —— EuropePMC 元数据、annotations、JATS XML 全文
- `"$PYTHON_BIN" tools/fetch_biorxiv.py paper <biorxiv-doi>` —— bioRxiv content API
- `"$PYTHON_BIN" tools/extract_bio_ner.py --profile protein-drug --input <prepared-body.tex-or-xml>` —— NER 预扫描；默认 `protein-drug` profile；H5 列出其它 profile

### Shared References

- `.claude/skills/shared-references/citation-verification.md`

### Skills

- `/init` —— 通过 INIT MODE 并行调用 `/ingest` 子代理
- `/check` —— 在 `/ingest` 完成后审计 wiki，负责所有 `/ingest` 故意不做的语义检查；<!-- bio-C1 --> C8 bio-lint 校验 `/ingest` 写出的 A3 标识符格式
- `/discover` —— 可选后续，当 `--discover` 开启时运行；产出用户可能想接着 ingest 的相关论文 shortlist；<!-- bio-C1 --> C2 把 `/discover` 扩到查询同一 bio 源

### External APIs

- Semantic Scholar（via `tools/fetch_s2.py`）
- DeepXiv（via `tools/fetch_deepxiv.py`，可选；不可用时自动降级）
- arXiv（源下载）
- <!-- bio-C1 --> CrossRef REST API
- <!-- bio-C1 --> NCBI E-utilities（PubMed、PMC）
- <!-- bio-C1 --> EuropePMC REST API
- <!-- bio-C1 --> bioRxiv content API
