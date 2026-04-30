---
title: "FoldDock pipeline"
aliases: [FoldDock, AlphaFold2 dimer pipeline, paired-MSA AF2 docking]
tags: [alphafold2, protein-protein-interaction, structure-prediction, pipeline]
maturity: active
key_papers: [towards-structurally-resolved-human-protein-interaction]
first_introduced: "2022"
date_updated: 2026-04-30
related_concepts: []
---

## Definition

FoldDock is a pipeline that adapts AlphaFold2 to the prediction of protein-protein complexes (dimers). It builds paired multiple sequence alignments (MSAs) for the two interacting chains, runs AlphaFold2 in a configuration that treats the pair as a single chain with a chain break, and combines the resulting per-residue plDDT with interface size into the [[pdockq-score]] for ranking the output.

## Intuition

AlphaFold2 was originally designed for monomers. Dimer prediction can be obtained by feeding it a concatenated input where the two chains share an MSA whose rows are evolutionarily paired across species (so co-evolutionary signal that flags interface residues survives the concatenation). FoldDock packages this trick — paired-MSA construction, the chain-break input, and the post-hoc confidence calibration — into a reproducible pipeline so that AF2 can be applied to large dimer batches.

## Formal notation

Given two query chains A and B:

1. Build separate MSAs for A and B.
2. Pair rows by species (or by other evolutionary linkage) to produce a combined paired MSA.
3. Feed the paired MSA to AF2 with a residue-index break separating A and B.
4. From the resulting structure compute interface contacts, mean interface plDDT, and interface size.
5. Map those features through the [[pdockq-score]] to get a predicted DockQ for ranking.

## Variants

- Original FoldDock with monomer-trained AF2 (Bryant, Pozzati, Elofsson 2022).
- FoldDock-style pipelines that swap in AF-Multimer weights as the structure step.
- Iterative-assembly extensions that take FoldDock dimers as primitives and chain them into higher-order complexes (used in [[towards-structurally-resolved-human-protein-interaction]] for RFC, TFIIH, 20S proteasome).

## Comparison

- AlphaFold-Multimer: trained natively on multimer data with iPTM as confidence; conceptually competing approach to the same problem. FoldDock predates and partly motivates it.
- Classical docking (e.g. ZDOCK, ClusPro): start from solved monomers and dock; FoldDock predicts both monomer fold and interface jointly via co-evolution.
- Homology-based interaction modeling (Interactome3D, 3did): require homologs of the complex; FoldDock does not.

## When to use

- Large-scale dimer prediction where AF-Multimer is unavailable or undesired (e.g. specific control over MSA construction or confidence calibration).
- Pipelines that require [[pdockq-score]] specifically for ranking and downstream filtering.
- As the dimer primitive in iterative higher-order assembly procedures.

## Known limitations

- Inherits AF2's limits: poor on highly transient interactions, poor when paired-MSA depth is low (the human interactome work shows HuRI's protein pairs are MSA-poor and disorder-rich, depressing pDockQ).
- Cannot distinguish among paralogous chains in homologous-subunit complexes.
- Depends on quality of MSA pairing; species-based pairing breaks for paralogous expansions.
- Single-pass dimer; multi-copy or asymmetric stoichiometries are out of scope without external assembly logic.

## Open problems

- Robust MSA pairing for paralog-rich families.
- Native handling of weak/transient interactions where co-evolution is sparse.
- Tighter integration with orthogonal constraints (XL-MS distances, co-localisation) at the structure-prediction step rather than as post-hoc filters.

## Key papers

- [[towards-structurally-resolved-human-protein-interaction]] — applies the pipeline at human-interactome scale (65,484 pairs) and demonstrates its operational regime.

## My understanding

FoldDock was the practical, reproducible bridge between AF2-as-released and the dimer-prediction problem. Its lasting contribution is less the specific paired-MSA construction (AF-Multimer subsumes it) and more the operational framing: a small wrapper around a powerful monomer predictor plus a calibrated confidence head is enough to do real structural biology at interactome scale, given enough careful validation.
