---
description: 实验执行全流程：准备代码 → 部署运行 → 监控状态 → 收集结果，支持三种运行模式；setup-type 检测路由到 ML / MD / wet-lab / docking / workflow-manager 的目录模板
argument-hint: <experiment-slug> [--review] [--collect] [--full] [--env local|remote] [--setup-type {auto|ml|md|wet-lab|docking|snakemake|nextflow}]
---

<!-- bio-C7: 镜像自 i18n/zh/skills/exp-run/SKILL.md，加入 C7（按 setup-type 分目录模板）草稿。
     真值源：i18n/zh/skills/exp-run/SKILL.md。本路径不参与运行；要测试请先合回真值源。
     跨节依赖：
       A5 —— experiments[*].setup.assay_type / in_silico_or_wet / force_field 驱动 setup-type 自动检测器。
       A6 —— estimated_cost.md_wallclock_hours / wet_lab_usd 在 DEPLOY_REPORT 中替代非 ML 类型的 estimated_hours 显示。
       C4 —— experiment.type {negative_control, mechanism, dose_response, cross_context} 对应 Phase-1 流程的微调。
       C6 —— statistical_protocol 驱动 Phase 4 的结果聚合（replicate_matrix_BxT 折成 mean±SEM 跨 biological reps，而非 seeds）。
     按类型模板（计划中）位于：
       skills/exp-run/references/templates/{ml,md,wet-lab,docking,snakemake,nextflow}/
     模板尚未编写 —— 作为后续工具落地。模板落地之前，自动检测器仍能挑出类型并写出占位 layout，
     bio 专属部分由用户填。 -->

# /exp-run

> 执行 wiki/experiments/ 中已规划的实验。
> **三种运行模式**，适应不同场景：
> - **默认（deploy）**：仅 Phase 1-2，部署后立即返回，适合需要数小时/天的实验。
> - **`--collect`**：仅 Phase 3-4，检查已部署实验是否完成，完成则收集结果（`--check` 为 alias）。
> - **`--full`**：完整 Phase 1-4，适合几分钟内即可完成的本地快速实验。
>
> <!-- bio-C7 --> **Setup-type 路由**：Phase 1 中按 `setup` frontmatter（`assay_type`、`in_silico_or_wet`、`framework`、`force_field`）检测实验是 ML / MD / wet-lab / docking / Snakemake / Nextflow 形态，并写出对应的 `references/templates/{type}/` 目录模板。无 bio 字段时回退到旧的 `train.py + config.yaml + run.sh + requirements.txt` ML layout。
>
> 推荐流程：`/exp-run <slug>` 部署 → `/exp-status` 监控 → `/exp-run <slug> --collect` 收集。

## Inputs

- `experiment`：wiki/experiments/ 中的 slug
  - deploy 模式：status 必须为 `planned`
  - --collect 模式：status 必须为 `running`
  - --full 模式：status 必须为 `planned`
- `--review`（可选）：Phase 1 中启用 Review LLM code review 审查实验代码（deploy / full 模式有效）
- `--collect`（可选）：collect 模式——检查实验是否完成，完成则收集结果；`--check` 是 alias
- `--full`（可选）：完整模式——执行全部 4 个 Phase（适合快速本地实验）
- `--env local|remote`（可选，默认 `local`）：部署环境
  - `local`：本机 GPU 直接运行
  - `remote`：通过 SSH 部署到远程机器（需 `config/server.yaml`）
- <!-- bio-C7 --> `--setup-type {auto|ml|md|wet-lab|docking|snakemake|nextflow}`（可选，默认 `auto`）：强制选择目录模板。`auto` 从 `setup` frontmatter 推断（见 Phase 1 步骤 3 的检测规则）。仅在自动检测器选错时才用此 flag —— 更好的修法通常是补齐缺失的 `setup` 字段。

## Outputs

- **deploy 模式**：
  - 实验代码：`experiments/code/{slug}/`（Phase 1 生成）—— 目录形状取决于检测到的 setup type   <!-- bio-C7 -->
  - `wiki/experiments/{slug}.md` — status: planned → running
  - **DEPLOY_REPORT**（输出到终端）— 部署确认、session 信息、下一步指引，<!-- bio-C7 --> 检测到的 setup-type 与模板路径
  - `wiki/log.md` — 追加部署日志
- **collect 模式**（实验已完成时）：
  - `wiki/experiments/{slug}.md` — status: running → completed，填充 outcome/key_result/date_completed
  - **RUN_REPORT**（输出到终端）— 结果摘要、metrics 对比、下一步建议
  - `wiki/log.md` — 追加收集日志
- **collect 模式**（实验仍在运行时）：
  - 仅输出进度报告到终端，不修改 wiki
- **full 模式**：同 deploy + collect 的全部输出

## Wiki Interaction

### Reads
- `wiki/experiments/{slug}.md` — 实验配置：setup、metrics、baseline、hypothesis、target_claim，<!-- bio-C7 --> setup-type 检测器输入（`assay_type`、`in_silico_or_wet`、`force_field`、`solvent_model`、`framework`）
- `wiki/claims/{target-claim}.md` — 目标 claim 的上下文（理解实验目的）
- `wiki/ideas/{linked-idea}.md` — 关联 idea 的 approach sketch（指导代码实现）
- `wiki/papers/*.md` — 相关论文的方法细节和超参数（参考实现）
- `wiki/experiments/*.md` — 同一 claim 的其他实验（参考 setup、避免重复错误）
- <!-- bio-C7（依赖 A1）--> `wiki/datasets/*.md` — dataset 访问层级与版本信息（驱动 wet-lab block 的 lead-time 与 MD block 的输入版本固定）

### Writes
- `experiments/code/{slug}/` — 实验代码目录（Phase 1 生成，deploy / full 模式）；形状取决于检测到的 setup type   <!-- bio-C7 -->
  - **ml**（旧默认）：`train.py`、`config.yaml`、`run.sh`、`requirements.txt`
  - <!-- bio-C7 --> **md**：`mdrun.sh`、`system.gro`/`system.pdb`（输入结构）、`system.top`（topology）、`mdp/em.mdp` + `mdp/nvt.mdp` + `mdp/npt.mdp` + `mdp/prod.mdp`（各阶段 config）、`analysis.ipynb`、`requirements.txt`
  - <!-- bio-C7 --> **wet-lab**：`protocol.md`（实验员可读）、`materials.csv`（RRID / Cellosaurus / Addgene ID / 货号）、`analysis.ipynb`（针对结果 CSV）、`data/raw/`（占位）、`data/processed/`（占位）、`requirements.txt`
  - <!-- bio-C7 --> **docking**：`dock.sh`、`receptor.pdbqt`、`ligand_library.smi`、`box.txt`（搜索盒定义）、`scoring.yaml`、`analysis.ipynb`、`requirements.txt`
  - <!-- bio-C7 --> **snakemake**：`Snakefile`、`config.yaml`、`envs/*.yaml`、`rules/*.smk`、`scripts/*.py`、`requirements.txt`
  - <!-- bio-C7 --> **nextflow**：`main.nf`、`nextflow.config`、`modules/*.nf`、`params.yaml`、`scripts/*.py`、`requirements.txt`
- `wiki/experiments/{slug}.md` — 更新 status、outcome、key_result、date_completed、run_log、remote 块
- `wiki/log.md` — 追加操作日志

### Graph edges created
- **无**。实验与 claim 的 tested_by 边已在 /exp-design 中创建。

## Workflow

**前置**：确认工作目录为 wiki 项目根（包含 `wiki/`、`raw/`、`tools/` 的目录）。

---

### Deploy 模式（默认，status == planned）

**Phase 1: 准备（Prepare）**

1. **读取实验页面**：
   - `wiki/experiments/{slug}.md`：提取 setup（model, dataset, hardware, framework）、metrics、baseline、hypothesis
   - <!-- bio-C7 --> 同时提取存在的 bio 字段：`setup.in_silico_or_wet`、`setup.assay_type`、`setup.species`、`setup.cell_line`、`setup.force_field`、`setup.solvent_model`、`setup.simulation_length`、`setup.weight_version`、`experiment.type`（C4 枚举）、`statistical_protocol`（C6 枚举）
   - 验证 status == `planned`
   - 若 status 为 `running`，提示用户使用 `--collect` 模式
   - 若 status 为 `completed`/`abandoned`，拒绝执行

2. **加载实现上下文**：
   - 读取关联 idea 的 approach sketch（实现指南）
   - 读取相关论文的方法描述（算法细节）
   - 读取同一 claim 的其他实验（参考代码结构）

3. <!-- bio-C7 --> **检测 setup type**（已传 `--setup-type` 时跳过）：

   按以下顺序匹配，命中即用：

   | 信号 | 检测到的类型 |
   |------|--------------|
   | `setup.in_silico_or_wet == "wet"` 或 `setup.in_silico_or_wet == "hybrid"` | **wet-lab** |
   | `setup.assay_type` ∈ `{MD, MD-relaxation, FEP, GROMACS, AMBER}`（不分大小写） 或 `setup.force_field` 非空 | **md** |
   | `setup.assay_type` ∈ `{docking, virtual-screen, AutoDock, Vina, Glide, Schrödinger}` | **docking** |
   | `setup.framework` 提到 `snakemake` 或关联 idea/paper 上下文有 Snakefile | **snakemake** |
   | `setup.framework` 提到 `nextflow` / `nf-core` | **nextflow** |
   | 其他（旧 CS 路径） | **ml** |

   把检测到的类型打印到 DEPLOY_REPORT。当检测器选了 `ml` 但实际有 bio 字段时，几乎一定是 setup 字段未声明 —— 在报告中发 🟡 提示，但不阻塞部署。

4. **编写实验代码**，从 `references/templates/{detected-type}/` 写入 `experiments/code/{slug}/`：

   **ml**（旧默认，与 CS workflow 不变）：
   - `train.py`：根据 setup 配置生成训练/评估脚本，包含：
     - 参数解析（argparse，所有超参数可配置）
     - 数据加载（支持 setup.dataset）
     - 模型初始化（支持 setup.model 和 baseline 模型）
     - 训练/推理循环
     - 指标计算（对应 metrics 列表）
     - 结果保存（JSON 格式，路径：`results/{slug}/seed_{N}.json`）
     - 随机种子控制（多 seed 运行）
     - Checkpoint 保存/恢复（`checkpoints/{slug}/`）
   - `config.yaml`：所有超参数（learning_rate, batch_size, epochs, seeds 等）
   - `run.sh`：封装完整启动命令（含 CUDA_VISIBLE_DEVICES、logging、conda 激活）
   - `requirements.txt`：实验专属依赖（若与主项目 requirements 不同）

   <!-- bio-C7 -->

   **md**：从 MD 模板生成。必填项（任一缺失则拒绝部署）：
   - `mdrun.sh`：GROMACS 风格启动（`gmx grompp` + `gmx mdrun`），含 seed 固定与每阶段 checkpoint。遵循 `setup.force_field`、`setup.solvent_model`、`setup.simulation_length`。
   - `system.gro` / `system.pdb`（占位 + 注释清晰指明源 PDB ID 与所需预处理：solvation、ions、minimization）。
   - `system.top`（topology —— 由 `gmx pdb2gmx` 针对 `setup.force_field` 生成）。
   - `mdp/em.mdp`（能量最小）、`mdp/nvt.mdp`（NVT 平衡）、`mdp/npt.mdp`（NPT 平衡）、`mdp/prod.mdp`（生产）。从 `setup.simulation_length` 推 `nsteps`（如 `100ns` → 2-fs dt 时 `nsteps = 50000000`）。
   - `analysis.ipynb`：RMSD、RMSF、回转半径、二级结构指派的 cell 模板，标 "filled after collect"。
   - `results/{slug}/`：结果保存为 `traj.xtc` + `summary.json`（Phase 4 由 analysis notebook 读取）。

   **wet-lab**：从 wet-lab 模板生成。必填项：
   - `protocol.md`：实验员可读的台面协议，分章节 —— Materials、Reagents、Equipment、Step-by-step procedure、Read-out、Pause points、Safety。自动生成器预填 `setup.assay_type`、`setup.cell_line`、`setup.species` 与 C6 复制矩阵（biological × technical）。
   - `materials.csv`：列 `kind | name | identifier | identifier_type | catalog | vendor | lot | url`。`identifier_type` ∈ `{RRID, CVCL, Addgene, NCBI-Taxonomy, ChEBI, free-text}`。`assay_type ∈ {immunoblot, IF, IHC, flow}` 时空 materials 拒绝部署 —— 这些 assay 抗体质量复现风险高，必须有 RRID。
   - `analysis.ipynb`：以 CSV 结果文件为前提的 cell 模板；`replicate_matrix_BxT`（C6）时预填每复制聚合（biological reps 取 mean±SEM；technical reps 显示原始点）。
   - `data/raw/.gitkeep` 与 `data/processed/.gitkeep` 占位。
   - **wet-lab 的 Phase-2 部署有意是 no-op**（见下文 Phase 2）。

   **docking**：从 docking 模板生成。必填项：
   - `dock.sh`：默认 AutoDock Vina 风格；`setup.framework` 指明其他 docker 时按其调整。
   - `receptor.pdbqt`（占位 + 源 PDB ID）。
   - `ligand_library.smi`（占位 + 源库名与版本，如 ZINC22 子集）。
   - `box.txt`（搜索盒中心 + 维度；`setup.binding_site` 存在时填，否则占位 + 清晰 "TODO" 注释）。
   - `scoring.yaml`：scoring 函数选择 + 复现 seed。
   - `analysis.ipynb`：top-N pose 提取、redocking RMSD、scoring 分布。

   **snakemake / nextflow**：从对应 workflow-manager 模板生成。必填项：
   - `Snakefile` / `main.nf`：每个 workflow 阶段的顶层 rule / process。
   - `config.yaml` / `params.yaml`：含默认值的参数；遵循 `setup` 字段。
   - `envs/*.yaml`（Snakemake）或每 process container 指令（Nextflow）：固定工具版本以保证复现。
   - `rules/*.smk` / `modules/*.nf`：阶段逻辑；自动生成器按实验的 metric 列表发出 skeletal `rule` / `process`，**拒绝**编造用户应填的逻辑。
   - `requirements.txt`：workflow 运行器版本（`snakemake>=8`、`nextflow>=24.04`）。

5. **可选 Review LLM code review**（`--review`）：
   ```
   mcp__llm-review__chat:
     system: "You are a senior {ML | MD | wet-lab | docking | workflow-manager} engineer reviewing experiment code.   <!-- bio-C7 -->
              Focus on: correctness of the core procedure, proper evaluation protocol,
              fair baseline comparison, reproducibility (seeds / determinism / replicate
              matrix / version pinning), proper metric computation, and common pitfalls
              (data leakage, wrong split, gradient accumulation bugs;
              MD: incomplete equilibration, wrong barostat/thermostat coupling, periodic-image artefacts;
              wet-lab: missing RRID, no biological replicates, missing positive control;
              docking: wrong protonation state, undefined search box, scoring-function bias;
              snakemake/nextflow: undeclared inputs/outputs, missing container pinning)."
     message: |
       ## Experiment
       {experiment title and hypothesis, plus detected setup-type}     <!-- bio-C7 -->

       ## Code
       {generated code}

       ## Expected Behavior
       {setup details from wiki page}

       Review for correctness and potential issues.
   ```
   根据 Review LLM 反馈修正代码。system prompt 的术语随检测到的类型专化，让 reviewer 给出贴合该类型失败模式的 flag（MD reviewer 不应在 `gmx mdrun` 脚本上静默套用 ML pitfalls）。

6. **Sanity check（小规模验证）**：
   - **ml**：用极小规模运行（1 epoch / 100 steps / 小 subset）；验证 loss 下降。
   - <!-- bio-C7 --> **md**：跑 100-step `gmx mdrun -nsteps 100`；验证 trajectory 写出且能量有限。"loss decreases" 的同位替代。
   - <!-- bio-C7 --> **docking**：dock 5 个 ligand；验证 pose 文件生成、score 落入合理区间（AutoDock 的 -15 到 0 kcal/mol）。
   - <!-- bio-C7 --> **snakemake / nextflow**：dry-run（`snakemake --dry-run` / `nextflow run main.nf -with-trace --stub`）—— 验证 DAG 解析、rule/process 的输入输出全部声明。
   - <!-- bio-C7 --> **wet-lab**：sanity check N/A；在 DEPLOY_REPORT 中跳过并注明 —— wet-lab 的 "sanity" 是研究者对协议的肉眼复审，不是自动化检查。
   - 若 sanity 失败 → 修复代码，重试一次；仍然失败则报告错误并停止。

**Phase 2: 部署（Deploy）**

#### Local 模式（`--env local` 或默认）

<!-- bio-C7：Phase-2 按检测到的类型路由 -->

**ml** 实验（旧路径，不变）：

1. **检查 GPU**：`nvidia-smi` 确认 GPU 可用、显存足够
2. **启动**：
   ```bash
   screen -dmS exp-{slug} bash -c \
     "cd $(pwd) && bash experiments/code/{slug}/run.sh 2>&1 | tee logs/exp-{slug}.log"
   ```
3. 更新 `wiki/experiments/{slug}.md`：
   - status: `running`
   - run_log: `logs/exp-{slug}.log`
4. **估算运行时长**，写入 frontmatter：
   根据 `setup.hardware`（GPU 型号/数量）、`setup.model`（参数量）、`setup.dataset`（规模）合理估算：

   | 典型场景 | 估算范围 |
   |----------|----------|
   | 单 GPU + 小数据集（CIFAR / 小 NLP benchmark） | 0.5 – 3h |
   | 单 A100 + 中等数据集（ImageNet / GLUE） | 4 – 12h |
   | 多 GPU 或大模型 fine-tuning（≥7B） | 8 – 48h |

   ```bash
   python3 tools/research_wiki.py set-meta \
     wiki/experiments/{slug}.md started "{YYYY-MM-DDTHH:MM}"
   python3 tools/research_wiki.py set-meta \
     wiki/experiments/{slug}.md estimated_hours {N}
   ```
5. 追加日志：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | deployed {slug} | env: local | session: exp-{slug} | eta: {N}h | type: ml"
   ```

<!-- bio-C7 -->

**md** 实验：

1. **检查 GPU**：与 ML 同；MD 在 CPU 上允许但发 🟡 提示（约 10× 慢）。
2. **启动**：
   ```bash
   screen -dmS exp-{slug} bash -c \
     "cd $(pwd) && bash experiments/code/{slug}/mdrun.sh 2>&1 | tee logs/exp-{slug}.log"
   ```
3. 更新 wiki frontmatter，同 ml。
4. **估算 MD wall-clock**，按 `setup.simulation_length` 与硬件。参考表（单 A100、GROMACS 2024、AMBER ff14SB、~50k 原子系统）：

   | simulation_length | 估算 wall-clock |
   |-------------------|------------------|
   | 100 ns            | 8 – 16h          |
   | 500 ns            | 1.5 – 3 天       |
   | 1 µs              | 3 – 7 天         |
   | 10 µs             | 1 – 2 月         |

   写入 `estimated_cost.md_wallclock_hours`（A6）；旧 `estimated_hours` 保留同值以做向后兼容。
5. 追加日志，附 `type: md`。

**docking** 实验：

1. **检查 GPU**：docking 小库可纯 CPU；库 > 10k 时再要求 GPU。
2. **启动**：同 `screen -dmS` 模式；entrypoint 是 `dock.sh`。
3. 估算：单 GPU ~0.5–2s/ligand；10M ligand 库未经用户明确确认拒绝部署。
4. 写入 `estimated_cost.gpu_hours` 与 `estimated_cost.cpu_hours`。

**snakemake / nextflow** 实验：

1. **预部署 DAG 检查**：`snakemake --dry-run` / `nextflow run main.nf -with-trace --stub`（已在 Phase 1 sanity 跑过）；DAG 不通过拒绝部署。
2. **启动**：`screen -dmS exp-{slug} bash -c "snakemake --cores all"` 或 `screen -dmS exp-{slug} bash -c "nextflow run main.nf -resume"`。
3. 估算：取最长阶段；nextflow `-resume` 让重新部署能从上次断点续跑。

**wet-lab** 实验：

1. **wet-lab 的 Phase-2 部署是 no-op**。在 DEPLOY_REPORT 中打印 protocol 路径，并提示用户在台面执行实验。
2. 把 status 设为 `running`、`started` 设为今天，让 `/exp-status` 跟踪 elapsed time。
3. 从 `setup` 字段写入 `estimated_cost.wet_lab_usd` 与 `estimated_cost.fte_weeks`。
4. 追加日志附 `type: wet-lab`，让 `/exp-status --collect-ready` 不去轮询不存在的 screen session。

#### Remote 模式（`--env remote`）

**前提**：用户已配置 `config/server.yaml`。

1. **确认连通**：`python3 tools/remote.py status`
   - 若不可达 → 报错并建议检查 config/server.yaml
2. **查找空闲 GPU**：`python3 tools/remote.py gpu-status`
   - 若无空闲 GPU → 报告各 GPU 占用情况，建议等待
3. **同步代码**：`python3 tools/remote.py sync-code`
4. **安装依赖**（首次或 requirements 有变化）：`python3 tools/remote.py setup-env`
5. **启动远程实验**：
   ```bash
   python3 tools/remote.py launch \
     --name "exp-{slug}" \
     --cmd "{每类型的 entrypoint：bash run.sh | bash mdrun.sh | bash dock.sh | snakemake --cores all | nextflow run main.nf}"   <!-- bio-C7 -->
     --gpu {gpu_index}
   ```
6. 更新 `wiki/experiments/{slug}.md` frontmatter —— 以下字段已由 /exp-design 写入完整 CLAUDE.md 模板,都是空值:
   ```bash
   # 顶层 scalar 字段 —— 用 set-meta
   python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md status running
   python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md run_log "logs/exp-{slug}.log"
   ```

   嵌套 `remote:` 块无法通过 `set-meta` 更新（set-meta 只处理顶层 scalar 字段）。直接用 `Edit` 工具就地替换这五个空的子字段值。文件里已有的 block 形如：
   ```yaml
   remote:
     server: ""
     gpu: ""
     session: ""
     started: ""
     completed: ""
   ```
   用 5 次 Edit 调用（每个子字段一次）设置 `server`、`gpu`、`session`、`started`。`completed: ""` 留空由 Phase 4 填写。如果发现文件里没有 `remote:` block,说明 /exp-design 没写完整的 CLAUDE.md 模板;停下来报 bug,不要在这里追加 block（追加会让字段顺序偏离 canonical 模板,破坏后续 edit 的匹配）。

7. **估算运行时长**，写入 frontmatter（按检测到的类型，规则同 local；<!-- bio-C7 --> 非 ML 类型填 `estimated_cost.*` 而非仅 `estimated_hours`）。
8. 追加日志，附 `type: {detected}`：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | deployed {slug} | env: remote | server: {host} | gpu: {gpu} | eta: {N}h | type: {detected}"
   ```

**输出 DEPLOY_REPORT 到终端**：

```markdown
# Deploy Report: {experiment title}

### Status: DEPLOYED ✅

- Setup type: {ml | md | wet-lab | docking | snakemake | nextflow}    <!-- bio-C7 -->
- Template: skills/exp-run/references/templates/{type}/                <!-- bio-C7 -->
- Session: exp-{slug}
- Environment: local | remote ({host} GPU {gpu})
- Log file: logs/exp-{slug}.log
- Code: experiments/code/{slug}/
- Estimated: ~{N}h（{estimated_cost.* 主导维度 — md_wallclock_hours / gpu_hours / wet_lab_usd / fte_weeks}）   <!-- bio-C7 -->

### Next Steps

1. Monitor progress: `/exp-status`
2. Check this experiment: `/exp-run {slug} --collect`
3. In /research pipeline: progress saved to wiki/outputs/pipeline-progress.md
{wet-lab only:} 4. 在台面用 protocol.md 执行实验；results.csv 就位后 `/exp-run {slug} --collect`。   <!-- bio-C7 -->

### Quick Commands
```bash
# Local: check if still running
screen -ls | grep exp-{slug}

# Local: tail log
tail -f logs/exp-{slug}.log
```
```

---

### Collect 模式（`--collect` 或 `--check`，status == running）

**Phase 3: 监控/检查运行状态（Monitor）**

1. **读取部署信息**：从 `wiki/experiments/{slug}.md` frontmatter 获取环境（local 或 remote）和 session 名。<!-- bio-C7 --> 同时从部署日志行重读检测到的 setup-type。

2. **检查进程是否还活着**（wet-lab 跳过）：
   - **Local**：`screen -ls | grep exp-{slug}`
   - **Remote**：`python3 tools/remote.py check --name "exp-{slug}"`，解析 `alive` 字段
   - <!-- bio-C7 --> **wet-lab**：没有进程可查。检查 `data/processed/results.csv`（或协议 read-out 章节命名的路径）；不存在则提示用户。

3. **若实验仍在运行（alive == true）**：
   - 获取最近日志：
     - Local：`tail -30 logs/exp-{slug}.log`
     - Remote：`python3 tools/remote.py tail-log --name "exp-{slug}" --lines 30`
   - **异常检测**（按 setup-type）<!-- bio-C7 -->：
     - **ml**：`loss: nan`、`loss: inf`、`CUDA out of memory`、Python traceback
     - **md**：能量 NaN、LINCS warning、"Step ... has too large of a force"、瞬时力暴涨提示的 PBC artefact
     - **docking**：返回零 pose；所有 score < -100（多半是 bug，不是真实结果）
     - **snakemake / nextflow**：rule/process 失败；点出失败步骤与日志路径
   - **自动修复尝试**（若检测到异常，最多 1 次）：
     - **ml** NaN/爆炸 → 从最近 checkpoint 恢复，降低学习率
     - **ml** OOM → 减小 batch size，重启
     - **md** 启动 LINCS warning → 用更紧的 `emtol` 重做能量最小
     - **docking** 零 pose → 把搜索盒放大 50%（提醒用户）
     - workflow-manager：不自动重试 —— 暴露失败 stage 由用户决定
   - **输出进度报告**（不修改 wiki，仅报告）：
     ```
     Experiment {slug}: RUNNING
     Type: {检测到的 setup-type}    <!-- bio-C7 -->
     Progress: step {N} / epoch {E}（md：模拟 ns 数；docking：已处理 ligand 数；workflow：阶段完成数）
     Latest metric: {metric} = {value}
     Anomalies: {none | NaN detected | ...}
     Estimated remaining: ~{N} hours
     Run `/exp-status` to monitor all running experiments.
     ```
   - **返回**（不执行 Phase 4）

4. **若实验已完成（alive == false / session gone，或 wet-lab 的 CSV 就位）**：
   - 继续执行 Phase 4

**Phase 4: 收集结果（Collect Results）**

1. **拉取远程结果**（仅 remote 模式）：同 `tools/remote.py pull-results` 流程；`results/{slug}/` 内的路径取决于 setup-type。

2. **检查结果文件存在**：
   - **ml**：`results/{slug}/seed_*.json`
   - <!-- bio-C7 --> **md**：`results/{slug}/traj.xtc` + `results/{slug}/summary.json`（能量、RMSD 时间序列）
   - <!-- bio-C7 --> **docking**：`results/{slug}/poses_*.pdbqt` + `results/{slug}/scores.csv`
   - <!-- bio-C7 --> **wet-lab**：`data/processed/results.csv`（按协议 read-out 章节命名的精确路径）
   - <!-- bio-C7 --> **snakemake / nextflow**：按 workflow 定义声明的输出 channel

3. **解析结果**（按 setup-type 与 C6 statistical_protocol）<!-- bio-C7 -->：
   - **ml**（`seeds_only`）：每 metric 跨 seeds 取 mean ± std
   - **md**：读 summary.json —— RMSD steady-state、RMSF、回转半径；用 per-frame 样本做 bootstrap CI
   - **docking**：top-N pose score + redocking RMSD；报告中位数 + 95% 范围
   - **wet-lab**（`replicate_matrix_BxT`）：跨 biological replicates 取 mean ± SEM；technical replicates 显原始点；不要混在一起折叠
   - **bootstrap_ci**：1000 次 resample；报告 95% CI（用 `scipy.stats.bootstrap` 或同等）
   - **stratified_kfold**：每 fold 的 metric + macro mean；类不平衡时不要盲目跨 fold 平均
   - 与 baseline 对比，按对应 statistical-protocol 的置信区间报告改进幅度

4. **更新实验页面** `wiki/experiments/{slug}.md`：
   - status: `completed`
   - outcome: `succeeded` / `failed` / `inconclusive`
     - succeeded：所有 success criteria 满足
     - failed：核心指标未达标
     - inconclusive：结果混合或方差过大
   - key_result: 一句话总结核心发现
   - date_completed: 今天日期
   - 填充 `## Results` section：完整结果表格，caption 中点名所用统计协议   <!-- bio-C7（依赖 C6） -->
   - 填充 `## Analysis` section：初步分析
   - 若 remote 模式：更新 `remote.completed` 时间戳

5. **追加日志**：
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "exp-run | completed {slug} | outcome: {outcome} | key: {key_result} | type: {detected}"
   ```

6. **输出 RUN_REPORT 到终端**：
   ```markdown
   # Run Report: {experiment title}

   ## Outcome: {succeeded / failed / inconclusive}
   ## Setup type: {ml / md / wet-lab / docking / snakemake / nextflow}    <!-- bio-C7 -->
   ## Statistical protocol: {seeds_only / bootstrap_ci / stratified_kfold / replicate_matrix_BxT}    <!-- bio-C7（C6） -->

   ## Results
   | Metric | Baseline | Ours ({mean±std | mean±SEM | bootstrap-CI | per-fold}) | Δ |
   |--------|----------|-------------------------------------------------------|---|
   | {metric} | {baseline-value} | {ours} | +{delta} |

   ## Key Finding
   {key_result}

   ## Next Steps
   - Run `/exp-eval {slug}` to update claims in wiki
   - {if succeeded: proceed to next experiment in plan}
   - {if failed: analyze failure, consider /exp-design revision}
   ```

---

### Full 模式（`--full`，status == planned）

依次执行全部 4 个 Phase（Phase 1 → Phase 2 → Phase 3 → Phase 4），中间不返回。

适用场景：本地 CPU/GPU 几分钟内可完成的快速实验（sanity check、toy dataset 验证等）。

Phase 3 中不需要先检查 "是否还在运行"，而是等待 screen session 真正结束后再执行 Phase 4：
```bash
# 等待 session 结束（轮询）
while screen -ls | grep -q "exp-{slug}"; do
  sleep 30
done
# session 消失，进入 Phase 4
```

<!-- bio-C7 --> `--full` 模式**不支持** `wet-lab` setup-type —— wet-lab 不能在数分钟内完成。明确拒绝："wet-lab experiments use the deploy + bench-execute + collect flow; use `/exp-run {slug}` then run protocol.md, then `/exp-run {slug} --collect`."

---

## Constraints

- **deploy 模式只接受 planned 实验**：若 status 为 running，提示使用 --collect；若为 completed，拒绝执行
- **collect 模式只接受 running 实验**：若 status 为 planned，提示先 deploy；若为 completed，提示已完成
- **collect 模式：alive 时不写 wiki**：仅报告进度，不修改任何 wiki 文件
- **代码统一写入 experiments/code/{slug}/**：不写到项目根目录或其他位置
- **不修改 claims**：实验结果只写入 experiments/ 页面，claims 的更新由 /exp-eval 负责
- **sanity check 必须通过**：Phase 1 sanity 失败则不部署（除非用户明确 override）。<!-- bio-C7 --> wet-lab 是唯一例外 —— sanity N/A。
- **结果文件必须保存**：所有实验结果以 JSON 格式保存在 `results/{slug}/seed_{N}.json`，<!-- bio-C7 --> ml 路径如此；md / docking / wet-lab / workflow-manager 按类型 artefact（见 Phase 4 步骤 2）。
- **多 seed 结果取均值**：报告 mean ± std，不报告单次运行。<!-- bio-C7 --> 当 `statistical_protocol != seeds_only` 时按对应聚合（bootstrap CI / per-fold / replicate matrix）报告 —— 不要静默退回 mean ± std。
- **graph edges 不在此 skill 创建**：tested_by 边已在 /exp-design 中创建
- **自动修复最多尝试 1 次**：防止无限重启循环
- <!-- bio-C7 --> **setup-type 自动检测不是权威**：用户可用 `--setup-type` 覆盖。检测器是 `setup` 字段上的启发式，字段为空时会误路由。修法几乎总是补齐缺失字段，而不是静默覆盖检测器。
- <!-- bio-C7 --> **wet-lab 模板要 materials**：当 `materials.csv` 为空、或 `assay_type` 暗示需要抗体但无 RRID 时拒绝部署 —— 复现性损失太大。

## Error Handling

- **experiment 找不到**：提示用户检查 slug，列出 wiki/experiments/ 中的候选（status=planned 或 running）
- **deploy 模式但 status == running**：提示 "已在运行中，使用 `/exp-run {slug} --collect` 检查状态"
- **collect 模式但 status == completed**：提示 "已完成，直接运行 `/exp-eval {slug}`"
- **GPU 不可用**：报告错误，建议用 --env remote 或等待 GPU 释放
- **Review LLM 不可用**（--review 模式）：跳过 code review，在 DEPLOY_REPORT 中标注「unreviewed」
- **sanity check 失败**：详细报告错误信息，尝试自动修复一次，仍失败则停止并建议手动调试
- **远程连接失败**：报告 SSH 错误，建议检查连接配置和 config/server.yaml
- **结果文件缺失**（collect 模式）：报告哪些 seeds 缺失结果，对已有结果正常汇总；若成功 seeds < 2 则标记 inconclusive
- **实验 crash**（collect 模式检测到 traceback）：在报告中附上 crash 信息和建议修复方向
- **--full 模式等待超时**：若 screen session 超过预期时间的 2x 仍存在，警告用户但不强制终止
- <!-- bio-C7 --> **setup-type 检测器在有 bio 字段的情况下选了 `ml`**：发 🟡 提示，仍按 `ml` 模板部署；用户填齐缺失字段后可重新部署。
- <!-- bio-C7 --> **目标 setup-type 模板尚未编写**（当前状态，直至后续工具落地）：当 `references/templates/{type}/` 不存在时，生成只含 section header 与 "fill from setup fields" 注释的占位目录（每类型的 entrypoint 形如 `protocol.md`），并提示用户模板支架不完整。
- <!-- bio-C7 --> **wet-lab CSV collect 模式缺失**：不要自动标 `inconclusive`；提示用户 "drop your CSV at data/processed/results.csv and rerun /exp-run {slug} --collect" —— 实验真的还在台面跑。

## Dependencies

### Skills（via Skill tool）
- 无直接调用子 skill

### Tools（via Bash）
- `python3 tools/research_wiki.py log wiki/ "<message>"` — 追加日志
- `python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md <field> <value>` — 更新顶层 scalar
- `python3 tools/remote.py <command>` — 远程操作（status, gpu-status, sync-code, setup-env, launch, check, tail-log, pull-results）
- `nvidia-smi` — 本地 GPU 状态
- `screen` — 本地后台运行管理
- <!-- bio-C7 --> `gmx grompp` / `gmx mdrun`（GROMACS，MD 路径）—— 由 `mdrun.sh` 调用；不是 `/exp-run` 直接依赖
- <!-- bio-C7 --> `vina` / `smina` / `gnina`（docking 路径）—— 由 `dock.sh` 调用；不是 `/exp-run` 直接依赖
- <!-- bio-C7 --> `snakemake` / `nextflow` —— 由 workflow-manager 模板调用

### Configuration
- `config/server.yaml` — 远程服务器配置（仅 `--env remote` 时需要）

### MCP Servers
- `mcp__llm-review__chat` — Phase 1 代码审查（可选，`--review` 时使用）。system prompt 按检测到的 setup-type 专化。   <!-- bio-C7 -->

### Claude Code Native
- `Read` — 读取 wiki 页面和日志文件
- `Write` — 写入 `experiments/code/{slug}/` 下的实验代码
- `Bash` — 执行部署命令、监控进程

### Local References
- <!-- bio-C7 --> `skills/exp-run/references/templates/ml/`（既有的隐式模式）
- <!-- bio-C7 --> `skills/exp-run/references/templates/md/`（计划中）
- <!-- bio-C7 --> `skills/exp-run/references/templates/wet-lab/`（计划中）
- <!-- bio-C7 --> `skills/exp-run/references/templates/docking/`（计划中）
- <!-- bio-C7 --> `skills/exp-run/references/templates/snakemake/`（计划中）
- <!-- bio-C7 --> `skills/exp-run/references/templates/nextflow/`（计划中）

### Called by
- `/research` Stage 3a（deploy 模式）和 Stage 3c（collect 模式）
- `/exp-status --collect-ready`（collect 模式）
- 用户手动调用
