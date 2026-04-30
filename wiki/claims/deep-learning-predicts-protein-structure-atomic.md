---
title: "Deep learning can predict protein structure at near-experimental atomic accuracy from sequence alone"
slug: "deep-learning-predicts-protein-structure-atomic"
status: supported
confidence: 0.92
tags: [protein-structure-prediction, deep-learning, casp14, alphafold, atomic-accuracy]
domain: "Structural Biology / ML for Science"
source_papers: [highly-accurate-protein-structure-prediction-alphafold]
evidence:
  - source: highly-accurate-protein-structure-prediction-alphafold
    type: supports
    strength: strong
    detail: "AlphaFold2 in CASP14 attains median backbone Calpha r.m.s.d.95 = 0.96 angstrom (vs 2.8 angstrom for the next best method) on n=87 protein domains, and median full-chain Calpha r.m.s.d.95 = 1.46 angstrom on n=3,144 recent PDB chains, demonstrating regularly-atomic-accuracy prediction from sequence + MSA + templates without the post-prediction structure being available."
conditions: "Holds when (a) input MSA depth is sufficient (median Neff per residue greater than ~30, with diminishing returns above ~100), (b) the protein is a single chain whose fold is not predominantly determined by hetero-chain contacts or unspecified ligands/cofactors, and (c) the target distribution is within the regime spanned by the PDB. Accuracy degrades on orphan sequences, bridging domains, and stoichiometry- or ligand-conditioned folds."
date_proposed: 2026-04-30
date_updated: 2026-04-30
---

## Statement

Given a protein's amino acid sequence, an MSA derived from large public sequence databases, and optional structural templates, a deep neural network with the right architectural and loss inductive biases can predict the full 3D structure of the protein at near-experimental atomic accuracy — competitive with X-ray crystallography for the majority of single-chain targets — without requiring a homologous structure to be solved.

## Evidence summary

- **CASP14 (blind test)**: AlphaFold2's median backbone Calpha r.m.s.d.95 of 0.96 angstrom is within the ~1.4 angstrom width of a carbon atom and beats the second-best method by a factor of ~3.
- **Recent PDB chains (post-cutoff)**: median full-chain Calpha r.m.s.d.95 of 1.46 angstrom on a redundancy-filtered set of 3,144 chains.
- **Confidence calibration**: the network's pLDDT and pTM heads correlate strongly with realised accuracy (Pearson r = 0.76 and 0.85 respectively on n=10,795 chains), so the claim of atomic accuracy is paired with a usable per-prediction reliability estimate.
- **Ablations**: removing key inductive biases (IPA, triangle updates, end-to-end structure gradients, recycling) materially degrades accuracy, indicating that the result is not generic-deep-learning but tied to specific design choices.

## Conditions and scope

The atomic-accuracy claim applies to:

- Single chains in the regime spanned by the PDB.
- Chains with sufficient MSA depth (median Neff per residue greater than ~30; diminishing returns past ~100).
- Targets where the fold is not predominantly shaped by interactions with other chains, ligands, ions, or cofactors that are not implied by the sequence.

Outside these conditions, accuracy degrades, and the appropriate weaker claim is that confidence-calibrated structure prediction is possible but not yet at experimental accuracy.

## Counter-evidence

- AlphaFold2 reports its own failure modes (low-MSA-depth proteins, hetero-complex bridging domains, ligand-dependent folds) which are localised counter-evidence. These do not refute the claim under its stated conditions but bound its scope.
- Subsequent work on conformational ensembles and intrinsically disordered regions raises an open question about whether "near-experimental atomic accuracy" extends from the most-likely-PDB-conformation to the biologically relevant ensemble.

## Linked ideas

Pending — to be populated as `/ideate` proposes follow-up directions for biomolecular complex prediction, ensemble prediction, and ligand-conditioned structure prediction.

## Open questions

- How does the claim transfer to biomolecular complexes (protein-protein, protein-NA, protein-ligand)?
- For orphan sequences and de novo designs, can self-distillation or large language models on protein sequences close the MSA-depth gap?
- Are pLDDT/pTM still well-calibrated outside the PDB-spanned regime where the claim is established?
