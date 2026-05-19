<div align="center">

<img src="../../assets/logo.png" width="160" alt="ΩmegaWiki Logo">

# ΩmegaWiki · bio-adaptation

### A bioinformatics-shaped fork of LLM-Wiki / LLM-Wiki 的生信形态分支

**PTM-aware degrader · structural biology · ML for molecules**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../../LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![Entity Types](https://img.shields.io/badge/Entity_Types-10_(vs_9)-green.svg)](#wiki-structure-differences)
[![Bio Edges](https://img.shields.io/badge/Bio_Edge_Types-14-purple.svg)](#wiki-structure-differences)
[![Skills](https://img.shields.io/badge/Skills-24-orange.svg)](#skills-differences)

[**English**](#english) · [**中文**](#chinese) · [upstream README](../../README.md)

</div>

---

## Author / 作者

<div align="center">
<table>
  <tr>
    <td align="center" width="200">
      <img src="../../assets/DiChenyang_circle.jpg" width="100" alt="Di Chenyang"/>
      <br/><br/>
      <b>Di Chenyang</b>
      <br/>
      <sub>PKU</sub>
      <br/>
      <sub>Undergraduate · 2023</sub>
    </td>
  </tr>
</table>
</div>

> Bio-adaptation fork built on top of upstream [ΩmegaWiki](../../README.md) by [DAIR Lab](https://cuibinpku.github.io/) at Peking University. /
> 本 fork 在北京大学 [DAIR Lab](https://cuibinpku.github.io/) 团队的上游 [ΩmegaWiki](../../README.md) 之上做生信场景改造。

---

# <a id="english"></a>English

## Introduction

Upstream ΩmegaWiki defaults to a CS shape — `arxiv` is the primary paper ID, single dataset concept, experiment records get by with `model + dataset + hardware` only, and `claims/` is the evidence ledger. That shape is efficient for ML paper workflows; it gets uncomfortable the moment you bring it to **bioinformatics / structural biology / drug discovery**: DOI and PMID are more universal than arXiv IDs, datasets need versioning, wet-lab vs in-silico experiments must be distinguishable, and cellosaurus / RRID / PDB version provenance must trace cleanly.

This fork applies 12 schema + skill + tooling adaptations on top of upstream, **fully backwards-compatible** — an upstream wiki can pull this fork without any migration. The driving scenario is [PTM-aware degrader target nomination](../../wiki/ideas/ptm-aware-degrader-target-nomination.md): starting from the PTMI-DD review, we build a typed graph with 14 bio relations, auto-derive 22 ideas (11 validated / 2 failed) and 8 cascaded experiments, and feed the same idea graph to `/paper-plan` + `/paper-draft` to produce an ICLR 8-page paper.

**Who this fork is for**:

- Researchers working on computational drug discovery / PROTAC / structure prediction / multi-omics
- People who want a research knowledge base that remembers *"which paths have been tried and which are dead-ends"*
- Research groups automating the paper → idea → experiment → paper loop

## Updates

### Core differences from upstream

| | upstream ΩmegaWiki | bio fork |
|---|---|---|
| **Entity types** | 9 | **10** (adds `datasets/`) |
| **Edge types** | 13 (CS citations + reasoning) | **+ 14 bio relations** (binds / phosphorylates / ubiquitinates / clinical_trial_for / fda_approved_for ...) |
| **Edge metadata** | free-text `evidence` field | **+ 5 closed-set typed schemas** (runtime-validated) |
| **Paper IDs** | `arxiv` only | **+ `doi` + `pmid` + `s2_id`** three-axis |
| **Experiment setup** | model / dataset / hardware | **+ 9 bio fields** (in_silico_or_wet · species · cell_line · assay_type · force_field · solvent_model · simulation_length · weight_version · random_seed_protocol) |
| **Experiment budget** | single `estimated_hours` | **+ 6 fields** (GPU-h · CPU-h · MD wall-clock-h · wet-lab USD · FTE-weeks · data NDA wait days) |
| **Reproducibility** | git commit hash | **+ 5-ID block** (RRID · Cellosaurus · Addgene · PDB versions · dataset versions) |
| **Idea rating** | `priority` 1-5 | **+ GRADE evidence strength** (low / moderate / high) |
| **Failed ideas** | only `status: failed` | **+ `scope:` block** — failure bans only the saturated subspace, leaves other subspaces open |
| **Concept maturity** | 4 enums (stable / active / emerging / deprecated) | **+ 5 bio enums** (consensus / well-supported / contested / hypothesis / falsified) |
| **Literature search** | Semantic Scholar | **+ PubMed E-utilities** (much higher coverage for bio literature) |
| **Lint** | `tools/lint.py` | **+ `tools/lint_bio.py`** (5 bio-specific cross-checks) |
| **Domain slugs** | free text | **15 canonical slugs** (`bioinformatics` · `comp-drug-discovery` · `protein-engineering` ...) |

Full changelog: [`CHANGELOG.zh.md`](CHANGELOG.zh.md). Full design + migration: [`REPORT.zh.md`](REPORT.zh.md) / [`REPORT.en.md`](REPORT.en.md). End-to-end paper produced from the same idea graph: [`paper/main.tex`](../../paper/main.tex).

## Quick Start

**Prerequisites**: Python 3.9+, Node.js 18+, [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

```bash
# 1. Clone
git clone https://github.com/skyllwt/OmegaWiki.git
cd OmegaWiki

# 2. One-shot setup (shared with upstream)
chmod +x setup.sh && ./setup.sh          # Linux / macOS
# Windows (PowerShell):
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1

# 3. Configure .env with API keys (see .env.example)
#    SEMANTIC_SCHOLAR_API_KEY=...        (S2, optional)
#    DEEPXIV_TOKEN=...                   (semantic search, optional)
#    LLM_API_KEY=... + LLM_BASE_URL=... + LLM_MODEL=...   (cross-model review, optional)

# 4. Verify the bio fork is installed
.venv/bin/python tools/lint.py           # base: 0 🔴 / 0 🟡 / 11 🔵
.venv/bin/python tools/lint_bio.py       # bio: 0 🔴 / 0 🟡 / 0 🔵

# 5. See the 10th entity type — datasets/ (not in upstream)
cat wiki/datasets/ternarydb.md

# 6. See an experiment page with all 9 bio setup fields
cat wiki/experiments/deepternary-baseline-ternarydb-crbn-vhl-reproduction.md

# 7. Inspect a typed-metadata edge
grep dataset_version_used wiki/graph/edges.jsonl | python3 -m json.tool

# 8. Open the SPA knowledge graph (search ptm-aware-degrader-target-nomination)
.venv/bin/python tools/serve.py          # http://localhost:8765/

# 9. Run the daily-arxiv pipeline (DeepSeek ranks 9 candidate papers)
bash demo/run-demo.sh                    # requires LLM_* env vars
cat examples/output/digest.md            # see the produced digest

# 10. Start a bio workflow in Claude Code
claude
# Then type: /init bioinformatics  → start a new wiki with bio prefill
# Or:        /ingest <paper.pdf>   → auto DOI / PMID / PubMed three-axis parsing
```

`bash demo/run-demo.sh` gracefully degrades to tool-signals-only ranking if `LLM_API_KEY` is missing — the system still produces a digest. A pre-rendered output is in `examples/output/digest-sample.md` (no API call needed).

## <a id="skills-differences"></a>Skills (Differences)

Full 24-skill catalog is in the [upstream README](../../README.md#skills). This fork modifies the prompts / defaults of 5 skills; **no new skills added, none removed**:

| Skill | What the bio fork changes |
|---|---|
| `/ingest` | Adds a bio NER pre-pass: auto-extracts DOI, PubMed ID, Cellosaurus CVCL ID, PDB ID, UniProt accession from PDF / arXiv into frontmatter |
| `/ideate` | A failed idea's `scope:` block participates in ban judgment — only same-domain + same-data-regime gets blocked; cross-species / low-data / new-disease-area is let through |
| `/exp-design` | Default produces 4 statistical forms (bootstrap CI · stratified k-fold · LOO-CV · bio×tech replicates), auto-routed by `setup.in_silico_or_wet`; auto-fills 9 bio setup fields by setup type |
| `/novelty` | Adds **PubMed E-utilities** as a full-weight channel (much higher bio literature coverage than S2); for bio novelty runs, this is the primary channel |
| `/check` | Runs `tools/lint_bio.py` 5-check cross-validator on top of base lint |

`/paper-draft` also has a "result-first writing" bio-style adjustment (state results before method), but that is a prompt nudge rather than a structural difference.

## <a id="wiki-structure-differences"></a>Wiki Structure (Differences)

### New 10th entity: `datasets/`

```yaml
# wiki/datasets/ternarydb.md
---
slug: "ternarydb"
maturity: active
access: public                                # public / on_request / restricted
aliases: ["TernaryDB CRBN+VHL", "TernaryDB CRBN/VHL"]
versions:
  - version: "v1"
    released: ""
    url: ""
    n_entries: ""
    notes: "Release alongside DeepTernary (Nat. Commun. 2025)..."
canonical_url: ""
license: ""
key_papers: []                                # back-references from papers using this dataset
date_updated: 2026-05-11
---
```

Downstream experiments reference a specific dataset via `setup.dataset: [[ternarydb]]`. `tools/lint_bio.py` cross-checks `experiments.reproducibility.dataset_versions[].version` against `datasets/*.versions[].version` in both directions.

### 14 bio relation edge types

`runtime/schema/edges.yaml` registers — on top of upstream's 13 CS edges — these bio relations:

```
binds · targets_protein · degrades · phosphorylates · ubiquitinates ·
sumoylates · acetylates · methylates · glycosylates ·
wet_lab_validated · clinical_validated ·
clinical_trial_for · fda_approved_for ·
validates_in_species · dataset_version_used
```

Each edge may carry `confidence: high | medium | low` (upstream edges default to no confidence).

### 5 closed-set typed-metadata schemas

Edges can carry structured metadata, validated at load time by `runtime/loader.py::validate_edge_attributes`:

```yaml
# runtime/schema/edges.yaml (excerpt)
edges:
  dataset_version_used:
    metadata:
      version: { type: str, required: true }
      subset:  { type: str }
      accessed_date: { type: str }
  clinical_trial_for:
    metadata:
      nct_id: { type: str }
      phase: { type: enum, values: [0, 1, "1/2", 2, "2/3", 3, 4] }
      indication: { type: str }
      year: { type: int }
  fda_approved_for:
    metadata:
      indication: { type: str, required: true }
      approval_kind: { type: enum, values: [standard, accelerated, breakthrough, fast-track] }
  binds:
    metadata:
      recruitment_ligand_class: { type: str }
      clinical_anchor: { type: str }
      kd_nM: { type: float }
  validates_in_species:
    metadata:
      species: { type: str, required: true }
      source_db: { type: str }
```

Undeclared keys → lint warning (with "known keys" hint). Required key missing → error. Type mismatch → rejected. The other 9 bio edges currently accept arbitrary metadata (forward-compatibility).

### Experiment page — 3 new blocks

```yaml
# wiki/experiments/*.md frontmatter
setup:
  model: "..."
  dataset: "[[ternarydb]] CRBN+VHL test split"
  hardware: "1 × A100 80GB"
  framework: "PyTorch + DeepTernary inference repo"
  in_silico_or_wet: "in_silico"                # bio: new
  species: ["human"]                           # bio: new
  cell_line: ""                                # bio: new
  assay_type: "scoring"                        # bio: new
  force_field: ""                              # bio: new
  solvent_model: ""                            # bio: new
  simulation_length: ""                        # bio: new
  weight_version: "..."                        # bio: new
  random_seed_protocol: "ranking-shuffle (>=3 seeds)"   # bio: new

estimated_cost:                                # bio: entirely new
  gpu_hours: 4
  cpu_hours: 0
  md_wallclock_hours: 0                        # MD billed separately — 50 ns MD costs wall-clock but no GPU
  wet_lab_usd: 0
  fte_weeks: 0.25
  dataset_access_lead_time_days: 0

reproducibility:                               # bio: entirely new
  rrid: []                                     # lab resource RRID
  cellosaurus: []                              # cell line CVCL_[A-Z0-9]{4}
  addgene: []                                  # Addgene plasmid ID
  pdb_versions: []                             # structure PDB ID + release date
  dataset_versions:                            # cross-checked with datasets/*.versions[]
    - dataset_slug: ternarydb
      version: v1
      accessed_date: 2026-05-02
```

### Idea page — GRADE + scope ban

```yaml
# wiki/ideas/ptm-aware-degrader-target-nomination.md
grade: low                                     # bio: new — low / moderate / high

# wiki/ideas/ptm-site-disorder-predictor.md (status: failed)
failure_reason: "[filter] saturated by SAPP (2025), PhosAF (2024), ..."
scope:                                         # bio: new
  species: [human, mouse]                      # the saturated species
  disease_area: []
  data_regime: high_data                       # the saturated data regime
```

When `/ideate` runs, new ideas go through scope-overlap validation: `scope.species ∩ banlist.species == ∅` → let through.

### `concepts.maturity` 9-enum dual scale

```yaml
# wiki/concepts/*.md
maturity: <one of>
  # upstream CS scale
  stable / active / emerging / deprecated
  # bio scale (new)
  consensus / well-supported / contested / hypothesis / falsified
```

Each concept picks one scale; **mixing is prohibited** (lint detects). The bio cognitive-progression axis (`hypothesis → contested → well-supported → consensus`, or `→ falsified`) is orthogonal to the CS engineering-maturity axis (`emerging → active → stable → deprecated`).

### Schema files at a glance

| File | upstream | bio fork |
|---|---|---|
| `runtime/schema/entities.yaml` | 9 entity types | + `datasets:` block |
| `runtime/schema/edges.yaml` | 13 edge types | + 14 bio edges + 5 typed-metadata schemas |
| `runtime/schema/conventions.yaml` | CS conventions | + Phase/Stage disambiguation |
| `runtime/loader.py` | base validators | + `validate_edge_attributes` typed metadata |
| `tools/lint.py` | base 5 checks | unchanged |
| `tools/lint_bio.py` | _(new)_ | 5 bio cross-checks |

---

# <a id="chinese"></a>中文

## 介绍

upstream ΩmegaWiki 默认是 CS 形态——`arXiv` 是论文主 ID、单一 dataset 概念、实验记录里 `model + dataset + hardware` 三字段就够、`claims/` 是证据账本。这套形态在做 ML 论文工作流时高效；放到**生信 / 结构生物 / 药物发现**就处处别扭：DOI/PMID 比 arXiv ID 更主流、数据集要版本化、湿实验和干实验要明确区分、cellosaurus / RRID / PDB version 要可复现 trace。

本 fork 在不破坏 upstream 工作流的前提下做了 12 项 schema + skill + tooling 改造，**全部向下兼容**——upstream wiki 直接 pull 本 fork 不需要任何迁移。驱动场景是 [PTM-aware degrader target nomination](../../wiki/ideas/ptm-aware-degrader-target-nomination.md)：从 PTMI-DD 综述出发，构建带 14 类生物关系的 typed graph，自动派生 22 个 idea（11 validated / 2 failed）和 8 个 cascaded experiments，最终喂给 `/paper-plan` + `/paper-draft` 产出 ICLR 8 页论文。

**这个 fork 适合谁**：

- 在做计算药物发现 / PROTAC / 结构预测 / 多组学的科研人员
- 需要一个能记住"哪些路走过 / 哪些走不通"的研究知识库
- 想把"论文 → idea → 实验 → 论文"整个 loop 自动化的研究组

## 更新

### 跟 upstream 的核心区别

| | upstream ΩmegaWiki | bio fork |
|---|---|---|
| **实体类型** | 9 类 | **10 类**（新增 `datasets/`）|
| **边类型** | 13 类（CS 引用 + 推理关系）| **+ 14 类生物关系**（绑定 / 磷酸化 / 泛素化 / 临床试验 / FDA 批准 ...）|
| **边 metadata** | free-text `evidence` 字段 | **+ 5 类 closed-set typed schemas**（runtime 强校验）|
| **论文 ID** | `arxiv` 字段 | **+ `doi` + `pmid` + `s2_id`** 三轴 |
| **实验 setup** | model / dataset / hardware | **+ 9 bio 字段**（in_silico_or_wet · species · cell_line · assay_type · force_field · solvent_model · simulation_length · weight_version · random_seed_protocol）|
| **实验预算** | `estimated_hours` 单字段 | **+ 6 字段**（GPU-h · CPU-h · MD wall-clock-h · wet-lab USD · FTE-weeks · 数据 NDA 等待天数）|
| **实验复现** | git commit hash | **+ 5-ID 块**（RRID · Cellosaurus · Addgene · PDB versions · dataset versions）|
| **Idea 评级** | `priority` 1-5 | **+ GRADE 证据强度**（low / moderate / high）|
| **失败 idea** | 仅 `status: failed` | **+ `scope:` 块**——失败只屏蔽 saturated 子空间，其他子空间放行 |
| **概念成熟度** | 4 enum（stable / active / emerging / deprecated）| **+ 5 bio 评级**（consensus / well-supported / contested / hypothesis / falsified）|
| **文献检索** | Semantic Scholar | **+ PubMed E-utilities**（生信文献覆盖率高于 S2）|
| **Lint** | `tools/lint.py` | **+ `tools/lint_bio.py`**（5 项 bio 专用 cross-check）|
| **领域 slug** | 自由文本 | **15 个受控词表**（`bioinformatics` · `comp-drug-discovery` · `protein-engineering` ...）|

完整 changelog: [`CHANGELOG.zh.md`](CHANGELOG.zh.md)。完整设计文档与迁移表: [`REPORT.zh.md`](REPORT.zh.md) / [`REPORT.en.md`](REPORT.en.md)。同一 idea graph 端到端产出的论文: [`paper/main.tex`](../../paper/main.tex)。

## Quick Start

**前置**：Python 3.9+，Node.js 18+，Claude Code（[安装](https://docs.anthropic.com/en/docs/claude-code)）。

```bash
# 1. Clone
git clone https://github.com/skyllwt/OmegaWiki.git
cd OmegaWiki

# 2. 一键 setup（与 upstream 共用）
chmod +x setup.sh && ./setup.sh           # Linux / macOS
# Windows (PowerShell):
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1

# 3. 配 .env 加 API key（参考 .env.example）
#    SEMANTIC_SCHOLAR_API_KEY=...        (S2，可选)
#    DEEPXIV_TOKEN=...                   (semantic search，可选)
#    LLM_API_KEY=... + LLM_BASE_URL=... + LLM_MODEL=...   (cross-model review，可选)

# 4. 验证 bio fork 已装好
.venv/bin/python tools/lint.py            # base: 0 🔴 / 0 🟡 / 11 🔵
.venv/bin/python tools/lint_bio.py        # bio: 0 🔴 / 0 🟡 / 0 🔵

# 5. 看 dataset 一等公民（upstream 没这一类）
cat wiki/datasets/ternarydb.md

# 6. 看带 9 bio 字段的实验页
cat wiki/experiments/deepternary-baseline-ternarydb-crbn-vhl-reproduction.md

# 7. 看 typed metadata 实例
grep dataset_version_used wiki/graph/edges.jsonl | python3 -m json.tool

# 8. 浏览器看知识图谱（搜 ptm-aware-degrader-target-nomination 看 PTM 邻域）
.venv/bin/python tools/serve.py           # http://localhost:8765/

# 9. 跑 daily-arxiv 流水线（DeepSeek 排序 9 篇候选论文）
bash demo/run-demo.sh                     # 需 LLM_* env 已配
cat examples/output/digest.md             # 看产出 digest

# 10. 在 Claude Code 里启动 bio 工作流
claude
# 输 /init bioinformatics  → 用 bio prefill 启动新 wiki
# 或 /ingest <paper.pdf>    → 自动 DOI/PMID/PubMed 三轴解析
```

跑 `bash demo/run-demo.sh` 缺 LLM key 时会优雅退化为 tool-signals-only ranking，仍产出 digest——系统不靠 LLM 也能跑。预渲染输出在 `examples/output/digest-sample.md` 可直接 cat 看长什么样。

## Skills（区别）

完整 24 skills 见 [主 README](../../README.md#skills)。本 fork 影响以下 5 个 skill 的 prompt / 默认值，**没有新增 skill 也没有移除 skill**：

| Skill | bio fork 的改动 |
|---|---|
| `/ingest` | 增加 bio NER pre-pass：自动从 PDF / arXiv 抽取 DOI、PubMed ID、Cellosaurus CVCL ID、PDB ID、UniProt accession 填入 frontmatter |
| `/ideate` | 失败 idea 的 `scope:` 块参与 ban 判定——同领域同 data_regime 才屏蔽，跨物种 / 低数据 / 新 disease_area 放行 |
| `/exp-design` | 默认产出 4 种统计方案（bootstrap CI · stratified k-fold · LOO-CV · bio×tech replicates），按 `setup.in_silico_or_wet` 自动路由；自动按 setup 类型补 9 bio 字段 |
| `/novelty` | 新增 **PubMed E-utilities** 作为满权重通道（生信文献覆盖率远高于 S2），bio 论文跑 novelty 时主要看这个 |
| `/check` | 在 base lint 之外额外跑 `tools/lint_bio.py` 5 项 cross-check |

`/paper-draft` 也有"result-first writing"的 bio 风格调整（先抛出结果再讲方法），但这是 prompt 微调，不算结构性区别。

## Wiki Structure（区别）

### 新增第 10 类实体：`datasets/`

下游 experiment 通过 `setup.dataset: [[ternarydb]]` wikilink 引用具体 dataset。`tools/lint_bio.py` 校验 `experiments.reproducibility.dataset_versions[].version` 与 `datasets/*.versions[].version` 双向一致。完整字段结构见上面 **English § Wiki Structure (Differences)**。

### 新增 14 类生物关系边

```
binds · targets_protein · degrades · phosphorylates · ubiquitinates ·
sumoylates · acetylates · methylates · glycosylates ·
wet_lab_validated · clinical_validated ·
clinical_trial_for · fda_approved_for ·
validates_in_species · dataset_version_used
```

每条边可加 `confidence: high | medium | low`（upstream 边默认无 confidence）。

### Typed Edge Metadata（5 种 closed-set schemas）

边可携带结构化 metadata，由 `runtime/loader.py::validate_edge_attributes` 在 load 时强校验。完整 schema 见上面 **English § Wiki Structure (Differences)** 段。未声明 key → lint warning（附 "known keys" 提示），必需 key 缺失 → error，类型不匹配 → 拒绝。

### 实验 page 的 3 个新 block

- **`setup`** 加 9 bio 字段（`in_silico_or_wet` / `species` / `cell_line` / `assay_type` / `force_field` / `solvent_model` / `simulation_length` / `weight_version` / `random_seed_protocol`）
- **`estimated_cost`** 6 字段（GPU-h / CPU-h / MD wall-clock-h / wet-lab USD / FTE-weeks / 数据 NDA 等待天数）
- **`reproducibility`** 5-ID 块（RRID / Cellosaurus / Addgene / PDB versions / dataset versions）—— 与 `datasets/*.versions[]` 双向 cross-check

### Idea page 的 GRADE 评级与 scope ban

- 新增 `grade: low | moderate | high` 字段（按经典 GRADE 框架）
- 失败 idea 加 `scope: {species, disease_area, data_regime}` 块标"哪个子空间已 saturated"
- `/ideate` 跑同领域时按 scope join 决定是否屏蔽：`scope.species ∩ banlist.species == ∅` → 放行

### Concepts.maturity 9-enum 双轨制

```yaml
maturity: <one of>
  # upstream CS scale
  stable / active / emerging / deprecated
  # bio scale (new)
  consensus / well-supported / contested / hypothesis / falsified
```

每个 concept 自选 scale，**禁止混用**（lint 检测）。bio 概念的认知演进维度（`hypothesis → contested → well-supported → consensus` 或 `→ falsified`）跟 CS 概念的工程成熟度（`emerging → active → stable → deprecated`）是两套正交的轴。

---

## Acknowledgments / 致谢

upstream ΩmegaWiki is built by the [DAIR Lab](https://cuibinpku.github.io/) team at Peking University (Weitong Qian · Beicheng Xu · Zhongao Xie · Bowen Fan · Guozheng Tang · Xinzhe Wu · Jiale Chen · Mingtian Yang). The bio-adaptation fork adapts that foundation to bioinformatics scenarios.

upstream ΩmegaWiki 由北京大学 [DAIR Lab](https://cuibinpku.github.io/) 团队（Weitong Qian · Beicheng Xu · Zhongao Xie · Bowen Fan · Guozheng Tang · Xinzhe Wu · Jiale Chen · Mingtian Yang）构建。bio-adaptation fork 在其上做生信场景改造。

## License

[MIT](../../LICENSE) — same as upstream / 与 upstream 一致。
