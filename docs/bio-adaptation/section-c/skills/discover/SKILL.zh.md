---
description: 基于 anchor 论文、topic 关键词或当前 wiki 状态，产出一份排好序的候选论文 shortlist，供用户或上游 skill 决定是否进一步 `/ingest`。当用户问 "接下来该读什么"、"找和这篇相似的论文"、"推荐相关工作"、"这个方向周围有什么" 时触发；`/ingest --discover` 也会内部调用本 skill。本身不 ingest，只提出候选。
argument-hint: "(--anchor <id> [--anchor <id>] [--negative <id>] | --doi <doi> | --pmid <pmid> | --topic <str> | --from-wiki) [--limit N] [--bio-channels {auto|on|off}]"
---

<!-- bio-C2: 镜像自 i18n/zh/skills/discover/SKILL.md，加入 C2（PubMed + EuropePMC + bioRxiv 并行通道，DOI/PMID anchor key）草稿。
     真值源：i18n/zh/skills/discover/SKILL.md。本路径不参与运行；要测试请先合回真值源。
     跨节依赖：
       C1 —— bio fetcher 工具（tools/fetch_pubmed.py、fetch_crossref.py、fetch_europepmc.py、fetch_biorxiv.py）已在 runnable 目录存在；
            本镜像把它们接入 discovery 通道集合。
       A3 —— papers/{slug}.md frontmatter 必须接受 doi/pmid/biorxiv 用于 wiki 侧 dedup。
     `tools/discover.py` 本身需小改：新增 `from-bio-anchor` 子命令与 bio-channel 编排器。
     工具落地之前，bio 路径降级为 S2 标题搜索。 -->

# /discover

> 从三种 seed 模式之一产出一份排好序的候选论文 shortlist，附带每条候选的 rationale，呈现给用户或调用方 skill。`/discover` 绝不自动 ingest —— 它只负责提出候选，实际动作由 `/ingest` 负责。
> <!-- bio-C2 --> 当 seed 输入是 bio canonical（DOI / PMID / bioRxiv DOI）或 wiki 状态显示 bio domain 时，与既有 S2 + DeepXiv 通道并行查询 PubMed + EuropePMC + bioRxiv。bio 研究者在 discovery 阶段需要 recall 而非 precision。

按需打开下列本地参考文件：

- `references/seed-modes.md` —— 如何把用户的措辞映射到 anchor / topic / wiki 模式，以及三者的选择规则
- `references/ranking-signals.md` —— `tools/discover.py` 的打分依据，以及为什么 discovery 不共享 `/init` 的 survey 偏好
- `references/wiki-dedup.md` —— 候选如何被过滤掉已 ingest 的论文，以及 dedup 边界
- <!-- bio-C2 --> `references/bio-channels.md`（计划中）—— 通道特异：PubMed MeSH 扩展、EuropePMC 全文 annotations、bioRxiv 时延、dedup 优先级 DOI > PMID > arXiv > bioRxiv-DOI > 标题模糊

## Inputs

- `--anchor <id>`（可重复）：一或多个 anchor 论文 ID（优先 arXiv ID，也接受 S2 paperId）。驱动 **anchor 模式** —— 主要使用场景，包括 `/ingest` 后的 "接下来该读什么"。
- <!-- bio-C2 --> `--doi <doi>`（可重复）：DOI 作为 anchor。驱动 **bio-anchor 模式** —— 经 CrossRef + PubMed 解析到 paper，再与 S2 通道并行跑 bio 通道集合。多个 `--doi` 与 `--anchor` 的多 arXiv 并集逻辑相同。
- <!-- bio-C2 --> `--pmid <pmid>`（可重复）：PubMed ID 作为 anchor。路由同 `--doi`；即便 CrossRef 无记录也能到达 PubMed/EuropePMC。
- `--negative <id>`（可重复，可选）：希望推开的论文 ID。只在配合 `--anchor` / `--doi` / `--pmid` 时有意义。
- `--topic "<str>"`：topic / query 字符串。驱动 **topic 模式** —— 相对 `/init` planner 更轻量的替代。
- `--from-wiki`：自动从 wiki 最近修改过的论文页派生 seed。驱动 **wiki 模式**。
- `--limit N`（可选，默认 10）：shortlist 最大长度。
- <!-- bio-C2 --> `--bio-channels {auto|on|off}`（可选，默认 `auto`）：强开/强关 bio 通道集合。`auto` 在以下任一条件成立时启用：(a) 任一 anchor 是 `--doi` / `--pmid` / bioRxiv URL；(b) `--from-wiki` 时最近修改的论文带 bio 标识符；(c) `--topic` 含任一 bio 锚名（gene symbol、药名、MeSH 风格描述符）。`off` 即便检测到 bio 锚也跳过 bio 通道 —— 慎用，会显著伤 recall。

`--anchor` / `--doi` / `--pmid` / `--topic` / `--from-wiki` 必须恰好选其一（`--anchor`、`--doi`、`--pmid` 之间可组合）。

## Outputs

- `.checkpoints/discover-{seed-slug}-{YYYY-MM-DD}.json` —— 完整 shortlist payload，机器可读；seed slug 基于首个 anchor 或 topic 派生
- 给用户的 markdown 摘要，包含每条候选的 rationale
- `wiki/log.md` —— 通过 `tools/research_wiki.py log` 追加一行

`/discover` 除了 `log.md` 外不向 `wiki/` 写入任何内容，也不触碰 `raw/`。是否把候选拉进 wiki 是调用方的决定（之后的 `/ingest`）。

## Wiki Interaction

### Reads

- `wiki/papers/*.md` —— frontmatter 中的 `arxiv`（或旧版 `arxiv_id`），用于与已 ingest 的论文做 dedup
- <!-- bio-C2（依赖 A3）--> `wiki/papers/*.md` frontmatter `doi`、`pmid`、`biorxiv` —— bio 侧 dedup；优先级 `doi > pmid > arxiv > biorxiv > 标题模糊`
- `wiki/papers/*.md` 修改时间 —— 用于 `--from-wiki` 模式下 anchor 选取
- <!-- bio-C2 --> `wiki/papers/*.md` `gene_symbols`、`pdb_ids`、`uniprot_ids`、`nct_ids`、`domain` —— `auto` 通道检测器使用

### Writes

- `wiki/log.md` —— 通过 `tools/research_wiki.py log` APPEND

### Graph edges created

- 无。图变更属于 `/ingest`，不属于 `/discover`。

## Workflow

**前置条件**：工作目录包含 `wiki/`、`raw/`、`tools/`。一次解析 Python 解释器路径并复用：

```bash
if [ -x .venv/bin/python ]; then
  PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PYTHON_BIN=.venv/Scripts/python.exe
else
  PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Step 1: 选定 seed 模式

把用户请求映射到 `from-anchors`、`from-bio-anchor`、`from-topic` 或 `from-wiki` 之一。决策规则见 `references/seed-modes.md`，简版：

- 用户指明了一或多篇具体 arXiv 论文，或这是 `/ingest --discover` 在 arXiv anchor 上的后续 → **anchors**
- <!-- bio-C2 --> 用户传 `--doi` / `--pmid`，或 post-`/ingest` 的论文 canonical id 是 DOI / PMID / bioRxiv DOI → **bio-anchor**
- 用户给的是 topic / 方向 / 关键词 → **topic**
- 用户问开放式 "接下来读什么"，没有 anchor 也没有 topic → **wiki**

如果用户同时提到 "不要这些"，仅在 anchor / bio-anchor 模式下通过 `--negative` 传入。

### Step 2: 决定通道集合

<!-- bio-C2 -->

调用 `tools/discover.py` 之前先把 `--bio-channels` 解析成具体通道列表：

- **bio off**（CS 路径，当前行为）：每 anchor 跑 `s2-recommend + s2-references + s2-citations`；topic 模式跑 `s2-search + deepxiv-search`。
- **bio on**：上述通道**外加** `pubmed-similar + europepmc-citations + biorxiv-related`。bio 通道与 S2 通道并行运行，合并到同一 shortlist。
- **bio auto**：按上文 `--bio-channels` 规则从 anchor / wiki 状态 / topic 字符串检测。把检测决策写进报告，方便用户下次调用时手动覆盖。

### Step 3: 运行 discovery 工具

```bash
"$PYTHON_BIN" tools/discover.py from-anchors \
  --id <arxiv-id> [--id <arxiv-id>...] [--negative <id>...] \
  --wiki-root wiki \
  --limit 10 \
  --output-checkpoint .checkpoints/ \
  --markdown
```

或 topic / wiki 模式：

```bash
"$PYTHON_BIN" tools/discover.py from-topic "<query>" --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown
"$PYTHON_BIN" tools/discover.py from-wiki --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown
```

<!-- bio-C2 -->
bio-anchor 模式（计划中的 `tools/discover.py` 子命令）：

```bash
"$PYTHON_BIN" tools/discover.py from-bio-anchor \
  [--doi <doi>...] [--pmid <pmid>...] [--biorxiv <doi>...] [--negative <id>...] \
  --wiki-root wiki \
  --limit 10 \
  --bio-channels {auto|on|off} \
  --output-checkpoint .checkpoints/ \
  --markdown
```

子命令内部：
1. 用 `tools/fetch_crossref.py` + `tools/fetch_pubmed.py` 中先回的把 `--doi` / `--pmid` 解析成 canonical record。
2. 从 `tools/fetch_pubmed.py similar <pmid>`（PubMed similar-articles）、`tools/fetch_europepmc.py citations <pmid-or-doi>`、`tools/fetch_biorxiv.py related <doi>` 拉相似论文集。
3. 与 S2 通道按 `doi > pmid > arxiv > biorxiv > 标题模糊` 优先级合并。
4. 用同一份 `references/ranking-signals.md` 排序。bio 通道不引入独立 ranking —— 只是扩大候选池。

anchor（与 wiki）模式每个 anchor 默认跑三个 S2 通道 —— `recommend` + `references` + `citations`。这正是 `/discover` 明显区别于 `/daily-arxiv` 的关键：references 带进 anchor 站在其肩膀上的 canonical 老论文，citations 带进高影响后续工作。只有在 API 成本成为硬约束时才考虑 `--no-citation-expand` 退回到只跑 recommend —— 质量退化会很明显。

工具内部处理候选抓取、wiki dedup、ranking，并写 checkpoint。始终传 `--wiki-root wiki`，否则已 ingest 论文会继续出现在 shortlist 中，浪费用户 review 时间。

topic 模式下若 S2 不可用，工具会继续用可用的通道产出；检查输出并向用户说明 degraded discovery。<!-- bio-C2 --> 同样的优雅降级规则适用于 PubMed / EuropePMC / bioRxiv：每个通道独立可重试；单通道失败只会缩小 shortlist，不会让整次失败。若全部通道失败，需明确报错而不是把空 shortlist 当作真实推荐返回。

### Step 4: 展示 shortlist

把 markdown 输出呈现给用户。每条候选要能让用户判断是否值得 ingest：

- 标题和 arXiv ID（或 S2 paperId fallback）<!-- bio-C2 --> 或 DOI / PMID / bioRxiv DOI（候选来自 bio 通道时）
- 一行 rationale（工具已产出：anchor 命中数、influential citations、年份，<!-- bio-C2 --> bio 候选附 source channel）
- 工具带出 TLDR 时一并展示（topic 模式常有；anchor 模式通常没有 —— recommendations endpoint 不返回 TLDR；<!-- bio-C2 --> EuropePMC abstract subjects 在缺 TLDR 时可作替代）

最后附一行 "next step" 提示：

```
如需 ingest：/ingest https://arxiv.org/abs/<arxiv-id>
           | /ingest <doi>            （bio-canonical）         <!-- bio-C2 -->
           | /ingest PMID:<pmid>      （bio-canonical）         <!-- bio-C2 -->
```

不要自行 ingest。选择权归用户。

### Step 5: 日志

```bash
"$PYTHON_BIN" tools/research_wiki.py log wiki "discover | mode=<anchors|bio-anchor|topic|wiki> | seed=<short-desc> | shortlist=<N> | bio-channels={on|off|auto→on|auto→off}"
```
<!-- bio-C2：log 行末尾记录 bio-channel 的最终解析 -->

## Internal Callers

`/discover` 既供用户手动调用，也供其他 skill 作为子例程调用。

### 来自 `/ingest --discover`

`/ingest` 支持可选的 `--discover` flag（默认关闭）。开启时，`/ingest` 在最终 report 之后以刚 ingest 论文的 canonical ID 作为单 anchor 调用 `/discover`。<!-- bio-C2 --> 当刚 ingest 论文的 canonical ID 是 DOI / PMID / bioRxiv DOI 时，post-ingest 调用使用 `--doi` / `--pmid` 而非 `--anchor`，自动激活 bio 通道集合。把 shortlist 以 "接下来可能想 ingest 的相关论文" 段落附在 report 里。`/ingest` 不会从这份列表自动 ingest 任何东西。

### 来自 `/init`

`/init` **不调用** `/discover`。`/init` 的 planner（`tools/init_discovery.py plan`）有自己的打分策略，偏爱 survey、广覆盖、seed anchor —— 适合 bootstrap 场景。`/discover` 的 ranking 有意不同（不偏 survey；以 anchor 相似度 + influential citations 为主），替换进 `/init` 会稀释 shortlist 质量。两者保持独立。

## Constraints

- **不自动 ingest**：`/discover` 产出 shortlist 就结束。即便被 `/ingest --discover` 调用，调用方也只是呈现结果，最终 ingest 由用户决定。
- **除 `log.md` 外不写 `wiki/`**：paper 页、concept、claim、graph edge 全都属于 `/ingest`。
- **不写 `raw/`**：`/discover` 不下载论文。用户选定某个候选后，再手动 `/ingest <arxiv-url>`。
- **始终对 wiki 做 dedup**：必须传 `--wiki-root wiki`，否则已 ingest 论文会污染 shortlist，这是最常见的低质量失败模式。
- <!-- bio-C2 --> **bio 侧 dedup 用 canonical-id 优先级**：把候选与 `wiki/papers/` 比对时按 `doi > pmid > arxiv > biorxiv > 标题模糊` 顺序检索。同一篇论文可能 wiki 同时存 arXiv ID 与 DOI —— 标题模糊是最后兜底。
- **ranking 是 discovery 专属**：不要复用或复制 `tools/init_discovery.py` 的打分函数。两者目标不同 —— `/init` 要宽覆盖与基础面；`/discover` 要相关的 *next reads*。见 `references/ranking-signals.md`。
- **三通道 anchor 抓取**：anchor 模式默认对每个 anchor 同时跑 S2 `recommend` + `references` + `citations`。砍掉 citation 通道（`--no-citation-expand`）会让结果退化为偏最新的语义聚类，和 `/daily-arxiv` 严重重合。除非 API 成本成为硬约束，否则保留三个通道。见 `references/ranking-signals.md`。
- **部分 S2 endpoint 字段较扁平**：`/citations`、`/references`、`/recommendations/*` 拒绝嵌套 selector —— 没有 `authors.hIndex`，没有 `tldr`。`/paper/{id}` 和 `/paper/search` 接受，所以 topic 模式的候选带完整 enrichment；anchor 模式下只从 citations/references/recommend 进来的候选没有。这是 S2 的真实约束，不是 bug。
- **rate limit**：anchor 模式每个 anchor 最多三次 S2 调用（recommend + references + citations）。默认 recs 每 anchor 拉 50 条、references/citations 各 30 条。多 anchor 时调用量成倍增长；有 API key（1 req/sec）时三 anchor 约 10 秒。
- <!-- bio-C2 --> **bio rate limit 叠加**：PubMed E-utilities（无 `NCBI_API_KEY` 时 3 req/s，有时 10 req/s）、EuropePMC（无公开 rate limit 但重查询昂贵）、bioRxiv content API（宽松）。bio-anchor 模式每 anchor 在 S2 三通道之上再加 3 通道 —— 3 anchor 共 ~6 通道 × 3 anchor = 18 次调用。尽量并行。

## Error Handling

- **所有 seed 通道都失败**：明确报错、不写 shortlist，也不记录成功日志。
- **S2 不可用但 DeepXiv 可用（topic 模式）**：仅用 DeepXiv 继续；在 report 中注明 degraded。
- <!-- bio-C2 --> **S2 不可用但 bio 通道可用（anchor / bio-anchor 模式）**：仅用 PubMed + EuropePMC + bioRxiv 继续；在 report 中注明 degraded。shortlist 会偏 bio recall —— 这是正确行为，不是 bug。
- **S2 对某个 anchor 返回零推荐**：保留其他 anchor 的结果继续；若所有 anchor 都返回零，视为整体失败。
- **`--from-wiki` 找不到可用 anchor**（`wiki/papers/` 为空或全部缺少 `arxiv_id` 与 bio id）：告诉用户 wiki 过于稀疏，建议改用 topic 模式。
- **anchor ID 非法或未知**：S2 会返回 404；在 report 中暴露该坏 ID，并用剩余 anchor 继续。
- <!-- bio-C2 --> **DOI / PMID 全通道未命中**：seed 无法解析；明确报错而非降级到标题模糊（会静默漂移 seed 身份）。
- <!-- bio-C2 --> **`--bio-channels on` 强开但无 bio fetcher 工具可用**：降级到 `off`，并在 report 中以 🟡 风格提示；不阻塞运行。

## Dependencies

### Tools（via Bash）

- `"$PYTHON_BIN" tools/discover.py from-anchors --id <id> [--id <id>...] [--negative <id>...] --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- `"$PYTHON_BIN" tools/discover.py from-topic "<query>" --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- `"$PYTHON_BIN" tools/discover.py from-wiki --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- <!-- bio-C2 --> `"$PYTHON_BIN" tools/discover.py from-bio-anchor [--doi <doi>...] [--pmid <pmid>...] [--biorxiv <doi>...] [--negative <id>...] --wiki-root wiki --bio-channels {auto|on|off} --limit <N> --output-checkpoint .checkpoints/ --markdown` —— 计划中子命令；底层 fetcher（`fetch_crossref.py`、`fetch_pubmed.py`、`fetch_europepmc.py`、`fetch_biorxiv.py`）已按 C1 落地。
- `"$PYTHON_BIN" tools/research_wiki.py log wiki "<message>"`

### Skills

- `/ingest` —— 通过 `--discover` flag 调用；也是用户对选中候选执行的动作
- `/init` —— 独立 planner，不调用 `/discover`

### External APIs

- Semantic Scholar —— recommendations (`/recommendations/v1/papers/forpaper/{id}`, `POST /recommendations/v1/papers/`)、search、paper detail（通过 `tools/fetch_s2.py`）
- DeepXiv —— topic 模式下的 search 辅助通道（通过 `tools/fetch_deepxiv.py`，可选，失败时优雅降级）
- <!-- bio-C2 --> NCBI E-utilities (PubMed) —— `esearch` 用于 similar-articles 与 topic query；通过 `tools/fetch_pubmed.py`
- <!-- bio-C2 --> EuropePMC —— citation 扩展、全文 annotations、MeSH；通过 `tools/fetch_europepmc.py`
- <!-- bio-C2 --> bioRxiv content API —— preprint 发现；通过 `tools/fetch_biorxiv.py`
- <!-- bio-C2 --> CrossRef —— DOI 解析与 metadata fallback；通过 `tools/fetch_crossref.py`
