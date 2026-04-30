---
title: "Frame-aligned point error (FAPE)"
aliases: [fape, fape-loss, frame-aligned-point-error-loss]
tags: [loss-function, structure-prediction, equivariance, se3, alphafold]
maturity: active
key_papers: [highly-accurate-protein-structure-prediction-alphafold]
first_introduced: "AlphaFold2 (Jumper et al., Nature 2021)"
date_updated: 2026-04-30
related_concepts: [invariant-point-attention, evoformer]
---

## Definition

Frame-aligned point error (FAPE) is the primary structure-loss term used to train AlphaFold2. For each predicted backbone frame (R_k, t_k) and the corresponding true frame, FAPE expresses every predicted atom position x_i in that frame's local coordinates, expresses every true atom position in the true frame's local coordinates, and penalises their L1 distance under a clamp. The loss is summed over all (frame, atom) pairs.

## Intuition

A naive coordinate L2 loss is not invariant to global alignment, and a single-alignment per-atom RMSD loss biases learning toward whatever global rotation the optimiser happens to use. FAPE replaces "one alignment, all atoms" with "every-frame alignment, every atom": each residue's local frame becomes a viewpoint, and the model is asked to place every other atom correctly from each viewpoint. This rewards the model heavily for getting atoms correct relative to nearby residues' frames (via the L1 clamp dominating local errors) while still propagating long-range error signals.

## Formal notation

Given predicted frames {(R_k^p, t_k^p)} and true frames {(R_k^t, t_k^t)}, predicted atom positions {x_i^p} and true atom positions {x_i^t}:

FAPE = (1 / (N_frames * N_atoms)) * sum_{k, i} min(d_clamp, |R_k^{p,T} (x_i^p - t_k^p) - R_k^{t,T} (x_i^t - t_k^t)|).

The clamp d_clamp prevents very-far atoms from dominating gradient. FAPE is invariant under global rigid motion of either the predicted or true structure independently, and — crucially — distinguishes mirror images, since the residue frames are oriented bases. This makes FAPE the main source of chirality during training.

## Variants

- **Backbone FAPE** (computed only over backbone atoms within backbone frames): used for the structure module's intermediate auxiliary losses and for fine-tuning at lower computational cost.
- **All-atom FAPE** (every heavy atom in every frame): used for the final structure-module output and during fine-tuning.
- **Side-chain torsion auxiliaries**: not FAPE itself but companion losses on chi-angle predictions, which combine with FAPE to give all-atom accuracy.

## Comparison

- **Per-atom RMSD with global alignment**: not differentiable through the alignment in a stable way; biased by a single global frame.
- **Distogram / contact-map loss**: trains pairwise distances but cannot enforce chirality and does not directly encourage atomic-precision local geometry.
- **Plain L2 in global coordinates**: not SE(3)-invariant; a constant rotation can change the loss without changing the structure.

## When to use

- Training any model that outputs a set of rigid frames + atoms and that must be SE(3)-invariant in evaluation.
- Settings where local geometric correctness around each frame matters more than a single global alignment (protein structure, antibody CDR loops, biomolecular complexes).

## Known limitations

- Cost is O(N_frames * N_atoms) — quadratic-like in chain length unless restricted (e.g. backbone FAPE during early training).
- The clamp d_clamp must be tuned; too small loses long-range signal, too large lets outliers dominate.
- FAPE alone does not enforce peptide-bond geometry; AlphaFold2 adds an explicit violation loss and a final Amber relaxation for stereochemistry.

## Open problems

- Versions of FAPE for ensembles or distributions over structures rather than a single target.
- Efficient FAPE variants that scale to very large complexes without sacrificing the every-frame-aligned property.

## Key papers

- [[highly-accurate-protein-structure-prediction-alphafold]]

## My understanding

FAPE is the loss that turns the residue-gas + structure-module formulation into an actually trainable end-to-end system. The trick of evaluating every atom from every frame — rather than picking one alignment — is what gives the model a clean SE(3)-invariant supervisory signal that still distinguishes mirrors. Without FAPE, the structure module's iterative frame updates would lack the per-residue local correctness pressure that makes pLDDT-quality predictions possible.
