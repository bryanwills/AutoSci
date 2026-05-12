---
title: "AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences"
slug: "alphafold-protein-structure-database-2024-providing"
arxiv: ""
venue: "Nucleic Acids Research"
year: 2024
tags: [structural-biology, protein-structure-prediction, databases, alphafold, bioinformatics]
importance: 4
date_added: 2026-04-30
source_type: tex
s2_id: ""
keywords: [alphafold, protein-structure, database, plddt, predicted-aligned-error, foldseek, uniprot, structural-biology]
domain: "structural-bio"
code_url: "https://alphafold.ebi.ac.uk"
cited_by: []
---

## Problem

Modern protein structure predictors (AlphaFold2, RoseTTAFold, OpenFold) can predict near-experimental-accuracy structures for arbitrary sequences, but two practical barriers prevent the field from realizing that capability at scale: (1) running prediction software is non-trivial for non-specialists and computationally redundant when many users would predict the same proteins, and (2) without a centralized, queryable archive of pre-computed predictions, integration with primary biological data resources (UniProt, PDB, Ensembl, InterPro, MobiDB) is impossible. The carbon footprint of redundant inference and the seconds-vs-hours latency gap between lookup and on-demand prediction further argue for a single curated resource.

## Key idea

Build and maintain a public, free database — the AlphaFold Protein Structure Database (AlphaFold DB) — that archives AlphaFold2-generated predictions for essentially all UniProt sequences, expose them through multiple access channels (FTP, Google Cloud Public Datasets, REST API, web UI), and continuously enrich the resource with confidence metrics (pLDDT, PAE), structural similarity clusters (Foldseek), interactive visualization (Mol*), and integration with primary biological databases. The 2024 update reports the scaling from ~360k structures at launch (2021) to over 214 million predictions covering 48 model organism / WHO pathogen proteomes plus essentially all of UniProt.

## Method

- **Data generation pipeline**: Google DeepMind runs AlphaFold2 inference; outputs are stored as PDB, mmCIF (modelCIF-conformant), and binaryCIF, with per-residue pLDDT in the B-factor field and JSON metadata holding the Predicted Aligned Error (PAE).
- **Confidence metrics**: pLDDT estimates per-residue accuracy on the lDDT-Cα scale (0–100); regions >90 are high-accuracy, 70–90 reliable backbone, 50–70 cautious, <50 likely disordered. PAE encodes domain-level relative-position confidence; the JSON schema was compacted in 2022 (`predicted_aligned_error` + `max_predicted_aligned_error`).
- **Coverage strategy**: phased releases by use case — model organisms (2021-07, 360k), Swiss-Prot (2021-12), WHO global-health proteomes (2022-01), most of UniProt 2021_04 plus MANE-select (2022-07), and a 2022-11 fix-pass for a numerical bug affecting ~4% of predictions (low pLDDT artifact).
- **Coverage exclusions**: sequences <16 aa, >2700 aa for Swiss-Prot/proteomes (>1280 aa for other UniProt), non-standard amino acids, non-canonical UniProt entries, and viral proteins.
- **Single vs multi-seed**: bulk UniProt entries are single-model runs; Swiss-Prot/proteome entries are the most-confident of five different-seed runs.
- **Access**: EMBL-EBI FTP (subset, no PAE), Google Cloud Public Datasets (full ~23 TiB CC-BY-4.0 mirror), REST API keyed on UniProt accessions, and web UI with refined filtering (Swiss-Prot vs TrEMBL, reference-proteome status, popular-organism shortcuts).
- **Sequence-similarity search**: BLAST integrated via Google Cloud + the BioSolr XJoin Solr plugin to merge BLAST hits with the regular Solr search index.
- **Structure-similarity clustering**: integration of Foldseek Cluster results from Barrio-Hernandez et al. — MMseqs2 reduces 214M UniProtKB sequences to 52M sequence clusters, then Foldseek structural clustering yields 18.8M clusters, finalized to 2.30M robust multi-member clusters; AFDB/Foldseek and AFDB50/MMseqs cluster tables are exposed per-prediction page and via API.
- **Visualization**: enhanced PAE 2D heatmap (non-consecutive region highlighting), tighter coupling between PAE viewer and Mol* 3D viewer (selecting an off-diagonal PAE cell highlights the corresponding 3D regions), and finer atom/residue/chain selection plus inter-residue distance measurement in Mol*.

## Results

- 214M+ predicted structures archived as of September 2023 — a ~700× expansion from the 2021 launch.
- 48 organism proteomes (model organisms + WHO pathogens of interest) hosted as TAR files on EMBL-EBI's FTP.
- Full ~23 TiB dataset mirrored on Google Cloud Public Datasets under CC-BY-4.0; downloadable in ~2.5 days at 1 Gbps.
- Integrations live with PDB, UniProt, Ensembl, InterPro, MobiDB, PDBe-KB, GeneCards.
- New BLAST-based sequence search and Foldseek/MMseqs2-derived structure-similarity clusters are exposed per-prediction.
- Improved Predicted Aligned Error viewer with non-consecutive region support and Mol* coupling.

## Limitations

- Coverage gaps: <16 aa peptides, very long sequences (>2700 aa for SP/proteomes, >1280 aa for bulk UniProt), non-standard amino acids, non-canonical UniProt records, viral proteins — explicitly under discussion.
- Bulk UniProt predictions are single-seed; only Swiss-Prot/proteome entries are best-of-five-seed.
- Predictions can lag UniProt updates because AlphaFold DB releases are less frequent than UniProt's.
- pLDDT in the 50–70 band requires user judgement; <50 regions are often artifactually structured-looking and easy to misinterpret.
- No isoform-level coverage, no multimeric predictions, no bound ligands/cofactors in the core archive (AlphaFill is referenced but separate).
- 2022-07 release contained a numerical bug producing ~4% low-pLDDT artifacts; v3 files retained for reproducibility but downstream pipelines built before the 2022-11 fix may be poisoned.
- The PAE viewer currently struggles with very large complexes (UI scaling).

## Open questions

- How should isoform-level structural coverage be represented and indexed? UniProt isoforms are currently absent from AFDB.
- What is the right schema for multimeric / complex predictions (when AlphaFold-Multimer or AlphaFold3 results enter the archive)?
- How to integrate small-molecule binding (AlphaFill cross-references) without breaking the modelCIF archive contract?
- How to systematically integrate domain annotations (Chainsaw, CATH-style) at the 214M-prediction scale?
- How to lower the entry barrier for users unfamiliar with macromolecular structure data — the manuscript flags a training-platform initiative as ongoing work.
- Versioning UX: with v3 (pre-fix) and v4 coordinates coexisting, how should downstream pipelines decide which to consume?

## My take

This is a database/resource paper rather than a methods paper, but its leverage is enormous: it is the layer that turns AlphaFold2 from "a model you could run" into "a knowledge resource the rest of biology can build on". The interesting research-grade content is concentrated in three places — (i) the operational specification of what pLDDT and PAE actually mean and how to consume them, which is now the de-facto standard for confidence reasoning in downstream pipelines, (ii) the integration of Foldseek/MMseqs2 clustering at proteome scale, which makes structure-based similarity search tractable for ~214M structures, and (iii) the candid documentation of failures and exclusions (the 2022 numerical bug, viral exclusion, length cutoffs). The combination of CC-BY-4.0 licensing and Google-Cloud-mirrored bulk download is what made downstream work like structurally-resolved PPI networks, large-scale evolutionary comparison, and ESM-Atlas-style alternatives feasible at all. For [[medpredict]], AFDB is the canonical "structural-evidence" lookup that downstream PPI / drug-target / PTM prediction pipelines cite.

## Related

- [[alphafold-db]] — concept page for the resource itself
- [[predicted-aligned-error]] — concept page for PAE confidence metric
- [[plddt]] — concept page for the per-residue confidence metric
- [[precomputed-structure-databases-enable-proteome-scale-biology]] — supported claim
- [[plddt-and-pae-are-complementary-confidence-metrics]] — supported claim
- [[demis-hassabis]] — corresponding author (Google DeepMind)
- [[john-jumper]] — AlphaFold2 lead, co-author
- [[sameer-velankar]] — corresponding author (EMBL-EBI)
- [[medpredict]] — topic
