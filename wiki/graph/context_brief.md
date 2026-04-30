# Query Pack (general)

_Auto-generated compressed context. Do not edit._

## Claims (15 total)
- [supported] AlphaFold2 enables large-scale structural modeling of human PPI network (conf: 0.75)
- [weakly_supported] Deep-learning ensembles with sequence-only input outperform feature-engineered classical ML for PTM site prediction across most PTM types (conf: 0.6)
- [supported] Deep learning can predict protein structure at near-experimental atomic accuracy from sequence alone (conf: 0.92)
- [weakly_supported] Diffusion-based atom-coordinate generation eliminates the need for equivariant frame-based structure modules (conf: 0.55)
- [supported] E3 ligase deregulation in cancer alters substrate stability and is therapeutically exploitable in a context-dependent manner (conf: 0.85)
- [supported] Heterogeneous biological evidence integrated by naive Bayes predicts human E3-substrate interactions at proteome scale (conf: 0.75)
- [supported] Equivariant 3D neural networks reliably outperform 2D-graph baselines for quantum-chemistry targets but not consistently for drug-discovery property prediction (conf: 0.7)
- [supported] Geometric priors (equivariance / invariance) systematically improve neural-network modelling of molecular systems (conf: 0.75)
- [supported] Stringent high-throughput Y2H recovers many novel disease-associated human PPIs at low inspection bias (conf: 0.8)
- [supported] MSA depth bounds the achievable accuracy of MSA-conditioned protein structure predictors (conf: 0.85)
- [weakly_supported] Integrating multi-omics data with machine learning and network-pharmacology models enables identification of multi-target therapeutic strategies that single-omics analysis cannot recover (conf: 0.55)
- [supported] pLDDT and PAE are complementary confidence metrics — pLDDT for per-residue local accuracy, PAE for pairwise relative-position accuracy (conf: 0.9)
- [supported] Pre-computed AlphaFold-predicted structure databases enable proteome-scale structural biology that on-demand prediction cannot (conf: 0.85)
- [weakly_supported] PTM protein isoforms enable sele
## Open Gaps
_Auto-generated open questions. Do not edit._
- [paper/accurate-structure-prediction-biomolecular-interactions-alphafold] Can a generative structure predictor be coupled to an MSA-resampling or ensemble-sampling scheme to recover dynamical / multi-state behaviour rather than collapsing to a single PDB-like snapshot?
- [paper/accurate-structure-prediction-biomolecular-interactions-alphafold] How much of AF3's lift over specialised docking tools comes from joint training versus the diffusion formulation versus dataset scale? Ablations isolating each are not reported.
- [paper/accurate-structure-prediction-biomolecular-interactions-alphafold] What is the smallest training set (or which data slices) sufficient to match AF3 quality on a given complex class — i.e. how data-efficient is the unified framework relative to specialised predictors per class?
- [paper/accurate-structure-prediction-biomolecular-interactions-alphafold] Can the diffusion module's lack of equivariance be exploited (or replaced) to add cheap symmetry-aware prior, narrowing the chirality-violation gap?
- [paper/accurate-structure-prediction-biomolecular-interactions-alphafold] Does the same recipe transfer to membrane proteins, glycan-only structures, RNA-RNA tertiary contacts, or ribozyme catalysis intermediates that are under-represented in the PDB?
- [paper/alphafold-protein-structure-database-2024-providing] How should isoform-level structural coverage be represented and indexed? UniProt isoforms are curren
## Papers (11 total)
- [5] Accurate structure prediction of biomolecular interactions with AlphaFold 3 (Computational Biology / ML for Science)
- [5] Highly accurate protein structure prediction with AlphaFold (Structural Biology / ML for Science)
- [4] AlphaFold Protein Structure Database in 2024: providing structure coverage for over 214 million protein sequences (Structural Bioinformatics)
- [4] Geometric deep learning on molecular representations (ML for Molecules)
- [5] Towards a proteome-scale map of the human protein-protein interaction network (Computational Biology)
- [4] Towards a structurally resolved human protein interaction network (Computational Biology)
- [4] Ubiquitin ligases in oncogenic transformation and cancer therapy (Cancer biology / Molecular oncology)
- [2] From Data to Cure: A Comprehensive Exploration of Multi-omics Data Analysis for Targeted Therapies (Computational Biology)
- [3] Drug design targeting active posttranslational modification protein isoforms (Computational Drug Design / Chemical Biology)
- [3] An integrated bioinformatics platform for investigating the human E3 ubiquitin ligase-substrate interaction network (computational biology)
- [3] MusiteDeep: a deep-learning based webserver for protein post-translational modification site prediction and visualization (Bioinformatics)
## Recent Relationships (41 total)
  papers/towards-structurally-resolved-human-protein-interaction --uses_concept--> concepts/folddock-pipeline
  papers/towards-structurally-resolved-human-protein-interaction --uses_concept--> concepts/pdockq-score
  papers/towards-structurally-resolved-human-protein-interaction --uses_concept--> concepts/protein-protein-interaction-interface
  papers/towards-structurally-resolved-human-protein-interaction --supports--> claims/alphafold2-enables-large-scale-structural-modeling
  papers/alphafold-protein-structure-database-2024-providing --introduces_concept--> concepts/alphafold-db
  papers/alphafold-protein-structure-database-2024-providing --uses_concept--> concepts/predicted-aligned-error
  papers/alphafold-protein-structure-database-2024-providing --uses_concept--> concepts/plddt
  papers/alphafold-protein-structure-database-2024-providing --supports--> claims/precomputed-structure-databases-enable-proteome-scale-biology
  papers/alphafold-protein-structure-database-2024-providing 
