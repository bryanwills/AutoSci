---
description: Multi-phase research idea generation pipeline: landscape scan → dual-model brainstorm → first-pass filter → deep validation → write to wiki
argument-hint: "[research-direction-or-topic] [--max-ideas N] [--skip-validation] [--auto] [--scope species=...|disease_area=...|data_regime=...]"
---

<!-- bio-C3: Mirror of i18n/en/skills/ideate/SKILL.md with C3 (failed-idea banlist gains scope: species / disease_area / data_regime) drafted.
     Source of truth: i18n/en/skills/ideate/SKILL.md. Do not run from this path; for testing, merge to source first.

     Cross-section dependencies:
       A4 — bio domain controlled vocabulary; the new `scope.disease_area` reuses A4 values where applicable
       A1 — `scope.data_regime` distinguishes high-data (e.g. PROTAC-DB-scale) from low-data (e.g. one-off
            phospho-PROTAC cohorts); when paired with `wiki/datasets/{slug}.versions[*].n_test`, banlist
            matching can use real numbers rather than guesswork

     The `scope` field is purely additive on `wiki/ideas/{slug}.md` frontmatter — pre-C3 ideas without it
     match the legacy "global banlist" semantics, so behavior is unchanged for the existing wiki. -->

# /ideate

> Generates high-quality research ideas through a 5-phase pipeline, grounded in the wiki knowledge base and external search.
> Phase 1 scans the research landscape (wiki + WebSearch + S2), Phase 2 runs a dual-model brainstorm (Claude + Review LLM independently),
> Phase 3 applies a first-pass filter (feasibility + quick novelty check), Phase 4 performs deep validation (calls /novelty + /review),
> Phase 5 writes to the wiki (ideas/ + graph edges), including eliminated ideas (failure reasons recorded as anti-repetition memory).
> <!-- bio-C3 --> Failed-idea matching is **scope-aware**: an idea banned in `species: human, data_regime: high-data` does not block exploration of the same architectural family in `species: plant` or in low-data regimes. Scope is optional metadata on every idea; absent scope means "global" (legacy behavior).

## Inputs

- `direction` (optional): research direction, keywords, or specific problem description. If omitted, automatically selects the most valuable direction from open_questions.md.
- `--max-ideas N` (optional, default 3): maximum number of ideas to write to the wiki
- `--skip-validation`: skip Phase 4 deep validation (fast mode: Phase 1–3 + Phase 5 only)
- `--auto`: fully automatic mode, no pause for user confirmation (used when called by /research)
- <!-- bio-C3 --> `--scope species=<value>|disease_area=<value>|data_regime=<value>` (optional, repeatable in `key=value` form, comma- or space-separated): the bio-axis scope the run should target. New ideas inherit this scope; banlist matching only fires for failed ideas whose `scope` overlaps. Omitting `--scope` for a CS direction is fine — banlist falls back to global. Omitting it for a bio direction is allowed but emits a 🟡-style warning in the IDEA_REPORT ("scope unset on a bio direction; banlist will treat all failed ideas as global"). Allowed key set is open-ended in v1; A4's bio vocabulary is the suggested controlled list for `disease_area`.

## Outputs

- `wiki/ideas/{slug}.md` — one page per idea (status: proposed), covering both top ideas and eliminated ideas
- `wiki/graph/edges.jsonl` — new idea → claim/gap relationship edges
- `wiki/graph/context_brief.md` — rebuilt compressed context
- `wiki/graph/open_questions.md` — rebuilt knowledge gap map
- **IDEA_REPORT** (printed to terminal) — pipeline execution summary, ranked results, novelty scores, <!-- bio-C3 --> scope decision and banlist hits broken down by scope-overlap reason

## Wiki Interaction

### Reads
- `wiki/graph/context_brief.md` — global context
- `wiki/graph/open_questions.md` — knowledge gaps, drives idea direction
- `wiki/ideas/*.md` — existing ideas, especially status=failed ideas and their failure_reason (banlist), <!-- bio-C3 --> *and their `scope` block when present*
- `wiki/claims/*.md` — current claims status, identifies weakly_supported and challenged claims
- `wiki/papers/*.md` — existing paper methods and results
- `wiki/concepts/*.md` — technical concepts, find cross-domain combination opportunities
- `wiki/topics/*.md` — research direction maps, SOTA and open problems
- `wiki/experiments/*.md` — existing experiment results, avoid duplication
- <!-- bio-C3 (depends on A1) --> `wiki/datasets/*.md` — `versions[*].n_test` informs the `data_regime` scope value (high-data ≥ 1000 entries, low-data < 1000)

### Writes
- `wiki/ideas/{slug}.md` — create new idea pages
- `wiki/graph/edges.jsonl` — add idea → claim/gap relationship edges (addresses_gap, inspired_by)
- `wiki/graph/context_brief.md` — rebuild
- `wiki/graph/open_questions.md` — rebuild
- `wiki/log.md` — append operation log

### Graph edges created
- `addresses_gap`: idea → claim/topic (knowledge gap the idea targets)
- `inspired_by`: idea → paper/concept (source of inspiration for the idea)

## Workflow

**Pre-conditions**:
1. Confirm working directory is the wiki project root (directory containing `wiki/`, `raw/`, `tools/`).
2. **Check wiki maturity**:
   ```bash
   python3 tools/research_wiki.py maturity wiki/ --json
   ```
   Adjust subsequent behavior based on maturity level:
   - **cold**: expand Phase 1 external search (WebSearch queries from 5 to 8, S2/DeepXiv limit from 20 to 30),
     skip wiki internal context loading (empty, no value), annotate "cold-start mode: heavier external search"
   - **warm**: standard behavior (current default)
   - **hot**: reduce Phase 1 external search (WebSearch queries from 5 to 2, S2/DeepXiv limit from 20 to 10),
     raise Phase 3 gap_alignment_bonus from +2 to +3, prioritize resolving weak claims already in the wiki
3. **Snapshot wiki state** (for the Growth Report at the end):
   Save the JSON returned by maturity to memory variable `maturity_before`
4. <!-- bio-C3 --> **Resolve current scope** (skip if direction is clearly CS — `domain` matches `NLP|CV|ML Systems|Robotics`):
   - If `--scope` was passed: parse the `key=value` pairs and stash as `current_scope`
   - Otherwise infer from `direction`: extract gene symbols / disease names / dataset names; map to `species` / `disease_area` (A4 vocabulary) / `data_regime`
   - If inference yields an empty scope on a clearly bio direction: emit the warning above; treat banlist matching as global for this run

### Phase 1: Landscape Scan

Goal: build a comprehensive view of the target domain, including existing work, knowledge gaps, and recent advances.

1. **Load wiki internal context**:
   - Read `wiki/graph/context_brief.md` (global compressed context)
   - Read `wiki/graph/open_questions.md` (knowledge gap list)
   - Read all `wiki/ideas/*.md`, extract:
     - status=failed ideas → **banlist** (with failure_reason <!-- bio-C3 --> *and `scope` block when present*)
     - status=proposed/in_progress ideas → **active list** (avoid duplication)
   - Read `wiki/claims/*.md`, find claims with status=weakly_supported or challenged → **weak claims list**
   - If `direction` is specified, filter to the relevant subset
   - <!-- bio-C3 --> **Banlist scope filter**: each entry on the banlist gains a `scope_overlap` annotation: `True` if the failed idea has no `scope` block (legacy global ban), `True` if the failed idea's scope overlaps the resolved `current_scope` on at least one key, `False` otherwise. Phase 2/3 only treat `scope_overlap == True` entries as hard blockers; the others remain visible in the report as "out-of-scope precedent — informational".

2. **External search** (run in parallel using Agent tool):
   - **WebSearch**: search for recent 6-month papers and advances in the target direction (3–5 queries)
   - **Semantic Scholar**:
     ```bash
     python3 tools/fetch_s2.py search "<direction-keywords>" --limit 20
     ```
     Fetch details for the top 5 highly-cited papers
   - **DeepXiv semantic search**:
     ```bash
     python3 tools/fetch_deepxiv.py search "<direction-keywords>" --mode hybrid --limit 20
     ```
     Fetch TLDR and keywords for top 5 most relevant results:
     ```bash
     python3 tools/fetch_deepxiv.py brief <arxiv_id>
     ```
     Semantic search supplements S2 keyword search for conceptually related papers that keyword search may miss.
   - **DeepXiv trending papers**:
     ```bash
     python3 tools/fetch_deepxiv.py trending --days 14
     ```
     Trending papers indicate community focus areas, useful for discovering trend-driven gaps.
   - **arXiv latest**: `site:arxiv.org <direction> 2025 2026`
   - **If DeepXiv is unavailable**: skip DeepXiv search and trending, rely on S2 + WebSearch only (fallback to original behavior).

3. **Compile landscape report** (internal use, not written to wiki):
   - Current SOTA methods and performance
   - Known open problems / unresolved challenges
   - Recent trends and hot topics
   - Knowledge gaps in the wiki (from gap_map)
   - Prohibited directions (from banlist), <!-- bio-C3 --> *with scope-overlap status next to each entry*

### Phase 2: Dual-Model Brainstorm

Goal: generate ideas independently with Claude and Review LLM, exploiting the diversity that comes from different model perspectives.

**Follow `shared-references/cross-model-review.md`**: Claude and Review LLM generate independently without seeing each other's output.

1. **Claude generates 6–10 ideas**:
   - Input: landscape report + wiki gaps + weak claims + banlist <!-- bio-C3 --> *(in-scope subset only; out-of-scope ban entries are listed separately as informational precedent)*
   - Strategies:
     - Cross-domain combination (method from Topic A + problem from Topic B)
     - Fill gaps in the gap_map
     - Strengthen weakly_supported claims
     - Alternative hypotheses that challenge challenged claims
     - Known limitations of SOTA → improvement directions
     - <!-- bio-C3 --> **Out-of-scope precedent translation**: if a failed idea is flagged out-of-scope, consider whether the same architecture could legitimately apply to the current scope (e.g. "single-PTM phospho predictor saturated in human / high-data" does not preclude "same backbone in plant / low-data" — the value of the precedent is its evidence about what's already crowded, not a generic ban)
   - Each idea includes: title, hypothesis (1–2 sentences), approach sketch (3–5 sentences), target claims, estimated feasibility (high/medium/low), <!-- bio-C3 --> *and a proposed `scope` block (inherits `current_scope` by default; deviate only when the idea is deliberately scoped differently)*

2. **Review LLM independently generates 4–6 ideas** (run in parallel):
   ```
   mcp__llm-review__chat:
     system: "You are a creative ML researcher brainstorming research ideas.
              Generate novel, concrete, and feasible ideas based on the given context.
              For each idea, provide: title, hypothesis (1-2 sentences),
              approach sketch (3-5 sentences), and feasibility assessment.
              When the run is bio-scoped (species / disease_area / data_regime
              are provided), prefer ideas that fit that scope; out-of-scope
              banned precedents are informational, not hard blockers."   <!-- bio-C3 -->
     message: |
       ## Research Landscape
       {landscape report from Phase 1 — gaps, SOTA, trends}

       ## Current Scope                                                 <!-- bio-C3 -->
       {current_scope key=value list, or "global / unset"}

       ## Knowledge Gaps
       {gap_map entries}

       ## Banlist (DO NOT revisit these)
       {failed ideas with failure_reason — IN-SCOPE OVERLAPS ONLY}      <!-- bio-C3 -->

       ## Out-of-scope Precedent (informational)                        <!-- bio-C3 -->
       {failed ideas whose scope does not overlap current_scope — these
        are not bans; they tell you what's already saturated elsewhere}

       ## Active Ideas (avoid duplicating)
       {proposed/in_progress ideas}

       Generate 4-6 novel research ideas that address the gaps above.
       Focus on ideas that are: (1) genuinely novel, (2) feasible within 3-6 months,
       (3) directly address a knowledge gap.
   ```

3. **Merge and deduplicate**:
   - Combine Claude's and Review LLM's ideas (10–16 candidates)
   - Remove highly similar ideas (merge ideas with the same core method, keep the more specific version)
   - Remove ideas that overlap with the **in-scope** banlist <!-- bio-C3 -->
   - Remove ideas that heavily duplicate the active list
   - Output: 8–12 candidate ideas

### Phase 3: First-Pass Filter

Goal: quickly eliminate ideas that are clearly infeasible or insufficiently novel.

Apply the following checks to each candidate idea:

1. **Feasibility check**:
   - Are GPU/compute requirements within reasonable range? (reference experiment setups already in the wiki)
   - Data availability (public datasets vs. private data)
   - Implementation complexity (achievable within 3–6 months?)
   - Label as feasibility: high/medium/low

2. **Quick novelty screening** (2–3 WebSearch queries per idea):
   - `"<idea-core-method>" + "<task>"` exact-match search
   - `<component-1> + <component-2>` component-combination search
   - If a highly similar published work is found → eliminate or flag

3. **Wiki alignment check**:
   - Does the idea address a known gap in the gap_map? (+score)
   - Does the idea target a weakly_supported claim? (+score)
   - Does the idea build on existing wiki knowledge? (+score)

4. **Filter decision**:
   - Eliminate if: feasibility=low AND quick novelty screening found similar published work
   - Eliminate if: highly correlated with a `scope_overlap == True` failure_reason in the banlist <!-- bio-C3 -->
   - Retain if: feasibility >= medium AND not eliminated
   - Output: 4–6 surviving ideas (ranked)

### Phase 4: Deep Validation

(Skip if `--skip-validation` is set; proceed directly to Phase 5.)

Apply deep validation to the top 3 ideas from Phase 3:

1. **Call /novelty** (one at a time):
   ```
   For each top idea:
   Skill: novelty
   Args: "<idea-title-and-hypothesis>"
   ```
   Record novelty score (1–5) and recommendations

2. **Call /review** (for top 2 ideas):
   ```
   Skill: review
   Args: "<idea-full-description>" --difficulty hard --focus method
   ```
   Record review score (1–10) and weaknesses

3. **Composite ranking**:
   - Final score = novelty_score × 2 + review_score + gap_alignment_bonus
   - gap_alignment_bonus: +2 if the idea directly targets a gap_map entry
   - If novelty_score <= 2 → downgrade to "modify needed"
   - If review_score <= 4 → downgrade to "major issues"

4. **If `--auto` is not set**: display ranked results in terminal, wait for user confirmation or adjustment

### Phase 5: Write to Wiki

Write the validated ideas to the wiki (including eliminated ideas, with their elimination reasons recorded).

1. **Write top ideas** (status: proposed):
   For the top `--max-ideas` ideas:
   ```bash
   # generate slug
   python3 tools/research_wiki.py slug "<idea-title>"
   ```
   Create `wiki/ideas/{slug}.md` **following the CLAUDE.md ideas template exactly** (all fields required; `lint.py` enforces `status` and `priority`):
   ```yaml
   ---
   title: "<idea title>"
   slug: "<idea-slug>"
   status: proposed
   origin: "ideate: <short description of the driving gap / weak claim / paper>"
   origin_gaps: []           # [[claim-slug]] list — claims or topics this idea targets
   tags: []                  # 2-5 topic tags (inherit from target claims / direction)
   domain: ""                # NLP / CV / ML Systems / Robotics (inherit from direction)
   priority: 3               # 1-5 — see Priority computation below
   pilot_result: ""          # empty until /exp-eval fills it
   failure_reason: ""        # empty for proposed ideas
   linked_experiments: []    # empty until /exp-design creates experiments
   date_proposed: YYYY-MM-DD
   date_resolved: ""         # empty until validated/failed
   # bio-C3: optional scope block; inherits current_scope by default. Pre-C3
   # ideas without this block fall back to "global" semantics.
   scope:
     species: ""              # e.g. human | mouse | plant | microbial; empty = global
     disease_area: ""         # e.g. cancer-bio | structural-bio (A4 vocab); empty = global
     data_regime: ""          # high-data | low-data | unknown; empty = global
   ---
   ```

   **Priority computation** (maps Phase 4 signals into the 1-5 scale):
   - If `--skip-validation`: default `priority = 3`
   - Otherwise start from `novelty_score` (1-5 from /novelty)
   - `+1` if `gap_alignment_bonus > 0` (directly targets a gap_map entry)
   - `-1` if `review_score <= 4` (major issues downgrade)
   - Clamp to `[1, 5]`

   **Body sections** (exactly match the CLAUDE.md template — do not rename):
   ```markdown
   ## Motivation
   Which gap / weakly_supported claim / paper limitation drives this idea. Reference wiki pages via `[[slug]]`.

   ## Hypothesis
   1-2 sentences stating the testable proposition.

   ## Approach sketch
   3-5 sentences on the proposed method. Reference `[[paper-slug]]` or `[[concept-slug]]` for any component borrowed from existing work.

   ## Expected outcome
   What success looks like (metric / claim status change), plus the Phase 4 novelty & review summary:
   - Novelty score: N/5 — <one-line reason from /novelty>
   - Review score: M/10 — <one-line summary from /review>

   ## Risks
   Feasibility rating (high/medium/low) + top 2-3 risks. Include the main weaknesses surfaced by /review.

   ## Pilot results
   (empty — filled by /exp-eval after running the experiment)

   ## Lessons learned
   (empty — filled by /exp-eval after the idea reaches a terminal status)
   ```

2. **Write eliminated ideas** (status: failed):
   For ideas eliminated in Phase 3/4, also create `wiki/ideas/{slug}.md` using the **same template above**, with these overrides:
   - `status: failed`
   - `priority: 1` (eliminated ideas never block higher-priority work)
   - `date_resolved: YYYY-MM-DD` (today)
   - `failure_reason: "[filter] <specific elimination reason>"` — the `[filter]` prefix distinguishes ideate-stage eliminations from post-experiment failures (which /exp-eval tags differently). Examples: `"[filter] highly similar published work exists: <paper-title>"`, `"[filter] insufficient feasibility: GPU requirements too high"`
   - <!-- bio-C3 --> `scope:` populated with the eliminated idea's intended scope (NOT a global ban) — this lets a later run in a different scope correctly bypass this entry. If the elimination reason is genuinely scope-independent (e.g. "core math is wrong"), explicitly leave all three sub-fields empty AND state in the failure_reason that the ban is global (e.g. `"[filter] global: core derivation is incorrect"`).
   - Body `## Motivation` and `## Hypothesis` should still be filled (so future banlist matching has content); `## Approach sketch` may be brief; `## Expected outcome` and `## Risks` can note why the idea was eliminated
   - These failed ideas become the banlist for future ideate runs

3. **Add graph edges**:
   ```bash
   # for each idea
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "ideas/{slug}" --to "claims/{target-claim}" \
     --type addresses_gap --evidence "Generated by ideate"

   python3 tools/research_wiki.py add-edge wiki/ \
     --from "ideas/{slug}" --to "papers/{source-paper}" \
     --type inspired_by --evidence "Inspired by method in {paper-title}"
   ```

4. **Rebuild derived data**:
   ```bash
   python3 tools/research_wiki.py rebuild-context-brief wiki/
   python3 tools/research_wiki.py rebuild-open-questions wiki/
   ```

5. **Append log**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "ideate | {N} ideas proposed, {M} ideas filtered out | direction: {direction} | scope: {scope_summary}"
   ```
   <!-- bio-C3: log line gains the resolved scope summary for grep-ability -->

6. **Print IDEA_REPORT to terminal**:
   ```markdown
   # Idea Generation Report

   ## Pipeline Summary
   - Direction: {direction}
   - Scope: {current_scope or "global / unset"}                          <!-- bio-C3 -->
   - Phase 1: Scanned {N} external papers, {M} wiki gaps identified, {B} banlist entries (in-scope: {B_in}, out-of-scope precedent: {B_out})   <!-- bio-C3 -->
   - Phase 2: Generated {X} candidates (Claude: {a}, Review LLM: {b})
   - Phase 3: {Y} survived initial filter (from {X})
   - Phase 4: Deep validation on top {Z}
   - Phase 5: {K} ideas written to wiki

   ## Top Ideas (ranked)

   | Rank | Idea | Scope | Novelty | Review | Gap Align | Status |   <!-- bio-C3 -->
   |------|------|-------|---------|--------|-----------|--------|
   | 1 | [[slug]] | human / cancer-bio / high-data | 4/5 | 7/10 | +2 | proposed |
   | 2 | [[slug]] | (inherits current) | 3/5 | 6/10 | +0 | proposed |

   ## Filtered Out
   | Idea | Scope | Reason | Status |   <!-- bio-C3 -->
   |------|-------|--------|--------|
   | [[slug]] | (intended scope) | Similar published work exists | failed |
   | [[slug]] | global | Core derivation is incorrect | failed |

   ## Banlist Trace                                                    <!-- bio-C3 -->
   In-scope hits ({B_in}):
   - [[failed-slug]] → blocks "{candidate-title}" (overlap: species=human, data_regime=high-data)
   Out-of-scope precedents ({B_out}, informational only):
   - [[failed-slug]] (scope: human / high-data) — current scope is plant / low-data; not blocked but worth knowing

   ## Suggested Next Steps
   - Run `/exp-design {top-idea-slug}` to design experiments
   - Run `/novelty` on any idea before investing time

   ## Wiki Growth
   | Metric | Before | After | Delta |
   |--------|--------|-------|-------|
   | Papers | {before} | {after} | +{delta} |
   | Claims | {before} | {after} | +{delta} |
   | Ideas | {before} | {after} | +{delta} |
   | Edges | {before} | {after} | +{delta} |
   | Maturity | {before_level} | {after_level} | {unchanged/upgraded} |
   (Only rows with delta != 0 are shown. Data is computed by comparing `maturity_before` from the pre-condition step against a fresh `maturity --json` call here.)
   ```

## Constraints

- **Auto-switch to cold-start mode when wiki is cold**: expand external search (WebSearch 8 queries, S2/DeepXiv limit 30), do not block execution
- **Every idea must have wiki grounding**: each idea must reference at least 2 wiki pages (paper/concept/claim)
- **Banlist must be loaded**: Phase 1 must read failed ideas' failure_reason; Phase 2/3 must check for overlap
- <!-- bio-C3 --> **Banlist matching is scope-aware**: a failed idea blocks a candidate only when its `scope` overlaps the current run's `current_scope` on at least one key, OR when the failed idea has no `scope` block (legacy global ban). Out-of-scope precedents must still be visible in the report but never block.
- <!-- bio-C3 --> **Failed ideas should record their scope, not the global scope**: when writing an eliminated idea, populate `scope` with the *intended* scope of that idea, not the run's current scope. The only exception is when the elimination reason is provably scope-independent — then leave `scope` empty AND prefix the failure_reason with `[filter] global:`.
- **Review LLM independence**: in Phase 2, Review LLM does not see Claude's idea list (cross-model-review.md)
- **Eliminated ideas are also written to wiki**: status=failed + failure_reason, as anti-repetition memory
- **No fabrication**: all ideas must be derived from existing wiki knowledge or external search results; do not invent non-existent papers or methods
- **Slug uniqueness**: check whether the same slug already exists in wiki/ideas/ before creating
- **Graph edges via tools/research_wiki.py**: do not manually edit edges.jsonl

## Error Handling

- **Wiki is empty**: proceed with external search (Phase 1 sources B/C/D), but skip wiki internal context; prompt user to build the knowledge base first
- **WebSearch unavailable**: skip external search, generate ideas from wiki internal knowledge only (degraded mode, noted in report)
- **Semantic Scholar API unavailable**: skip S2 search, rely on DeepXiv + WebSearch for compensation
- **DeepXiv API unavailable**: skip DeepXiv search and trending, fall back to S2 + WebSearch (original behavior)
- **Review LLM unavailable**: Phase 2 uses Claude only (no dual-model diversity, noted in report)
- **/novelty fails**: if novelty fails for a single idea in Phase 4, mark "novelty unverified" and continue
- **/review fails**: if review fails in Phase 4, mark "unreviewed" and continue; recommend user manually runs /review
- **Slug conflict**: if the same slug already exists in wiki/ideas/, append a numeric suffix (e.g. `sparse-lora-v2`)
- **All ideas eliminated**: still write to wiki (status: failed); report recommends user broaden the search direction or /ingest more papers
- <!-- bio-C3 --> **`--scope` parsed but key is unknown** (not in `species|disease_area|data_regime`): emit a warning, drop the unknown key, continue with the remaining valid keys. Do not silently treat unknown keys as "match any".
- <!-- bio-C3 --> **Bio direction with empty scope**: emit the warning at Step 4 of pre-conditions; banlist matching falls back to global. The IDEA_REPORT shows a "scope: global / unset (warning)" row.

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py maturity wiki/ --json` — check wiki maturity + Growth Report
- `python3 tools/research_wiki.py slug "<title>"` — generate slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild query_pack
- `python3 tools/research_wiki.py rebuild-open-questions wiki/` — rebuild gap_map
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/fetch_s2.py search "<query>" --limit 20` — Semantic Scholar search
- `python3 tools/fetch_deepxiv.py search "<query>" --mode hybrid --limit 20` — DeepXiv semantic search
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — fetch paper TLDR
- `python3 tools/fetch_deepxiv.py trending --days 14` — trending paper trends

### Skills（via Skill tool）
- `/novelty` — Phase 4 deep novelty validation
- `/review` — Phase 4 cross-model review

### MCP Servers
- `mcp__llm-review__chat` — Phase 2 Review LLM independent brainstorm

### Claude Code Native
- `WebSearch` — Phase 1 external search, Phase 3 quick novelty screening
- `Agent` tool — Phase 1 parallel search, Phase 2 parallel brainstorm

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Phase 2 Review LLM independence principle
