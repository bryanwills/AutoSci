---
title: "pLDDT and PAE are complementary confidence metrics — pLDDT for per-residue local accuracy, PAE for pairwise relative-position accuracy"
slug: "plddt-and-pae-are-complementary-confidence-metrics"
status: supported
confidence: 0.9
tags: [confidence-metrics, alphafold, structural-biology]
domain: "Structural Bioinformatics"
source_papers: [alphafold-protein-structure-database-2024-providing]
evidence:
  - source: alphafold-protein-structure-database-2024-providing
    type: supports
    strength: strong
    detail: "Operationalizes pLDDT (per-residue, lDDT-Cα target, 0–100) and PAE (pairwise Å error, L×L matrix) as the two confidence outputs of AlphaFold and stores both in AFDB. The 2024 update further improves the PAE viewer's coupling with the 3D viewer (Mol*) precisely because users need to consume both metrics together to reason about multi-domain prediction confidence."
conditions: "Both metrics are *predicted* and may be miscalibrated, especially out of training distribution. The complementarity claim assumes consumers correctly distinguish 'each region is locally confident but their relative orientation is not' (high pLDDT + high inter-region PAE) from 'whole prediction is high quality' (high pLDDT + low PAE)."
date_proposed: 2026-04-30
date_updated: 2026-04-30
---

## Statement

pLDDT and PAE are not redundant: pLDDT estimates per-residue local accuracy (in the lDDT-Cα sense), while PAE estimates the *pairwise* error in residue `i`'s position when the prediction is aligned at residue `j`. Multi-domain reasoning — including AlphaFold-Multimer interface scoring and AFDB Foldseek-cluster downstream interpretation — requires both: a region with high pLDDT but high outward PAE is locally well-modelled but globally orientationally uncertain, which pLDDT alone cannot reveal.

## Evidence summary

The AlphaFold DB 2024 paper documents both metrics as first-class outputs, codifies the operational pLDDT tier guidance (>90 / 70-90 / 50-70 / <50), and invests engineering effort specifically in coupling the PAE viewer to the 3D viewer for inter-domain interpretation. The investment makes sense only if the two metrics are non-redundant.

## Conditions and scope

- Both metrics are *predicted*; calibration on out-of-distribution sequences (viral, designed, IDR-rich) is uncertain.
- For single-domain / short-sequence predictions, pLDDT alone may be adequate; PAE's added value is concentrated in multi-domain and complex reasoning.
- The 2022-07 numerical bug poisoned ~4% of pLDDT values until the 2022-11 fix; the v3-vs-v4 split must be respected when evaluating downstream pipelines that pre-date the fix.

## Counter-evidence

- For users whose downstream task only needs binding-site / single-residue reasoning, PAE provides little marginal information beyond pLDDT.
- Aggregate PAE summaries (mean inter-domain PAE) and aggregate pLDDT correlate strongly on average, so for *coarse* confidence triage, either metric alone may suffice.

## Linked ideas

(None yet.)

## Open questions

- What is the right principled fusion of pLDDT and PAE into a single downstream-task-aware confidence score?
- How calibrated is PAE on out-of-distribution sequences?
- Should pLDDT-low regions be treated as predicted IDRs by default?
