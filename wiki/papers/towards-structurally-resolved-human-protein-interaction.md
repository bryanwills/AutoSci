---
title: "Towards a structurally resolved human protein interaction network"
slug: "towards-structurally-resolved-human-protein-interaction"
arxiv: ""
venue: "Nature Structural & Molecular Biology"
year: 2023
tags: [alphafold2, protein-protein-interaction, structural-biology, deep-learning, interactome]
importance: 4
date_added: 2026-04-30
source_type: tex
s2_id: ""
keywords: [AlphaFold2, FoldDock, pDockQ, HuRI, hu.MAP, protein complex prediction, disease mutations, phosphorylation]
domain: "Computational Biology"
code_url: ""
cited_by: []
---

## Problem

Cellular function arises from protein-protein interactions (PPIs), but fewer than 5% of the hundreds of thousands of known human PPIs have any structural characterization. Existing experimental and homology-modeling pipelines (e.g. Interactome3D) only cover a small slice of the human interactome, leaving most binary complexes — and therefore the molecular mechanisms by which disease mutations and post-translational modifications act on them — structurally opaque. Deep-learning protein structure predictors had shown strong dimer-level accuracy, but their behaviour at the scale of the full human interactome was untested: which interactions can be predicted reliably, what filters confidence, and what the resulting structures actually buy biology had not been systematically demonstrated.

## Key idea

Apply AlphaFold2 via the [[folddock-pipeline]] to all 65,484 nonredundant human protein pairs from the HuRI Y2H map and hu.MAP 2.0 affinity-purification compendium, then use a learned interface confidence score — [[pdockq-score]] — to rank the resulting complex models. Models with `pDockQ > 0.5` are treated as high-confidence; the authors validate this cutoff against 1,465 experimentally solved complexes (80% correct at this threshold), against orthogonal crosslinking mass-spectrometry data, and against expected enrichment of pathogenic disease mutations at predicted interface residues. The structurally resolved subset is then mined for biological insight: disease-mutation interfaces, phosphorylation hotspots and their co-regulation, and iterative dimer-to-higher-order-assembly construction.

## Method

- **Inputs**: 55,586 HuRI Y2H pairs and 10,207 high-quality hu.MAP 2.0 pairs; small overlap (309) so 65,484 unique pairs total. 62,019 of these have no experimental or homology model.
- **Structure prediction**: [[folddock-pipeline]] based on AlphaFold2 (ref. 17), feeding paired MSAs for each pair.
- **Confidence score**: pDockQ combines the size of the predicted [[protein-protein-interaction-interface]] with mean interface plDDT into a single scalar; calibrated against DockQ on solved complexes. Cutoffs: `pDockQ > 0.23` (loose, 70% correct) and `pDockQ > 0.5` (strict, 80% correct).
- **Validation 1 — solved structures**: compared 1,465 predictions to known complexes; 50% (742) correct overall, rising to 80% above pDockQ 0.5.
- **Validation 2 — large heteromeric complexes (12 PDB cases)**: directly interacting chains had pDockQ > 0.5 in 38% of cases vs. only 6% for indirectly contacting chains, showing pDockQ tracks direct contact rather than mere co-membership in a complex.
- **Validation 3 — crosslink mass-spectrometry**: collected XL-MS pairs across 528 protein pairs; 51% of all predictions and 75% of pDockQ > 0.5 predictions had at least one crosslink within the maximal feasible distance of the linker.
- **Disease-mutation analysis**: mapped ClinVar pathogenic variants and TCGA cancer mutations onto interface residues of high-confidence models; ran FoldX ΔΔG on a benchmark of mutations with known impact on binding (1,320 samples). Found 280 interfaces with pathogenic variants and 602 with top-25% recurrent cancer mutations; 2.3-fold enrichment of pathogenic over benign at interface residues (P = 2.7e-31).
- **Phosphorylation analysis**: mapped 4,145 unique phosphosites to interface residues, computed cross-condition correlations across >200 conditions for 260 regulated sites, hierarchical-clustered into 16 co-regulated groups; ran kinase-substrate enrichment and GO enrichment per cluster.
- **Higher-order assembly**: iteratively aligned predicted dimers to build larger complexes (RFC, TFIIH, 20S proteasome and others), using shared subunits as alignment anchors; sorted by pDockQ.

## Results

- 3,137 high-confidence (pDockQ > 0.5) human PPI structures, 10,061 at the looser pDockQ > 0.23 cutoff.
- Of the 3,137 confident models, 1,371 have **no homology to any known structure** — net new structural coverage of the human interactome.
- Crosslink validation: 479 crosslinks support 171 confident models; 41 of those models correspond to interactions with no prior experimental or homology structure (e.g. ERLIN1/ERLIN2, IMMT/CHCHD3, METTL1/WDR4, HNRNPC/RALY).
- HuRI predictions are systematically less confident than hu.MAP predictions; the gap correlates with intrinsic disorder, fewer sequences in paired MSAs, lower subcellular co-localisation, and lower co-expression — consistent with HuRI capturing more transient interactions that AF2 cannot reliably model.
- Disease mutations: pathogenic variants are 2.3× enriched at predicted interface residues; very-high-plDDT (>90) interface residues give the best discrimination of disruptive vs. neutral mutations under FoldX. Concrete mechanistic hypotheses produced for WDR4–METTL1 (Galloway-Mowat), TWIST1 (Saethre–Chotzen), TCF4, RAD51D/XRCC2 (familial breast/ovarian cancer).
- Phosphorylation: interface phosphosites have higher functional scores than random; tyrosine-kinase substrates (ERBB2, AXL, ABL2, FER) are enriched at interfaces; 16 co-regulated phospho-clusters emerge with cell-cycle, kinase-inhibitor, and chromatin-related GO signatures, generating directly testable regulatory hypotheses.
- Higher-order assembly: TFIIH (5 subunits) and RFC (5 subunits) reconstructed from pairwise dimers in good agreement with cryoEM (PDB:6NMI, PDB:6VVO); 20S proteasome (14 subunits) places chains correctly but cannot resolve homologous-subunit identity.

## Limitations

- pDockQ > 0.5 still has ~20% error rate — high-confidence does not mean correct; downstream biological claims need independent confirmation.
- AF2 cannot reliably distinguish among paralogous subunits in complexes (e.g. 20S proteasome chain identity is wrong even when the geometry is right).
- Transient and disorder-dominated interactions (much of HuRI) are systematically under-modeled; pDockQ alone cannot rescue them.
- Iterative dimer-to-assembly construction compounds alignment error: the further a subunit is from the alignment anchor the worse its placement (visible in RFC).
- FoldX-based ΔΔG is only useful at very high plDDT (>90); the method is therefore a hypothesis generator on most of the modeled interactome rather than a quantitative variant-effect predictor.
- The set is restricted to binary pairs from HuRI and hu.MAP; interactions absent from those datasets — and weaker/transient ones — remain uncovered.
- No assessment of stoichiometry: the procedure produces 1:1 dimers and cannot natively recover multi-copy or asymmetric complexes.

## Open questions

- How can confidence calibration (pDockQ or successors) be extended so that transient and disordered interactions become reliably distinguishable from non-interactions, rather than collapsed together at low score?
- What modifications to AF2 / AF-Multimer let the model break paralog symmetry and recover the correct chain identity in homologous-subunit complexes?
- Can iterative dimer-to-assembly construction be replaced by a global-consistency optimizer that bounds compounding alignment error and admits non-1:1 stoichiometries?
- For the 1,371 brand-new high-confidence interfaces, which pathogenic variants and phospho-regulation hypotheses survive wet-lab validation, and what does the false-positive rate look like in practice?
- Beyond HuRI and hu.MAP, what fraction of the long tail of the human interactome is structurally accessible at all to AF2-class methods, and what is the residual gap that requires new architectures?

## My take

This is the first paper to operationalize AlphaFold2 as a structural-biology instrument at human-interactome scale, and it does so honestly: it surfaces both where AF2-class predictors give real biology (3,137 confident models, 1,371 of them genuinely novel) and where they fail (paralogs, transients, MSA-poor pairs). The confidence-calibration story — pDockQ tied to DockQ, then independently sanity-checked by crosslink MS and pathogenic-mutation enrichment — is the right pattern for any large-scale predictor; future work should treat orthogonal experimental constraints as a first-class part of the prediction loop, not an after-the-fact audit. The follow-on assembly results foreshadow the AF-Multimer and Bryant-et-al sequential-assembly line; their compounding-error problem is the key research opening here.

## Related

- [[folddock-pipeline]] — the dimer-prediction wrapper around AF2 used here
- [[pdockq-score]] — the interface-confidence score introduced and validated
- [[protein-protein-interaction-interface]] — the structural object the paper resolves at scale
- [[alphafold2-enables-large-scale-structural-modeling]] — the central claim this paper supports
- [[pedro-beltrao]] — co-corresponding author
- [[arne-elofsson]] — co-corresponding author
- [[patrick-bryant]] — co-first author; primary FoldDock developer
- [[david-burke]] — co-first author
