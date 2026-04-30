---
title: "AlphaFold Protein Structure Database (AlphaFold DB)"
aliases: ["AlphaFold DB", "AFDB", "AlphaFold Database"]
tags: [structural-biology, protein-structure-prediction, databases, bioinformatics]
maturity: stable
key_papers: [alphafold-protein-structure-database-2024-providing]
first_introduced: "2021"
date_updated: 2026-04-30
related_concepts: []
---

## Definition

AlphaFold DB is the public, EMBL-EBI / Google DeepMind co-maintained archive of AlphaFold2-generated predicted protein structures, distributed under CC-BY-4.0. As of September 2023 it covers over 214 million UniProt sequences with per-residue pLDDT confidence and per-residue-pair Predicted Aligned Error (PAE), plus integration with primary biological resources (UniProt, PDB, Ensembl, InterPro, MobiDB, PDBe-KB, GeneCards).

## Intuition

A pre-computed lookup table for the function "UniProt accession → predicted 3D structure + confidence", scaled to essentially all of UniProt. Lookup takes seconds versus the hours it would take to run AlphaFold2 from scratch, and the centralization makes the resource integratable into other primary biological databases — which on-demand prediction cannot achieve.

## Formal notation

For each UniProt accession `u` in the covered set, AlphaFold DB stores:

- coordinates: PDB / mmCIF (modelCIF-conformant) / binaryCIF files
- per-residue pLDDT(u, i) ∈ [0, 100] in the B-factor field
- per-residue-pair PAE(u, i, j) in JSON (with `predicted_aligned_error` and `max_predicted_aligned_error`)
- metadata JSON (UniProt cross-refs, version, model index)
- structural-similarity cluster memberships (AFDB/Foldseek and AFDB50/MMseqs)

Coverage policy excludes sequences <16 aa, >2700 aa (Swiss-Prot/proteomes) or >1280 aa (other UniProt), non-standard amino acids, non-`one-sequence-per-gene` UniProt entries, and viral proteins.

## Variants

- **Bulk UniProt subset**: single-model run per sequence.
- **Swiss-Prot / proteome subset**: best-of-five-seed model runs (more conservative confidence).
- **Versioned mirrors**: v3 (pre-2022-11 numerical-bug fix) and v4 (post-fix) coordinates coexist on FTP for reproducibility.
- **AFDB/Foldseek vs AFDB50/MMseqs cluster tables**: structure- vs sequence-similarity views.

## Comparison

- **vs ESM Atlas**: ESM Atlas covers metagenomic / non-UniProt sequence space using ESMFold; AFDB covers UniProt with AlphaFold2. Different sequence universes, different predictors, complementary coverage.
- **vs PDB**: PDB is experimentally determined structures (~200k); AFDB is predicted structures (>214M). Two-orders-of-magnitude gap in coverage; PDB is ground truth, AFDB is high-throughput prediction.
- **vs running AlphaFold2 yourself**: the Database is faster (lookup vs inference) and integratable with cross-database joins, but locked to specific AlphaFold2 versions and to UniProt's sequence set.

## When to use

- Any analysis that needs structural context for a UniProt accession at scale (PPI prediction, binding-site characterization, structural bioinformatics).
- As a structural cross-reference resource when integrating with UniProt / Ensembl / InterPro pipelines.
- For structure-based clustering of large protein populations via the integrated Foldseek/MMseqs2 cluster tables.

Avoid as a stand-in for experimental ground truth; consult pLDDT and PAE before drawing conclusions, and do not use it for sequences known to fall in the excluded set (viral, very short, very long, non-standard).

## Known limitations

- Predictions are AlphaFold2-only as of the 2024 update; no AlphaFold3 / multimer predictions in the core archive.
- No isoforms, no ligands/cofactors in the core archive (AlphaFill is a separate cross-referenced resource).
- Releases lag UniProt's release cadence.
- 2022-07 release had a numerical bug producing ~4% low-pLDDT artifacts; pipelines depending on the pre-fix v3 coordinates may carry the bug.
- Viral protein exclusion is operationally significant for infectious-disease research.

## Open problems

- Multimeric / complex predictions at proteome scale.
- Isoform-level structural coverage.
- Systematic small-molecule (ligand / cofactor) integration without breaking the modelCIF archive.
- Domain-annotation overlay at 214M-prediction scale.
- User-experience / training for non-structural-biology users consuming the data.

## Key papers

- [[alphafold-protein-structure-database-2024-providing]] — the 2024 NAR Database-issue paper (Varadi et al.) reporting the 214M-scale state.

## My understanding

AlphaFold DB is the "missing layer" that converted AlphaFold2 from a method into infrastructure for all of structural biology. The interesting design choices are mostly around confidence-metric storage and integration semantics — pLDDT in the B-factor field is a clever piece of plumbing because it makes every existing PDB-aware tool confidence-aware for free. The Foldseek-cluster integration is the most research-relevant addition in this 2024 update: it turns the database from a per-protein lookup into a structure-clustered one, which is a prerequisite for proteome-scale evolutionary and functional analyses.
