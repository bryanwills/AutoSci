---
title: "medpredict — ML for Biomedical Molecular Prediction"
scope: "Computational and ML methods that predict protein structure, protein-protein and protein-substrate interactions, post-translational modification sites, and drug-design-relevant features feeding targeted therapies."
key_topics: [medpredict]
paper_count: 12
date_updated: 2026-04-29
---

## Overview

This area collects ML and computational pipelines that turn sequence- or omics-level inputs into actionable biomedical predictions. The seed corpus spans (a) end-to-end protein structure prediction (AlphaFold2/3 and the AlphaFold DB at 214M-sequence scale), (b) PTM-site prediction (MusiteDeep) and PTM-aware drug design, (c) E3 ubiquitin-ligase / substrate prediction (UbiBrowser) and ubiquitin-ligase oncology context, (d) experimentally measured and structurally annotated human protein-protein interaction networks (CCSB-HI1 Y2H map; AlphaFold2-resolved PPI structures), and (e) molecular representation learning (geometric deep learning) plus multi-omics analytics for targeted therapy.

## Core areas

- **Structure prediction**: AlphaFold-family models for monomers, complexes, and biomolecular interactions; AlphaFold DB as predicted-structure infrastructure.
- **PTM prediction and PTM-aware design**: deep-learning PTM-site predictors and drug-design strategies that target activated/modified protein isoforms.
- **Interaction-network prediction**: large-scale Y2H interactome scaffolding plus ML/structural inference of protein-substrate (E3-ubiquitin ligase) and protein-protein interaction structures.
- **Molecular representation learning**: geometric / graph deep learning on molecular representations supporting downstream property and activity prediction.
- **Multi-omics-to-therapy**: integrating omics layers into target identification and ML-driven targeted-therapy design.

## Evolution

- Mid-2000s — first proteome-scale binary PPI maps motivate later ML interactome work.
- Mid-2010s — bioinformatics platforms (UbiBrowser) and oncology synthesis (ubiquitin ligases as cancer targets) create demand for predictive E3-substrate inference.
- 2020-2021 — deep-learning predictors for PTM sites become production webservers; AlphaFold2 sets a new accuracy regime for monomer structure.
- 2022-2024 — AlphaFold2 used to structurally annotate large PPI catalogues; AlphaFold DB scales to 214M; AlphaFold3 extends to ligands, nucleic acids, and antibodies; multi-omics integration matures into a unified targeted-therapy pipeline.

## Current frontiers

- Joint structure prediction of arbitrary biomolecular complexes (AlphaFold3-class).
- PTM-aware structure prediction and PTM-aware drug design.
- Linking predicted PPI structures to functional / disease consequences.
- Integrating multi-omics layers with structural and interaction predictions for targeted-therapy decisions.

## Key references

Populated by `/ingest`. The 12 seed papers are listed in the topic page [[medpredict]] under `## Seminal works`.

## Related

- [[medpredict]]
