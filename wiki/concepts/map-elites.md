---
title: MAP-Elites
aliases: [map-elites-algorithm, multidimensional-archive-of-phenotypic-elites]
tags: [evolutionary-algorithms, quality-diversity, optimization, neuroevolution]
maturity: stable
definition: "MAP-Elites (Multidimensional Archive of Phenotypic Elites) is a quality-diversity algorithm that partitions the solution space into a discrete grid based on behavioral descriptors, maintaining the highest-fitness solution (elite) for each occupied cell."
key_papers: [kernelfoundry-hardware-aware-evolutionary-gpu-kernel]
first_introduced: "Mouret & Clune, 2015"
date_updated: 2026-05-14
related_concepts: [quality-diversity-search]
linked_ideas: [llm-agent-gpu-kernel-optimization]
---

## Definition

MAP-Elites is a quality-diversity (QD) algorithm that maintains a diverse archive of high-performing solutions by partitioning the solution space into a discrete grid based on behavioral descriptors. Each cell in the grid stores the best-performing solution (elite) discovered for that behavioral region. The algorithm iterates through four phases: selection, variation, evaluation, and insertion.

## Intuition

Instead of optimizing a single objective (which risks convergence to local optima), MAP-Elites explores multiple behavioral dimensions simultaneously. Think of it as creating a map of the best solutions across different strategies, ensuring diversity by construction since each cell evolves independently.

## Variants

- **CMA-ME**: Adds continuous optimization to MAP-Elites
- **PGA-MAP-Elites**: Integrates policy gradients for improved search
- **KernelFoundry adaptation**: Uses kernel-specific behavioral descriptors (memory access patterns, algorithmic structure, parallelism coordination)

## Comparison

| Feature | Standard EA | MAP-Elites |
|---------|------------|------------|
| Diversity | Implicit | Explicit via behavioral grid |
| Mode collapse | Risk | Prevented by design |
| Exploration | Single trajectory | Multiple behavioral regions |
| Solution archive | Single best | Grid of elites |

## Known limitations

- Grid resolution must be chosen carefully (too coarse loses diversity, too fine wastes computation)
- Behavioral descriptors must be meaningful for the domain
- Computational cost scales with grid size

## Open problems

- Adaptive grid resolution based on search progress
- Automatic discovery of relevant behavioral dimensions
- Integration with LLM-based code generation

## Relationship to foundations

MAP-Elites builds on quality-diversity algorithms and evolutionary computation, providing a structured approach to maintaining diverse high-performing solutions.

## My understanding

MAP-Elites is particularly well-suited for kernel optimization because the space has natural behavioral dimensions (memory access patterns, algorithmic structure, parallelism coordination) that can be captured via static code analysis.
