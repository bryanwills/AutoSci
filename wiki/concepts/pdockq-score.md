---
title: "pDockQ score"
aliases: [predicted DockQ, pDockQ, AlphaFold interface confidence score]
tags: [alphafold2, protein-protein-interaction, confidence-score, structural-biology]
maturity: active
key_papers: [towards-structurally-resolved-human-protein-interaction]
first_introduced: "2022"
date_updated: 2026-04-30
related_concepts: []
---

## Definition

pDockQ is a scalar interface-confidence score for AlphaFold2-predicted protein-protein complexes. It combines the predicted local Distance Difference Test (plDDT) at the interface with the size of the predicted interface into a single number trained to approximate the experimental DockQ score, allowing predicted dimers to be ranked by likely correctness without ground-truth structures.

## Intuition

A predicted complex can be wrong in two ways: the model may be globally low-confidence (low plDDT everywhere), or the interface itself may be tiny and incidental even if both monomers are well predicted. pDockQ folds both signals into one number: confidence at the contact patch, weighted by how much of a contact patch there is. High pDockQ should mean both monomers are well placed *and* there is a real interface to be confident about.

## Formal notation

pDockQ is fit to predict the DockQ score of a complex from features computed on the AlphaFold2 prediction:

- `interface_plDDT`: mean plDDT over residues within the predicted interface contact distance
- `interface_size`: number of residues at the interface (or a related size measure)

The original [[folddock-pipeline]] paper trains a logistic-style mapping from these features to predicted DockQ. Calibration thresholds reported on human PPIs:

- `pDockQ > 0.23`: ~70% of models above this score are correct (DockQ > 0.23)
- `pDockQ > 0.5`: ~80% of models above this score are correct

## Variants

- pDockQ on AF2 dimers (this concept's default)
- pDockQ used as a ranking signal for iterative higher-order assembly (paper [[towards-structurally-resolved-human-protein-interaction]] sorts dimers by pDockQ before chaining alignments)

## Comparison

- DockQ: ground-truth metric from CAPRI; needs a reference structure. pDockQ is a *prediction* of DockQ usable when no reference exists.
- plDDT (per-residue): AF2's per-residue confidence; not interface-aware on its own.
- iPTM (AF-Multimer): AlphaFold-Multimer's interface-PTM score; a sibling concept aimed at the same problem with different feature inputs.

## When to use

- Ranking large batches of AF2-predicted complexes when no experimental references exist (interactome-scale screening, structural-biology pipelines).
- Picking high-confidence subsets for downstream biology (interface-mutation analysis, phosphosite mapping, assembly construction).

## Known limitations

- ~20% of pDockQ > 0.5 predictions are still incorrect — high-confidence does not mean correct.
- Cannot break paralog symmetry: in complexes with homologous subunits, pDockQ may be high while the chain identities are swapped.
- Underperforms on transient and disorder-dominated interactions, where AF2 itself struggles; pDockQ inherits this failure mode.
- Calibration constants depend on the underlying predictor and pipeline (FoldDock + AF2); they may not transfer to other complex predictors without re-fitting.

## Open problems

- A confidence score that distinguishes "no interaction" from "transient interaction we cannot model" rather than collapsing both into low pDockQ.
- Joint calibration with orthogonal experimental constraints (XL-MS, co-evolution, co-localisation) so confidence reflects multiple evidence channels.

## Key papers

- [[towards-structurally-resolved-human-protein-interaction]] — applies pDockQ at human-interactome scale; calibrates against 1,465 solved complexes and orthogonal XL-MS data.

## My understanding

pDockQ is a pragmatic, well-validated interface confidence score for the AF2 era. Its main value is operational: it lets you rank tens of thousands of predicted complexes and pick the strict cutoff (~0.5) for downstream mechanistic claims and the loose cutoff (~0.23) for hypothesis generation. Future complex predictors will likely retire pDockQ in favour of model-native confidences (iPTM and successors), but the calibration pattern — predict the gold-standard metric from the model's own internal features and validate against orthogonal experiments — is the durable lesson.
