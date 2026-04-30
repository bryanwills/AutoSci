---
title: "Highly accurate protein structure prediction with AlphaFold"
slug: "highly-accurate-protein-structure-prediction-alphafold"
arxiv: ""
venue: "Nature"
year: 2021
tags: [protein-structure-prediction, deep-learning, attention, geometric-deep-learning, structural-biology, alphafold]
importance: 5
date_added: 2026-04-30
source_type: tex
s2_id: ""
keywords: [alphafold, evoformer, msa, invariant-point-attention, fape, casp14, protein-folding, pLDDT, triangle-attention, structure-module]
domain: "Structural Biology / ML for Science"
code_url: "https://github.com/deepmind/alphafold"
cited_by: []
---

## Problem

Determining the three-dimensional structure of a protein from its amino acid sequence — the structure-prediction half of the protein folding problem — has been an open challenge for more than 50 years. Experimental techniques (X-ray crystallography, NMR, cryo-EM) have resolved roughly 100,000 unique structures, a tiny fraction of the billions of known protein sequences, and each new structure can take months to years of effort. Prior computational methods, whether physics-based (force-field simulation, statistical potentials) or evolutionary-history-based (homology modelling, coevolution-derived contact prediction), fall well short of atomic accuracy when no homologous structure is available, which limits their utility for the proteins biologists most need to study.

## Key idea

Cast structure prediction as joint inference over a multiple sequence alignment (MSA) and a residue-pair representation, processed by a deep network whose architecture and losses bake in the physical and geometric inductive biases of protein structure. Two design choices carry most of the novelty: (1) the **Evoformer** trunk, which alternates attention over the MSA and triangle-consistent updates over the pair representation so that evolutionary signal and pairwise spatial reasoning continuously cross-inform each other; and (2) an **end-to-end structure module** built around invariant point attention (IPA) and a residue-gas representation, trained directly to predict 3D coordinates with the frame-aligned point error (FAPE) loss. Iterative refinement (recycling), self-distillation on unlabelled sequences, and a masked-MSA BERT-style auxiliary loss compound these two designs into a system that delivers regularly-atomic-accuracy predictions in CASP14, including for targets without homologous templates.

## Method

- **Inputs**: primary amino acid sequence; an MSA produced by genetic-database search; templates from structural-database search.
- **Trunk — Evoformer (48 blocks, no shared weights)**: maintains an Nseq x Nres MSA representation and an Nres x Nres pair representation. Within each block: (a) row-wise gated self-attention over the MSA biased by the pair representation; (b) column-wise gated self-attention over the MSA; (c) outer-product mean from MSA into the pair representation; (d) two **triangle multiplicative updates** (using outgoing and incoming edges) and two **triangle self-attention** operations on the pair representation that enforce triangle-inequality-style consistency on pairwise distances; (e) transitions. The pair representation supplies attention bias back into the MSA, closing the loop between evolutionary and spatial reasoning.
- **Structure module (8 blocks, shared weights)**: operates on a residue gas — Nres independent backbone frames (rotation, translation), each initialised at the origin. Uses **invariant point attention** (IPA), which augments standard attention queries/keys/values with 3D points expressed in each residue's local frame, making the operation invariant to global rigid motions. Each block updates frames, predicts side-chain torsion (chi) angles, and computes all heavy-atom positions. The chain constraint is allowed to be violated mid-network and is enforced only by an auxiliary violation loss plus a final Amber gradient-descent relaxation.
- **Losses**: the primary loss is **FAPE** — for every (predicted-frame, true-frame) alignment, sum the clamped L1 distance between every predicted atom and its true position. Auxiliary heads include masked-MSA prediction (BERT-style), distogram prediction, and per-residue confidence (pLDDT) prediction.
- **Recycling**: the entire network output is fed back as additional input three times, enabling iterative refinement at near-zero extra training cost.
- **Self-distillation**: a trained AlphaFold predicts structures for ~350,000 Uniclust30 sequences; a high-confidence subset is added to PDB training data for a from-scratch retrain. This significantly enhances accuracy on targets with poor MSA depth.
- **Confidence outputs**: pLDDT (per-residue lDDT-Calpha) and pTM (predicted TM-score) — both calibrated against the model's own errors, enabling reliability estimates per prediction.

## Results

- **CASP14**: median backbone Calpha r.m.s.d.95 of 0.96 angstrom (95% CI 0.85-1.16) on n=87 protein domains; the next best method achieved 2.8 angstrom (95% CI 2.7-4.0). For reference, a carbon atom is ~1.4 angstrom wide. All-atom r.m.s.d.95 was 1.5 angstrom for AlphaFold versus 3.5 angstrom for the best alternative.
- **Recent PDB chains** (n=3,144, all post-training-cutoff, template-coverage-filtered): overall median full-chain Calpha r.m.s.d.95 = 1.46 angstrom (95% CI 1.40-1.56).
- **Confidence calibration**: lDDT-Calpha = 0.997 x pLDDT - 1.17 (Pearson r = 0.76, n=10,795 chains); TM-score = 0.98 x pTM + 0.07 (Pearson r = 0.85). Both confidence measures are usable in practice as reliability estimates.
- **Long proteins**: a 2,180-residue chain (CASP target T1044) was predicted with correct domain packing and r.m.s.d.95 = 2.2 angstrom, TM-score = 0.96.
- **Ablations**: removing IPA + recycling, removing triangle updates/biasing/gating, removing the end-to-end structure gradients, removing recycling alone, or removing the masked-MSA auxiliary head each cost meaningful GDT/lDDT-Calpha. Self-distillation training adds ~2 lDDT-Calpha on the PDB test chains.
- **Speed**: GPU-minutes to GPU-hours per prediction — roughly one GPU-minute per model for 384 residues — opening proteome-scale prediction.

## Limitations

- **MSA depth threshold**: accuracy degrades sharply when the median per-residue effective MSA depth (Neff) drops below ~30 sequences and improvements above ~100 sequences yield diminishing returns. Truly orphan sequences remain hard.
- **Hetero-complex bridging domains**: AlphaFold (this version) predicts single chains; proteins whose fold is shaped predominantly by interactions with other chains (high heterotypic-to-homotypic-contact ratio) are predicted poorly. Hetero-complex prediction is left to a future model.
- **Disordered regions and ligand-dependent folds**: when a fold depends on a haem group, ion, or stoichiometry not implied by the sequence, AlphaFold falls back to its training-distribution prior, which may or may not match the experimental condition.
- **Compute footprint**: training (and self-distillation retraining) is heavy; the released system is inference-friendly but not retrainable on a researcher laptop.
- **No explicit physics**: the model does not perform a physics-based search; the post-prediction Amber relaxation removes stereochemical violations but does not improve GDT/lDDT-Calpha. Confidence in mechanistically novel folds outside PDB coverage rests on pLDDT, not on a physical energy.

## Open questions

- How far can the Evoformer + structure-module recipe be extended to **biomolecular complexes** (protein-protein, protein-ligand, protein-nucleic-acid, antibody-antigen) without losing the single-chain accuracy?
- Can the residue-gas + IPA formulation be adapted to model **conformational ensembles, dynamics, and allosteric states** rather than a single high-likelihood structure?
- What is the right way to incorporate **explicit cofactors, ligands, and stoichiometry** as inputs so that ligand-dependent folds are no longer undercut by the sequence-only prior?
- How should pLDDT/pTM be used for **downstream decisions** (variant-effect prediction, drug design, protein engineering) where calibration in unfamiliar regions of sequence space matters?
- Are the triangle-consistency and IPA inductive biases transferable to **other geometric inference problems** (RNA structure, small-molecule conformers, materials), or are they protein-specific?

## My take

AlphaFold2 is the rare paper that simultaneously moves a 50-year scientific problem and a methodological frontier. The Evoformer's triangle-consistent pair updates and the structure module's invariant point attention are not just engineering hacks; they encode geometric priors (triangle inequality, SE(3) equivariance) into a neural architecture in a way that learns more efficiently from the limited PDB. The decision to train end-to-end into 3D coordinates, with FAPE as the primary loss, is what closes the gap between contact-prediction-style pipelines and atomic-accuracy structure prediction. The pLDDT/pTM heads matter as much as the structure itself: a structure predictor without calibrated confidence is hard to use downstream, and AlphaFold's confidence outputs are what enabled the AlphaFold DB and the wave of biological applications that followed. The clear limitations — single-chain only, MSA-dependent, no explicit ligand handling — set the agenda for AlphaFold-Multimer, AlphaFold3, and structurally-resolved interactome work.

## Related

- [[evoformer]]
- [[invariant-point-attention]]
- [[frame-aligned-point-error]]
- [[deep-learning-predicts-protein-structure-atomic]]
- [[msa-depth-bounds-structure-prediction-accuracy]]
- [[john-jumper]]
- [[demis-hassabis]]
