---
title: "Evolutionary-Guided Program Search"
aliases: [llm-evolutionary-search, evolutionary-tiling-search]
tags: [evolutionary-algorithm, program-search, hardware-in-the-loop, llm-agent, auto-tuning]
maturity: emerging
definition: "Evolutionary-Guided Program Search uses LLMs as intelligent mutation operators within an evolutionary algorithm to search over program structures (e.g., tiling configurations), with hardware execution feedback serving as the fitness function."
key_papers: [ascendoptimizer]
first_introduced: "AscendOptimizer (2026)"
date_updated: 2026-05-14
related_concepts: [gpu-kernel]
linked_ideas: []
---

## Definition

A search paradigm where an evolutionary algorithm maintains a population of candidate programs (e.g., tiling functions), uses an LLM as a semantic-aware mutation operator to generate offspring, and evaluates fitness through real hardware execution. Infeasible candidates (compilation failures, precision errors) are immediately discarded, forcing the search to converge to valid, high-performance regions.

## Intuition

Traditional auto-tuning uses numerical search over parameters. By using an LLM as the mutator, the search can make semantic-level code changes (e.g., restructuring loop logic, adjusting memory alignment strategies) that go beyond simple parameter tweaking.

## Variants

- **Parameter-only evolution**: Mutate numeric parameters within fixed templates
- **Structural evolution**: Mutate code logic and control flow
- **Hybrid evolution**: Combine parameter fine-tuning with logic rewriting

## Comparison

| Approach | Search Space | Semantic Awareness | Hardware Feedback |
|----------|-------------|-------------------|------------------|
| Grid/Random Search | Parameters only | None | Yes |
| Bayesian Optimization | Parameters only | Cost model | Yes |
| LLM Evolutionary Search | Code structure | High (LLM priors) | Yes |

## Known limitations

- Requires hardware-in-the-loop (expensive per evaluation)
- LLM mutation quality depends on the model's code understanding
- Population diversity can collapse prematurely

## Open problems

- Reducing the number of hardware evaluations needed
- Incorporating cost models to pre-filter candidates
- Scaling to larger program search spaces

## Relationship to foundations

Combines ideas from evolutionary programming, neural architecture search, and LLM code generation. The key insight is that LLMs bring semantic priors that guide exploration more efficiently than random mutation.

## My understanding

The novelty is treating the LLM as a "smart mutator" rather than a generator. The evolutionary framework provides exploration pressure, while the LLM provides semantic awareness. The zero-tolerance hardware feedback is what makes this work on the discontinuous tiling landscape.
