# 生信适配会话 Checkpoint —— 2026-05-11

> 对应英文镜像：[`CHECKPOINT-2026-05-11.en.md`](CHECKPOINT-2026-05-11.en.md)。任何实质性修改必须同步两侧。
>
> 2026-05-11 会话结束时的生信适配 pilot 进度冻结快照。**尚未 commit** —— 下次对话可以继续叠加 pilot，或推进 commit-split / push。

## 1. 分支当前状态

- **分支**：`feat/qwt-ptm-degrader-ideate`
- **HEAD commit**（最后已提交的）：`acc0c47` —— `chore(gitignore): exclude .checkpoints/ (skill local state)`
- **工作树**：27 modified + 5 untracked 目录/文件。**全部未 commit。**
- **Lint**：`0 🔴 / 0 🟡 / 11 🔵`（与 baseline 同一组蓝色 informational —— 所有 pilot 全加性）
- **Push target**：仍未定（`origin/dev` 已被删除；项目规范 `branch-from-dev → PR-to-dev` 在当前现状不适用）

## 2. 本次会话合并的 13 项 pilot

| # | Pilot | 类型 | 状态 |
|---|---|---|---|
| 1 | A1 minimal | schema（新实体类型） | `datasets/` 注册 + ternarydb.md 已建 |
| 2 | A2 light | schema（新可选字段） | concepts/ 加 gene_symbol+uniprot_id+pdb_ids+species；crbn.md 已建 |
| 3 | A3 minimal | schema（新可选字段） | papers/ 加 doi+pmid；musitedeep 已填 |
| 4 | A5 slice | 内容重连 | deepternary-baseline 的 setup.dataset 已 wikilink |
| 5 | A6 | schema（新结构化块） | 全部 8 个实验页填 estimated_cost |
| 6 | A7 minimal | schema（新可选字段） | ideas/ 加 grade enum；PTM idea 填 `grade: low` |
| 7 | B1 full | 10 个新边类型 | targets_protein、binds、inhibits、activates、degrades、phosphorylates、ubiquitinates、methylates、acetylates、is_substrate_of |
| 8 | B2 minimal | 3 个新边类型 | clinical_trial_for、fda_approved_for、validates_in_species |
| 9 | B3 minimal | 1 个新边类型 | dataset_version_used |
| 10 | `add-edge --metadata` CLI | 首次 Python 代码改动 | edge JSON 序列化时支持类型化 metadata |
| 11 | C1 minimal | skill prompt | /ingest Step 2.5 生信标识符抽取（prompt 内 LLM NER） |
| 12 | C2 minimal | skill prompt | /exp-design Step 6 输出 A6 estimated_cost 块 —— 闭合 A6↔C2 环 |
| 13 | A2 light B1 后续 | live 内容 | PROTAC 药物类 binds CRBN 带类型化 metadata |

（A2 light 是一组：schema 改 + 首个 live 蛋白质概念 + B1 边 —— 算一项 pilot。）

## 3. 最终数据快照

```
entities: 10                            （datasets/ 是第 10 种，A1 minimal）
edge types: 35                          （上游基线 21 + 14 个 bio 边）
  ├── Section B 覆盖：14/14             （B1 ×10 + B2 ×3 + B3 ×1）
  └── live bio relation 边：7            （3 B1 + 1 B2 + 2 B3 + CRBN 多 1 条 B1）

graph 边：80                             （+7 条 bio relation 边）
带类型化 metadata.* 的边：3              （通过 add-edge --metadata CLI）

具体蛋白质概念页：1                      （crbn.md，A2 light）
A6 结构化 cost 覆盖：8/8 实验            （sum 96 gpu_h + 8 md_wallclock_h = 104 h）

SKILL.md 更新：24 个 skill 中 2 个        （ingest 297→327、exp-design 351→366）
runtime/schema/entities.yaml：+datasets 实体 + 5 字段集扩展（papers/concepts/ideas/experiments）+ bio-A6 estimated_cost 块
runtime/schema/edges.yaml：+14 个 bio 边类型
tools/research_wiki.py：add-edge CLI 加 --metadata flag（净增 ~10 行）

lint：0 🔴 / 0 🟡 / 11 🔵                 （13 项 pilot 后 informational 集合不变）
```

## 4. 逐节覆盖率

| Section | 状态 | 已合并 | 仍 drafted |
|---|---|---|---|
| **A — Schema 添加** | **6/8 项已合并** | A1 minimal、A2 light、A3 minimal、A5 切片、A6、A7 minimal | A4（domain 受控词表）、A8（paper_style） |
| **B — Graph 规则** | **14/14 边类型注册完成** | B1 完整、B2 minimal、B3 minimal（schema 完整；live 边密度不一） | 类型化 metadata nested-schema 验证；C1 bio NER 驱动的完整内容 |
| **C — Skill prompt** | **2/9 项已合并** | C1 minimal（`/ingest`）、C2 minimal（`/exp-design`） | C3（lint_bio.py）、C4（/ideate）、C5（/novelty）、C6（/paper-plan）、C7（/paper-draft）、C8（/rebuttal）、C9（/exp-run、/discover） |
| **Infrastructure** | 1 项 Python 改动 | `add-edge --metadata KEY=VALUE`（可重复） | `validate_edge_attributes` 的 nested-metadata schema 验证 |
| **本次会话外**（未涉及） | — | — | Section D–G（其他 skill）、Section H（子领域验证） |

## 5. 工作树清单

**已修改（27 文件）**：

```
.claude/skills/exp-design/SKILL.md       # C2 minimal
.claude/skills/ingest/SKILL.md           # C1 minimal
README.md                                 # 生信适配 hero + See-it-live（en+zh）
docs/runtime-page-templates.en.md         # A1/A2/A3/A6/A7 模板更新
docs/runtime-page-templates.zh.md         # 同（中文镜像）
i18n/en/skills/exp-design/SKILL.md        # C2 minimal 源
i18n/en/skills/ingest/SKILL.md            # C1 minimal 源
i18n/zh/skills/exp-design/SKILL.md        # C2 minimal 中文源
i18n/zh/skills/ingest/SKILL.md            # C1 minimal 中文源
runtime/schema/edges.yaml                 # +14 bio 边类型（B1+B2+B3）
runtime/schema/entities.yaml              # +datasets + concepts 蛋白锚点 + ideas.grade + papers doi/pmid + experiments.estimated_cost
tools/research_wiki.py                    # add-edge --metadata 扩展
wiki/experiments/*.md（8 文件）             # A6 estimated_cost 块
wiki/graph/context_brief.md                # 重新生成
wiki/graph/edges.jsonl                     # +7 条 bio relation 边（3 条带 metadata）
wiki/graph/open_questions.md               # 重新生成
wiki/ideas/ptm-aware-degrader-target-nomination.md   # A7 grade: low
wiki/index.md                              # datasets: 块 + crbn 概念
wiki/log.md                                # 会话 milestone（×14）
wiki/papers/musitedeep-deep-learning-based-webserver-protein.md   # A3 doi+pmid
```

**未跟踪（新增文件）**：

```
demo/run-demo.sh                          # daily-arxiv 重放
demo/sample-feed.json                     # 9 篇 mock feed
docs/bio-adaptation/                      # 整个目录
  ├── CHANGELOG.{en,zh}.md                 # 含全部 13 项 pilot 的累积 diff
  ├── DEMO_PLAN.{en,zh}.md                 # v2 用户向 plan
  ├── REPORT.{en,zh}.md                    # 完整证据
  ├── CHECKPOINT-2026-05-11.{en,zh}.md     # 本文件
  ├── preview/                              # 3 个 caption 取景材料
  └── section-{a,b,c}/                      # 原始草案
docs/bioinformatics-adaptation-backlog.{en,zh}.md   # P0/P1/P2 审计
examples/output/digest-sample.md          # 预渲染的 LLM 排序输出
runtime/templates/datasets.md.tmpl        # A1 minimal
wiki/concepts/crbn.md                     # A2 light 首个蛋白质概念
wiki/datasets/ternarydb.md                # A1 minimal 首个数据集页面
```

## 6. 推荐的 commit-split（5 commit）

这是早先 3-commit 方案的**修订版**——pilot 10–13 扩了足够多表面（Python CLI 改动、skill prompt 改动、新概念页），拆 5 commit 更清晰。全部 `git add <file>` 即可，不需 `-p` 拆 hunk。

```bash
# ============================================================
# Commit 1: 生信适配基础（backlog + 设计文档）
# ============================================================
git add docs/bioinformatics-adaptation-backlog.en.md
git add docs/bioinformatics-adaptation-backlog.zh.md
git add docs/bio-adaptation/                # 所有 CHANGELOG/REPORT/DEMO_PLAN/CHECKPOINT/section/preview
git add demo/ examples/                     # demo + 预渲染输出

# ============================================================
# Commit 2: Pilot 合并 —— schema + 内容（Section A + B）
# ============================================================
git add runtime/schema/entities.yaml         # A1、A2 light、A3、A6、A7
git add runtime/schema/edges.yaml            # B1 完整、B2 minimal、B3 minimal
git add runtime/templates/datasets.md.tmpl   # A1 minimal 模板
git add docs/runtime-page-templates.en.md docs/runtime-page-templates.zh.md
git add wiki/datasets/ wiki/concepts/crbn.md
git add wiki/experiments/                    # A6 在 8 个实验上
git add wiki/papers/musitedeep-deep-learning-based-webserver-protein.md   # A3
git add wiki/ideas/ptm-aware-degrader-target-nomination.md                 # A7
git add wiki/index.md
git add wiki/log.md
git add wiki/graph/edges.jsonl wiki/graph/context_brief.md wiki/graph/open_questions.md

# ============================================================
# Commit 3: 工具 —— add-edge --metadata CLI 扩展
# ============================================================
git add tools/research_wiki.py

# ============================================================
# Commit 4: Skill prompt —— C1 + C2 minimal
# ============================================================
git add i18n/en/skills/exp-design/SKILL.md i18n/zh/skills/exp-design/SKILL.md   # C2
git add i18n/en/skills/ingest/SKILL.md i18n/zh/skills/ingest/SKILL.md           # C1
git add .claude/skills/exp-design/SKILL.md .claude/skills/ingest/SKILL.md       # active 同步

# ============================================================
# Commit 5: README hero
# ============================================================
git add README.md
```

实际是 5 commit —— 在内容（commit 2）、工具（3）、skill prompt（4）之间区分更清晰。如果想要 4 commit 平铺，可把 3+4 合并。

## 7. 待用户决策

| 决策 | 选项 |
|---|---|
| Push target | 重建 `origin/dev`？直接 PR 到 main？维持不 push？ |
| Commit 分组 | 用上面的 5-commit 方案，还是不同边界（例如合并 infra + skill）？ |
| 录素材 | 录 `assets/demo.gif`、导出 `assets/canvas-ptm-focus.png`、截 `assets/graph-view.png`（按 DEMO_PLAN §6 storyboard，现在它在 13-pilot 状态下事实准确） |
| 继续 pilot？ | A4、C5、C7、C3（Python 工具）……见 DEMO_PLAN §7 |

## 8. 新对话恢复指令

```
读 docs/bio-adaptation/CHECKPOINT-2026-05-11.zh.md（或 .en.md）。分支
feat/qwt-ptm-degrader-ideate @ acc0c47；lint 干净（0 🔴 / 0 🟡 / 11 🔵）。

13 项生信适配 pilot 已合并在工作树，但**尚未 commit**。
5-commit-split 方案在 CHECKPOINT §6；待决事项在 §7。
逐节覆盖率在 §4 —— A 6/8 项、B 14/14 边类型、C 2/9 项。

要继续 pilot：从 §7 "继续 pilot？" 或 DEMO_PLAN §7 选。
要走 commit：执行 §6 然后决定 push target。
要录 demo 素材：DEMO_PLAN §6 storyboard 已与 13-pilot 状态一致。
```

## 9. 本次会话解锁了什么

本次会话的大部分价值在于 **schema 和 prompt 级别的能力**，而不在 graph 内容数量：

- 未来对 bio paper 跑 `/ingest` 时会自动填 `doi`/`pmid`、把 dataset 提及升级为 wikilink（C1 minimal）。
- 未来跑 `/exp-design` 时会产出 A6 兼容的 `estimated_cost` 块（C2 minimal）。
- 全部 14 个 Section B 边类型可通过 `add-edge` 立即使用 —— 在填 live 边前不需要更多 schema 工作。
- `add-edge --metadata KEY=VALUE` 让未来任何边都能携带类型化属性，无需再改 Python。
- A2 light 的 `concepts/` 蛋白锚点模式意味着接下来 49 个具体蛋白质概念页可以加入而不用改 schema。第 50 个则触发 A2 heavy `proteins/` 实体类型晋升。

原本驱动 fork 的生信研究工作流（PTM-aware degrader ideate 周期、8 个实验、11 篇论文）现在端到端用生信形状的数据结构而非 CS 形状的文本字段表达。
