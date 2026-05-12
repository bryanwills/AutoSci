# ΩmegaWiki — 生信适配 Report

> 对应的英文镜像：[`REPORT.en.md`](REPORT.en.md)。任何实质性修改必须同步到两侧。
>
> Reviewer 与未来贡献者用的完整证据。视觉化 demo（hero / GIF / canvas 截图）见项目 [README](../../README.md)。产出本 report 的工作计划见 [DEMO_PLAN.en.md](DEMO_PLAN.en.md) / [DEMO_PLAN.zh.md](DEMO_PLAN.zh.md)。
>
> Snapshot：分支 `feat/qwt-ptm-degrader-ideate` @ `acc0c47`，2026-05-11。Lint：`0 🔴 / 0 🟡 / 11 🔵`。Wiki：11 papers / 22 ideas / 8 experiments / 16 people / 73 graph edges + 1 citation。

## 1. 为什么 fork

上游 ΩmegaWiki 面向 CS / AI 研究——页面模板、lint 规则、skill prompt 都默认论文是 arXiv 形状、用 `claims/` 账本、用 CS 式 evidence 动词（`supports | contradicts | tested_by`）。当我们在 2026-05-02 用一个真实的生信工作流 `/exp-design ptm-aware-degrader-target-nomination` 把 wiki 跑通时，这些 CS-shaped 假设以下面 5 种具体、可重复的方式崩溃：

- **Dataset 引用没有锚点**：TernaryDB、PROTAC-DB、DegronMD、AlphaFold-DB、PhosphoSitePlus、dbPTM、UniProt、PDB 全都以裸文本形式出现，没有 wikilink、没有版本字段、没有 access tier、没有反向链接。
- **生信原生论文标识符不一等级**：`papers/` frontmatter 只暴露 `arxiv`，导致我们 ingest 的 11 篇论文里有 6 篇（DOI / PMID / bioRxiv 形态）没有规范的 ID 槽。
- **Evidence 动词词汇量不够**：`supports` / `contradicts` 无法表达 `wet_lab_validated`、`clinical_validated`、`mechanistic_basis`、`correlative`、`predicts`——而这些才是领域专家真正用的动词。
- **实验成本被压缩成单一字段**：`estimated_hours` 把 GPU 时、MD 墙钟时、湿实验美元、数据访问 lead time 全部坍缩成一个数字，真正的预算约束被掩盖。
- **图结构没有 bio 边类型**：缺少 bio relation（`targets_protein`、`binds`、`degrades`、`phosphorylates`、`ubiquitinates`、…）、validation / translation 事件（`clinical_trial_for`、`fda_approved_for`）、dataset-version provenance（`dataset_version_used`）。

完整审计（每条 finding 一条 P0/P1/P2 条目）：[`docs/bioinformatics-adaptation-backlog.zh.md`](../bioinformatics-adaptation-backlog.zh.md)（en：[`bioinformatics-adaptation-backlog.en.md`](../bioinformatics-adaptation-backlog.en.md)）。Section A–H 于 2026-05-02 起草；目前落地的是 A1–A8 这八个 schema 条目。

## 2. 整合时间线

在上游基线 `3ed31ed` 之上的 10 个 commit（按时间顺序）：

```
53cfdb8 chore(integrate): pull upstream v1.1.0 — SSOT runtime + visualize + tools refactor
8efea8c chore(integrate): pull upstream v1.2.0 — daily-arxiv pipeline + workflow
e5cb75b chore(integrate): regenerate .claude/skills + CLAUDE.md from new i18n via setup.sh
b07c030 refactor(people): merge ## Key papers into ## Recent work for new schema
8d46f52 refactor(claims): migrate 15 wiki/claims/*.md → wiki/ideas/* per new schema
a83b15b feat(ptm): close PTM ideate cycle + finish claims-to-ideas migration for WIP
aba1670 refactor(graph): align WIP tested_by edges with experiment → idea direction
3e56592 chore(gitignore): exclude visualize-generated artifacts
787803b chore(integrate): pull upstream app/ SPA missed during v1.1.0 surgical-checkout
acc0c47 chore(gitignore): exclude .checkpoints/ (skill local state)
```

本地复现：`git log --graph --oneline 3ed31ed..HEAD`。

模式是 **3 次上游拉取 + 3 次正向迁移 + 4 次清理**：
- **上游拉取**（`53cfdb8`、`8efea8c`、`787803b`）：拉入 v1.1.0 的 SSOT runtime / visualize / tools 重构，v1.2.0 的 daily-arxiv 流水线，以及 v1.1.0 surgical checkout 时遗漏的 SPA bundle。
- **正向迁移**（`b07c030`、`8d46f52`、`aba1670`）：把老 wiki 内容重塑成新 schema——people 的 `Key papers → Recent work`、claims-to-ideas、以及实体改名带出的 graph 边方向修正。
- **清理 commit**（`e5cb75b`、`a83b15b`、`3e56592`、`acc0c47`）：从新的 `i18n/` 重新生成 `.claude/skills`、关闭 PTM ideate 循环、gitignore 生成产物以保持工作树干净。

## 3. Schema 迁移：`claims/` → `ideas/`

最大的一次正向迁移是 claims-to-ideas 重构（`8d46f52`）。上游 v1.1.0 把 `wiki/claims/` 作为顶层实体废弃，把它的内容合并进生命周期更丰富的 `wiki/ideas/`。我们改写了 15 个页面、重指了 21 条 graph 引用。

状态字段映射（取自上游 `runtime/schema/entities.yaml`）：

| 旧 `claims/` 状态 | 新 `ideas/` 状态 | 含义 |
|---|---|---|
| `supported` | `validated` | 多条独立的支持证据；高置信 |
| `weakly_supported` | `tested` | 有部分证据但尚未定论 |
| `disputed` | `tested` | 证据冲突；仍在主动研究 |
| `unverified` | `proposed` | 尚无直接证据；仅为假设 |
| `refuted` | `failed` | 证据排除该假设 |

迁移涉及：
- **15 个页面改写** —— `wiki/claims/*.md` → `wiki/ideas/*.md`，frontmatter 改成 ideas schema，`evidence` 数组按情况转换为 `pilot_result` + `failure_reason`。
- **21 条 graph 边重指** —— `wiki/graph/edges.jsonl` 中 `claims/{slug}` 引用改为 `ideas/{slug}`。
- **1 次 index 合并** —— `wiki/index.md` 的 `claims:` 区块并入 `ideas:`。
- **Graph 边方向修正**（`aba1670`）—— 原本指向 `claim → experiment` 的 `tested_by` 边按新 edges schema 方向约定反向为 `experiment → idea`。
- **`wiki/claims/` 删除** —— 目录完全删除；该实体类型从 wiki 中消失。

## 4. 整合窗口内的 Lint 指标

在每个关键 commit 上 checkout 并跑 `tools/lint.py` 抓出的实测数据。列依次为：红（错误）/ 黄（警告）/ 蓝（信息）。

| # | Commit | 状态 | 🔴 | 🟡 | 🔵 | 备注 |
|---|---|---|---:|---:|---:|---|
| 0 | `3ed31ed` | 整合前基线（老 wiki + 老 lint） | 0 | 0 | 11 | 老 lint 跑在老 wiki 上：干净。11 条蓝色是已存在的 low-key_paper 信息提示。 |
| 1 | `e5cb75b` | 整合后/迁移前（新 lint + 新模板 + 老 wiki 内容） | 0 | **43** | 11 | 新 lint 跑在老 shape 的内容上，浮出 43 条 schema-mismatch 警告——大头是 `claims/` 页面和 `people/` 页面里被废弃的 `## Key papers` 区块。 |
| 2 | `b07c030` | people 迁移后（`Key papers → Recent work`） | 0 | **26** | 11 | 减 17 条警告（`people/` 形状已对齐）。剩下的黄色都是等待迁移的 `claims/` 页面。 |
| 3 | `8d46f52` | claims-to-ideas 迁移后 | 0 | **0** | 11 | 对新 lint 完全干净。 |
| 4 | `acc0c47` | pilot merge 前的 HEAD | 0 | 0 | 11 | 经过 PTM ideate 循环 + 图边方向修正后，干净状态保持。 |
| 5 | 工作树（A1 minimal + A5 切片 + A6 + B3 + A7 + A3 minimal + B1 完整 + B2 minimal + add-edge --metadata pilot merge 后，2026-05-11） | 0 | 0 | 11 | 第 10 种实体 `datasets/` 已注册 + ternarydb 已建；一个实验的 `setup.dataset` 已 wikilink；8 个实验 `estimated_cost` 结构化块 live；**新增 14 种边类型**（全部 10 个 B1 + 3 个 B2 + 1 个 B3）→ **总 35**；**Section B schema 完整注册 14/14**；**6 条 live bio 边**（3 B1 + 1 B2 + 2 B3，其中 2 条带类型化 metadata）；PTM idea 上有 `grade: low`；musitedeep paper 上有 `doi` + `pmid`。与第 4 行同一组蓝色 informational —— 所有 pilot 保持完全加性。 |

剩下的 11 条蓝色信息提示记录在 [第 6 节 / 后续工作](#6-后续工作) ——它们是 `concepts/` 页面 `key_paper` 计数 ≤1 的提示（这些页面我们知道需要更宽的引用覆盖）。另外两条是没有任何 incoming `tested_by` 的孤立 `ideas/` 页面（PTM ideate 循环提出了它们，但还没有 experiment block 去验证）。

**关于 demo GIF 分镜的提醒**：当前 `DEMO_PLAN.zh.md` 的 Scene 1 写的是 "checkout `3ed31ed` 跑 lint 应该红黄一片"。这个预期是错的——在 `3ed31ed`，wiki 和 lint 都还是老 shape，所以 lint 是干净的。Lint 警告是**上游拉取之后**才出现的（上表第 1 → 2 → 3 行）。GIF Scene 1 应该改成：先展示上游合并后的 `e5cb75b` 状态有 43 条 schema 警告，再展示两次迁移后 HEAD 是 0。是否修订分镜由用户决定。

## 5. Section 级别适配状态

Schema 层面的改动（模板、frontmatter、lint hook、skill prompt）以镜像副本形式起草在 `docs/bio-adaptation/section-{a,b,c}/`，对应着各自的 source-of-truth 文件。每个 section 被采纳时，对应的 hunk 会被合并回去，`CHANGELOG` 条目状态从 `STATUS: drafted` 改为 `STATUS: merged`。

| Section | 范围 | 镜像位置 | 覆盖的 backlog 条目 | 采纳状态 |
|---|---|---|---|---|
| A — Schema 添加 | 页面模板 + frontmatter（datasets/、蛋白质锚点、bio 标识符、GRADE evidence、结构化实验成本） | [`section-a/runtime-page-templates.zh.md`](section-a/runtime-page-templates.zh.md)、[`section-a/runtime-page-templates.en.md`](section-a/runtime-page-templates.en.md)、[`section-a/CLAUDE.md`](section-a/CLAUDE.md) | A1–A8 | **A1（最小）+ A2（light）+ A3（最小）+ A5（单实验切片）+ A6 + A7（最小）已于 2026-05-11 pilot-merge；A4/A8 仍 drafted** |
| B — Graph 规则 | bio relation 边、validation / translation 边、dataset-version provenance | [`section-b/runtime-support-files.zh.md`](section-b/runtime-support-files.zh.md)、[`section-b/runtime-support-files.en.md`](section-b/runtime-support-files.en.md)、[`section-b/CLAUDE.md`](section-b/CLAUDE.md) | B1–B3 | **Section B schema 已于 2026-05-11 完整注册**：B1（10/10 动词、3 条 live 边）+ B2（3/3 动词、**1 条 live：`validates_in_species`，带类型化 metadata `species=human`**）+ B3（1/1、**2 条 live，其中 1 条带类型化 metadata `version=v1`**）—— 总 14/14（整个图谱 35 边类型）。`tools/research_wiki.py add-edge` 现支持 `--metadata KEY=VALUE`（可重复）；6 条 live bio 边中 2 条带类型化 `metadata.*` 属性。Loader 层面的 nested-schema 验证仍延后。 |
| C — Skill prompt | 对 `/ingest`、`/exp-design`、`/check`、`/ideate`、`/novelty`、`/paper-plan`、`/paper-draft`、`/rebuttal`、`/exp-run`、`/discover` 的逐技能改动 | [`section-c/skills/{skill}/SKILL.{zh,en}.md`](section-c/skills/) | C1–C9 | **C1 + C2 minimal 已于 2026-05-11 pilot-merge**（C1：`/ingest` Step 2.5 生信标识符抽取；C2：`/exp-design` Step 6 输出 A6 `estimated_cost` 块 —— 闭合 A6 ↔ C2 环）。两者完整版本仍延后计划中的 bio fetcher / NER / 成本推断自动化。C3–C9 仍 drafted。 |

逐条 diff 与理由：[`CHANGELOG.zh.md`](CHANGELOG.zh.md) / [`CHANGELOG.en.md`](CHANGELOG.en.md)。

## 6. 后续工作

当前 snapshot 下尚未关闭的事项：

- **把 Section A、B、C 的镜像合并回 source-of-truth**。每个 section 的 CHANGELOG 状态从 `STATUS: drafted` → `STATUS: merged`，对应的 hunk 应用到 `i18n/en/`、`i18n/zh/`、`runtime/schema/` 以及 `.claude/skills/` 下的活动 skill prompt，然后清理镜像。
- **Backlog Section D–G** —— Section C 尚未覆盖的 skill（paper-compile、ask、edit、…），以及依赖 A/B 落地后的 lint 扩展。
- **Backlog Section H** —— DNA 测序、转录组、单细胞、微生物组、临床 / 群体基因组、系统发育基因组等子领域条目目前是**外推**得出的，尚未由观察到的 wiki failure 验证。每次首次 ingest 该子领域的论文时重新评估。
- **11 条蓝色信息提示** —— 9 条是 `concepts/` 页面 single `key_paper` 的提示，2 条是孤立 ideas/ 页面（`chirality-aware-af3-diffusion`、`ptm-site-disorder-predictor`），缺少入链覆盖。这两类会随更多论文 ingest 自然累积。
- **Push target 未定** —— `origin/dev` 上游已被删除；项目规范里 "branch from dev → PR to dev" 在当前现状下不适用。Push 本分支前需确认 PR target（main？重建 dev？）。

逐条 changelog 见 [`CHANGELOG.zh.md`](CHANGELOG.zh.md) / [`CHANGELOG.en.md`](CHANGELOG.en.md)。
