# 生信适配 Demo Plan（v2 — 用户向）

> 对应英文镜像：[`DEMO_PLAN.en.md`](DEMO_PLAN.en.md)。任何实质性修改必须同步到两侧。
>
> v1 围绕整合机制展开（commit 时间线、lint 指标、claims→ideas 迁移）。v2 改为围绕**用户能拿到什么**：新增了什么功能、对比上游改了什么、实际效果如何。v1 的整合叙事完整保留在 [`REPORT.zh.md`](REPORT.zh.md)。

## 1. Pitch（每类受众一句话）

- **仓库访客**：ΩmegaWiki / bio-adaptation 把 CS 形态的上游改造成可用于生物研究的工具——dataset、protein、DOI 论文都成为一等公民；图谱携带 bio relation 边；skill 理解湿实验预算和 GRADE 证据。我们用一次真实的 PTM-aware degrader 目标提名工作流把它跑通了。
- **生信研究者**：丢一篇 PROTAC 或 PTM 论文进去。Wiki 会创建带 bio 标识符的条目，链接数据集和靶蛋白，以 GRADE 置信度记录临床证据。`/exp-design` 给出真实预算——GPU 时数、湿实验美元、数据访问 lead time 全包含，而不只是 GPU。
- **未来贡献者**：20 项 backlog 条目（A1–A8、B1–B3、C1–C9）以 merge-ready 镜像形式存放在 `docs/bio-adaptation/section-{a,b,c}/`。线上 wiki 已吸收 schema-中立的升级（ideas 生命周期、people Recent-work）。Section A/B/C 都是加性改动，随时可采纳。

## 2. 功能目录

三个模块。每行写明：(a) 功能做什么，(b) 用户看到什么，(c) live / drafted 状态。

### 2.1 Schema 类（Section A —— 8 项）

| # | 功能 | 用户看到 | 状态 |
|---|------|---------|------|
| A1 | `datasets/` 作为第 10 种实体 | `[[ternarydb]]` wikilink，带版本、access tier、源论文 | **pilot-merged 2026-05-11**（最小切片；ingest 时自动建页延后到 C1） |
| A2 | `concepts/` 加蛋白质锚点 | `concepts/p53.md` 含 `uniprot_id`、`pdb_ids`、`species` | **A2 light 已于 2026-05-11 pilot-merge**（concepts/ 加 4 个可选字段；首个具体蛋白质概念页 `concepts/crbn.md` 已写，HGNC + UniProt + PDB + species 全部填好；A2 heavy / `proteins/` 实体类型延后） |
| A3 | `papers/` frontmatter 加 bio 标识符 | DOI / PMID / bioRxiv / s2_id 槽位，不只 `arxiv` | **A3 最小切片已于 2026-05-11 pilot-merge**（加 doi + pmid；一篇 paper 已填值；biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species 延后到 C1 bio NER） |
| A4 | `paper_style` 识别 venue | `/paper-draft` 对 bio venue 切换 result-first 写法 | drafted |
| A5 | `setup.dataset` 改为 wikilink | `/exp-design` 输出 `[[ternarydb]]` 而非裸字符串 | **pilot-merged 2026-05-11**（单实验切片；剩余 7 个实验仍是 plain-string，完整 A5 的 bio modality 字段延后） |
| A6 | 结构化 `estimated_cost` 块 | gpu_hours / md_wallclock_hours / wet_lab_usd / fte_weeks / dataset_access_lead_time_days | drafted |
| A7 | 扩展 evidence 动词 + GRADE | `wet_lab_validated`、`clinical_validated`、`mechanistic_basis`、`correlative`、`predicts`；可选 `grade: very-low \| low \| moderate \| high` | **A7 最小切片已于 2026-05-11 pilot-merge**（ideas/ 顶层加可选 `grade` 字段；一个 idea 已填 `grade: low`；per-edge GRADE + 扩展证据动词延后） |
| A8 | Bio 领域词表 | `domain: structural-bio \| chembio \| comp-drug-discovery \| ...` 由 lint 校验 | drafted |

### 2.2 Graph 类（Section B —— 3 项）

| # | 功能 | 用户看到 | 状态 |
|---|------|---------|------|
| B1 | Bio relation 边 | 图谱含 `targets_protein`、`binds`、`inhibits`、`activates`、`degrades`、`phosphorylates`、`ubiquitinates`、`methylates`、`acetylates`、`is_substrate_of` | **B1 完整切片已于 2026-05-11 pilot-merge**（10/10 动词注册；3 条 live 边：`targets_protein` + `ubiquitinates` + `binds`；剩余 7 个动词等 C1 bio NER 做系统化 live-edge 填充） |
| B2 | Validation / translation 边 | `clinical_trial_for`、`fda_approved_for`、`validates_in_species`，带类型化 metadata（trial id、phase、species） | **B2 最小切片已于 2026-05-11 pilot-merge**（3/3 动词注册；1 条 live `validates_in_species` 边，借 `add-edge --metadata` CLI 扩展带上了类型化 `metadata: {species: human, source_db: uniprotkb-swissprot}`；剩余 2 个动词等 wiki 出现临床试验/FDA-approval 锚点） |
| B3 | Dataset-version provenance 边 | `experiment → dataset` 携带 `dataset_version_used`，含 `metadata.version` | **pilot-merged 2026-05-11**（边类型已注册；1 条 live 边 `deepternary-baseline → ternarydb`；版本信息暂存 `evidence` 字符串，类型化 `metadata.version` 延后到 add-edge CLI 扩展之后） |

### 2.3 Skill 类（Section C —— 9 项）

| # | Skill | 用户看到 | 状态 |
|---|-------|---------|------|
| C1 | `/ingest` | Bio NER 预扫；自动链接 datasets/proteins；保留 DOI/PMID；JATS-XML 与 `.tex` 同优先级 | **C1 minimal 已于 2026-05-11 pilot-merge**（SKILL.md 新增 Step 2.5 让 LLM agent 填 doi+pmid + 升级 dataset 提及为 `[[ ]]` wikilink；完整 fetcher 工具 + 结构化 NER + DOI/PMID 输入延后） |
| C2 | `/exp-design` | 结构化 cost 块；真实湿实验 / MD 预算；预算削减顺序固定 | **C2 minimal 已于 2026-05-11 pilot-merge**（Step 6 frontmatter 模板对每个新实验输出 A6 `estimated_cost` 块；闭合 A6 ↔ C2 环；自动 framework 推断 + 固定削减顺序延后） |
| C3 | `/check` | 新增 `tools/lint_bio.py` 校验 bio frontmatter（UniProt 格式、GRADE 一致性、dataset 版本漂移） | drafted |
| C4 | `/ideate` | 在 claim gap 之外，浮现 bio relation gap（未靶蛋白、未验证磷酸化等） | drafted |
| C5 | `/novelty` | GRADE 加权评分；bio 先期工作检索（Semantic Scholar bio 子集） | drafted |
| C6 | `/paper-plan` | venue-aware `paper_style` 解析（Nature 与 claim domain 冲突时 Nature 胜出） | drafted |
| C7 | `/paper-draft` | Bio claim result-first 写作；嵌入生物统计；bio caption 格式 | drafted |
| C8 | `/rebuttal` | Bio reviewer 关切（机理、临床相关性、cohort 泛化） | drafted |
| C9 | `/exp-run`、`/discover` | 湿实验交接 hook；bio 论文发现 profile | drafted |

逐条理由：[`CHANGELOG.zh.md`](CHANGELOG.zh.md)。

## 3. 已经生效的改动

以下改动已合并，现在就可以验证：

| 改动 | 生效起点 | 用户能感知到的效果 |
|------|---------|--------------------|
| 上游 v1.1.0 SSOT runtime + visualize | `53cfdb8` | 模板 / 边规则有单一来源；SPA 在 `http://127.0.0.1:8765/` 提供 |
| 上游 v1.2.0 daily-arxiv 流水线 | `8efea8c` | `python tools/daily_arxiv.py prepare/recommend-llm/finalize` 端到端跑通，使用 DeepSeek v4-flash |
| `people/` schema 重构 | `b07c030` | Person 页面使用 `## Recent work`（不再用废弃的 `## Key papers`） |
| **claims/ → ideas/ 生命周期迁移** | `8d46f52` | 15 个旧 claim 改造成 idea，状态枚举更丰富（`proposed`/`tested`/`validated`/`failed`）；21 条 graph 边重指；lint 从 26 🟡 降到 0 🟡 |
| Graph 边方向修正 | `aba1670` | `tested_by` 边按新规范从 `experiment → idea` 方向流转 |
| .gitignore 清理 | `3e56592`、`acc0c47` | 生成产物（visualize 输出、`.checkpoints/`）不再进入 git |

`feat/qwt-ptm-degrader-ideate @ acc0c47` (2026-05-11) 的快照：lint `0 🔴 / 0 🟡 / 11 🔵`，wiki 含 11 papers / 22 ideas / 8 experiments / 16 people / 73 graph edges + 1 citation。

## 4. 实际应用——PTM-aware degrader 工作流

整套适配是被真实的生物研究需求驱动出来的。端到端流程：

1. **Seed wiki** —— 11 篇结构生物学 / PTM / 药物设计论文：AlphaFold 2 & 3、AlphaFold-DB 2024、MusiteDeep、面向分子的几何深度学习、E3 ubiquitin ligase 平台（Ronai）、面向 targeted therapy 的多组学、DegronMD 类 PTM-substrate 网络。
2. **`/ideate`** —— 提出 3 个 idea（优先级 5/4/5），过滤掉 2 个失败 idea 进 banlist。锚点 idea：[`ideas/ptm-aware-degrader-target-nomination`](../../wiki/ideas/ptm-aware-degrader-target-nomination.md) —— 用 noise-floor 校准的 ΔpTernary 给 PTM-isoform 选择性 degrader 排序。
3. **`/exp-design`** —— 在锚点 idea 上设计 8 个实验，分 5 stage（sanity → baseline → Phase-0 噪声底 → 主验证 → 消融 → 鲁棒性），总预算约 104 GPU-h。每个实验通过 `linked_idea` 反链回 idea；每个 idea 拆解时写 `target_claim`（迁移前的旧字段名）。
4. **`/daily-arxiv`** —— 用一份 9 篇 q-bio.BM mock feed，DeepSeek v4-flash 排出 5 strong / 3 maybe / 1 skip。结果存在 [`examples/output/digest-sample.md`](../../examples/output/digest-sample.md)。
5. **每个功能在该工作流的落地点**（当前 vs Section A/B/C 合并后）：

| 功能 | 在哪里出现 | 当前 | A/B/C 合并后 |
|------|----------|------|--------------|
| A3 bio 标识符 | `wiki/papers/musitedeep-...md` frontmatter | `arxiv: ""`（论文有 DOI 但 frontmatter 没槽位） | `doi: 10.1093/nar/gkaa275` 填充 |
| A5 dataset wikilink | `wiki/experiments/deepternary-baseline.md` 的 `setup.dataset` | **live** —— `[[ternarydb]] CRBN+VHL test split ...` wikilink，并已有 `wiki/datasets/ternarydb.md` 实体页。其他 7 个 sibling 实验仍是 plain-string（向后兼容 demo） | 完整 A5 会改造全部 8 个实验，且把 `setup` 扩展加 `in_silico_or_wet`、`species`、`cell_line`、`assay_type`、`force_field` |
| A6 结构化 cost | 同上实验，`estimated_*` 字段 | `estimated_hours: 4` | `estimated_cost: { gpu_hours: 4, dataset_access_lead_time_days: 7, ... }` |
| A7 GRADE 证据 | `wiki/ideas/ptm-aware-degrader-target-nomination.md` `origin_gaps` 引用的证据 | 只有 `confidence: 0.6` | + `grade: moderate`，evidence type 为 `mechanistic_basis` |
| B1 bio 边 | `wiki/graph/edges.jsonl` | 8 种边 live；无 bio relation | + `targets_protein`、`phosphorylates`、…；由 C1 改造后的 `/ingest` 自动抽取 |
| C7 bio 写作 | 未来 bio 论文的 `/paper-draft` 输出 | CS claim-first | Result-first + 嵌入生物统计 |

## 5. Demo 交付物

本次会话已产出：

- ✅ [`REPORT.en.md`](REPORT.en.md) / [`REPORT.zh.md`](REPORT.zh.md) —— 完整证据、整合时间线、lint 指标、section A/B/C 状态
- ✅ [`demo/run-demo.sh`](../../demo/run-demo.sh) —— 可跑的 3 步 daily-arxiv 流水线，bilingual 头注释；无 DeepSeek key 时优雅降级
- ✅ [`demo/sample-feed.json`](../../demo/sample-feed.json) —— 9 篇 q-bio.BM mock feed
- ✅ [`examples/output/digest-sample.md`](../../examples/output/digest-sample.md) —— 预渲染的 DeepSeek 排序输出（无需 API 配额）
- ✅ `wiki/log.md` 2026-05-11 milestone 条目
- ✅ README.md 双语生信适配 hero 章节

待办交付物（分工见下）：

- ⏳ `assets/demo.gif` —— 30–60s 走查，按 §6 storyboard 录制（用户）
- ⏳ `assets/canvas-ptm-focus.png` —— Obsidian canvas 导出 PTM 邻域（用户）
- ⏳ `assets/graph-view.png` —— SPA 全图截图（用户）
- ❓ `assets/feature-preview-*.png` —— 为 drafted-but-not-live 功能制作的静态 mockup（哪些场景需要见 §8 数据审计）

## 6. 新版 GIF storyboard —— 5 场 × 约 10s ≈ 50s

Storyboard 锚定在真实 wiki 页面上。每一场都标注哪部分是 live、哪部分是 drafted，让 demo 诚实。

| # | 时长 | 内容 | 高亮功能 | Live 还是 drafted？ |
|---|------|------|---------|-------------------|
| 1 | 8s | 打开 `wiki/papers/musitedeep-deep-learning-based-webserver-protein.md` —— 展示丰富 frontmatter：`doi: 10.1093/nar/gkaa275`、`pmid: 32324217`（A3 最小切片 pilot）、`domain: Bioinformatics`、`venue: Nucleic Acids Research`、`code_url: github.com/duolinwang/MusiteDeep_web`；caption 指出剩余 A3 字段（biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species）延后到 C1 bio NER | live A3 minimal | **live**（DOI/PMID 可见）；剩余 A3 caption |
| 2 | 12s | 打开 `wiki/ideas/ptm-aware-degrader-target-nomination.md` —— 滚动 Motivation / Hypothesis / Approach；高亮 `grade: low`（A7 最小切片 pilot）、`linked_experiments`（8 条）、`status: in_progress`、`pilot_result` 槽、`origin_gaps` wikilinks；caption：per-edge GRADE + 扩展证据动词（wet_lab_validated、mechanistic_basis、…）属完整 A7 范围，延后 | live A7 minimal + ideas 生命周期 | **live**（idea 上 GRADE + status / 链接）；完整 A7 caption |
| 3 | 12s | 打开 `wiki/experiments/deepternary-baseline-ternarydb-crbn-vhl-reproduction.md` —— `setup.dataset` 解析为 `[[ternarydb]]`；点击跳到 `wiki/datasets/ternarydb.md`（Overview / Versions / Access / Used by experiments / Known caveats）；返回实验页，`estimated_hours: 4` 仍是单数字，旁注展示 section-a 结构化 `estimated_cost` 块 | A1 + A5 live；A6 caption | **live**（实验 + datasets/ternarydb.md，2026-05-11 pilot merge）；仅 A6 caption |
| 4 | 12s | 打开 SPA `http://127.0.0.1:8765/` —— 在 PTM-aware degrader 邻域平移；悬停跨 section-b 三家族的 bio 边：B1 —— `targets_protein`、`ubiquitinates`、`binds`；B2 —— `validates_in_species`（musitedeep → post-translational-modification-site-prediction，**带类型化 metadata `{species: human, source_db: uniprotkb-swissprot}`**）；B3 —— `dataset_version_used` ×2（deepternary-baseline → ternarydb，evidence 字符串编码版本；phase0-noise-floor → ternarydb，**带类型化 metadata `{version: v1, subset: crbn-vhl-training}`**）；同时展示一条 `experiment → idea` 的 `tested_by` 边作方向对照；caption 浮层列出 7 个 B1 动词 + 2 个 B2 动词暂无 live 边，等 C1 bio NER | live `tested_by` + 6× bio 边覆盖 B1/B2/B3 | **live**（35 种边类型；**section-b 三家族都有 live 边**；2 条边借新 `add-edge --metadata` CLI 演示类型化 `metadata.*`） |
| 5 | 8s | 终端窗格：`bash demo/run-demo.sh` → digest.md 打开，DeepSeek 给出 strong/maybe/skip 推荐 | live daily-arxiv | live |

**录制工具**：Linux/WSL：`peek` 或 OBS + `gifski`；macOS：`Kap`；纯终端片段：`asciinema rec` + `agg`。编码：`ffmpeg -i input.mp4 -vf fps=12,scale=900:-1 -f image2pipe - | gifski - -o demo.gif`。目标 < 5 MB（GitHub 友好）。

## 7. 任务分工

### Claude 能做（无需人工交互）

- [ ] 重构 `REPORT.{en,zh}.md`，让 §2 以功能目录开头（当前以整合时间线开头）。整合时间线降为附录。
- [ ] 收紧 README hero：在对比表前加一句 "生信研究者获益" 的 3 条 bullet 提要。
- [ ] 可选：在 `docs/bio-adaptation/preview/` 下手工撰写静态 feature-preview 页面以支撑 storyboard 1–4 场（哪些需要见 §8）。双语镜像。

### 用户必须做（本地交互）

- [ ] 按 §6 storyboard 录 `assets/demo.gif`。
- [ ] Obsidian：导出 `assets/canvas-ptm-focus.png`。
- [ ] 浏览器：在 `http://127.0.0.1:8765/` 截 `assets/graph-view.png`。
- [ ] 把素材放进 `assets/`；push 分支。

## 8. 数据审计 —— storyboard 还缺什么

用户提出可以重跑任何能产生所需数据的流程。**诚实的答复：没有缺失的流水线数据。缺口在 feature 合并状态，不在数据。** 每个 storyboard 场景当前展示的都是真实的 wiki 状态；"缺"的是尚未合并回 source-of-truth 的 drafted 功能。

逐场就绪度：

| 场景 | live 数据就绪？ | 缺口 | 补法 |
|------|----------------|------|------|
| 1 (paper page) | ✅ `musitedeep-...md` 内容丰富；**`doi` + `pmid` 已填**（A3 最小切片 pilot 2026-05-11） | 剩余 6 个 A3 字段（biorxiv / pdb_ids / uniprot_ids / nct_ids / gene_symbols / species）仍 drafted | caption 浮层指出延后的 6 个；`docs/bio-adaptation/preview/paper-with-bio-ids.md` 展示完整 A3 形态作参考。C1（bio NER）的 ingest 时自动填充是非 pilot 论文的解锁路径。 |
| 2 (idea page) | ✅ `ptm-aware-degrader-target-nomination.md` 内容充实，ideas 生命周期 status 可见；**`grade: low` 已填**（A7 最小切片 pilot 2026-05-11） | `pilot_result` 槽空（没跑过 /exp-run）；per-edge GRADE 和扩展证据动词仍 drafted | 完整 A7 用 caption 处理。*pilot_result* 需要至少跑通 baseline 实验的 `/exp-run` —— 重型任务（真实 GPU 计算），**不建议作为 demo 准备工作** |
| 3 (experiment page) | ✅ `deepternary-baseline-...md` 内容充实，`setup.dataset: [[ternarydb]]` 已 live，`wiki/datasets/ternarydb.md` 已 live | A6 结构化 cost 块仍 drafted；`estimated_hours: 4` 还是 live 形态 | 静态 caption overlay 展示 section-a 的 `estimated_cost` 提案。若希望此处也 live，A6 pilot merge 仍是开放选项。 |
| 4 (SPA 图) | ✅ 79 边、**35 种边类型 live**；**6 条 live bio 边覆盖 section-b 三家族**（3 B1 + 1 B2 + 2 B3）；ternarydb + ubiquitin-ligase-e3 + post-translational-modification-site-prediction 概念是连接 hub；**`add-edge --metadata` CLI 扩展已 live** —— 6 条 bio 边中 2 条带类型化 `metadata.*`（1 B2 + 1 B3） | 7/10 个 B1 动词、2/3 个 B2 动词仍无 live 边，等 C1 bio NER 做系统化内容抽取 | CLI 支持类型化 metadata 后，加更多 live 边只是小加性步骤；剩余主要解锁路径是 C1 skill-prompt 升级（`/ingest` 加 bio NER 预扫）。 |
| 5 (digest) | ✅ `digest-sample.md`、`run-demo.sh` 就绪 | 无 | — |

**重跑无法解决的事**（因为功能没合并）：

- 今天对 bio 论文跑 `/ingest`，产出 shape 和现有页面一样——没有 DOI/PMID frontmatter、没有 bio NER 预扫。
- 重跑 `/exp-design` 复现的仍是 `estimated_hours` 字段。
- 重跑 `/novelty` 还不是 GRADE 加权。
- 重跑 `/visualize` 可能刷新 canvas 文件，但不会引入 bio 边类型。

**重跑会有用的事**：

- **用一份新鲜 feed 跑 `/daily-arxiv`** —— 产生一份当天真实 digest 而非 mock。对 "这玩意儿生产环境跑得通" 的论述有用，但对 storyboard 不是必需。
- **截一个 `/exp-status` 快照给 GIF caption** —— 当前状态的快读。轻量。

**如果你想让场景 1–4 直接展示 live 功能而不是用 caption 浮层兜底，最小解锁动作是先把 A/B 里一两个最易 demo 的条目 pilot merge 进 source-of-truth**。两个便宜的候选：

- **A6（结构化 cost）+ 一次性重写 8 个 experiment 页面** —— 小规模机械改动；立即让场景 3 有 live 的结构化 cost demo。**剩余的开放选项。**
- ~~**A5 + A1 minimal（创建 `wiki/datasets/ternarydb.md` + 改一个实验的 `setup.dataset` 字段）**~~ —— **已于 2026-05-11 合并**；逐文件 diff 见同日 CHANGELOG 条目。

两者都不触碰上游 skill prompt（C1–C9）或 graph 规则（B1–B3）；都是隔离的加性 schema 改动。决定权在你——想做就告诉我。

## 9. 未决项

- **Push target**：`origin/dev` 上游已删；项目规范里 "branch from dev → PR to dev" 当前不适用。Push 前需确认 PR target。
- **Section A/B/C 合并节奏**：20 个 drafted 条目——单 PR 还是按 section 分阶段？Demo 强度依赖这一决定。
- **Section H 验证**：子领域条目（DNA 测序、转录组、单细胞、微生物组、临床基因组、系统发育基因组）目前是外推；每个子领域首次 ingest 时重新评估。

## 新对话恢复指令

```
2026-05-11 会话结束时工作树有 13 项 pilot 已合并（未 commit）。
先读 docs/bio-adaptation/CHECKPOINT-2026-05-11.zh.md —— 含完整快照、commit-split
方案与待决事项。

分支 feat/qwt-ptm-degrader-ideate @ acc0c47（最后已提交）；lint 干净（0/0/11）。
逐节覆盖率：A 6/8 + B 14/14 边类型 + C 2/9；A2 light 加了首个具体蛋白质概念页
（crbn.md）；add-edge CLI 现支持 --metadata KEY=VALUE。

要继续 pilot：从 CHECKPOINT §7 或 DEMO_PLAN §7 选。
要 commit：执行 CHECKPOINT §6（5-commit split），然后决定 push target。
要录 demo 素材：DEMO_PLAN §6 storyboard 已与当前状态一致。
```
