# 运行时页面模板（生信适配，A 节）

> **镜像副本。** 真值源：`docs/runtime-page-templates.zh.md`。本文件应用 `docs/bioinformatics-adaptation-backlog.zh.md` 的 A1–A8。
> 逐条改动详见 `docs/bio-adaptation/CHANGELOG.zh.md`。当某条 A 项从"草拟"提升到"采纳"时，把对应 hunk 合回真值源并删除（或缩减）镜像。

> 仅按需读取的 wiki 页面模板。graph 派生文件以及 `index.md`、`log.md` 请看 `docs/runtime-support-files.zh.md`。

<!-- bio-A1: 页面类型从 9 类增长到 10 类 —— `datasets/` 升为首位实体。 -->
## 10 类页面

`papers`、`concepts`、`topics`、`people`、`ideas`、`experiments`、`claims`、`Summary`、`foundations`、`datasets` <!-- bio-A1 -->。

### papers/{slug}.md

```yaml
---
title: ""
slug: ""
arxiv: ""                    # 保留 —— 部分 bio paper 也走 bioRxiv → arXiv
# bio-A3: bio paper 多无 arXiv ID，下列字段是 bio 主标识符。
# /ingest 应从 CrossRef / PubMed E-utilities / EuropePMC 填充，不仅依赖 Semantic Scholar。
doi: ""                      # bio-A3: bio 主标识符
pmid: ""                     # bio-A3: PubMed ID
biorxiv: ""                  # bio-A3: bioRxiv DOI 后缀
pdb_ids: []                  # bio-A3: paper 引入的结构
uniprot_ids: []              # bio-A3: paper 表征的蛋白
nct_ids: []                  # bio-A3: 提及的临床试验
gene_symbols: []             # bio-A3: HGNC 符号
species: []                  # bio-A3: 模式生物
venue: ""
year:
tags: []
importance: 3                # 1-5
date_added: YYYY-MM-DD
source_type: tex             # tex | pdf
s2_id: ""
keywords: []
# bio-A4: domain 字段约定半受控。CS 取值：NLP / CV / ML Systems / Robotics。
#         Bio 推荐受控词表（lint 对未在表的值发 warning，详见 C8）：
#         structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio |
#         bioinformatics | clinical-translation
domain: ""
code_url: ""
cited_by: []
---
```

正文：`## Problem` / `## Key idea` / `## Method` / `## Results` / `## Limitations` / `## Open questions` / `## My take` / `## Related`

### concepts/{concept-name}.md

```yaml
---
title: ""
aliases: []
tags: []
# bio-A2 (轻量): maturity 可选用 bio 等级 (consensus | well-supported | contested |
#                hypothesis | falsified)，详见 D2；本节默认沿用 CS 等级，两者皆可。
maturity: active             # stable | active | emerging | deprecated
key_papers: []
first_introduced: ""
date_updated: YYYY-MM-DD
related_concepts: []
# bio-A2 (轻量): 蛋白锚定可选字段。仅当 concept 本身就是某个具体基因产物（p53、CRBN、…）
# 时填写。当此类 concept 累积 ≥ 50 条或 graph 查询有需要时，再升级为独立 `proteins/`
# 实体类型（A2 的重型方案）。
gene_symbol: ""              # bio-A2: HGNC 符号，例如 "TP53"
uniprot_id: ""               # bio-A2: 例如 "P04637"
pdb_ids: []                  # bio-A2: 代表性结构
species: []                  # bio-A2: 例如 ["human", "mouse"]
---
```

正文：`## Definition` / `## Intuition` / `## Formal notation` / `## Variants` / `## Comparison` / `## When to use` / `## Known limitations` / `## Open problems` / `## Key papers` / `## My understanding`

### topics/{topic-name}.md

```yaml
---
title: ""
tags: []
my_involvement: none         # none | reading | side-project | main-focus
sota_updated: YYYY-MM-DD
key_venues: []
related_topics: []
key_people: []
---
```

正文：`## Overview` / `## Timeline` / `## Seminal works` / `## SOTA tracker` / `## Open problems` / `## My position` / `## Research gaps` / `## Key people`

### people/{firstname-lastname}.md

```yaml
---
name: ""
affiliation: ""
tags: []
homepage: ""
scholar: ""
date_updated: YYYY-MM-DD
---
```

正文：`## Research areas` / `## Key papers` / `## Recent work` / `## Collaborators` / `## My notes`

### Summary/{area-name}.md

```yaml
---
title: ""
scope: ""
key_topics: []
paper_count:
date_updated: YYYY-MM-DD
---
```

正文：`## Overview` / `## Core areas` / `## Evolution` / `## Current frontiers` / `## Key references` / `## Related`

### foundations/{slug}.md

```yaml
---
title: ""
slug: ""
domain: ""
status: mainstream           # mainstream | historical
aliases: []
first_introduced: ""
date_updated: YYYY-MM-DD
source_url: ""
---
```

正文：`## Definition` / `## Intuition` / `## Formal notation` / `## Key variants` / `## Known limitations` / `## Open problems` / `## Relevance to active research`

Foundations **没有外向链接字段**。其他页面可链接到 foundation；foundation 不写反向链接。

### ideas/{idea-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed             # proposed | in_progress | tested | validated | failed
origin: ""
origin_gaps: []
tags: []
domain: ""                   # bio-A4: 与 papers/ 同一受控词表
priority: 3                  # 1-5
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: YYYY-MM-DD
date_resolved: ""
---
```

正文：`## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

### experiments/{experiment-slug}.md

```yaml
---
title: ""
slug: ""
status: planned              # planned | running | completed | abandoned
target_claim: ""
hypothesis: ""
tags: []
domain: ""                   # bio-A4: 与 papers/ 同一受控词表
# bio-A5: setup 从纯 ML 流水线形状扩到覆盖 bio 细节。
# 所有 bio-* 字段为可选，skill 仅在适用时填入。
setup:
  model: ""
  dataset: ""                # A1 落地后应是 datasets/{slug} 的 wikilink
  hardware: ""
  framework: ""
  # ── bio-A5: 实验形态 ──
  in_silico_or_wet: in_silico   # in_silico | wet_lab | mixed
  species: []                   # human | mouse | yeast | …
  cell_line: ""                 # 优先 Cellosaurus ID（CVCL_xxxx）
  assay_type: ""                # Y2H | AP-MS | cryo-EM | NMR | MD | docking | scoring
  # ── bio-A5: 仅 MD ──
  force_field: ""               # 例如 AMBER ff14SB + phosaa14SB
  solvent_model: ""             # explicit | implicit | vacuum
  simulation_length: ""         # 例如 "50 ns"
  # ── bio-A5: ML 模型版本 ──
  weight_version: ""            # 例如 "Boltz-2 Jan-2026 weights"
  random_seed_protocol: ""      # ranking-shuffle | bootstrap | LOO-CV
metrics: []
baseline: ""
outcome: ""                  # succeeded | failed | inconclusive
key_result: ""
linked_idea: ""
date_planned: YYYY-MM-DD
date_completed: ""
run_log: ""
started: ""
# bio-A6: estimated_hours 已 DEPRECATED —— 对 MD / 湿实验 / 多模态成本太粗。
#         为旧实验页向后兼容暂时保留，待逐页迁移。
estimated_hours: 0           # 已废弃，见下方 estimated_cost
# bio-A6: 结构化成本块。所有子字段可选，skill 按情况填入。
#         工具配套：`docs/bio-compute-references.md` 维护按 assay / 体系大小的参照表，
#         供 /exp-design 直接读取，避免凭空估算。
estimated_cost:
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0      # MD 经常是瓶颈，单独跟踪
  wet_lab_usd: 0             # 抗体、细胞培养、测序
  fte_weeks: 0               # 不可自动化的 postdoc / RA 时间
  dataset_access_lead_time_days: 0   # 注册、MTA、IRB
# bio-A8: 触及任何湿实验数据的实验（含下游消费 —— 例如来自已发表 assay 的
#         phospho-PROTAC 阳性集）补可选可复现性元数据；纯 in-silico 可省略。
reproducibility:
  rrid: []                   # 抗体 / 试剂 RRID
  cellosaurus: []            # 细胞系（CVCL_xxxx）
  addgene: []                # 质粒 ID
  pdb_versions: []           # 具体 PDB 条目 + 版本
  dataset_versions: []       # 列表 {dataset_slug, version, accessed_date}
remote:
  server: ""
  gpu: ""
  session: ""
  started: ""
  completed: ""
---
```

正文：`## Objective` / `## Setup` / `## Procedure` / `## Results` / `## Analysis` / `## Claim updates` / `## Follow-up`

### claims/{claim-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed             # proposed | weakly_supported | supported | challenged | deprecated
confidence: 0.5              # 0.0-1.0
tags: []
domain: ""                   # bio-A4: 同一受控词表
source_papers: []
# bio-A7: evidence type 枚举针对 bio 扩充；`strength` 原样保留以向后兼容；
# 新增可选 `grade` 记录 GRADE 风格证据等级（very-low | low | moderate | high）。
# 机制 > 相关；clinical_validated > wet_lab_validated > mechanistic_basis；
# `predicts` 标记尚未验证的前瞻性计算预测。
evidence:
  - source: ""
    type: supports           # supports | contradicts | tested_by | invalidates |
                             # wet_lab_validated | clinical_validated | mechanistic_basis |
                             # correlative | predicts
    strength: moderate       # weak | moderate | strong（向后兼容保留）
    grade: ""                # bio-A7: 可选 GRADE —— very-low | low | moderate | high
    detail: ""
conditions: ""
date_proposed: YYYY-MM-DD
date_updated: YYYY-MM-DD
---
```

正文：`## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`

<!-- bio-A1: 下方为新增实体类型。Dataset 升为首位类，使数据集引用可被 wikilink、版本可追踪、
     access 等级可上浮给 /exp-design 与 /exp-run。 -->
### datasets/{slug}.md

```yaml
---
title: ""
slug: ""
aliases: []
tags: []
maturity: stable             # stable | active | emerging | deprecated
access: public               # public | registration | restricted | wet-lab-derived
# `versions` 是发布记录列表；下游 skill 用它与
# `experiments[*].reproducibility.dataset_versions[*].version` 对比检测漂移。
versions: []                 # 列表 {version, released, url, n_entries, notes}
canonical_url: ""
license: ""
key_papers: []               # 反向链 —— 由引用本数据集的 papers/ 填入
key_concepts: []
date_updated: YYYY-MM-DD
---
```

正文：`## Overview` / `## Versions` / `## Access and licensing` / `## Schema and entries` / `## Known caveats` / `## Used by experiments` / `## Key papers`
