---
title: "Protein-protein interaction interface"
aliases: [PPI interface, protein interface, binding interface]
tags: [protein-structure, protein-protein-interaction, structural-biology]
maturity: stable
key_papers: [towards-structurally-resolved-human-protein-interaction]
first_introduced: ""
date_updated: 2026-04-30
related_concepts: []
---

## Definition

A protein-protein interaction (PPI) interface is the set of residues from two interacting protein chains that come into direct physical contact when the chains form a complex. Operationally, residues are called "interface" when their inter-chain Cα–Cα or atom-atom distance falls below a chosen cutoff (commonly 8 Å Cα–Cα, or atom contacts <5 Å), and a minimum number of contacts is often required to exclude transient brush-by contacts.

## Intuition

The interface is where the biology happens: it is the physical handle through which one protein modulates another. Mutations that alter binding affinity, phospho-sites that act as switches, and small-molecule binders that disrupt or stabilize complexes all live at or near the interface. Mapping a residue to "interface vs. non-interface" is therefore a basic discretization that sits under almost every PPI analysis — disease-mutation enrichment, conservation analysis, drug-target tractability, and confidence scores like [[pdockq-score]].

## Formal notation

Given a complex with chains A and B and a residue-residue distance function d(i, j):

- residue r ∈ A is at the interface iff there exists r' ∈ B with d(r, r') < τ (typical τ: 8 Å Cα–Cα or 5 Å heavy-atom).
- The interface size is |{r ∈ A : ...}| + |{r ∈ B : ...}|.
- A "direct" interaction (vs. indirect co-membership in a larger complex) is often required to exceed a minimum contact count, e.g. > 20 Cα contacts at < 8 Å (used in Burke et al. 2023).

## Variants

- Direct vs. indirect interface: direct = chains touch each other; indirect = chains only co-occur in the same larger complex without touching.
- Stable vs. transient interface: stable interfaces typically larger, more hydrophobic, evolutionarily conserved; transient interfaces smaller, more polar, often regulated by PTMs.
- Predicted interface (from AF2/FoldDock or docking) vs. observed interface (from cryo-EM/X-ray/NMR).

## Comparison

- Surface vs. interface: interface residues are a subset of surface residues that happen to bind another chain.
- Active site vs. interface: an active site is where chemistry happens; PPI interfaces are where binding happens. They sometimes overlap (e.g. allosteric or competitive regulation).

## When to use

- Whenever you need a residue-level handle for PPI biology: variant-effect prediction, phospho-site annotation, binder design, conservation analysis.
- As a feature for confidence scoring (interface plDDT, interface size in [[pdockq-score]]).

## Known limitations

- Cutoff-based definitions are arbitrary and discontinuous; small geometric perturbations flip residues in/out of "interface".
- Predicted interfaces depend on the predictor's confidence; treating them as ground truth without validation systematically inflates downstream claims.
- Transient or partially-disordered interfaces resist clean residue-level definition.

## Open problems

- A continuous, probabilistic definition of "interface-ness" that integrates predicted-structure uncertainty.
- Handling ensembles: interfaces that exist only in a subset of conformations.
- Defining interfaces in highly disordered or fuzzy complexes.

## Key papers

- [[towards-structurally-resolved-human-protein-interaction]] — uses interface residues from AlphaFold2-predicted complexes to map disease mutations and phosphosites at human-interactome scale, and uses interface size as a feature in [[pdockq-score]].

## My understanding

"Interface" is one of those concepts that looks simple until a predictor's confidence is in play. The Burke et al. work shows that the right move at scale is to define interfaces from high-confidence predicted structures, validate them against orthogonal experiments (XL-MS distances, mutation impact), and use them as hypothesis generators rather than final answers. Future probabilistic interface definitions — soft membership weighted by predictor confidence and ensemble fraction — should make downstream enrichment statistics cleaner.
