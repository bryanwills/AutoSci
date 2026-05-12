---
description: Multi-source novelty verification — WebSearch + Semantic Scholar + PubMed + EuropePMC + wiki + Review LLM cross-verify — outputs novelty score and recommendations
argument-hint: <idea-description-or-slug> [--quick] [--verbose] [--bio-channels {auto|on|off}]
---

<!-- bio-C9: Mirror of i18n/en/skills/novelty/SKILL.md with C9 (parallel PubMed channel; EuropePMC supplement) drafted.
     Source of truth: i18n/en/skills/novelty/SKILL.md. Do not run from this path; for testing, merge to source first.
     Cross-section dependencies:
       C1 — bio fetcher tools (tools/fetch_pubmed.py, tools/fetch_europepmc.py) already exist in the runnable folder.
       C2 — same channel-set rule as /discover; both skills should resolve `auto` the same way to avoid surprises.
       A4 — domain controlled vocabulary used by the auto-detector.
     `tools/fetch_s2.py` and `tools/fetch_deepxiv.py` are unchanged; PubMed/EuropePMC are added as
     a parallel channel in Step 2 Source B (renamed Source B-bio for clarity). -->

# /novelty

> Verify the novelty of a research idea or method using multiple sources. Searches WebSearch,
> Semantic Scholar, <!-- bio-C9 --> PubMed (when bio channels are active), EuropePMC, existing wiki work, and arXiv recent preprints, then Review LLM cross-verifies.
> Outputs a novelty score (1-5), closest prior work, differentiation points, and next-step recommendations.
> Can be used standalone or called by /ideate Phase 4.

## Inputs

- `target`: one of the following:
  - free-text description of the idea (a paragraph or a few sentences)
  - slug of an ideas/ page in the wiki (e.g. `sparse-lora-for-edge-devices`)
  - paper title or arXiv URL (check novelty of that paper's method)
  - <!-- bio-C9 --> DOI / PMID / bioRxiv URL (check novelty against the bio prior-art it lives in)
- `--quick`: fast mode, skip Review LLM cross-verify (Step 3), search only
- `--verbose`: output full search results, not just summaries
- <!-- bio-C9 --> `--bio-channels {auto|on|off}` (optional, default `auto`): force-enable or force-disable PubMed + EuropePMC channels. `auto` enables when (a) the target is a DOI / PMID / bioRxiv URL, OR (b) the target slug's `domain` matches A4's bio vocabulary, OR (c) the free-text target contains any bio anchor noun (gene symbol, drug name, MeSH-style descriptor like "kinase", "PROTAC", "phospho-degron"). The auto rule mirrors `/discover`'s — they resolve the same way for the same input.

## Outputs

- **Novelty Report** (output to terminal, not written to wiki):
  - Novelty Score (1-5)
  - List of closest prior work (top 3-5)
  - Differentiation points versus each prior work
  - Review LLM cross-verify assessment (unless --quick)
  - Recommended action: proceed / modify / abandon
  - <!-- bio-C9 --> When bio channels ran: per-source breakdown — how many candidates came from S2 / PubMed / EuropePMC / DeepXiv / WebSearch — so the user can judge whether prior-art coverage was actually broad.
- This skill is a **read-only query** — it does not modify any wiki content

## Wiki Interaction

### Reads
- `wiki/papers/*.md` — search existing papers for similar methods
- `wiki/concepts/*.md` — check concept overlap
- `wiki/ideas/*.md` — check for duplication with existing ideas (especially `failure_reason` of failed ideas)
- `wiki/claims/*.md` — check the current status of claims the idea depends on
- `wiki/graph/context_brief.md` — global context to assist search
- <!-- bio-C9 --> `wiki/papers/*.md` frontmatter `domain`, `gene_symbols`, `pdb_ids`, `uniprot_ids`, `doi`, `pmid` — used by the `auto` channel detector and for bio-side dedup against external candidates

### Writes
- **None**. Novelty check is a pure query operation; it does not modify the wiki.

### Graph edges created
- **None**.

## Workflow

**Precondition**: confirm working directory is the wiki project root (containing `wiki/`, `raw/`, `tools/`).

### Step 1: Extract Method Signature

1. **If target is a slug**: read `wiki/ideas/{slug}.md`, extract title, Hypothesis, Approach sketch
2. **If target is free text**: use directly
3. **If target is an arXiv URL**: download the abstract, extract method description
4. <!-- bio-C9 --> **If target is a DOI / PMID / bioRxiv URL**: resolve via `tools/fetch_crossref.py paper <doi>` or `tools/fetch_pubmed.py paper <pmid>` to retrieve title + abstract + MeSH terms; extract method description and bio anchor entities.
5. Extract the "method signature" from the target — the core elements of the method:
   - **What**: what it does (task / goal)
   - **How**: the method used (technical approach)
   - **Why novel**: claimed innovation
6. Generate 3-5 core keywords for subsequent searches
7. <!-- bio-C9 --> When the target is bio-flavored, also generate 2-4 bio-anchor terms (gene symbols, drug names, PDB IDs, MeSH descriptors) for the PubMed / EuropePMC channels. These are passed verbatim to PubMed's MeSH-aware search and frequently surface prior art that keyword-search misses.

### Step 2: Multi-Source Search

Execute the following searches in parallel (use Agent tool for concurrency):

**Source A — Web Search (5+ queries):**
1. Direct query: `"<method-name>" + "<task>"` — exact phrase search
2. Component query: `<component-1> + <component-2> + <domain>` — component combination search
3. Survey query: `"survey" OR "review" + <task-area> + 2024 2025`
4. Competitor query: `<alternative-approach> + <same-task>`
5. Recent query: `<method-keywords> + arXiv + 2025 2026`

**Source B — Semantic Scholar + DeepXiv:**
```bash
python3 tools/fetch_s2.py search "<method-keywords>" --limit 20
python3 tools/fetch_deepxiv.py search "<method-keywords>" --mode hybrid --limit 20
```
Merge results from both sources (deduplicate by arxiv_id). DeepXiv's hybrid semantic search finds semantically similar work that S2 keyword search may miss.
- Fetch details and TLDR for top 5 results:
```bash
python3 tools/fetch_s2.py paper <s2_id>
python3 tools/fetch_deepxiv.py brief <arxiv_id>
```
Use DeepXiv brief TLDRs to quickly judge method similarity.
**If DeepXiv is unavailable**: fall back to S2 search only (original behavior).

<!-- bio-C9 -->

**Source B-bio — PubMed + EuropePMC** (active when `--bio-channels` resolves to `on`):

```bash
# PubMed: keyword + MeSH expansion. Returns up to 50 PMIDs ordered by relevance.
python3 tools/fetch_pubmed.py search "<method-keywords>" --limit 50

# Optional MeSH-aware narrowing for bio-anchor terms (gene symbols, drug names):
python3 tools/fetch_pubmed.py search "<bio-anchor>[MeSH]" --limit 30

# EuropePMC: full-text + abstract index, returns richer metadata in one call.
python3 tools/fetch_europepmc.py search "<method-keywords>" --limit 50
```

Merge results from PubMed + EuropePMC, deduping by DOI > PMID > title-fuzzy. Bio prior art is overwhelmingly in PubMed (>30M abstracts, only partially indexed by S2); missing this channel under-reports bio prior-art collisions and lets the user proceed on a method that already exists. Treat PubMed hits at full strength when scoring novelty for biological claims — do not down-weight relative to S2.

For top 5 candidates from this channel, fetch detail / abstract:
```bash
python3 tools/fetch_pubmed.py paper <pmid>            # abstract + MeSH + author list
python3 tools/fetch_europepmc.py annotations <id>     # entity-level annotations: UniProt, GO, ChEBI URIs
```

The EuropePMC `annotations` endpoint is what lets `/novelty` cheaply judge "is this candidate operating on the same protein / drug / pathway as my idea?" — it returns entity URIs alongside the abstract. Use this as the primary similarity signal for bio targets, not just abstract-bag-of-words.

**If PubMed is unavailable**: continue with EuropePMC only; note the degradation. **If both PubMed and EuropePMC are unavailable**: emit a hard warning that bio prior-art coverage is severely degraded and recommend retrying when at least one is reachable. Do **not** silently fall through to "S2 only" — bio prior art on S2 alone is known-incomplete.

**Source C — Wiki Internal Search:**
1. Scan Key idea and Method sections of all pages in `wiki/papers/`
2. Scan Definition and Variants sections of `wiki/concepts/`
3. Scan all content in `wiki/ideas/`, with special attention to:
   - ideas with status = failed and their failure_reason (anti-repetition)
   - ideas with status = proposed/in_progress (avoid internal duplication)
4. Read `wiki/graph/context_brief.md` for global perspective

**Source D — Recent arXiv Preprints:**
- Use WebSearch: `site:arxiv.org <method-keywords> 2025 2026`
- <!-- bio-C9 --> When bio channels are active, also: `site:biorxiv.org <method-keywords> 2025 2026` and `site:medrxiv.org <method-keywords> 2025 2026` for the preprint corpus the bio fetchers cannot fully cover.

### Step 3: Review LLM Cross-Verify

(Skip if `--quick`)

Submit the following to Review LLM for independent assessment:

```
mcp__llm-review__chat:
  system: "You are a senior researcher assessing the novelty of a proposed method.
           Be rigorous: if the method is essentially a recombination of known techniques
           with minor changes, score it low. Only score 4-5 if there is a genuinely new
           insight or formulation.
           When the method is bio-anchored, weight PubMed / EuropePMC hits at full
           strength — those corpora cover bio prior art that arXiv / S2 alone miss."   <!-- bio-C9 -->
  message: |
    ## Proposed Method
    {method signature from Step 1}

    ## Existing Similar Work Found
    {top 5 similar works from Step 2, with title + one-line summary, source-tagged: S2 / DeepXiv / PubMed / EuropePMC / WebSearch}   <!-- bio-C9 -->

    ## Questions
    1. Is this method genuinely novel, or a minor variation of existing work?
    2. What is the closest existing work and what's the real difference?
    3. Novelty score 1-5 with justification.
    4. If score <= 2, what modification could increase novelty?
    5. <!-- bio-C9 --> If the method is bio-anchored: are there clinical-validation or wet-lab-validation precedents that the search missed but should have surfaced? Name them by DOI/PMID.
```

### Step 4: Generate Novelty Report

Synthesize Step 2 search results and Step 3 Review LLM assessment into a structured report:

```markdown
# Novelty Report: {idea title}

## Score: {1-5}/5 — {label}

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Published | Highly similar published work exists |
| 2 | Very Similar | Very similar method exists, only minor differences |
| 3 | Incremental | Clear incremental contribution over existing work |
| 4 | Novel Combination | Creatively combines existing techniques, producing new insight |
| 5 | Fundamentally New | Proposes an entirely new paradigm or formulation |

## Search Coverage   <!-- bio-C9 -->
| Source | Hits | Used for top-5 |
|--------|------|----------------|
| Semantic Scholar | {N} | {n} |
| DeepXiv | {N} | {n} |
| PubMed | {N} | {n} |
| EuropePMC | {N} | {n} |
| WebSearch | {N} | {n} |
| Wiki internal | {N} | {n} |

## Closest Prior Work

1. **{title}** ({year}) — {one-sentence description of the similarity}
   - Source: {S2 | DeepXiv | PubMed | EuropePMC | WebSearch}    <!-- bio-C9 -->
   - Identifier: {arxiv | doi | pmid | biorxiv}                  <!-- bio-C9 -->
   - Difference: {key distinction between this method and the prior work}
   - Wiki link: [[slug]] (if it exists)
2. ...

## Review LLM Assessment
{summary of Review LLM's independent judgment}

## Anti-repetition Check
- Failed ideas in wiki: {list relevant failed ideas with failure_reason}
- In-progress ideas in wiki: {list potentially overlapping ideas}

## Recommendation
- **{proceed / modify / abandon}**
- Rationale: {one paragraph}
- If modify: suggested differentiation directions: {specific suggestions}
```

**Scoring rules (composite judgment):**
- Take the lower of Claude's search-based score and Review LLM's score (conservative principle)
- If wiki contains a failed idea whose failure_reason overlaps with this idea → lower score by 1
- If wiki contains a highly overlapping in_progress idea → mark as abandon (internal duplication)
- <!-- bio-C9 --> When bio channels were active and PubMed surfaced ≥1 hit with overlapping method + same protein target + ≤5 years old, treat as a 1 (Published) regardless of S2 results — bio prior art trumps the CS-leaning S2 corpus for bio claims.

## Constraints

- **Do not modify the wiki**: novelty check is a pure query; all results are output to terminal only
- **Conservative scoring**: underestimate novelty rather than overestimate to avoid wasting effort on known work
- **Must check failed ideas**: ideas with status=failed in wiki/ideas/ are important anti-repetition signals
- **Search coverage**: at least 5 distinct WebSearch queries + Semantic Scholar + wiki internal search; <!-- bio-C9 --> when bio channels are active, also at least 2 PubMed queries (one keyword, one MeSH-narrowed) + 1 EuropePMC query
- **Review LLM independence**: do not include Claude's own novelty judgment when submitting to Review LLM; let Review LLM assess independently
- **Cite real sources**: all prior work listed in the report must be real (returned by WebSearch/S2/<!-- bio-C9 --> PubMed/EuropePMC); do not fabricate
- <!-- bio-C9 --> **Bio channels do not down-weight wiki internal search**: PubMed coverage is broad but does not subsume the wiki's claim/idea graph. Always run wiki internal search even when bio channels return many candidates.

## Error Handling

- **WebSearch unavailable**: skip Sources A and D, rely only on S2 + wiki search; note limited coverage in report
- **Semantic Scholar API unavailable**: skip S2 portion, use DeepXiv + WebSearch as compensation
- **DeepXiv API unavailable**: skip DeepXiv portion, rely on S2 + WebSearch (fall back to original behavior)
- <!-- bio-C9 --> **PubMed unavailable**: skip the PubMed sub-channel; continue with EuropePMC. Note bio prior-art coverage is partial.
- <!-- bio-C9 --> **PubMed and EuropePMC both unavailable** (auto or `on`): emit a hard warning at the top of the report — "Bio prior-art coverage is severely degraded; consider retrying when at least one bio channel is reachable" — and continue with S2-only at the user's discretion. Do not silently produce a confident novelty score on a bio target without bio-channel confirmation.
- **Review LLM unavailable**: skip Step 3; annotate report with "Review LLM cross-verify unavailable, single-model assessment only"
- **Wiki empty**: proceed with external searches normally; annotate wiki internal search section with "wiki empty"
- **idea slug not found**: prompt user to check the slug, list available slugs in wiki/ideas/
- <!-- bio-C9 --> **DOI / PMID resolution fails on every channel**: target could not be resolved; abort with a clear message rather than guessing.

## Dependencies

### Tools（via Bash）
- `python3 tools/fetch_s2.py search "<query>" --limit 20` — Semantic Scholar keyword search
- `python3 tools/fetch_s2.py paper <s2_id>` — fetch paper details
- `python3 tools/fetch_deepxiv.py search "<query>" --mode hybrid --limit 20` — DeepXiv semantic search
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>` — fetch paper TLDR for similarity judgment
- <!-- bio-C9 --> `python3 tools/fetch_pubmed.py search "<query>" --limit <N>` — PubMed E-utilities search; supports MeSH-tagged queries
- <!-- bio-C9 --> `python3 tools/fetch_pubmed.py paper <pmid>` — fetch abstract + MeSH terms + author list
- <!-- bio-C9 --> `python3 tools/fetch_europepmc.py search "<query>" --limit <N>` — EuropePMC search
- <!-- bio-C9 --> `python3 tools/fetch_europepmc.py annotations <pmid-or-doi>` — entity-level annotations (UniProt / GO / ChEBI URIs)
- <!-- bio-C9 --> `python3 tools/fetch_crossref.py paper <doi>` — DOI resolution to title + abstract for free-text bio targets

### MCP Servers
- `mcp__llm-review__chat` — Review LLM cross-verify (Step 3)

### Claude Code Native
- `WebSearch` — multi-query web search (Step 2 Sources A + D)
- `Agent` tool — parallel execution of multi-source search (Step 2)

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` (created in Phase 2, Review LLM independence principle)
