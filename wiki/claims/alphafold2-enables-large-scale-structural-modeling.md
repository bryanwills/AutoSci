---
title: "AlphaFold2 enables large-scale structural modeling of human PPI network"
slug: "alphafold2-enables-large-scale-structural-modeling"
status: supported
confidence: 0.75
tags: [alphafold2, protein-protein-interaction, interactome, structural-biology]
domain: "Computational Biology"
source_papers: [towards-structurally-resolved-human-protein-interaction]
evidence:
  - source: towards-structurally-resolved-human-protein-interaction
    type: supports
    strength: strong
    detail: "Predicts 65,484 human PPI structures via AlphaFold2 + FoldDock; 3,137 high-confidence (pDockQ > 0.5) models; 80% accuracy at this cutoff against 1,465 solved complexes; 75% of high-confidence models supported by orthogonal XL-MS data; 1,371 of the confident models have no homology to any known structure (genuinely new structural coverage)."
conditions: "Interactions need a paired MSA of reasonable depth and are not dominated by intrinsic disorder; predictions of interactions in the HuRI Y2H set (transient, MSA-poor, low subcellular co-localisation) are systematically less confident than hu.MAP affinity-purification-derived pairs. Paralogous-subunit complexes are not reliably resolved at chain identity even when geometry is correct."
date_proposed: 2026-04-30
date_updated: 2026-04-30
---

## Statement

AlphaFold2, applied via the FoldDock pipeline and ranked by pDockQ confidence, can produce high-confidence structural models for thousands of human protein-protein interactions at interactome scale, with calibration good enough to support downstream mechanistic analyses (disease mutations at interfaces, phosphorylation co-regulation, partial higher-order assembly).

## Evidence summary

The supporting paper applies AF2 + FoldDock to all 65,484 nonredundant human PPI pairs from HuRI and hu.MAP 2.0. Three independent validation channels back the claim:

1. **Solved structures (1,465 complexes)**: 80% of pDockQ > 0.5 predictions match the experimental complex (DockQ > 0.23); 70% at pDockQ > 0.23.
2. **Orthogonal crosslink mass spectrometry**: 75% of pDockQ > 0.5 models have at least one experimental crosslink within the linker's maximal feasible distance.
3. **Disease-mutation enrichment**: pathogenic ClinVar variants are 2.3× enriched at predicted interface residues vs. non-interface (P = 2.7e-31), consistent with the predicted interfaces being structurally meaningful rather than random.

The 3,137 high-confidence models include 1,371 with no homology to any known structure, demonstrating net new structural coverage rather than mere recapitulation.

## Conditions and scope

- Interactions need a reasonably deep paired MSA. HuRI's Y2H set is enriched in transient, MSA-poor, disorder-rich pairs and is systematically harder to model.
- The claim is about **binary complexes**. Higher-order assembly via iterative dimer alignment works for some systems (TFIIH, RFC) and partially fails for others (20S proteasome chain identity, eIF2B without trimer scaffolds).
- "High confidence" means pDockQ > 0.5 with the validation above; lower-confidence models (0.23-0.5) should be treated as hypothesis generators only.
- Paralogous-subunit complexes can have correct overall geometry but swapped chain identities.

## Counter-evidence

- ~20% of pDockQ > 0.5 predictions are still incorrect (DockQ < 0.23) — not negligible at interactome scale.
- Indirect-contact pairs in large complexes occasionally produce high pDockQ scores (e.g. RFC3-RFC5), so high pDockQ does not guarantee a real direct interaction.
- For transient interactions (much of HuRI), the method's recall is low and unmeasured: the framework cannot tell "no interaction" from "real but unmodelable interaction".

## Linked ideas

- [[ptm-resolved-structurally-modeled-interactome]] — extends the AF2-Multimer interactome with PTM stratification (ΔpDockQ-per-PTM operator)

## Open questions

- What is the true precision-recall tradeoff at lower pDockQ cutoffs once orthogonal experimental constraints are folded in?
- Does AF-Multimer materially improve over FoldDock + pDockQ on the same 65,484 pairs, especially for the HuRI subset?
- How well do follow-up assembly methods (e.g. Bryant et al. sequential assembly, Nat Commun 2022) extend the binary-complex result to native multi-subunit stoichiometries?
