# Preview — A3 bio identifiers in `papers/` frontmatter

> A3 is **still drafted** (not pilot-merged). This file is a tightly-framed example of what the new frontmatter shape will look like once A3 lands, suitable as a single-screen reference for storyboard scene 1's caption overlay.
>
> Compare against an actual live paper page (e.g., [`../../../wiki/papers/musitedeep-deep-learning-based-webserver-protein.md`](../../../wiki/papers/musitedeep-deep-learning-based-webserver-protein.md)) — note that `arxiv: ""` is empty today because the paper has a DOI but no arXiv ID and `papers/` schema has no slot for it.

## Live paper frontmatter today (musitedeep, 11 fields)

```yaml
---
title: "MusiteDeep: a deep-learning based webserver for protein post-translational modification site prediction and visualization"
slug: "musitedeep-deep-learning-based-webserver-protein"
arxiv: ""                          # ← empty: paper has no arXiv ID
venue: "Nucleic Acids Research"
year: 2020
tags: [deep-learning, ptm, post-translational-modification, bioinformatics, webserver, ...]
importance: 3
date_added: 2026-04-30
source_type: tex
s2_id: ""
domain: "Bioinformatics"
code_url: "https://github.com/duolinwang/MusiteDeep_web"
cited_by: []
---
```

The body has the DOI written as inline prose under `## Method` but it is not in frontmatter, so it cannot be machine-extracted by `/novelty`, `/discover`, `/ingest --discover`, or any downstream skill.

## After A3 lands (proposed frontmatter — 19 fields)

```yaml
---
title: "MusiteDeep: a deep-learning based webserver for protein post-translational modification site prediction and visualization"
slug: "musitedeep-deep-learning-based-webserver-protein"
arxiv: ""                          # kept — some bio papers also route bioRxiv → arXiv
# bio-A3 (still drafted): /ingest C1 will fill these from CrossRef / PubMed E-utilities / EuropePMC
doi: "10.1093/nar/gkaa275"         # bio-A3: primary bio identifier
pmid: "32324217"                   # bio-A3: PubMed ID
biorxiv: ""                        # bio-A3: bioRxiv DOI suffix (none for this paper — Nature journal)
pdb_ids: []                        # bio-A3: structures introduced by the paper (MusiteDeep is sequence-only)
uniprot_ids: []                    # bio-A3: proteins characterised by the paper (PTM-site predictor, no specific UniProt anchors)
nct_ids: []                        # bio-A3: clinical trials referenced (none — methods paper)
gene_symbols: []                   # bio-A3: HGNC symbols (none — general predictor)
species: ["human"]                 # bio-A3: model organisms (trained on UniProtKB/Swiss-Prot human)
venue: "Nucleic Acids Research"
year: 2020
tags: [deep-learning, ptm, post-translational-modification, bioinformatics, webserver, ...]
importance: 3
date_added: 2026-04-30
source_type: tex
s2_id: ""
# bio-A4 (still drafted): controlled vocabulary for bio domain
domain: "bioinformatics"           # bio-A4: was "Bioinformatics" (uppercase) — A4 normalises
code_url: "https://github.com/duolinwang/MusiteDeep_web"
cited_by: []
---
```

## What this unlocks for a bio researcher

| New field | What downstream skill does with it |
|---|---|
| `doi` | `/novelty` Semantic Scholar lookup gains an authoritative anchor (DOI-based dedup beats title-fuzzy match); `/discover --doi` becomes a valid invocation |
| `pmid` | `/discover` can pull PubMed citation network around this paper; clinical-relevance scoring (C5 drafted) needs PMID for PubMed reach |
| `biorxiv` | Preprint–publication pairs (same work, two records) get deduplicated by canonical biorxiv DOI suffix |
| `pdb_ids` | Structures introduced by the paper get linked to `concepts/` with `pdb_ids` field (A2 light option, also drafted) |
| `uniprot_ids` | Proteins characterised by the paper get the same anchor mechanism — graph queries like "papers introducing structure of UniProt P04637" become first-class |
| `nct_ids` | Clinical trial linkage for translational-medicine claims (B2 drafted: `clinical_trial_for` edge type uses NCT IDs in `metadata.trial_id`) |
| `gene_symbols` | HGNC symbol resolution for "papers mentioning TP53" queries; deduplication of free-text gene names (TP53, p53, "tumor protein 53") |
| `species` | Validation/translation edges (B2) can carry `validates_in_species: ["mouse", "human"]` and lint can flag scope creep |

## What's blocked behind A3

- **`/ingest` bio NER pre-pass (C1)** — drafted. Will auto-extract DOI/PMID/PDB IDs/UniProt accessions from .tex / .pdf during ingest. Without A3 frontmatter slots, there's nowhere to put them.
- **bio paper discovery (`/discover from-bio-anchor`, C2)** — drafted in `tools/discover.py`. Reads DOI/PMID/bioRxiv inputs.
- **PubMed-fallback citation network** — depends on PMID being a first-class field.

A3 is **independent of** the merged A1 (datasets/), A5 (setup.dataset wikilink), and A6 (structured cost) — these don't depend on each other.
