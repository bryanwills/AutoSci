# /dream Agent Response Schema

终结器接受严格 JSON。将响应写入 Step 1 返回的运行目录：

```text
wiki/outputs/evolution/dream/<run>/dream_agent_response.json
```

## Top-Level Shape

```json
{
  "proposals": [
    {
      "operation": "forgetting",
      "target": "ideas/example",
      "title": "Archive a repeated failed idea trace",
      "proposed_action": "Mark this idea for archive review and fold its reusable lesson into concepts/example.",
      "rationale": "The idea is failed, repeated in nearby notes, and has no active experiment path.",
      "confidence": "medium",
      "related_entities": ["ideas/example", "concepts/example"],
      "candidate_ids": ["dream-candidate-001"],
      "evidence": [
        {
          "source": "dream-candidate-001",
          "summary": "Candidate cue links failed status and repeated memory trace."
        },
        {
          "source": "ideas/example",
          "summary": "The page status is failed and the failure reason is already recorded."
        }
      ]
    }
  ]
}
```

## Required Proposal Fields

- `operation`：`forgetting`、`consolidation`、`association` 之一
- `target`：来自上下文的实体 id；仅当提案为集群级记忆操作时可为空
- `title`：简短的提案标题
- `proposed_action`：可逆的提案优先操作
- `rationale`：agent 的记忆组织推理，包括提案被接受后将如何改善未来的检索、构想或规划周期
- `confidence`：`low`、`medium` 或 `high`
- `related_entities`：上下文实体 id 列表
- `candidate_ids`：适用时引用的 `dream-candidate-*` id 列表
- `evidence`：引用的上下文证据记录列表

每个提案必须通过 `candidate_ids`、`triggering_signals` 或 `evidence[*].source` 引用至少一个已知上下文引用。目标页面本身不计为证据。

在安全自动应用模式下，中/高置信度已验证提案可作为可逆 frontmatter 元数据加 append-only 审计注释被应用。低置信度提案保留供审查，不会被自动应用。仅审查模式是部署安全选择；它们不降低实际的闭环能力。

## Evidence Records

使用以下格式：

```json
{
  "source": "concepts/example",
  "summary": "Why this source supports the proposal."
}
```

`source` 可以是：

- 实体 id，例如 `papers/foo`
- 信号 id，例如 `sig-...`
- 候选 id，例如 `dream-candidate-003`
- 反复出现模式 id，例如 `pattern-memory-concepts-cache-failure-...`
- edge id，例如 `graph-edge-4` 或 `projected-edge-2`

除非该路径出现在已准备的上下文中，否则不要将原始文件路径作为 `source` 引用。验证器检查已知 id，而非散文主张。

## Operation Examples

Forgetting：

```json
{
  "operation": "forgetting",
  "target": "ideas/old-ablation-plan",
  "title": "Down-weight obsolete ablation plan",
  "proposed_action": "Keep the page, but mark it for archive review after extracting one reusable failure lesson.",
  "rationale": "The idea is failed, stale, and duplicates the lesson already captured by a newer experiment note.",
  "confidence": "medium",
  "related_entities": ["ideas/old-ablation-plan", "experiments/newer-ablation"],
  "candidate_ids": ["dream-candidate-002"],
  "evidence": [
    {"source": "dream-candidate-002", "summary": "Failed/stale cue with related experiment."}
  ]
}
```

Consolidation：

```json
{
  "operation": "consolidation",
  "target": "concepts/retrieval-cache",
  "title": "Cluster retrieval cache memory pages",
  "proposed_action": "Review these pages as one memory neighborhood; merge if they describe the same mechanism, otherwise cross-link under a shared topic.",
  "rationale": "The pages share mechanism tags and repeated summaries, so retrieval currently sees scattered fragments.",
  "confidence": "medium",
  "related_entities": ["concepts/retrieval-cache", "methods/cache-tuning"],
  "candidate_ids": ["dream-candidate-005"],
  "evidence": [
    {"source": "concepts/retrieval-cache", "summary": "Mechanism summary overlaps cache-tuning."},
    {"source": "methods/cache-tuning", "summary": "Method appears to instantiate the same memory mechanism."}
  ]
}
```

Association：

```json
{
  "operation": "association",
  "target": "methods/cache-tuning",
  "title": "Review cache tuning as a method for retrieval-memory ideas",
  "proposed_action": "Create a low-confidence review proposal to link the method with the active retrieval-memory idea.",
  "rationale": "The method and idea share evidence around memory cache behavior, but no explicit relation exists yet.",
  "confidence": "low",
  "related_entities": ["methods/cache-tuning", "ideas/retrieval-memory"],
  "candidate_ids": ["dream-candidate-008"],
  "evidence": [
    {"source": "dream-candidate-008", "summary": "Shared tags and no existing pair in the context."}
  ]
}
```

## Rejection Reasons

以下情况终结器将拒绝项目：

- `operation` 不属于三个允许值之一
- `target` 或 `related_entities` 不是已知上下文 id
- 未引用已知上下文证据
- `proposed_action` 或 `rationale` 为空
- 该项目与同一响应中的另一个提案重复

修正被拒绝的 JSON，而非弱化验证器。
