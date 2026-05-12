---
title: "TernaryDB"
slug: "ternarydb"
aliases: ["TernaryDB CRBN+VHL", "TernaryDB CRBN/VHL"]
tags: [protac, ternary-complex, e3-ligase, crbn, vhl, drug-discovery]
maturity: active
access: public
versions:
  - version: "v1"
    released: ""
    url: ""
    n_entries: ""
    notes: "Release alongside DeepTernary (Nat. Commun. 2025). CRBN+VHL subset used by every PROTAC ternary-complex predictor cited in `ptm-aware-degrader-target-nomination`."
canonical_url: ""
license: ""
key_papers: []
key_concepts: []
date_updated: 2026-05-11
---

## Overview

TernaryDB is a curated collection of (POI, E3, PROTAC) ternary-complex tuples used to train and evaluate PROTAC ternary-complex predictors. It is the canonical benchmark behind the current generation of compute pipelines — DeepTernary (Nat. Commun. 2025), PROTAC-STAN (Adv. Sci. 2025), ET-PROTACs (Brief. Bioinform. 2024). The [[crbn]]+VHL subset is the de-facto evaluation split because [[crbn]] and VHL are the two recruitable E3 ligases for which there is enough wet-lab signal to fit a scorer.

The dataset is one of the central anchors of [[ptm-aware-degrader-target-nomination]] — every PTM-blind baseline this idea seeks to displace was trained on TernaryDB CRBN+VHL.

## Versions

- **v1** — released with the DeepTernary publication. CRBN+VHL subset (≈100 training tuples per the Phase-0 noise-floor calibration design in [[phase0-noise-floor-calibration-deepternary-ptm-perturbations]]). Exact version date, canonical mirror URL, and total entry counts are not yet pinned — flag for the C8 (bio-lint) check once that lands.

When a new TernaryDB release ships, append a new versions entry rather than rewriting v1; downstream experiments record which version they ran on via `setup.dataset` plus an outgoing `dataset_version_used` edge (B3, drafted).

## Access and licensing

Public release accompanying the DeepTernary paper. License and canonical URL **TBD** — re-validate when ingesting the DeepTernary paper itself. Until then, treat `access: public` as a soft default; do not redistribute raw entries pending license confirmation.

## Schema and entries

Each entry is a (POI, E3, PROTAC) tuple with:

- **POI**: protein of interest — canonical sequence and PDB structure.
- **E3**: ligase identity (CRBN or VHL in the public subset; expanded set in v2 deferred).
- **PROTAC**: bifunctional small-molecule degrader linking POI ligand to E3 ligand.
- **pTernary**: the published ternary-complex score from the source paper that introduced the tuple.

Notable absence in the current schema: **PTM state of the POI is not recorded**. Every POI is treated as wild-type, canonical-sequence. This is the structural gap that motivates [[ptm-aware-degrader-target-nomination]] — the dataset does not expose phosphorylation / ubiquitylation / acetylation / methylation occupancy of the POI surface, so no PTM-blind scorer trained on it can distinguish a PTM-isoform from its canonical form.

## Known caveats

1. **CRBN/VHL coverage bias (~80%)**. Per the risk analysis in [[ptm-aware-degrader-target-nomination]], "PROTAC-DB is ≈80% CRBN/VHL-biased, so claims about 'extended-canon E3 set' do not generalize without v2 work." The same coverage bias is inherited by TernaryDB, which sources tuples from PROTAC-DB. Generalisation to MDM2 / IAP / exotic E3s is out of scope for current scorers.
2. **PTM-blindness** (see above). Any ΔpTernary analysis on TernaryDB CRBN+VHL is asking the scorer to discriminate inside its training-distribution noise floor — Phase-0 noise-floor calibration in [[phase0-noise-floor-calibration-deepternary-ptm-perturbations]] is the load-bearing mitigation.
3. **Thin positive set for PTM-selective degraders**. Truly PTM-selective experimental degraders number < 10 across the literature; the TernaryDB CRBN+VHL split inherits this scarcity. Mitigation: synthetic positives from kinase-substrate phospho-degron pairs (DegronMD).

## Used by experiments

- [[deepternary-baseline-ternarydb-crbn-vhl-reproduction]] — baseline reproduction (CRBN+VHL test split)
- [[phase0-noise-floor-calibration-deepternary-ptm-perturbations]] — Phase-0 calibration on CRBN+VHL training subset
- [[calibrated-deltapternary-phospho-protac-ranking]], [[ablation-uncalibrated-vs-calibrated-deltapternary]], [[ablation-boltz2-ptm-vs-md-relaxed-route]], [[ablation-deepternary-vs-protac-stan-scorer]], [[robustness-cross-ptm-type-ubiq-methyl]], [[robustness-mutant-isoform-track-y220c-r175h]] — downstream stages in the PTM-aware degrader pipeline; each will record its dataset version once the B3 `dataset_version_used` edge type is merged.

## Key papers

TBD — ingest the DeepTernary, PROTAC-STAN, and ET-PROTACs papers to populate this backlink list. Currently the `[[ternarydb]]` reference is reachable only through experiments and ideas, not papers.
