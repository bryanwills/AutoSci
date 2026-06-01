# /dream Evidence And Boundaries

`/dream` must look agentic without becoming unsafe. It can propose memory
operations, and safe auto-apply may apply narrow reversible metadata changes
plus an append-only audit note. It must not silently rewrite the wiki.

Conservative modes are safety posture, not reduced autonomy. `--propose-only`
keeps artifacts review-only for demos, and `yolo=false` avoids page archive/merge
by default, but the implemented loop can still apply validated memory updates
and rebuild downstream context.

## Evidence Sources

Acceptable evidence:

- entity ids from `dream_context.json`, such as `concepts/foo` or `methods/bar`
- candidate ids from `candidate_memory_cues`, such as `dream-candidate-003`
- recurring pattern ids from `recurring_patterns`, such as
  `pattern-memory-concepts-cache-failure-*`
- signal ids from `wiki/outputs/evolution/signals.jsonl`
- graph, projected-edge, or citation ids from the dream context
- page excerpts, summaries, tags, status, dates, and existing links in the
  dream context
- existing `/check` or lint reports as secondary evidence only

Evidence should answer: "Why did the agent believe this memory operation is
worth changing?"

## Boundary With `/check`

`/check` owns structural health:

- broken wikilinks
- malformed frontmatter
- missing required fields
- invalid enum values
- xref asymmetry
- malformed graph rows
- dangling graph endpoints
- deterministic default-field fixes

`/dream` may mention those only as weak supporting signals. They should never
be the main proposal. A proposal saying "fix missing parent_topics" is not a
dream unless the agent cites semantic evidence that the page belongs to a real
memory neighborhood.

## Safety Rules

Never:

- delete a page
- archive a page directly
- edit non-SciEvolve frontmatter
- add graph edges
- rewrite entity body sections
- create scientific claims not present in the wiki context
- treat a deterministic candidate cue as already true

Allowed:

- propose archive/down-weight/review
- propose merge/cluster/summarize/cross-link
- propose a low-confidence association for human review
- apply medium/high-confidence proposals to reversible frontmatter metadata and
  append-only audit notes through the safe auto-apply path
- cite a `/check` issue as supporting evidence
- leave the dream with zero proposals when evidence is thin

## Closed-Loop Standard

The run should leave a trace like this:

1. The system prepared a memory scene.
2. A pluggable policy runtime interpreted the scene as scientific memory, not
   just files. The runtime may be Claude Code, an API model, a local model, or a
   supplied agent response; the same validator and apply path are used.
3. The agent selected a few meaningful self-evolution operations.
4. Each operation explains how future memory retrieval, ideation, or planning
   would change if accepted.
5. The finalizer validated cited evidence.
6. Safe auto-apply wrote reversible SciEvolve metadata, an append-only audit
   note, and an application ledger entry.
7. The context brief was rebuilt so downstream skills can consume the changed
   memory state.
8. The proposal store recorded artifacts and marked applied items `applied`.

Avoid traces that look like this:

1. A deterministic scanner listed stale pages.
2. The system renamed the list "forgetting".
3. Every weak cue became a proposal.
4. The artifact never says how memory would evolve.
5. The system performs broad page rewrites without a reversible metadata trail.

## Confidence Guidance

- `high`: explicit evidence from multiple pages/signals, low ambiguity
- `medium`: evidence is clear enough for guarded safe auto-apply, or for
  review-only handling when `--propose-only` is selected
- `low`: plausible association or cleanup candidate; useful mainly as a prompt
  for later review

Use `low` freely for speculative associations. The proposal artifact is still
valuable when it honestly marks uncertainty.
