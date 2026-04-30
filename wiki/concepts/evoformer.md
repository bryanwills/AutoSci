---
title: "Evoformer"
aliases: [evoformer-block, alphafold-evoformer-trunk]
tags: [protein-structure-prediction, attention, msa, pair-representation, triangle-attention, alphafold]
maturity: active
key_papers: [highly-accurate-protein-structure-prediction-alphafold]
first_introduced: "AlphaFold2 (Jumper et al., Nature 2021)"
date_updated: 2026-04-30
related_concepts: [invariant-point-attention, frame-aligned-point-error]
---

## Definition

Evoformer is the trunk neural-network block in AlphaFold2. It maintains two coupled tensors — an MSA representation of shape (Nseq, Nres, c) and a pair representation of shape (Nres, Nres, c) — and updates them jointly through repeated blocks (48, no shared weights) so that evolutionary signal in the MSA and spatial-pairwise reasoning in the pair representation continuously cross-inform each other.

## Intuition

Cast structure prediction as graph inference in 3D space, where residues are nodes and pair-representation entries are directed edges. Two priors then become explicit:

1. Pair-representation entries must be jointly representable as a single 3D structure, which implies triangle-inequality-like constraints on triples of residues — captured by triangle multiplicative updates and triangle self-attention.
2. The MSA encodes evolutionary covariation between residues, which is information about which residue pairs are close in 3D — captured by row-wise attention biased by the pair representation, and by the outer-product-mean from MSA into the pair representation.

The block alternates these updates so each side biases the other; the network "thinks" about evolution and geometry in the same forward pass.

## Formal notation

Each Evoformer block applies, in sequence:

1. Row-wise gated self-attention over the MSA, with attention logits biased by a linear projection of the pair representation.
2. Column-wise gated self-attention over the MSA.
3. MSA transition (per-position MLP).
4. Outer-product mean: project MSA features and average outer products across the sequence dimension; add to the pair representation.
5. Triangle multiplicative update using outgoing edges.
6. Triangle multiplicative update using incoming edges.
7. Triangle self-attention around the starting node.
8. Triangle self-attention around the ending node.
9. Pair transition (per-edge MLP).

All updates are residual.

## Variants

- **Triangle-attention-only / triangle-multiplicative-only**: ablations that retain only one of the two pair-update families. Each alone produces high-accuracy structures; their combination is more accurate.
- **Axial-attention-only**: replaces both triangle update families with plain axial attention; loses meaningful accuracy.
- **Extra-MSA stack**: a lighter Evoformer variant runs over a much larger sampled MSA in early blocks before reducing to the main Evoformer trunk.

## Comparison

Earlier MSA + pair networks (e.g. AlphaFold1, trRosetta-style contact predictors) typically apply MSA-to-pair information fusion only once or use generic 2D convolutions on the pair tensor. Evoformer differs in (a) doing the MSA-pair fusion within every block and bidirectionally, and (b) replacing generic 2D operations with triangle-consistent updates that match the geometric prior of representable distance matrices.

## When to use

- When the prediction target has a natural pair representation that must be globally consistent (protein structures, RNA structures, biomolecular complexes).
- When the input includes a sequence ensemble (MSA, paired alignments) whose covariation signal must influence pairwise outputs.

## Known limitations

- Memory and compute scale with Nseq * Nres and Nres^2; very long chains and very deep MSAs require chunking, recycling, and other engineering tricks.
- The triangle priors are tied to the assumption that the pair representation must yield a single 3D structure; for tasks with different geometric priors (e.g. ensembles), the bias may be miscalibrated.
- Single-chain by design in this paper; hetero-complex generalisations require additional cross-chain machinery.

## Open problems

- Generalisation of triangle-consistency updates to non-protein geometric problems (RNA, small-molecule conformers).
- Reduction of the Nres^2 cost of the pair representation without losing the geometric prior.
- Conditional Evoformer variants that consume cofactor / ligand / stoichiometry tokens.

## Key papers

- [[highly-accurate-protein-structure-prediction-alphafold]]

## My understanding

The Evoformer is the "where geometry meets evolution" block. Its triangle-consistent updates are the architectural commitment that makes pairwise residue features behave like distances in a single embedding, and the MSA-row attention biased by the pair stack is what lets the network update its evolutionary read-out as its geometric belief sharpens. Most of the AlphaFold2 accuracy gain over its predecessors traces back to this trunk; the structure module turns the trunk's representation into atoms.
