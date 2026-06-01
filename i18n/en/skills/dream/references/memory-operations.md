# /dream Memory Operations

`/dream` is the SciMem self-evolution pass. It is not a health checker and not a
content generator. Its job is to make the memory system visibly act on itself:
weak traces fade, scattered traces become organized, and useful latent
associations become reviewable proposals. The result should improve future
retrieval, ideation, and experiment planning.

The agent should make semantic memory judgments from the prepared context. The
tool's candidate cues are like sensory input during sleep: useful, incomplete,
and not authoritative.

`/dream` is policy-runtime agnostic. The semantic judgment may come from the
Claude Code slash-command session, an OpenAI-compatible API model, a local model,
or another agent that returns the same evidence-grounded JSON contract. This is
not a weaker form of memory evolution: the self-evolving substrate is the
closed loop that turns SciMem state into validated proposals, guarded memory
mutations, and downstream context changes. The policy runtime is replaceable;
the evidence, validation, provenance, and safe-apply semantics are not.

A proposal is only a `/dream` proposal if it explains how accepting it would
change the future behavior of memory. If the action merely repairs a schema
issue, fills a missing field, or repeats a deterministic score, it belongs
outside `/dream`.

When safe auto-apply runs, only medium/high-confidence proposals may become
actual memory changes, and only as reversible frontmatter metadata plus an
append-only audit note. This gives `/dream` a closed loop without letting it
rewrite scientific content.
Applied metadata is consumed by downstream context compilation: downweighted
pages rank lower, consolidation sources fold into their canonical target, and
associations appear in the SciEvolve guidance section.

This conservative apply boundary is an industry safety convention for
unattended memory-editing agents, not a capability boundary. The same
evidence-grounded loop can act automatically through safe apply, and explicit
`--yolo` or scheduled `yolo=true` enables high-confidence archive/merge paths.

## Forgetting

Forgetting is a reversible proposal to reduce the retrieval weight of weak,
stale, noisy, superseded, or repeated memory traces.

Good forgetting proposals:

- identify a page, note, idea, or experiment that repeatedly adds little signal
- explain why the trace pollutes future retrieval or reasoning
- describe how fading it would make later retrieval or planning cleaner
- propose reversible actions such as archive, down-weight, mark superseded, fold
  into another page, or schedule human review
- cite evidence from page content, status fields, prior failed ideas, signals,
  or existing summaries

Safe apply effect: set `scievolve_memory_weight: downweighted` and record a
`scievolve_dream_notes` entry. It does not delete or archive the page.

Weak forgetting proposals:

- "old timestamp" alone
- "orphan page" alone
- "missing field" or broken link
- any automatic deletion
- pages that are sparse only because the wiki is still young

Examples of useful forgetting rationale:

- A failed idea has no reusable lesson and keeps appearing near active ideas.
- Two short notes repeat the same discarded experiment path; one should be
  folded into the failure memory.
- A concept is marked deprecated and has been replaced by a newer concept page
  with better evidence.

## Consolidation

Consolidation organizes scattered memory traces into a stronger unit.

Use consolidation when the wiki contains related fragments that are currently
too spread out for retrieval to use well:

- near-duplicate concepts, methods, foundations, or topic fragments
- multiple pages sharing mechanism, assumption, dataset, failure mode, or open
  research question
- repeated experiment lessons that should become a reusable long-term memory
- pages that should be clustered rather than merged because they are related but
  not identical

Good consolidation should make an implicit memory neighborhood explicit. The
agent should be able to say what future question, search, or experiment plan
will become easier after the fragments are grouped.

Safe apply effect: append related pages to `scievolve_consolidates_with` on the
target page and record the applied dream id.

Distinguish proposal actions:

- `merge`: two pages are probably the same concept/method/topic
- `cluster`: several pages should be grouped under a topic or synthesis note
- `summarize`: repeated experiment or review lessons should become reusable
  memory
- `cross-link`: pages should remain separate but become easier to traverse

Avoid unsupported consolidation:

- do not infer topic membership from a missing `parent_topics` field alone
- do not merge just because tags overlap
- do not collapse different scientific objects merely because they share
  keywords
- do not rewrite page content during `/dream`

## Association

Association proposes a new high-value relation that is plausible from existing
evidence but not already explicit.

Good association proposals:

- connect existing papers, concepts, methods, topics, foundations, ideas, or
  experiments
- explain the scientific or workflow value of reviewing the link
- explain what future research move the association could unlock
- cite concrete evidence: shared paper, shared experiment, repeated mechanism,
  failure lesson, signal, or graph neighborhood
- mark confidence low when the connection is suggestive rather than established

Association is the most agentic part of `/dream`: the agent should notice
latent bridges a deterministic scanner cannot fully judge.

Useful association patterns:

- method <-> concept: a method appears to instantiate a concept but the relation
  is absent
- idea <-> method: an active idea might use a method already in long-term memory
- experiment <-> concept: a result teaches something about a broader mechanism
- paper <-> topic: a paper supports an emerging topic neighborhood
- foundation <-> method/concept: a method relies on an unstated theoretical base

Do not propose fabricated links. If the evidence is interesting but thin, write
a low-confidence review proposal instead of claiming the association as fact.

Safe apply effect: append related pages to `scievolve_associations` only when
confidence is medium or high. Low-confidence associations remain proposals.

## Choosing Proposal Count

Prefer 0-5 meaningful proposals. A no-op dream is valid when the memory is too
sparse or no association is defensible. The run should show judgment, not a
long deterministic checklist.
