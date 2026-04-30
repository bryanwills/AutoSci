---
title: "Invariant point attention (IPA)"
aliases: [ipa, invariant-point-attention-module, alphafold-ipa]
tags: [attention, equivariance, se3, geometric-deep-learning, structure-module, alphafold]
maturity: active
key_papers: [highly-accurate-protein-structure-prediction-alphafold]
first_introduced: "AlphaFold2 (Jumper et al., Nature 2021)"
date_updated: 2026-04-30
related_concepts: [evoformer, frame-aligned-point-error]
---

## Definition

Invariant point attention (IPA) is the attention mechanism inside AlphaFold2's structure module. It augments the standard query/key/value attention with 3D point queries, keys, and values that are produced in the local backbone frame of each residue. Distances between transformed 3D queries and keys contribute to the attention logits, and 3D values are aggregated and projected back into each residue's local frame, making the entire operation invariant to global rigid (SE(3)) motions of the input geometry.

## Intuition

Standard attention is permutation-equivariant but ignores explicit 3D geometry. For protein structure, the right geometric prior is that the result of attending should not change when you globally rotate or translate the whole protein. IPA achieves that by lifting attention into per-residue frames: anything you read or write in 3D goes through (R_i, t_i)^{-1}, so global rigid motion of the residue gas leaves IPA's output unchanged. The 3D point distances between residues also impose a strong locality bias that fits the iterative refinement of a residue gas.

## Formal notation

For residue i with frame (R_i, t_i):

- standard scalar attention as usual: query q_i, key k_j, value v_j.
- 3D point queries Q_i, keys K_j, values V_j are predicted in each residue's local frame, then transformed into global coordinates: Q_i^g = R_i Q_i + t_i, similarly K_j^g, V_j^g.
- attention logit between i and j combines (a) the dot product q_i . k_j (scalar attention), (b) negative squared distance |Q_i^g - K_j^g|^2 (geometric attention), and (c) a linear projection of the pair representation entry (i, j).
- after softmax, the aggregated 3D value is gathered as sum_j alpha_{ij} V_j^g and pulled back into residue i's local frame: (V_i^{out}) = R_i^{-1} (V_i^{out,g} - t_i).

Because every 3D quantity is read and written in local frames, applying a global rotation R and translation t to all (R_i, t_i) leaves all attention outputs (and thus the predicted updates) unchanged.

## Variants

- **No-IPA (direct projection)**: replaces IPA with a plain projection from Evoformer features. Loses meaningful accuracy in ablations.
- **No-IPA + no-recycling**: cuts both refinement mechanisms; one of the largest ablation gaps reported in the paper.

## Comparison

- **Plain transformer attention**: not invariant to global rigid motions; cannot reason directly about pairwise 3D distances.
- **Equivariant graph networks (EGNN, SE(3)-Transformers)**: also impose SE(3) equivariance, but do so via spherical harmonics or scalar invariants computed from coordinate differences. IPA's per-residue-frame trick is simpler and integrates cleanly with standard attention.
- **Vector-Neuron / TFN-style layers**: more general equivariance but typically heavier; IPA targets the specific protein residue-gas setting.

## When to use

- Iterative refinement of a set of rigid frames where SE(3) invariance of the readout matters (protein backbone, biomolecular complexes, antibody loops).
- Whenever attention needs to combine learned per-token features with explicit 3D geometry between tokens.

## Known limitations

- Specific to a residue-gas-style representation; not directly applicable to settings without per-token frames.
- The geometric attention term costs O(Nres^2) point-distance evaluations per head per block.
- Invariance is only to global rigid motion; chirality must be supplied by other components (e.g. FAPE).

## Open problems

- Generalising IPA to multi-chain / hetero-complex residue gases without losing the locality bias.
- Variants that fold in time or conformational ensembles instead of a single static structure.

## Key papers

- [[highly-accurate-protein-structure-prediction-alphafold]]

## My understanding

IPA is a small, almost surgical idea: keep ordinary attention, but project all 3D quantities through each residue's local frame. The result is an attention mechanism that is genuinely SE(3)-invariant by construction, encodes pairwise distance bias for free, and slots into the structure module's iterative residue-gas update. It is one of the cleanest examples of an equivariance trick paying off without an exotic mathematical superstructure.
