---
title: "pLDDT (predicted lDDT-Cα)"
aliases: ["pLDDT", "predicted lDDT", "predicted local distance difference test"]
tags: [structural-biology, protein-structure-prediction, confidence-metrics, alphafold]
maturity: stable
key_papers: [alphafold-protein-structure-database-2024-providing]
first_introduced: "2021"
date_updated: 2026-04-30
related_concepts: []
---

## Definition

pLDDT is AlphaFold's per-residue confidence score: the model's predicted value of the lDDT-Cα metric (Mariani et al. 2013) for each residue, on a 0–100 scale. It estimates how accurately each Cα position is predicted relative to the (unknown) true structure under a local superposition-free distance-difference test.

## Intuition

pLDDT answers "how much should I trust this residue's local geometry?" residue-by-residue. The widely used operational tiers (from the AlphaFold DB documentation) are:

- **>90 — high accuracy**, suitable for fine-grained applications such as binding-site characterization.
- **70–90 — generally well-modelled**, reliable backbone.
- **50–70 — lower confidence**, use cautiously.
- **<50 — likely disordered**; the residue often *looks* structured (spaghetti-like helices) but the prediction is unreliable.

Importantly, pLDDT is *local*; even within a high-pLDDT prediction, the inter-domain orientation may still be uncertain — that is what [[predicted-aligned-error]] tracks.

## Formal notation

For a sequence of length `L`, pLDDT(i) ∈ [0, 100] is reported per residue. AlphaFold DB stores pLDDT in the B-factor field of PDB output and under `_ma_qa_metric_local` in the modelCIF mmCIF output, which makes every PDB-aware viewer / pipeline confidence-aware for free.

## Variants

- **Best-of-five pLDDT (Swiss-Prot / proteome subset of AFDB)** — the maximum pLDDT prediction across five different-seed AlphaFold2 runs, used as cluster representative selection criterion.
- **Single-seed pLDDT (bulk UniProt subset of AFDB)** — single-model output.

## Comparison

- **vs lDDT**: lDDT is the experimental ground-truth metric (computed against a known structure); pLDDT predicts it without ground truth.
- **vs PAE**: pLDDT is per-residue local; PAE is pairwise relative-position. Use both: high pLDDT + low PAE between two regions ⇒ both confidently positioned; high pLDDT + high inter-region PAE ⇒ each region is locally confident but their relative orientation is not.
- **vs B-factor**: in experimental structures, B-factor reports flexibility / disorder. AlphaFold reuses the B-factor field to carry pLDDT — semantically different but architecturally clever.

## When to use

- Filtering AFDB predictions before downstream structural analysis.
- Selecting "high-confidence" residues for binding-site / catalytic-residue / mutational analyses.
- Identifying predicted disordered regions (pLDDT <50) as a proxy for IDR detection.

## Known limitations

- pLDDT is *predicted* and can be miscalibrated, especially on out-of-distribution sequences.
- A pLDDT-low region is sometimes truly disordered, sometimes a training-data artifact, sometimes a genuinely difficult fold; the metric alone cannot distinguish.
- The 2022-07 AFDB release contained a numerical bug producing artifactually-low pLDDT in ~4% of predictions — pipelines that filtered by pLDDT before the 2022-11 fix may have silently dropped good predictions.
- pLDDT does not say anything about inter-domain or quaternary-structure confidence — pair it with PAE.

## Open problems

- Calibration of pLDDT across diverse sequence space (designed proteins, viral, IDR-rich, very long).
- Principled fusion of pLDDT + PAE into a single "trust this prediction for downstream task X" score.
- pLDDT-as-IDR-predictor: how reliable is "pLDDT < 50" as a substitute for dedicated disorder predictors?

## Key papers

- [[alphafold-protein-structure-database-2024-providing]] — codifies the pLDDT tier guidance and the B-factor / `_ma_qa_metric_local` storage convention used by every AFDB consumer.

## My understanding

pLDDT is one of those design choices that is more impactful than it looks. By smuggling per-residue confidence into the B-factor field, the AlphaFold team made every PyMOL / Mol* / Chimera workflow confidence-aware without those tools needing any code changes. For [[medpredict]] and any downstream pipeline (PPI, drug binding, PTM site prediction) that consumes AFDB structures, pLDDT thresholding is the first filter applied — it is also the metric most likely to be *misused* (e.g. ignoring the lDDT-vs-RMSD distinction, treating pLDDT as a global structure-quality score, or trusting pLDDT on viral / designed sequences outside training distribution).
