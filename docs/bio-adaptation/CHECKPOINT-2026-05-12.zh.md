# 生信适配会话 Checkpoint —— 2026-05-12

> 配套英文镜像（如需创建告诉我）：`CHECKPOINT-2026-05-12.en.md`。
>
> 2026-05-12 会话结束时的生信适配 backlog 完结快照。**全部已 commit；尚未 push**。下次窗口聚焦在 demo 制作（按 [`DEMO_GUIDE.zh.md`](DEMO_GUIDE.zh.md) 截图）。

## 1. 分支当前状态

- **分支**：`feat/qwt-ptm-degrader-ideate`
- **HEAD commit**：`372f7a5` —— `feat(runtime): typed metadata nested-schema validation closes B1/B2/B3 (B-infra) — A+B+C+D backlog complete`
- **工作树**：clean（只有 1 个 untracked：`docs/bio-adaptation/DEMO_GUIDE.zh.md`，下次会话决定何时 commit）
- **Ahead of main**：25 commits（10 pre-session + 15 this session）
- **Push target**：仍未定（`origin/dev` 已被删；项目规范 `branch-from-dev → PR-to-dev` 当前不适用）
- **Lint**：`0 🔴 / 0 🟡 / 11 🔵`（base）+ `0 🔴 / 0 🟡 / 0 🔵`（bio）

## 2. 本次会话的 15 个 commit

前 5 个是把 2026-05-11 会话遗留工作树（13 项 pilot）按 CHECKPOINT-2026-05-11 §6 5-commit-split 方案切分入库：

```
28424b4 docs(bio-adaptation): add backlog audit + 13-pilot design package
5e5df95 feat(bio): land Section A schema + Section B graph rules with live content
a3a2751 feat(tools): add-edge accepts --metadata KEY=VALUE for typed edge attributes
8813158 feat(skills): bio-aware prompts in /ingest and /exp-design (C1+C2 minimal)
bfe752c docs(readme): bio-adaptation hero + See-it-live section
```

后 10 个是本次会话**新合并**的 13 项 pilot：

```
3ffedfd feat(bio): close out P0 backlog — A5 full + C4 + C5 around /exp-design   ← 3 pilots
8e1fb46 feat(skills): /novelty gains PubMed E-utilities channel (C9 minimal)
328549e feat(skills): /exp-design statistical defaults rebuilt around bio regimes (C6 minimal)
2468980 feat(tools): tools/lint_bio.py adds 5 bio-specific lint checks (C8)
05e1b8b feat(skills): /ideate banlist gains scope-overlap matching (C3 minimal)
507f82f feat(skills): /exp-run routes 4 directory layouts by setup type (C7 minimal) — Section C 9/9 complete
e739608 feat(bio): experiments.reproducibility block + lint cross-check loop (A8) — Section A 8/8 complete
16fce00 feat(bio): domain controlled vocabulary + 24-page migration to canonical slugs (A4)
e64ed0c feat(bio): Section D conventions resolved — Phase/Stage disambiguation (D1) + maturity bio scale (D2)   ← 2 pilots
372f7a5 feat(runtime): typed metadata nested-schema validation closes B1/B2/B3 (B-infra) — A+B+C+D backlog complete
```

| Pilot | 类型 | commit | 关键改动 |
|---|---|---|---|
| A5 full | schema | `3ffedfd` | `experiments.setup` 加 9 个 bio 字段（in_silico_or_wet/species/cell_line/assay_type/force_field/solvent_model/simulation_length/weight_version/random_seed_protocol）+ 8 实验回填 |
| C4 minimal | skill prompt | `3ffedfd` | `/exp-design` 加 4 类 bio 块（negative_control/mechanism/dose_response/cross_context） |
| C5 minimal | skill prompt | `3ffedfd` | `/exp-design` Step 1 加湿实验依赖探测（14 个信号词） |
| C9 minimal | skill prompt | `8e1fb46` | `/novelty` Source E 加 PubMed E-utilities（bio claim 满权重） |
| C6 minimal | skill prompt | `328549e` | `/exp-design` 统计默认值 4 形态表（bootstrap CI / stratified k-fold / LOO-CV / bio×tech replicates） |
| C8 | Python 新工具 | `2468980` | `tools/lint_bio.py`（5 项 bio 检查）+ `/check` 调用 |
| C3 minimal | schema + skill prompt | `05e1b8b` | ideas/ 加 `scope` 字段（species/disease_area/data_regime）+ `/ideate` banlist scope-overlap |
| C7 minimal | skill prompt | `507f82f` | `/exp-run` 按 setup type 路由 4 布局（ML / MD / Docking / Wet-lab） |
| A8 | schema + Python | `e739608` | `experiments.reproducibility` 块（rrid/cellosaurus/addgene/pdb_versions/dataset_versions）+ lint_bio 闭合 dataset_version 双源 cross-check |
| A4 | schema soft check + 内容迁移 | `16fce00` | lint_bio `RECOGNISED_DOMAINS` 15-slug 集 + 24 页面规范化（9 free-text 变体 → 7 canonical slug） |
| D1 minimal | skill prompt | `e64ed0c` | `/exp-design` Step 4 加 "Vocabulary disambiguation"（Stage 0..4 vs bio Phase 0-3） |
| D2 minimal | schema | `e64ed0c` | `concepts.maturity` enum 4→9（加 consensus/well-supported/contested/hypothesis/falsified） |
| B-infra | schema + Python | `372f7a5` | 5 个边类型加 metadata schema + loader.py 验证（closed-set + required + type checks）+ 1 legacy edge 迁移 |

## 3. 最终数据快照

```
entities (kinds): 10                       （含 datasets/ 作为第 10 类，2026-05-11 加入）
edge types:      34                        （base 21 + bio 14 + cites）
edges with typed metadata schema declared: 5  （dataset_version_used / binds /
                                              clinical_trial_for / fda_approved_for /
                                              validates_in_species）

wiki/ 内容：
  papers:        11
  concepts:      25
  topics:         1
  people:        16
  ideas:         22 （11 validated / 2 failed / 9 in 其他状态）
  experiments:    8
  methods:        0
  summaries:      1
  graph edges:   80
  citations:      1

live bio relation edges: 7（3 B1 targets_protein/ubiquitinates/binds + 1 B2
                           validates_in_species + 2 B3 dataset_version_used + 1 额外 B1 binds）
edges with typed metadata.*: 4   （升自 3 —— B-infra 迁移加了 1 条）

lint：0 🔴 / 0 🟡 / 11 🔵  （base —— informational 集合与 acc0c47 时一致）
bio lint：0 🔴 / 0 🟡 / 0 🔵  （A4 域名迁移后从 9 🔵 降到 0）
```

## 4. 逐节覆盖率

| Section | 状态 | 已合并 | 仅剩"延后"项 |
|---|---|---|---|
| **A** Schema | **8/8 + A4 ✓ 完结** | A1 / A2 light / A3 minimal / A4(全量) / A5 full / A6 / A7 minimal / A8 | per-edge GRADE attribute（A7 full）/ proteins/ 实体（A2 heavy，触发条件 ≥50 蛋白概念页） |
| **B** Graph 规则 | **14/14 边类型 + infra ✓ 完结** | B1×10 / B2×3 / B3×1 / B-infra typed metadata 验证 | 更多 live 边（等 C1 bio NER full 系统化抽取） |
| **C** Skill 工作流 | **9/9 ✓ 完结** | C1 / C2 / C3 / C4 / C5 / C6 / C7 / C8 / C9 全部 minimal 或 full | 各 minimal 的 full 版本（PubMed/EuropePMC fetcher Python 工具、wet-lab cost ref DB、`/exp-run` 模板文件树等） |
| **D** 约定 | **2/2 minimal ✓ 完结** | D1 disambiguation note / D2 maturity bio scale | rename Stage→Block-X 全 wiki 迁移（D1 full）/ lint 检测 maturity scale 混用（D2 full） |
| **E** narrative | n/a（非可执行 backlog） | — | E1-E3 是模型自省反思，部分通过 A3/A6/A7/C6/C8 schema 改动隐式缓解 |
| **F** 实验可行性审计 | n/a（纯 docs） | — | 内容已在 `REPORT.{en,zh}.md` |

**bio-adaptation 实质完结**。Section A + B + C + D 每个可执行 backlog 子项都已 merge（minimal 或 full）。

## 5. Demo 制作 —— 下个会话的主要任务

详见 [`DEMO_GUIDE.zh.md`](DEMO_GUIDE.zh.md)（274 行，本次会话末尾创建，untracked）。

**核心交付物**：8 张静态 PNG 放入 `assets/demo-*.png`：

```
01 papers/musitedeep-...                  (frontmatter: A3 + A4)
02 ideas/ptm-aware-degrader-target-...    (main idea: A7 grade + linked_experiments)
03 ideas/ptm-site-disorder-predictor      (failed idea: C3 banlist scope)
04 experiments/deepternary-baseline-...   (setup + cost + reproducibility)
05 datasets/ternarydb                     (A1 versions list)
06 SPA 全图                                (B1/B2/B3 live edges)
07 SPA 边 tooltip                          (B-infra typed metadata)
08 终端 bash demo/run-demo.sh             (digest 输出)
[09 Obsidian canvas]                      (可选)
```

**Pre-flight**（已就绪，无需重做）：
- `tools/serve.py` 启动 SPA 即可
- `demo/run-demo.sh` 验证过可跑
- `demo/sample-feed.json` 在位
- `examples/output/digest-sample.md` 在位

**用户负责**：截图 + ShareX 标注 + pngquant 压缩 + commit。

**Claude 可帮**：截图完成后改 README 加 "Demo" 段引用这些图。

## 6. 待用户决策

| 决策 | 选项 |
|---|---|
| Push target | 重建 `origin/dev`？直 PR 到 main（违 memory 规则，需 explicit 例外）？维持不 push？ |
| DEMO_GUIDE 何时 commit | 现在 commit + 之后 8 张图另一次 commit？还是图都拍完 9 张一起 commit？ |
| CHECKPOINT / DEMO_GUIDE en 镜像 | 现在建？还是延后？（memory 规则 paired bilingual docs 应同步，但 demo 是临时操作文档，不一定双语必要） |

## 7. 新对话恢复指令

```
读 docs/bio-adaptation/CHECKPOINT-2026-05-12.zh.md 与
docs/bio-adaptation/DEMO_GUIDE.zh.md。分支
feat/qwt-ptm-degrader-ideate @ 372f7a5；lint clean（0/0/11 + 0/0/0）。
bio-adaptation backlog A+B+C+D 全部完结；25 commit ahead of main；0 push。
工作树仅 1 个 untracked：DEMO_GUIDE.zh.md。

本会话目标：按 DEMO_GUIDE.zh.md 截 8 张静态 PNG 放入 assets/demo-*.png：
  01-08 见 DEMO_GUIDE §1 清单 + §3 逐图操作。

需要 Claude 做的：
  - 启动 SPA：.venv/bin/python tools/serve.py（用户本地执行也可）
  - 可选：跑 /visualize --canvas --focus ideas/ptm-aware-degrader-target-nomination --depth 2
  - 截图完成后改 README 加 Demo 段引用 assets/demo-*.png
  - commit demo 资产 + CHECKPOINT + DEMO_GUIDE

需要用户做的：
  - 在 Windows 主机用 Snipping Tool 或 ShareX 截图（DEMO_GUIDE §3 逐图操作）
  - pngquant 压缩
  - 决定 push target

待决事项见 CHECKPOINT §6。
```

## 8. 文件清单速查

| 类别 | 路径 |
|---|---|
| 本次新 doc | `docs/bio-adaptation/DEMO_GUIDE.zh.md`（**untracked**） |
| 本 checkpoint | `docs/bio-adaptation/CHECKPOINT-2026-05-12.zh.md`（**untracked**） |
| 上次 checkpoint | `docs/bio-adaptation/CHECKPOINT-2026-05-11.zh.md` |
| 历史 plan | `docs/bio-adaptation/DEMO_PLAN.zh.md`（v2 storyboard，本指南是其静态图替代） |
| 累计 changelog | `docs/bio-adaptation/CHANGELOG.zh.md`（39 个 pilot entries） |
| 整体 report | `docs/bio-adaptation/REPORT.zh.md` |
| backlog 原档 | `docs/bioinformatics-adaptation-backlog.zh.md`（A1-A8 / B1-B3 / C1-C9 / D1-D2 + E/F/H narrative） |
| demo 脚本 | `demo/run-demo.sh` + `demo/sample-feed.json` |
| demo 预渲染输出 | `examples/output/digest-sample.md` |
| Python 工具 | `tools/lint_bio.py`（本会话新建）+ `tools/lint.py` + `tools/research_wiki.py` + `tools/serve.py` |
