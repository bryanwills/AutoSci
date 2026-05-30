# /dream Agent Response Schema

The finalizer accepts strict JSON. Write the response to the run directory from
Step 1:

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

- `operation`: one of `forgetting`, `consolidation`, `association`
- `target`: an entity id from the context, or blank only when the proposal is a
  cluster-level memory operation
- `title`: short reviewer-facing title
- `proposed_action`: reversible proposal-first action
- `rationale`: agent's memory-organization reasoning, including how the
  proposal would improve a future retrieval, ideation, or planning cycle
- `confidence`: `low`, `medium`, or `high`
- `related_entities`: list of context entity ids
- `candidate_ids`: list of cited `dream-candidate-*` ids when applicable
- `evidence`: list of cited context evidence records

Every proposal must cite at least one known context reference through
`target`, `related_entities`, `candidate_ids`, or `evidence[*].source`.

In `--apply-safe` mode, medium/high-confidence validated proposals may be
applied as reversible `scievolve_*` frontmatter metadata. Low-confidence
proposals are kept for review and are not auto-applied.

## Evidence Records

Use this shape:

```json
{
  "source": "concepts/example",
  "summary": "Why this source supports the proposal."
}
```

`source` may be:

- entity id, such as `papers/foo`
- signal id, such as `sig-...`
- candidate id, such as `dream-candidate-003`
- edge id, such as `graph-edge-4` or `projected-edge-2`

Do not cite raw file paths as `source` unless that path appears in the prepared
context. The validator checks known ids, not prose claims.

## Operation Examples

Forgetting:

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

Consolidation:

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

Association:

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

The finalizer rejects items when:

- `operation` is not one of the three allowed values
- `target` or `related_entities` are not known context ids
- no known context evidence is cited
- `proposed_action` or `rationale` is empty
- the item duplicates another proposal in the same response

Fix rejected JSON rather than weakening the validator.
