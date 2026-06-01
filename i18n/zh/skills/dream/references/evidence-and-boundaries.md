# /dream Evidence And Boundaries

`/dream` 必须表现得具有 agentic 特性，同时不变得不安全。它可以提出记忆操作，安全自动应用可应用狭义的可逆元数据变更加 append-only 审计注释。它不得悄无声息地重写 wiki。

保守模式是安全姿态，而非降低自主性。`--propose-only` 使产物在演示中保持仅供审查状态，`yolo=false` 默认避免页面归档/合并，但已实现的循环仍可应用已验证的记忆更新并重建下游上下文。

## Evidence Sources

可接受的证据：

- 来自 `dream_context.json` 的实体 id，例如 `concepts/foo` 或 `methods/bar`
- 来自 `candidate_memory_cues` 的候选 id，例如 `dream-candidate-003`
- 来自 `recurring_patterns` 的反复出现模式 id，例如 `pattern-memory-concepts-cache-failure-*`
- 来自 `wiki/outputs/evolution/signals.jsonl` 的信号 id
- 来自 dream 上下文的 graph、projected-edge 或引用 id
- dream 上下文中的页面摘录、摘要、标签、状态、日期和现有链接
- 现有 `/check` 或 lint 报告，仅作为次要证据

证据应回答："为什么 agent 认为该记忆操作值得变更？"

## Boundary With `/check`

`/check` 拥有结构健康：

- 断开的 wikilink
- 格式错误的 frontmatter
- 缺失的必填字段
- 无效的 enum 值
- xref 不对称
- 格式错误的 graph 行
- 悬空的 graph 端点
- 确定性默认字段修复

`/dream` 可将这些仅作为弱辅助信号提及。它们永远不应成为主要提案。若一个提案说"修复缺失的 parent_topics"，除非 agent 引用了语义证据表明该页面属于一个真实的记忆邻域，否则它不是 dream。

## Safety Rules

永远不得：

- 删除页面
- 直接归档页面
- 编辑非 SciEvolve frontmatter
- 添加 graph edge
- 重写实体正文章节
- 创建 wiki 上下文中不存在的科学声明
- 将确定性候选线索视为已成立的事实

允许：

- 提案归档/降权/审查
- 提案合并/聚类/摘要/交叉链接
- 为人工审查提出低置信度关联提案
- 通过安全自动应用路径将中/高置信度提案应用为可逆 frontmatter 元数据和 append-only 审计注释
- 引用 `/check` 问题作为支持证据
- 在证据薄弱时以零提案结束 dream

## Closed-Loop Standard

运行应留下如下痕迹：

1. 系统准备了一个记忆场景。
2. 一个可插拔策略运行时将该场景解读为科学记忆，而非仅仅是文件。运行时可以是 Claude Code、API 模型、本地模型或提供的 agent 响应；使用相同的验证器和应用路径。
3. agent 选择了少量有意义的自演化操作。
4. 每个操作都解释了若被接受，未来的记忆检索、构想或规划将如何改变。
5. 终结器验证了引用的证据。
6. 安全自动应用写入了可逆的 SciEvolve 元数据、append-only 审计注释及应用账本条目。
7. 上下文摘要已重建，使下游 skill 能使用变更后的记忆状态。
8. 提案存储记录了产物并将已应用项标记为 `applied`。

避免如下痕迹：

1. 确定性扫描器列出了陈旧页面。
2. 系统将该列表重命名为"遗忘"。
3. 每个弱线索都变成了一个提案。
4. 产物从未说明记忆将如何演化。
5. 系统在没有可逆元数据轨迹的情况下执行了大范围页面重写。

## Confidence Guidance

- `high`：来自多个页面/信号的明确证据，歧义低
- `medium`：证据足够清晰，可进行受保护的安全自动应用；或在选择 `--propose-only` 时进行仅供审查处理
- `low`：合理的关联或待清理候选；主要作为后续审查的提示

对推测性关联自由使用 `low`。当提案诚实地标记不确定性时，提案产物仍然有价值。
