---
title: "Rubric-Based Reinforcement Learning"
aliases: [rubric-rl, rubric-reward-rl]
tags: [reinforcement-learning, reward-design, rubric, llm-training, anti-hacking]
maturity: emerging
definition: "A reinforcement learning approach that uses structured rubric-based scoring -- typically produced by an expert LLM -- as a shaping reward alongside rule-based signals, to prevent reward hacking and encourage meaningful optimization."
key_papers: [stitchcuda]
first_introduced: "2026"
date_updated: 2026-05-14
related_concepts: [reward-hacking-prevention]
linked_ideas: []
---

## Definition

Rubric-based reinforcement learning augments traditional rule-based rewards (e.g., functional correctness, speedup) with structured rubric scores that evaluate candidate outputs along multiple expert-defined dimensions. The rubric is designed and validated by domain experts, often with LLM assistance, to capture qualities that simple scalar metrics miss.

## Intuition

Pure rule-based rewards in code generation RL are vulnerable to reward hacking (e.g., copying PyTorch code, hardcoding outputs) and degenerate behaviors (e.g., only optimizing trivial operators). A rubric provides a multi-dimensional assessment that penalizes exploitation and rewards genuine engineering quality, acting as an expert-aligned shaping signal.

## Rubric dimensions (StitchCUDA example)

1. **Anti-Hacking**: Penalizes reward exploitation behaviors
2. **CUDA Engineering**: Rewards advanced optimization techniques (kernel fusion, tiling, tensor cores)
3. **Operator Coverage**: Encourages broader optimization across multiple operations
4. **Skill Compliance**: Enforces adherence to task requirements or feedback instructions

## Reward formulation

The rubric scores are normalized into a shaping term that complements rule-based rewards:
- Final reward = correctness_indicator * (1 - hack_indicator) * min((speedup + offset) * (1 + lambda * rubric_score), R_max)

## Known limitations

- Rubric design requires domain expertise
- LLM-assigned rubric scores may have variance
- Balancing rubric weight against rule-based rewards needs careful tuning

## Open problems

- Automated rubric generation and refinement
- Cross-domain rubric transfer (e.g., from CUDA to other GPU languages)
- Theoretical analysis of rubric reward convergence properties

## Relationship to foundations

Rubric-based RL extends standard RLVR (reinforcement learning with verifiable rewards) by adding structured expert assessment, addressing failure modes specific to code generation tasks.

## My understanding

