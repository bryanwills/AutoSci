# /dream Evidence And Boundaries

`/dream` must look agentic without becoming unsafe. It can propose memory
operations, and in `--apply-safe` mode it may apply a narrow reversible metadata
change. It must not silently rewrite the wiki.

## Evidence Sources

Acceptable evidence:

- entity ids from `dream_context.json`, such as `concepts/foo` or `methods/bar`
- candidate ids from `candidate_memory_cues`, such as `dream-candidate-003`
- signal ids from `wiki/outputs/evolution/signals.jsonl`
- graph, projected-edge, or citation ids from the dream context
- page excerpts, summaries, tags, status, dates, and existing links in the
  dream context
- existing `/check` or lint reports as secondary evidence only

Evidence should answer: "Why did the agent believe this memory operation is
worth reviewing?"

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
- apply medium/high-confidence proposals to `scievolve_*` frontmatter only when
  `--apply-safe` is explicitly requested
- cite a `/check` issue as supporting evidence
- leave the dream with zero proposals when evidence is thin

## Reviewer-Facing Standard

The reviewer should see a trace like this:

1. The system prepared a memory scene.
2. The agent interpreted the scene as scientific memory, not just files.
3. The agent selected a few meaningful self-evolution operations.
4. Each operation explains how future memory retrieval, ideation, or planning
   would change if accepted.
5. The finalizer validated cited evidence.
6. Optional `--apply-safe` wrote reversible SciEvolve metadata and an
   application ledger entry.
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
- `medium`: evidence is clear but still needs human review before applying
- `low`: plausible association or cleanup candidate; useful mainly as a prompt
  for user review

Use `low` freely for speculative associations. The proposal artifact is still
valuable when it honestly marks uncertainty.
