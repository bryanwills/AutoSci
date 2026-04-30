---
title: "Pre-computed AlphaFold-predicted structure databases enable proteome-scale structural biology that on-demand prediction cannot"
slug: "precomputed-structure-databases-enable-proteome-scale-biology"
status: supported
confidence: 0.85
tags: [structural-biology, databases, alphafold, infrastructure]
domain: "Structural Bioinformatics"
source_papers: [alphafold-protein-structure-database-2024-providing]
evidence:
  - source: alphafold-protein-structure-database-2024-providing
    type: supports
    strength: strong
    detail: "Reports scaling AlphaFold DB from ~360k structures (2021) to >214M (2023) covering essentially all of UniProt, with integration into UniProt, PDB, Ensembl, InterPro, MobiDB, PDBe-KB, GeneCards. Lookup is seconds versus hours of on-demand inference; cross-database integration is impossible without the centralized archive."
conditions: "Holds for sequences within AlphaFold DB's coverage policy (≥16 aa, ≤2700 aa for SP/proteomes or ≤1280 aa for bulk UniProt, standard amino acids, non-viral, in UniProt one-sequence-per-gene FASTA). Does not generalize to multimeric structures, isoforms, ligand complexes, or sequence space outside UniProt (e.g. metagenomic — which ESM Atlas covers separately)."
date_proposed: 2026-04-30
date_updated: 2026-04-30
---

## Statement

Centralized, pre-computed databases of AlphaFold-predicted structures (specifically, AlphaFold DB) unlock classes of analysis — proteome-scale comparative structure work, structurally-resolved interactome construction, cross-database integration with primary biological resources — that running AlphaFold2 on demand cannot practically support, because of the gap between seconds-per-lookup and hours-per-prediction inference cost, redundant compute carbon footprint, and the need for stable cross-references for primary biological databases (UniProt, Ensembl, InterPro, etc.).

## Evidence summary

The AlphaFold DB 2024 update reports (a) >214M predictions covering essentially all of UniProt, (b) integration into 7+ primary biological databases that cite stable AFDB URLs, (c) integration of structure-similarity clusters from Foldseek at proteome scale (only feasible because all structures are pre-computed and stored), and (d) explicit cost arguments — the carbon footprint of redundant inference and the lookup-vs-inference latency gap. Downstream papers (e.g. structurally-resolved human PPI networks, cross-organism comparative structural biology) have only become feasible after AFDB scaled.

## Conditions and scope

- Coverage cutoffs limit applicability to viral sequences, very short / very long proteins, isoforms, multimers, and ligand complexes.
- AlphaFold2-only as of 2024; AlphaFold3 predictions are not yet integrated.
- Confidence-blind use of AFDB is unsafe; consumers must respect pLDDT and PAE.

## Counter-evidence

- For specialized sequence spaces (metagenomic, designed proteins, viral), running on-demand prediction (or using ESM Atlas / dedicated runs) remains necessary.
- For applications needing the full 5-seed ensemble or model-internal uncertainty, AFDB's bulk-UniProt single-seed predictions are insufficient.

## Linked ideas

(None yet.)

## Open questions

- How much of the proteome-scale work attributed to AFDB would have happened anyway via on-demand prediction at major HPC centres?
- What is the right governance model for keeping AFDB current as AlphaFold3 / multimer / isoform-aware predictors mature?
