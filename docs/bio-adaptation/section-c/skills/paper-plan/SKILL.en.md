---
description: Compile a paper outline from the claim graph — evidence map → narrative structure → section plan + figure plan + citation plan, Review LLM review mandatory
argument-hint: <claim-slugs...> --venue <ICLR|NeurIPS|ICML|ACL|CVPR|IEEE|Nature|Science|Cell|NEJM|JAMA|Lancet|...> [--title <working-title>] [--paper-style cs|bio|clinical]
---

<!-- bio-C10: Mirror of i18n/en/skills/paper-plan/SKILL.md with C10 (paper_style: cs|bio|clinical) drafted.
     Source of truth: i18n/en/skills/paper-plan/SKILL.md. Do not run from this path; for testing, merge to source first.

     Cross-section dependencies:
       A4 — bio domain controlled vocabulary; auto-detection rule for `paper_style` reads from
            `claims[*].domain` and the venue list
       A6 — `estimated_cost` block surfaces in bio papers' Methods section under "Resources"
       A7 — claim evidence types `wet_lab_validated` / `clinical_validated` / `mechanistic_basis`
            inform what kind of Results subsections the bio template should generate

     Per-style templates (planned) live at:
       skills/paper-draft/references/templates/{cs,bio,clinical}/
     Templates are NOT yet authored — referenced as planned follow-up tooling. /paper-plan still
     prescribes the section structure inline below; /paper-draft generates the LaTeX from those
     templates once they land. -->

# /paper-plan

> Compile a paper outline from the wiki's claim graph.
> Input target claims (status: supported or weakly_supported), specify the target venue,
> compile an evidence map from the wiki → determine narrative structure → generate a section outline + figure plan + citation plan.
> Review LLM review is a mandatory step (acting as area chair to assess outline persuasiveness).
> Output PAPER_PLAN.md to wiki/outputs/.
>
> Key distinction: the outline is claim-graph-driven — each section exists because it supports a claim,
> not because paper convention requires that section.
>
> <!-- bio-C10 --> The outline structure depends on `paper_style`: `cs` (Intro → Related Work → Method → Experiments → Conclusion); `bio` (Intro → Results → Discussion → Methods, with Methods de-emphasized and Results as the main scaffold); `clinical` (Intro → Methods → Results → Discussion, with Statistical Analysis as a dedicated subsection and explicit Limitations). Citation style and author-list expectations follow the same dispatch.

## Inputs

- `claims`: list of target claim slugs (space-separated)
  - each claim should have status `supported` or `weakly_supported`
  - if `proposed` or `challenged` claims are included, warn but continue
- `--venue` (required): target venue, determines page limit and format requirements
  - cs: `ICLR` / `NeurIPS` / `ICML` / `ACL` / `CVPR` / `IEEE`
  - <!-- bio-C10 --> bio: `Nature` / `Cell` / `Science` / `Nature Methods` / `Nature Biotech` / `Nat. Commun.` / `eLife` / `bioRxiv`
  - <!-- bio-C10 --> clinical: `NEJM` / `JAMA` / `Lancet` / `BMJ` / `Annals` / `medRxiv`
- `--title` (optional): working title; if omitted, generated from target claims
- <!-- bio-C10 --> `--paper-style {cs|bio|clinical}` (optional, default `auto`): drives the per-style outline template, citation conventions, and Review LLM area-chair persona. `auto` picks based on:
  - venue → cs (when in the CS list above), bio (Nature family + bioRxiv etc.), clinical (NEJM family + medRxiv);
  - then `claims[*].domain`: any A4 bio value (`structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics`) → bio; `clinical-translation` → clinical; otherwise → cs;
  - tie-break on disagreement: emit a warning and prefer venue. The user can always pin `--paper-style` to override.

## Outputs

- `wiki/outputs/paper-plan-{slug}-{date}.md` — complete paper plan (PAPER_PLAN.md), <!-- bio-C10 --> *with `paper_style` recorded in the metadata block*
- `wiki/graph/edges.jsonl` — new derived_from edges (plan → source claims/papers)
- `wiki/graph/context_brief.md` — rebuilt
- `wiki/log.md` — appended log entry
- **PAPER_PLAN_REPORT** (printed to terminal) — plan summary

## Wiki Interaction

### Reads
- `wiki/claims/*.md` — status, confidence, evidence list, conditions of target claims, <!-- bio-C10 --> *plus `evidence[*].type` (A7) and `.grade` for the bio Results subsection mapping*
- `wiki/experiments/*.md` — supporting experiments for claims (results, metrics, key_result), <!-- bio-C10 --> *plus `setup.in_silico_or_wet`, `estimated_cost.*`, `statistical_protocol` to feed the bio Methods section*
- `wiki/papers/*.md` — evidence source papers (Method, Results, Related)
- `wiki/concepts/*.md` — technical concepts involved (supports Method section writing)
- `wiki/topics/*.md` — research direction context (supports Introduction positioning)
- `wiki/ideas/*.md` — motivation and hypothesis of original ideas
- `wiki/graph/context_brief.md` — global context
- `wiki/graph/open_questions.md` — knowledge gaps (annotate paper limitations)
- `wiki/graph/edges.jsonl` — relationship graph (build narrative logic chain)
- <!-- bio-C10 (depends on A1) --> `wiki/datasets/*.md` — dataset access tier and version pinning, surfaced in bio/clinical Methods section
- `.claude/skills/shared-references/academic-writing.md` — writing principles
- `.claude/skills/shared-references/citation-verification.md` — citation discipline

### Writes
- `wiki/outputs/paper-plan-{slug}-{date}.md` — paper plan file
- `wiki/graph/edges.jsonl` — derived_from edges
- `wiki/graph/context_brief.md` — rebuilt
- `wiki/log.md` — appended operation log

### Graph edges created
- `derived_from`: paper-plan → claims (which claims the plan is derived from)
- `derived_from`: paper-plan → papers (which papers the plan cites)

## Workflow

**Precondition**: confirm the working directory is the wiki project root (the directory containing `wiki/`, `raw/`, `tools/`).

### Step 1: Load Claim Graph

1. Read `wiki/claims/{slug}.md` for all target claims
2. For each claim, collect its evidence list:
   - each evidence item's source (paper slug or experiment slug)
   - evidence type (supports / contradicts / tested_by / invalidates, <!-- bio-C10 --> *plus the A7 bio extensions: `wet_lab_validated` / `clinical_validated` / `mechanistic_basis` / `correlative` / `predicts`*)
   - evidence strength (weak / moderate / strong) <!-- bio-C10 --> *and optional `grade` (very-low / low / moderate / high) per A7*
3. For each evidence source, read the corresponding wiki page:
   - `wiki/experiments/{source}.md` → key_result, metrics, outcome
   - `wiki/papers/{source}.md` → Method, Results
4. Load relevant edges from `wiki/graph/edges.jsonl` to build relationships between claims
5. Read `wiki/graph/context_brief.md` for global context
6. Read `wiki/graph/open_questions.md` to annotate known limitations

**Validation**:
- If any target claim has status `proposed`: warn "claim is unvalidated; paper may lack evidence support"
- If any target claim has confidence < 0.5: warn "claim confidence is low; consider running more experiments first"
- If no experiment evidence supports any claim: error "at least one experimental result is required to plan a paper"

<!-- bio-C10 -->

### Step 1b: Resolve `paper_style`

Resolve to one of `{cs, bio, clinical}` before any structural decisions in Step 3:

1. If `--paper-style` was passed, use it. Stop.
2. Map `--venue` → tentative style using the venue lists in the Inputs section above.
3. Aggregate `claims[*].domain` and pick the dominant A4 bucket:
   - any of `structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio | bioinformatics` → bio
   - `clinical-translation` → clinical
   - none of the above → cs
4. If venue and domain agree: use the agreed value. If they disagree: emit a warning and prefer the venue (the venue's format requirements are not negotiable; the domain mismatch is a content concern, not a structural one).
5. Record the resolved `paper_style` in the PAPER_PLAN.md metadata block.

### Step 2: Compile Evidence Map from Wiki

Generate a structured matrix mapping claims → evidence → sections:

```markdown
| Claim | Status | Confidence | Evidence Sources | Type/Grade | Strength | Paper Section |   <!-- bio-C10 -->
|-------|--------|-----------|-----------------|------------|----------|---------------|
| [[primary-claim]] | supported | 0.85 | exp-main, paper-A | tested_by / moderate | strong | Method + Exp 5.2 |
| [[supporting-claim-1]] | supported | 0.75 | exp-ablation-1 | wet_lab_validated / high | moderate | Results 3.2 |   <!-- bio-C10 -->
| [[mechanism-claim]] | supported | 0.7 | exp-mechanism | mechanistic_basis / moderate | moderate | Results 3.3 |   <!-- bio-C10 -->
```

Map claims to paper structure along each dimension:
- **Target claim** → core contribution, drives Abstract + Introduction + Method/Results
- **Decomposition claims** → factor contributions, drives Ablation/Mechanism subsections
- **Contextual claims** → background knowledge, drives Related Work + Introduction
- <!-- bio-C10 --> **Mechanism / wet-lab claims** (A7 evidence types) → drive dedicated Results subsections in bio style; in cs style they fold into Experiments

### Step 3: Determine Narrative Structure

Follow the hourglass principle in `shared-references/academic-writing.md`:

1. **Identify the paper's core storyline**:
   - Gap (extracted from ideas/ motivation or gap_map)
   - Solution (extracted from target claim's approach)
   - Evidence (extracted from experiments' results)
   - Impact (inferred from claim confidence + scope)

2. **Determine the narrative angle**:
   - What problem does the paper solve? (problem-driven vs. method-driven vs. data-driven)
   - Who is the primary audience? (theory / systems / applications, <!-- bio-C10 --> *or for bio: structure / mechanism / discovery / clinical*)
   - How does it differentiate from the 3 most relevant recent papers?

3. **Establish section → claim mapping**:
   Every section must support at least one claim. A section with no claim support is filler and should be removed.

### Step 4: Generate Section Outline

Generate the outline according to venue format requirements **and the resolved `paper_style`**. <!-- bio-C10 --> Each section includes claims-addressed, paragraph plan, key citations, planned figures/tables.

<!-- bio-C10 -->

#### Style: cs (legacy default)

```markdown
## 1. Introduction (1.5 pages)
## 2. Related Work (1 page)
## 3. Method (2-3 pages)
## 4. Experiments (2-3 pages)
## 5. Conclusion (0.5 page)
```

(Section breakdown unchanged from the legacy template — see source SKILL.md for the full per-section paragraph plan.)

#### Style: bio

```markdown
## 1. Introduction (~1 page; 4-6 paragraphs)

### Claims addressed
- Gap claim
- Contribution claim (target)

### Paragraph plan
1. Broad biological / clinical context (the *why this matters* paragraph)
2. Specific knowledge gap, with a clear "what we did not yet know"
3. Conceptual approach in plain language (no equations)
4. Headline result preview (1-2 sentences with the strongest number)
5. (Optional) Implication / impact

### Key citations
- {3-5 papers establishing the gap and methods used}

---

## 2. Results (3-5 pages — the main scaffold)

### Claims addressed
- Target claim → Section 2.1 (headline figure)
- Each supporting/decomposition claim → its own subsection

### Subsection plan (one per claim)
- 2.1 {Headline result} — driven by [[target-claim]]; figure-first
- 2.2 {Mechanism / dose-response / cross-context} — A7 mechanism / dose_response / cross_context evidence
- 2.3 {Ablation / negative-control} — driven by decomposition claims
- 2.4 {Wet-lab validation or clinical correlate}
- (each subsection: 1 figure ± 1 table; ~0.5-1 page text)

### Figures
- Figure 1: Headline result with summary statistic + CI / replicate matrix
- Figure 2: Mechanism schematic + supporting data
- Figure 3-N: per-subsection figure
(each figure must include sample sizes, biological vs technical replicate distinction
when applicable, and statistical test name in the caption)

---

## 3. Discussion (~1.5 pages)

### Claims addressed
- Synthesis of all target/supporting claims
- Limitations (from gap_map and claim conditions)
- Implications and biological / clinical relevance

### Paragraph plan
1. Restate the headline finding in biological terms
2. Place the result in the context of prior work (this is where most lit citation density lands in a bio paper)
3. Mechanism / model proposed
4. Limitations (explicit; reviewers will look for this)
5. Implications and future directions

---

## 4. Methods (~2 pages, often de-emphasized; many bio venues allow longer Methods in supplementary)

### Claims addressed
- Reproducibility-supporting (no new claims; rather, *enables* claims to be tested)

### Subsection plan (one per assay/computational pipeline)
- 4.1 Datasets and code availability (link to wiki/datasets/{slug} versions[]; A1 dependency)
- 4.2 Wet-lab assays — for each: cell line (CVCL ID), antibodies (RRID), reagent catalog, biological × technical replicate matrix (C6 statistical_protocol)
- 4.3 Computational methods — model versions, force fields, dataset version pinning, random seed protocol
- 4.4 Statistical analysis — bootstrap CI / stratified k-fold / replicate aggregation per C6
- 4.5 Compute / wet-lab resources — gpu_hours / md_wallclock_hours / wet_lab_usd / fte_weeks (A6)
```

#### Style: clinical

```markdown
## 1. Introduction (0.5-1 page)
- Clinical context, prevalence, current standard of care
- Specific question this study answers
- Hypothesis (often pre-registered) and primary endpoint

## 2. Methods (1.5-2 pages — front-loaded, unlike bio)
- 2.1 Study design (RCT / observational / retrospective / prospective)
- 2.2 Participants — inclusion/exclusion criteria, recruitment
- 2.3 Interventions / Procedures
- 2.4 Outcomes — primary, secondary, safety
- 2.5 Statistical analysis — pre-registered plan, sample size justification, primary analysis vs sensitivity analyses
- 2.6 Ethics & registration — IRB approval, NCT ID (B2 dependency: clinical_trial_for edge metadata.nct_id)

## 3. Results (2-3 pages)
- 3.1 Participant flow (Figure 1: CONSORT diagram)
- 3.2 Baseline characteristics (Table 1)
- 3.3 Primary outcome
- 3.4 Secondary outcomes
- 3.5 Safety / adverse events

## 4. Discussion (1-1.5 pages)
- Principal findings
- Comparison with prior evidence
- Strengths and limitations (explicit; mandatory in clinical style)
- Generalizability
- Conclusions / implications

## (No "Conclusion" section as a separate top-level — it folds into Discussion's last paragraph)
```

**Page budget**: allocated by `--venue` (refer to the venue table in academic-writing.md); total section pages <= venue main-body limit. Bio venues often have explicit word-count caps in addition to page caps; cite both.

### Step 5: Figure Plan

Design each planned figure/table. Figure conventions vary by style:

- **cs**: line plots (scaling curves), tables (main comparison + ablation), architecture diagrams. Minimal narrative captions.
- <!-- bio-C10 --> **bio**: figure-first storytelling. Each figure has a multi-panel structure (a, b, c, ...) with the headline figure carrying the strongest data. Captions are *narrative* (often 4-6 sentences), include sample sizes, replicate types (biological vs technical), statistical test name, and significance thresholds. Mechanism schematics are usually figure 1 or 2.
- <!-- bio-C10 --> **clinical**: Figure 1 is almost always a CONSORT participant flow diagram. Table 1 is baseline characteristics. Forest plots / Kaplan-Meier curves are common. Captions name the analysis population (ITT / per-protocol).

```markdown
## Figure Plan

### Figure 1: {style-dependent}
- Type: {diagram | comparison-table | CONSORT}
- Source: {experiment slugs and the claim it supports}
- Caption-style: {cs minimal | bio narrative-with-stats | clinical analysis-population-named}
```

### Step 6: Citation Plan

Following `shared-references/citation-verification.md`. Citation conventions vary by style:

- **cs**: author-year (e.g. `\citep{vaswani2017attention}`); typical paper has 30-60 citations.
- <!-- bio-C10 --> **bio**: Vancouver / numeric ordered by appearance (e.g. `\cite{ref}` rendered as superscript `[1]`). Typical Nature paper has 30-50 references in main text + extended references in supplementary; Cell can carry 80+ in main text.
- <!-- bio-C10 --> **clinical**: Vancouver, with explicit reporting of trial registration ID (NCT) and pre-registration (e.g. on ClinicalTrials.gov / OSF). Typical clinical trial paper has 30-40 citations.

1. List all wiki papers referenced via `[[slug]]` in the outline
2. For each paper, pre-fetch BibTeX:
   - DBLP first, then CrossRef, then S2 — *for bio papers, prefer CrossRef + PubMed E-utilities order, since DBLP coverage of bio venues is sparse*   <!-- bio-C10 -->
   - Success: record BibTeX key + source
   - Failure: mark `[UNCONFIRMED]`
3. Generate citation coverage report:
   ```
   Citations: 35 total, 30 verified (CrossRef: 22, PubMed: 5, DBLP: 3), 5 [UNCONFIRMED]
   ```
4. For [UNCONFIRMED] entries, provide suggested URLs for manual verification

### Step 7: Review LLM Review (mandatory)

The Review LLM persona is dispatched on `paper_style`:

```
mcp__llm-review__chat:
  system: |
    {style-specific persona, see below}
  message: |
    ## Paper Outline
    {complete outline from Step 4}
    ## Resolved style: {paper_style}
    ## Evidence Map
    {evidence map from Step 2}
    ## Figure/Table Plan
    {plan from Step 5}
    ## Citation Coverage
    {report from Step 6}
    ## Questions for Review
    {style-specific questions}
```

Personas (pick one based on `paper_style`):

- **cs**: "You are an area chair at {venue} reviewing a paper outline. Assess: Is the narrative convincing? Does every section serve a clear purpose? Are the experiments sufficient to support the claims? Is the related work coverage adequate? Are there obvious gaps that reviewers will attack?"
- <!-- bio-C10 --> **bio**: "You are an editor at {venue} (Nature family / Cell family / eLife) reviewing a paper outline. Assess whether the Results section is figure-first and tells a coherent biological story; whether each Results subsection has the right experimental signature (mechanism via point mutagenesis or chemical probe; dose-response; orthogonal validation; cross-context); whether sample sizes and statistics are reported; whether the Methods section will let an outsider reproduce the work; whether limitations are explicit."
- <!-- bio-C10 --> **clinical**: "You are an editor at {venue} (NEJM / JAMA / Lancet) reviewing a clinical paper outline. Assess whether: pre-registration and ethics are clearly cited; primary endpoint is unambiguously defined and analyzed in the pre-registered way; CONSORT diagram is present; baseline characteristics table is comprehensive; analyses are pre-specified; limitations are explicit and not hedged. Reject overpromising or post-hoc reframing."

Revise the outline based on Review LLM feedback (add sections, adjust page budget, add figures/tables, correct narrative structure).

### Step 8: Write to Wiki

1. **Generate slug**:
   ```bash
   python3 tools/research_wiki.py slug "<working-title>"
   ```

2. **Write PAPER_PLAN.md**:
   Create `wiki/outputs/paper-plan-{slug}-{date}.md` containing:
   - Metadata (venue, title, date, target claims, **paper_style**)   <!-- bio-C10 -->
   - Evidence Map (Step 2)
   - Complete section outline (Step 4, with Review LLM revisions)
   - Figure/Table Plan (Step 5)
   - Citation Plan + coverage report (Step 6)
   - Review LLM Review Summary (Step 7 key feedback and revision record)

3. **Add graph edges**: same as legacy.

4. **Rebuild derived data**: same as legacy.

5. **Append log**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "paper-plan | {venue} {paper_style} paper outline for [[{slug}]] | claims: {claim-list} | citations: {verified}/{total}"
   ```
   <!-- bio-C10: log line gains paper_style for grep-ability -->

6. **Print PAPER_PLAN_REPORT to terminal**:
   ```markdown
   # Paper Plan Report

   ## Meta
   - Title: {working title}
   - Venue: {venue}
   - Paper style: {cs | bio | clinical}    <!-- bio-C10 -->
   - Page limit: {N} pages
   - Date: {date}

   ## Claims → Sections
   | Claim | Confidence | Type | Section |   <!-- bio-C10: type column reflects A7 evidence type -->
   |-------|-----------|------|---------|

   ## Page Budget
   | Section | Pages | Claims |

   ## Figures/Tables: {N} planned
   ## Citations: {verified}/{total} verified, {verify_count} [UNCONFIRMED]
   ## Review LLM Review: score {X}/10 (persona: {area_chair | bio_editor | clinical_editor})   <!-- bio-C10 -->

   ## Next Steps
   - Run `/paper-draft wiki/outputs/paper-plan-{slug}-{date}.md` to draft the paper (style is propagated from the plan)
   - Resolve {verify_count} [UNCONFIRMED] citations before /paper-compile
   ```

## Constraints

- **--venue is required**: page limits and format requirements vary significantly by venue; cannot be omitted
- **At least one experiment evidence**: purely theoretical claims are insufficient for an empirical paper; at least one experimental result is required
- **Page budget must be feasible**: total section pages <= venue main-body limit; otherwise adjust (compress or move to appendix)
- **Review LLM review is mandatory**: cannot be skipped; catching problems at the outline stage has the lowest cost
- **All citations from wiki**: every paper in the citation plan must exist in wiki/papers/
- **claim → section mapping must be complete**: every target claim must appear in at least one section
- **Every section must have a claim**: a section with no claim support is filler and should be removed or merged
- **Graph edges via tools/research_wiki.py**: do not manually edit edges.jsonl
- **Citations use [[slug]]**: all citations in the outline use wikilink syntax
- <!-- bio-C10 --> **`paper_style` is recorded, not inferred at draft time**: the resolved style is written into PAPER_PLAN.md metadata so `/paper-draft` consumes it without re-inferring. Auto-resolve happens once, in Step 1b.
- <!-- bio-C10 --> **Bio Methods section pulls from A1/A5/A6/A7/C6**: don't synthesize Methods from prose alone — pull dataset versions from `wiki/datasets/`, replicate counts from `experiments[*].statistical_protocol`, force-field/cell-line/RRID from `setup`, costs from `estimated_cost`. The bio Methods is largely a wiki-driven serialization, not a writing task.
- <!-- bio-C10 --> **Clinical style requires NCT ID and pre-registration**: when `paper_style == clinical`, refuse to finalize the plan unless target claims have an associated B2 `clinical_trial_for` edge with `metadata.nct_id` populated, OR the paper is explicitly marked observational (no NCT required).

## Error Handling

- Same as legacy, plus:
- <!-- bio-C10 --> **`paper_style` resolution disagreement**: emit a warning, prefer venue, record both signals in the report.
- <!-- bio-C10 --> **Clinical style with no NCT**: error unless the user explicitly passes `--paper-style clinical --observational`.
- <!-- bio-C10 --> **Bio venue with cs-shaped claims** (e.g. submitting a Nature paper but all evidence is `tested_by` ML benchmark): emit a 🟡-style warning that the venue likely expects mechanism / wet-lab / cross-context evidence; do not block.

## Dependencies

### Tools（via Bash）
- `python3 tools/research_wiki.py slug "<title>"` — generate slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — add graph edge
- `python3 tools/research_wiki.py rebuild-context-brief wiki/` — rebuild query_pack
- `python3 tools/research_wiki.py log wiki/ "<message>"` — append log
- `python3 tools/fetch_s2.py search "<title>"` — Semantic Scholar search (citation plan fallback)
- <!-- bio-C10 --> `python3 tools/fetch_crossref.py paper <doi>` — primary BibTeX source for bio papers
- <!-- bio-C10 --> `python3 tools/fetch_pubmed.py paper <pmid>` — fallback for bio papers; provides MeSH terms

### MCP Servers
- `mcp__llm-review__chat` — Step 7 outline review (mandatory; persona dispatched on `paper_style`)

### Claude Code Native
- `Read` — read wiki pages
- `Glob` — find claims, experiments, papers
- `WebFetch` — DBLP / CrossRef / PubMed BibTeX fetch (Step 6)

### Shared References
- `.claude/skills/shared-references/academic-writing.md` — narrative structure and section design principles
- `.claude/skills/shared-references/citation-verification.md` — citation fetch and verification rules

### Local References
- <!-- bio-C10 --> `skills/paper-draft/references/templates/cs/` (planned)
- <!-- bio-C10 --> `skills/paper-draft/references/templates/bio/` (planned)
- <!-- bio-C10 --> `skills/paper-draft/references/templates/clinical/` (planned)

### Called by
- `/research` Stage 5 (paper writing stage)
- Manual user invocation
