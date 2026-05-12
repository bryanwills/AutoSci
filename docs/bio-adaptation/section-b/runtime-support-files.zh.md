# 运行时辅助文件（生信适配，B 节）

> **镜像副本。** 真值源：`docs/runtime-support-files.zh.md`。本文件应用 `docs/bioinformatics-adaptation-backlog.zh.md` 的 B1–B3。
> 逐条改动详见 `docs/bio-adaptation/CHANGELOG.zh.md`。

> 按需读取的 graph 派生文件，以及非页面型运行时文件 `index.md` 与 `log.md`。

## Graph 文件

| 文件 | 内容 | 生成命令 |
|------|------|----------|
| `edges.jsonl` | 语义关系：paper-paper、paper-concept、claim/experiment/idea/provenance、bio 关系、验证/转化、数据集版本来源 edge <!-- bio-B1/B2/B3 --> | `python3 tools/research_wiki.py add-edge` |
| `citations.jsonl` | bibliographic paper citation（`type: cites`） | `python3 tools/research_wiki.py add-citation` |
| `context_brief.md` | 压缩上下文：claims + gaps + failed ideas + papers + edges（≤8000字符） | `python3 tools/research_wiki.py rebuild-context-brief` |
| `open_questions.md` | 开放问题：under-supported claims + open questions from papers/topics | `python3 tools/research_wiki.py rebuild-open-questions` |

<!-- bio-B1/B2/B3: edge JSON 增加可选嵌套 `metadata` 对象，承载按 edge type 区分的属性
     （如 `nct_id`、`phase`、`indication`、`year`、`species`、`version`）。顶层字段不变，
     旧的 edge 读取器照常工作；不识别 `metadata` 的消费者忽略即可。 -->

semantic edge 格式（基础）：

```json
{"from": "node_id", "to": "node_id", "type": "edge_type",
 "evidence": "...", "confidence": "high|medium|low", "date": "..."}
```

Bio 扩展 —— 带可选每 edge metadata 的 semantic edge 格式：

```json
{"from": "node_id", "to": "node_id", "type": "edge_type",
 "evidence": "...", "confidence": "high|medium|low", "date": "...",
 "metadata": { "<按 edge type 决定的键>": "<值>" }}
```

citation 格式：`{"from": "papers/citing", "to": "papers/cited", "type": "cites", "source": "semantic_scholar|parsed_bib|manual", "date": "..."}`

<!-- bio-B1/B2/B3: 按 edge type 列 schema。工具应据此校验 `metadata` 键。 -->
### Edge 类型清单

每行列出允许的端点类型、必填的 `metadata` 键（若有）、一行语义。
**所有非 citation 类 edge 都要求 `confidence: high|medium|low`。**

| Edge 类型 | 端点 | 必填 `metadata` | 语义 |
|-----------|------|-----------------|------|
| _paper-paper（已有）_ | | | |
| `same_problem_as` | paper ↔ paper（对称） | — | 解决同一任务 |
| `similar_method_to` | paper ↔ paper（对称） | — | 方法机理相近 |
| `complementary_to` | paper ↔ paper（对称） | — | 贡献可组合 |
| `builds_on` | paper → paper | — | 在前作之上扩展 |
| `compares_against` | paper → paper | — | 报告头对头比较 |
| `improves_on` | paper → paper | — | 在共同度量上超越 |
| `challenges` | paper → paper | — | 反驳前作声明 |
| `surveys` | paper → paper | — | 综述 |
| _paper-concept（已有）_ | | | |
| `introduces_concept` | paper → concept | — | 首次形式化定义 |
| `uses_concept` | paper → concept | — | 应用而非重新定义 |
| `extends_concept` | paper → concept | — | 加变体 / 推广 |
| `critiques_concept` | paper → concept | — | 反对 |
| _claim / experiment / provenance（已有）_ | | | |
| `supports`、`contradicts` | paper / experiment → claim | — | 证据方向 |
| `tested_by` | claim → experiment | — | 证据来源 |
| `invalidates` | experiment → claim | — | 证伪记录 |
| `addresses_gap` | idea / experiment → claim | — | 针对开放问题 |
| `derived_from`、`inspired_by` | idea → idea / paper | — | ideation 来源 |
| <!-- bio-B1 --> _bio 关系（新增）_ | | | |
| `targets_protein` | paper / claim / concept → concept（基因产物） | — | 药物或修饰对此蛋白起作用 |
| `binds` | concept → concept（蛋白-蛋白、配体-蛋白） | — | 直接物理相互作用 |
| `inhibits`、`activates`、`degrades` | paper / claim → concept（蛋白） | — | 功能扰动方向 |
| `phosphorylates`、`ubiquitinates`、`methylates`、`acetylates` | concept（酶）→ concept（底物） | — | PTM 动词；酶作用于底物 |
| `is_substrate_of` | concept（底物）→ concept（酶） | — | 上述四个 PTM 动词的反向 |
| <!-- bio-B2 --> _验证 / 转化（新增）_ | | | |
| `clinical_trial_for` | claim / paper → concept（drug-or-modality） | `nct_id`、`phase` | 注册中的临床试验 |
| `fda_approved_for` | concept（drug）→ concept（indication） | `indication`、`year` | 监管批准记录 |
| `validates_in_species` | claim / experiment → concept（或物种 wikilink） | `species` | 在该生物体中确认 |
| <!-- bio-B3 --> _数据集版本 provenance（新增）_ | | | |
| `dataset_version_used` | experiment → dataset | `version`（如 `slug` 与 `to` 节点 id 不同则附带） | 钉住实验所用数据集快照 |

**工具配套**：`tools/research_wiki.py add-edge` 应支持重复的 `--metadata key=value`；不带 metadata 的 edge 保留现有 CLI 形态。`add-edge` 应按 edge type 拒绝未知 `metadata` 键。

## index.md 格式

```yaml
papers:
  - slug: lora-low-rank-adaptation
concepts:
  - slug: parameter-efficient-fine-tuning
topics:
  - slug: efficient-llm-adaptation
people:
  - slug: tri-dao
ideas:
  - slug: sparse-lora-for-edge-devices
experiments:
  - slug: sparse-lora-latency-benchmark
claims:
  - slug: lora-preserves-quality-at-low-rank
```

## log.md 格式

```markdown
## [2026-04-07] ingest | added papers/lora-low-rank-adaptation | updated: concepts/parameter-efficient-fine-tuning
## [2026-04-07] lint | report: 0 🔴, 2 🟡, 1 🔵
## [2026-04-08] daily-arxiv | 3 papers ingested from RSS
```
