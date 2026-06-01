# /dream Automation

GitHub Actions 是 `/dream` 的无人值守调度器。它运行与手动 slash pass 相同的 agent-first 记忆循环，并通过 `tools/research_wiki.py dream` 完成终结；该工作流并非独立实现。

## Source Of Truth

- `.github/workflows/dream.yml`：定时执行器与手动触发。
- `config/dream.yml`（可选）：用户拥有的定时默认值，用于设置 mode、上下文限制和 `yolo`。
- `tools/research_wiki.py dream`：上下文准备、响应验证、提案写入、受保护应用及上下文重建。
- `tools/research_wiki.py scievolve-sense`：在上下文准备之前自动感知持久失败状态和应用跳过信号。
- `wiki/outputs/evolution/dream/`：每次运行的上下文、提示词、响应、报告及应用产物。
- `wiki/outputs/evolution/proposals.jsonl` 和 `applications.jsonl`：共享 SciEvolve 账本条目。

## Workflow Behavior

- 定时运行：`43 18 * * *` UTC。
- 定时运行在存在 `config/dream.yml` 时读取它。若不存在，则使用 `mode=auto-apply`、默认上下文限制和 `yolo=false`。
- 手动触发可设置 `mode=auto-apply` 或 `mode=propose-only`，调整上下文限制，并显式覆盖 `yolo`。
- `yolo=true` 可在 `config/dream.yml` 中为无人值守运行设置，或在手动触发输入中设置。页面归档/合并变更仍需要高置信度、有据可查且被确定性终结器接受的提案。
- 这些默认值是无人值守 CI 的安全姿态，而非能力限制：定时 `/dream` 仍可自动应用已验证的记忆更新，显式 `yolo=true` 可启用高置信度归档/合并应用路径。
- 当 `ANTHROPIC_API_KEY` 或 `CLAUDE_CODE_OAUTH_TOKEN` 存在时，优先使用 Claude Code Action。工作流先准备上下文，运行 `scievolve-sense`，对 wiki 进行快照，仅要求 Claude 写入 `dream_agent_response.json`，在确定性终结化之前拒绝任何 wiki/源代码的预终结编辑，然后使用确定性 Python 步骤对同一已准备运行目录进行终结。
- 若 Claude 鉴权不存在，回退路径通过 OpenAI 兼容的 `LLM_*` 环境变量调用 `tools/research_wiki.py dream --use-llm`。
- 若无可用策略运行时，工作流以失败方式关闭。

## Secrets

主要策略运行时：

- `ANTHROPIC_API_KEY`
- `CLAUDE_CODE_OAUTH_TOKEN`

回退策略运行时：

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LLM_FALLBACK_MODEL`（可选）

回退 Python 进程从环境变量读取 `LLM_*` 值，因此工作流在 job 级 `env:` 块中暴露这些密钥。仅添加 repo 密钥而不将其暴露给 job 是不够的。

## Artifacts And Writeback

每次运行上传：

- `.dream/run/config.json`
- `.dream/run/instructions.md`
- `.dream/run/sense.json`
- 使用 Claude 鉴权时：`.dream/run/prepare.json`
- `.dream/run/dream_agent_response.json`
- `.dream/run/finalize.json`
- `.dream/run/stage-paths.txt`
- `wiki/outputs/evolution/dream/**`
- 共享提案/应用账本及 `wiki/graph/context_brief.md`

工作流仅强制暂存终结器声明的路径，因为 repo 默认有意忽略生成的 wiki 输出。这包括运行产物、已感知信号、提案账本、安全记忆元数据/正文注释、启用 `yolo` 时的归档路径，以及重建的下游上下文。

## Setup And Status Checks

`/dream setup` 应检查：

- 工作流文件是否存在，且 `43 18 * * *` 定时计划是否正确
- `config/dream.yml` 中 mode、上下文限制和 `yolo` 的可选值
- job 级是否暴露了 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 及可选的 `LLM_FALLBACK_MODEL`
- `ANTHROPIC_API_KEY` 或 `CLAUDE_CODE_OAUTH_TOKEN` 的 Claude Code Action 鉴权指引
- 终结化之前是否有写边界守卫
- 是否使用终结器声明的路径强制暂存，而非宽泛的 `git add wiki`

`/dream status` 应检查相同的工作流健康状态，以及存在时近期本地 `wiki/outputs/evolution/dream/` 运行情况。

## Failure Behavior

- 缺少策略密钥：在运行虚假的仅报告循环之前失败。
- 缺少 Claude 响应文件：在终结化之前失败。
- Claude 在 `.dream/run/dream_agent_response.json` 之外写入：在确定性终结化和任何提交之前失败。
- 无效的 agent 响应：终结化记录被拒绝的项目；不执行不安全的应用。
- 无有意义的提案：写入空响应和已终结报告，使无人值守 pass 保持可检查状态。
