# Runtime Page Templates (bio-adaptation, Section A)

> **Mirror copy.** Source of truth: `docs/runtime-page-templates.en.md`. This file applies items A1–A8 from
> `docs/bioinformatics-adaptation-backlog.en.md`. See `docs/bio-adaptation/CHANGELOG.en.md` for the per-item diff.
> When a Section-A item is promoted from "drafted" to "adopted", merge the corresponding hunk back into the
> source file and delete (or shrink) the mirror.

> On-demand reference for full wiki page templates only. See `docs/runtime-support-files.en.md` for graph-derived files plus `index.md` and `log.md`.

<!-- bio-A1: page count grows from 9 to 10 — `datasets/` becomes a first-class entity. -->
## 10 Page Types

`papers`, `concepts`, `topics`, `people`, `ideas`, `experiments`, `claims`, `Summary`, `foundations`, `datasets` <!-- bio-A1 -->.

### papers/{slug}.md

```yaml
---
title: ""
slug: ""
arxiv: ""                    # kept — some bio papers also route bioRxiv → arXiv
# bio-A3: bio papers usually have no arXiv ID; the identifiers below are the canonical bio anchors.
# /ingest should fill these from CrossRef / PubMed E-utilities / EuropePMC, not only Semantic Scholar.
doi: ""                      # bio-A3: primary bio identifier
pmid: ""                     # bio-A3: PubMed ID
biorxiv: ""                  # bio-A3: bioRxiv DOI suffix
pdb_ids: []                  # bio-A3: structures introduced by the paper
uniprot_ids: []              # bio-A3: proteins characterised by the paper
nct_ids: []                  # bio-A3: clinical trials referenced
gene_symbols: []             # bio-A3: HGNC symbols
species: []                  # bio-A3: model organisms
venue: ""
year:
tags: []
importance: 3                # 1-5
date_added: YYYY-MM-DD
source_type: tex             # tex | pdf
s2_id: ""
keywords: []
# bio-A4: domain is informally controlled. CS values: NLP / CV / ML Systems / Robotics.
#         Bio values (recommended controlled vocabulary, lint warns when unlisted — see C8):
#         structural-bio | chembio | comp-drug-discovery | cancer-bio | systems-bio |
#         bioinformatics | clinical-translation
domain: ""
code_url: ""
cited_by: []
---
```

Body sections: `## Problem` / `## Key idea` / `## Method` / `## Results` / `## Limitations` / `## Open questions` / `## My take` / `## Related`

### concepts/{concept-name}.md

```yaml
---
title: ""
aliases: []
tags: []
# bio-A2 (light): maturity may use the bio scale (consensus | well-supported | contested |
#                 hypothesis | falsified) — see D2 for full rationale; this section keeps the
#                 CS scale as default and tolerates either.
maturity: active             # stable | active | emerging | deprecated
key_papers: []
first_introduced: ""
date_updated: YYYY-MM-DD
related_concepts: []
# bio-A2 (light): optional protein-anchored fields. Fill only when the concept *is* a specific
# gene product (p53, CRBN, …). When ≥50 such concepts accumulate or graph queries demand it,
# promote to a separate `proteins/` entity type (heavyweight option in A2).
gene_symbol: ""              # bio-A2: HGNC symbol, e.g. "TP53"
uniprot_id: ""               # bio-A2: e.g. "P04637"
pdb_ids: []                  # bio-A2: representative structures
species: []                  # bio-A2: e.g. ["human", "mouse"]
---
```

Body sections: `## Definition` / `## Intuition` / `## Formal notation` / `## Variants` / `## Comparison` / `## When to use` / `## Known limitations` / `## Open problems` / `## Key papers` / `## My understanding`

### topics/{topic-name}.md

```yaml
---
title: ""
tags: []
my_involvement: none         # none | reading | side-project | main-focus
sota_updated: YYYY-MM-DD
key_venues: []
related_topics: []
key_people: []
---
```

Body sections: `## Overview` / `## Timeline` / `## Seminal works` / `## SOTA tracker` / `## Open problems` / `## My position` / `## Research gaps` / `## Key people`

### people/{firstname-lastname}.md

```yaml
---
name: ""
affiliation: ""
tags: []
homepage: ""
scholar: ""
date_updated: YYYY-MM-DD
---
```

Body sections: `## Research areas` / `## Key papers` / `## Recent work` / `## Collaborators` / `## My notes`

### Summary/{area-name}.md

```yaml
---
title: ""
scope: ""
key_topics: []
paper_count:
date_updated: YYYY-MM-DD
---
```

Body sections: `## Overview` / `## Core areas` / `## Evolution` / `## Current frontiers` / `## Key references` / `## Related`

### foundations/{slug}.md

```yaml
---
title: ""
slug: ""
domain: ""
status: mainstream           # mainstream | historical
aliases: []
first_introduced: ""
date_updated: YYYY-MM-DD
source_url: ""
---
```

Body sections: `## Definition` / `## Intuition` / `## Formal notation` / `## Key variants` / `## Known limitations` / `## Open problems` / `## Relevance to active research`

Foundations have **no outward link fields**. Other pages may link to a foundation; foundations write no reverse link.

### ideas/{idea-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed             # proposed | in_progress | tested | validated | failed
origin: ""
origin_gaps: []
tags: []
domain: ""                   # bio-A4: same controlled vocabulary as papers/
priority: 3                  # 1-5
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: YYYY-MM-DD
date_resolved: ""
---
```

Body sections: `## Motivation` / `## Hypothesis` / `## Approach sketch` / `## Expected outcome` / `## Risks` / `## Pilot results` / `## Lessons learned`

### experiments/{experiment-slug}.md

```yaml
---
title: ""
slug: ""
status: planned              # planned | running | completed | abandoned
target_claim: ""
hypothesis: ""
tags: []
domain: ""                   # bio-A4: same controlled vocabulary as papers/
# bio-A5: setup grew from a pure ML pipeline shape to cover bio specifics.
# All bio-* fields are OPTIONAL; skills fill them only when applicable.
setup:
  model: ""
  dataset: ""                # should be a wikilink to datasets/{slug} once A1 lands
  hardware: ""
  framework: ""
  # ── bio-A5: experimental modality ──
  in_silico_or_wet: in_silico   # in_silico | wet_lab | mixed
  species: []                   # human | mouse | yeast | …
  cell_line: ""                 # prefer Cellosaurus ID (CVCL_xxxx)
  assay_type: ""                # Y2H | AP-MS | cryo-EM | NMR | MD | docking | scoring
  # ── bio-A5: MD-only fields ──
  force_field: ""               # e.g. AMBER ff14SB + phosaa14SB
  solvent_model: ""             # explicit | implicit | vacuum
  simulation_length: ""         # e.g. "50 ns"
  # ── bio-A5: ML-model versioning ──
  weight_version: ""            # e.g. "Boltz-2 Jan-2026 weights"
  random_seed_protocol: ""      # ranking-shuffle | bootstrap | LOO-CV
metrics: []
baseline: ""
outcome: ""                  # succeeded | failed | inconclusive
key_result: ""
linked_idea: ""
date_planned: YYYY-MM-DD
date_completed: ""
run_log: ""
started: ""
# bio-A6: estimated_hours is DEPRECATED — too coarse for MD / wet-lab / multi-modal cost.
#         Kept for backward compat with old experiment pages until they are migrated.
estimated_hours: 0           # deprecated, see estimated_cost below
# bio-A6: structured cost block. All sub-fields optional; skills fill what applies.
#         Tooling note: a per-assay reference table for sane defaults should live at
#         `docs/bio-compute-references.md` and be consumed by /exp-design instead of guessing.
estimated_cost:
  gpu_hours: 0
  cpu_hours: 0
  md_wallclock_hours: 0      # MD frequently dominates — track separately
  wet_lab_usd: 0             # antibodies, cell culture, sequencing
  fte_weeks: 0               # postdoc / RA time that can't be automated
  dataset_access_lead_time_days: 0   # registration, MTA, IRB
# bio-A8: optional reproducibility metadata for experiments that touch any wet-lab data
#         (including downstream consumption — e.g. a phospho-PROTAC positive set
#         compiled from published assays). Skip when fully in-silico.
reproducibility:
  rrid: []                   # antibody / reagent RRIDs
  cellosaurus: []            # cell lines (CVCL_xxxx)
  addgene: []                # plasmid IDs
  pdb_versions: []           # specific PDB entries + version
  dataset_versions: []       # list of {dataset_slug, version, accessed_date}
remote:
  server: ""
  gpu: ""
  session: ""
  started: ""
  completed: ""
---
```

Body sections: `## Objective` / `## Setup` / `## Procedure` / `## Results` / `## Analysis` / `## Claim updates` / `## Follow-up`

### claims/{claim-slug}.md

```yaml
---
title: ""
slug: ""
status: proposed             # proposed | weakly_supported | supported | challenged | deprecated
confidence: 0.5              # 0.0-1.0
tags: []
domain: ""                   # bio-A4: same controlled vocabulary
source_papers: []
# bio-A7: evidence type enum extended for bio; `strength` kept verbatim for backward compat;
# new optional `grade` records GRADE-style certainty (very-low | low | moderate | high).
# Mechanistic > correlative; clinical_validated > wet_lab_validated > mechanistic_basis;
# `predicts` marks a forward-looking computational prediction not yet validated.
evidence:
  - source: ""
    type: supports           # supports | contradicts | tested_by | invalidates |
                             # wet_lab_validated | clinical_validated | mechanistic_basis |
                             # correlative | predicts
    strength: moderate       # weak | moderate | strong  (kept for backward compat)
    grade: ""                # bio-A7: optional GRADE — very-low | low | moderate | high
    detail: ""
conditions: ""
date_proposed: YYYY-MM-DD
date_updated: YYYY-MM-DD
---
```

Body sections: `## Statement` / `## Evidence summary` / `## Conditions and scope` / `## Counter-evidence` / `## Linked ideas` / `## Open questions`

<!-- bio-A1: new entity type below. Datasets are first-class so dataset references can be
     wikilinked, versions tracked, and access tier surfaced to /exp-design and /exp-run. -->
### datasets/{slug}.md

```yaml
---
title: ""
slug: ""
aliases: []
tags: []
maturity: stable             # stable | active | emerging | deprecated
access: public               # public | registration | restricted | wet-lab-derived
# `versions` is a list of release records; downstream skills compare against
# `experiments[*].reproducibility.dataset_versions[*].version` to flag drift.
versions: []                 # list of {version, released, url, n_entries, notes}
canonical_url: ""
license: ""
key_papers: []               # backlink — populated by papers/ that cite the dataset
key_concepts: []
date_updated: YYYY-MM-DD
---
```

Body sections: `## Overview` / `## Versions` / `## Access and licensing` / `## Schema and entries` / `## Known caveats` / `## Used by experiments` / `## Key papers`
