---
description: Parse review comments → atomize concerns (Rvx-Cy) → map to wiki claims → check evidence → Review LLM stress-test → generate rebuttal; can scaffold follow-up wet-lab experiments via /exp-design
argument-hint: <review-file-or-path> [--paper-slug <slug>] [--venue <venue>] [--stress-test] [--format formal|rich] [--scaffold-followups]
---

<!-- bio-C11: Mirror of i18n/en/skills/rebuttal/SKILL.md with C11 (track promised follow-up wet-lab experiments) drafted.
     Source of truth: i18n/en/skills/rebuttal/SKILL.md. Do not run from this path; for testing, merge to source first.

     Cross-section dependencies:
       /exp-design (C4+C5+C6) — scaffolds the experiment page when a Strategy B response commits to a new
            wet-lab experiment. Bio reviewers in clinical / bio venues routinely demand additional wet-lab
            assays as a condition for acceptance; turning those promises into tracked deliverables prevents
            the rebuttal commitments from rotting.
       A5 — `experiments[*].setup.in_silico_or_wet | assay_type | cell_line | species` populated for any
            scaffolded follow-up so /check + /exp-status can track them later.
       C8 (lint_bio) — the new `triggered_by_rebuttal` field ties scaffolded experiments back to the
            review thread; missing field on a follow-up experiment is a 🟡 lint candidate (not in C8 v1
            but a natural extension).

     New skill flag `--scaffold-followups` is opt-in: legacy /rebuttal flow is unchanged when the flag is
     omitted (Strategy B still produces text-only commitments). When set, the skill collects all
     Strategy B commitments in Step 4, then optionally invokes /exp-design once per commitment with
     a `--triggered-by-rebuttal` provenance flag. -->

# /rebuttal

> Parse review comments, atomize each concern (Rvx-Cy numbering) and map it to a wiki claim,
> check whether evidence is sufficient (tracing back to wiki experiments),
> simulate reviewer follow-up questions with Review LLM (stress-test, scored 1-5), and generate
> a formal plain-text rebuttal and a rich-text rebuttal.
> Safety checks ensure no fabrication, no overpromise, full coverage.
> <!-- bio-C11 --> When `--scaffold-followups` is set, every Strategy B commitment that promises a new wet-lab or in-silico experiment is converted into a `wiki/experiments/{slug}.md` scaffold via `/exp-design`, with a `triggered_by_rebuttal` provenance field linking it back to the rebuttal. The plain-text rebuttal still ships only the textual commitment; the wiki gains a tracked deliverable.

## Inputs

- `review`: source of review comments, one of:
  - file path (e.g. `raw/reviews/reviewer1.txt`, `raw/reviews/meta-review.md`)
  - multiple file paths (comma-separated: `raw/reviews/R1.txt,raw/reviews/R2.txt,raw/reviews/R3.txt`)
  - directly pasted review text
- `--paper-slug` (optional): slug of the associated paper in wiki/outputs/, used to locate PAPER_PLAN
- `--venue` (optional): target conference/journal (ICLR / NeurIPS / ICML / ACL / CVPR / Nature / Cell / NEJM / JAMA / Lancet); affects rebuttal format and word limits
- `--stress-test` (optional, enabled by default): Review LLM simulates reviewer follow-up; disable with `--no-stress-test`
- `--format` (optional, default `formal`): output format
  - `formal`: formal plain-text rebuttal (suitable for pasting directly into submission system)
  - `rich`: rich-text version (with wiki [[links]], detailed analysis, improvement plan)
- <!-- bio-C11 --> `--scaffold-followups` (optional, default off): for every Strategy B commitment that promises a new experiment, scaffold a `wiki/experiments/{slug}.md` page via `/exp-design` (one call per commitment). Each scaffolded experiment gets a `triggered_by_rebuttal: <paper-slug>` provenance field. **Default off** because the legacy flow is text-only; opt-in keeps backward compatibility, and the user typically wants explicit confirmation before a rebuttal automatically spawns 3+ new tracked deliverables.

## Outputs

- **wiki/outputs/rebuttal-{slug}.md** — rich-text rebuttal (with [[wikilinks]], evidence tracing, analysis tables)
- **wiki/outputs/rebuttal-{slug}.txt** — formal rebuttal (plain text, suitable for pasting into submission system)
- **wiki/claims/*.md** — if a concern exposes an evidence gap, append a suggestion to `## Open questions`
- <!-- bio-C11 --> **wiki/experiments/{follow-up-slug}.md** — when `--scaffold-followups` is set, one scaffolded experiment page per Strategy B commitment, with `triggered_by_rebuttal: <paper-slug>` and `status: planned`.
- **wiki/log.md** — append log entry

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — map concerns to claims, check evidence sufficiency
- `wiki/experiments/*.md` — find experiment results supporting claims
- `wiki/papers/*.md` — find citation context for referenced papers
- `wiki/concepts/*.md` — understand the conceptual background of method-related concerns
- `wiki/ideas/*.md` — find the motivation and pilot results for ideas
- `wiki/outputs/PAPER_PLAN.md` — understand paper structure (from /paper-plan, if --paper-slug provided)
- `wiki/graph/context_brief.md` — global context
- `wiki/graph/edges.jsonl` — claim-experiment-paper relationships
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM stress-test independence

### Writes
- `wiki/outputs/rebuttal-{slug}.md` — rich-text version
- `wiki/outputs/rebuttal-{slug}.txt` — formal plain-text version
- `wiki/claims/*.md` — append reviewer-identified gaps to `## Open questions` (do not directly modify confidence/status; add suggestions only)
- <!-- bio-C11 --> `wiki/experiments/{follow-up-slug}.md` — scaffolded follow-up experiments (only when `--scaffold-followups` is set; created via `/exp-design`)
- `wiki/log.md` — append log entry

### Graph edges created
- None directly. <!-- bio-C11 --> When `--scaffold-followups` invokes `/exp-design`, that skill creates `tested_by` edges between the scaffolded experiment and its `target_claim` per its own contract; `/rebuttal` does not write graph edges directly.

## Workflow

**Precondition**:
1. Confirm working directory is the wiki project root (containing `wiki/`, `raw/`, `tools/`)
2. Read `cross-model-review.md` to confirm stress-test independence principle
3. Generate slug: `python3 tools/research_wiki.py slug "{paper-slug}-rebuttal"`

### Step 1: Parse Review Comments

(Same as legacy: read review files / pasted text; extract structure with overall score, summary, Strengths, Weaknesses, questions; output structured comments per reviewer.)

### Step 2: Atomize Concerns

(Same as legacy: split each weakness/question into Rvx-Cy atomic concerns; classify as evidence/method/missing/clarity/scope/novelty/minor; assess severity.)

### Step 3: Map Concerns to Wiki Claims

(Same as legacy: search claims/edges to find associated claim, check Evidence Status as sufficient/partial/insufficient/contradicted, choose Strategy A/B/C/D.)

### Step 4: Draft Rebuttal Responses

Draft a response for each concern according to its strategy:

**Strategy A — Evidence sufficient (respond directly):**
- Cite specific experiment results and data (annotate source, ensure traceability to wiki/experiments/)
- Point to evidence in the wiki (convert to paper citations)
- If the concern is based on a misunderstanding: politely clarify, point to the relevant Section in the paper

**Strategy B — Evidence insufficient (acknowledge + concrete plan):**
- Honestly acknowledge that current evidence is not sufficient
- Propose a concrete supplementary experiment plan (specifying assay type, cell line / species / data, replicate counts, statistical analysis, expected timeline)
- State a specific timeline and resource requirements
- Do not use vague commitments; only commit to concrete executable supplementary experiments
- <!-- bio-C11 --> **Capture commitment as a structured record** so it can become a tracked deliverable. For each Strategy B response, record:
  ```yaml
  commitment_id: Rvx-Cy
  proposed_title: "<short experiment title>"
  target_claim: "<existing claim slug if mapped, or 'unmapped'>"
  setup_hint:
    in_silico_or_wet: wet | in_silico | hybrid
    assay_type: ""             # e.g. CETSA | nanoBRET | RNA-seq | docking | MD
    species: ""
    cell_line: ""              # CVCL ID preferred
  estimated_cost_hint:         # rough numbers from the prose commitment, parsed for /exp-design
    gpu_hours: 0
    md_wallclock_hours: 0
    wet_lab_usd: 0
    fte_weeks: 0
  rationale: "<why this experiment addresses the concern>"
  ```
  These records sit in memory until Step 6e where they're either written into the rich-text rebuttal as "Suggested Experiments" only (default) or fed to `/exp-design` as scaffolded experiment pages (when `--scaffold-followups` is set).

**Strategy C — Clarity issue (commit to revision):**
(Same as legacy: acknowledge unclear expression, provide improved description, list Paper Edit plans.)

**Strategy D — Scope/Novelty challenge (argue):**
(Same as legacy: highlight differences from existing work, cite novelty-check results, point out overlooked differences.)

**Format for each response**:
```markdown
**[Rvx-Cy]** {concern summary}

{response text, 2-5 sentences, annotated sources for traceability}
```

**Safety checks (per response)**:
- [ ] No fabrication: do not fabricate data or experiment results
- [ ] No overpromise: only commit to specific executable supplementary experiments
- [ ] Cited data is recorded in wiki/experiments/
- [ ] If claim is challenged/deprecated, do not pretend it is supported
- <!-- bio-C11 --> [ ] Strategy B commitments include concrete enough setup hints (`assay_type` non-empty for wet-lab, `species` and `cell_line` for animal/cell experiments) for `/exp-design` to scaffold without further user input. If the prose commitment is too vague, surface a 🟡 in the report and ask the user to refine before scaffolding.

### Step 5: Review LLM Stress-Test

(Same as legacy: Review LLM rates each response 1-5; reviewers push back on weak responses; rewrite responses scoring ≤2; max 2 rounds; <!-- bio-C11 --> *the stress-test prompt is updated to specifically check whether Strategy B commitments are concrete enough to be scaffolded into a real experiment page — vague commitments now score lower*.)

```
mcp__llm-review__chat:
  system: "You are a critical reviewer who has just read a rebuttal to your review
           comments. You are skeptical and will push back on weak responses.
           For each rebuttal response, assess on a scale of 1-5:
           1 = unconvincing (deflection or fabrication suspected)
           2 = weak (vague, no concrete evidence; for Strategy B: too vague to scaffold)   <!-- bio-C11 -->
           3 = acceptable (addresses concern but could be stronger)
           4 = strong (concrete evidence, clear reasoning; for Strategy B: scaffoldable)   <!-- bio-C11 -->
           5 = fully convincing (compelling evidence, thorough response)
           Also check for overpromise: are commitments specific and feasible?
           When the response is Strategy B (commits to a new experiment),
           explicitly check whether the commitment names: assay type, system
           (cell line / species / dataset), readout, replicate counts,
           and a specific timeline. Generic 'we will run experiments' must
           score 1-2. A response that names CETSA on HEK293 cells, n=3 biological,
           with a 4-week timeline scores 4-5.   <!-- bio-C11 -->
           Provide a follow-up question for any response scoring <= 3."
  message: |
    ## Original Review Concerns
    {atomic concerns list with Rvx-Cy IDs}

    ## Author Rebuttal
    {drafted rebuttal responses}

    ## Please assess each response (score 1-5) and provide follow-up questions.
```

### Step 6: Format Output + Safety Check

**6a. Format formal rebuttal-{slug}.txt** (plain text, suitable for submission system):

(Same as legacy structure.)

**6b. Format rich-text rebuttal-{slug}.md**:

```markdown
# Rebuttal Analysis: {paper title}

## Coverage Summary
{table same as legacy}

## Responses
### Reviewer 1
**[Rv1-C1]** ...
**[Rv1-C2]** ...

## Evidence Gap Analysis
{same as legacy}

## Action Items

### Paper Edits
{same as legacy}

### Wiki Updates
{same as legacy}

### Suggested Experiments       <!-- bio-C11 -->
| Experiment | Target Claim | Suggested by | Setup Hint | Cost Hint | Scaffolded? |
|-----------|-------------|--------------|------------|-----------|-------------|
| ablation-dataset-x | [[claim-slug]] | Rv1-C2 | wet, CETSA, HEK293, n=3×3 | $8k wet-lab, 4 fte_weeks | ✅ wiki/experiments/ablation-dataset-x.md |
| mechanism-mutagenesis-y | [[claim-slug]] | Rv2-C3 | wet, point mutagenesis, HEK293, n=3×3 | $5k wet-lab, 3 fte_weeks | ❌ (--scaffold-followups not set) |

→ Run `/exp-design ablation-dataset-x` to refine the scaffolded experiment

## Review LLM Stress-Test Summary
{same as legacy}

## Safety Checklist
- [x] No fabrication: all cited data exists in wiki/experiments
- [x] No overpromise: all committed experiments are specific and feasible
- [x] Full coverage: {N}/{N} concerns addressed (no omissions)
- [x] Challenged claims not presented as supported
- [x] Strategy B commitments are scaffoldable (concrete assay/system/replicates)   <!-- bio-C11 -->
```

**6c. Final safety check**:
(Same as legacy.)

<!-- bio-C11 -->

**6d. Optional follow-up scaffolding** (when `--scaffold-followups` is set):

For each Strategy B commitment record collected in Step 4:

1. **Pre-flight check**: confirm the commitment's structured record has non-empty `proposed_title`, `target_claim` (or "unmapped"), and `setup_hint.in_silico_or_wet`. If any required field is missing, skip this commitment and surface a 🟡 in the report.

2. **Generate slug**:
   ```bash
   python3 tools/research_wiki.py slug "{commitment.proposed_title}"
   ```

3. **Invoke `/exp-design`** with the commitment as input:
   ```
   Skill: exp-design
   Args: "<proposed_title and rationale>" \
         --triggered-by-rebuttal {paper-slug} \
         --commitment-id {Rvx-Cy} \
         --setup-hint {parsed setup_hint as flags} \
         --auto
   ```

   Note: `/exp-design` does not currently document `--triggered-by-rebuttal`, `--commitment-id`, or `--setup-hint` as user-facing flags — these are bio-C11 follow-up additions to `/exp-design`'s SKILL.md (filed as planned tooling alongside C11). Until those flags land, `/rebuttal` falls back to invoking `/exp-design` *without* them and writing the `triggered_by_rebuttal` field into the resulting experiment page via a post-hoc `tools/research_wiki.py set-meta` call. Both paths produce the same final state.

4. **Verify the scaffold**: confirm `wiki/experiments/{slug}.md` was created with:
   - `status: planned`
   - `target_claim: <commitment.target_claim>` (or empty if "unmapped")
   - `triggered_by_rebuttal: <paper-slug>` (provenance field; required)
   - `triggered_by_concern: <Rvx-Cy>` (provenance field; required)
   - `setup` populated from `commitment.setup_hint`
   - `estimated_cost` populated from `commitment.estimated_cost_hint`

5. **Update the rich-text rebuttal**: in the "Suggested Experiments" table, mark the row's `Scaffolded?` column with a wikilink to the new page.

**6e. Update wiki**:
- For claims with evidence gaps: append reviewer-identified gaps to `## Open questions` in `wiki/claims/{slug}.md`
- Append log:
  ```bash
  python3 tools/research_wiki.py log wiki/ \
    "rebuttal | {N} concerns addressed | {M} evidence gaps | {S} stress-test avg | {F} follow-ups scaffolded"
  ```
  <!-- bio-C11: log line gains the follow-ups-scaffolded count -->

## Constraints

- **No fabrication**: never fabricate experiment data or results. Every cited number must be traceable to wiki/experiments/ with source annotated
- **No overpromise**: only commit to specific executable supplementary experiments. Use "we will run ablation on X with setup Y" not "we will investigate"
- **Full coverage**: every reviewer concern (Rvx-Cy) must have a response; omissions block output
- **Evidence traceability**: every piece of evidence cited in a response must be traceable to a wiki page with source slug annotated
- **Do not directly modify wiki claims**: rebuttal only appends suggestions to claims' Open questions; do not modify confidence/status
- **Review LLM independence**: during stress-test, follow cross-model-review.md; do not reveal response strategy to Review LLM
- **Concern ID format**: strictly use Rvx-Cy format (Rv1-C1, Rv1-C2, Rv2-C1) to ensure traceability
- **Specific commitments**: all revision commitments and experiment plans must be specific (specific Section, specific dataset, explicit metric)
- **Output to wiki/outputs/**: rebuttal files are stored uniformly in the wiki/outputs/ directory
- <!-- bio-C11 --> **Strategy B commitments must be scaffoldable**: when the rebuttal commits to a new experiment, the prose must include enough detail (assay type / system / replicate counts) to fill an `experiments/{slug}.md` page. The Review LLM stress-test enforces this.
- <!-- bio-C11 --> **Scaffolded follow-ups carry `triggered_by_rebuttal` provenance**: every experiment created via `--scaffold-followups` must have `triggered_by_rebuttal: <paper-slug>` and `triggered_by_concern: <Rvx-Cy>` in frontmatter. Future `/check` runs use this to detect un-honored rebuttal commitments (filed under "C8 future extensions" — not in C8 v1).
- <!-- bio-C11 --> **`--scaffold-followups` is opt-in**: even when bio reviewers explicitly demand follow-up experiments, the user must opt in. Spawning experiment pages silently from rebuttal text is the kind of action where surprise has a high cost (the user wakes up to 5 new "planned" experiments without remembering why).

## Error Handling

- **Review file not found**: report error, list available files under raw/reviews/
- **Review format cannot be parsed**: fall back to plain-text processing; use LLM to extract concerns; annotate in report
- **Concern cannot be mapped to a claim (unmapped)**: annotate as "unmapped"; still respond (based on paper content rather than wiki claim). <!-- bio-C11 --> *When --scaffold-followups is set and the Strategy B commitment is unmapped, scaffold the experiment with `target_claim: ""` and surface a 🟡 nudge to populate it post-hoc.*
- **Review LLM stress-test unavailable**: skip Step 5; annotate in report "stress-test skipped: Review LLM unavailable"
- **Evidence severely insufficient**: if >50% of concerns have insufficient evidence, warn the user and suggest supplementing experiments first
- **Wiki empty**: warn that wiki knowledge base is empty; suggest running /ingest to populate claims and experiments
- **All responses scored 1-2 by Review LLM**: halt output, report requires re-analysis, suggest supplementing experiments first
- <!-- bio-C11 --> **`/exp-design` invocation fails during scaffolding**: surface a 🔴 in the report; the rebuttal output ships text-only (legacy behavior); the user can rerun `/exp-design <slug>` manually with the commitment's structured record.
- <!-- bio-C11 --> **Strategy B commitment is too vague to scaffold even after the stress-test pushed back**: emit a 🟡 instead of scaffolding; the rich-text rebuttal's "Suggested Experiments" row marks `Scaffolded?` as `❌ (commitment not concrete enough)` and prompts the user to refine.

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "{title}"` — generate rebuttal slug + scaffolded experiment slug
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log entry
- <!-- bio-C11 --> `python3 tools/research_wiki.py set-meta wiki/experiments/{slug}.md triggered_by_rebuttal {paper-slug}` — fallback for setting the provenance field when `/exp-design` doesn't yet support `--triggered-by-rebuttal`

### Skills（via Skill tool）
- <!-- bio-C11 --> `/exp-design` — invoked once per Strategy B commitment when `--scaffold-followups` is set; passes the parsed commitment record as input

### MCP Servers
- `mcp__llm-review__chat` — Step 5 stress-test first round
- `mcp__llm-review__chat-reply` — Step 5 stress-test subsequent rounds

### Claude Code Native
- `Read` — read review comments, wiki pages, shared references
- `Write` — write rebuttal-{slug}.md, rebuttal-{slug}.txt
- `Glob` — find claims, experiments
- `Grep` — search wiki for concern keywords

### Shared References
- `.claude/skills/shared-references/cross-model-review.md` — Review LLM stress-test independence principle

### Suggested follow-up skills
- `/exp-design` — design supplementary experiments for concerns with insufficient evidence (also used internally when `--scaffold-followups` is set)
- `/paper-draft` — prepare revised paper (based on Paper Edits checklist)
