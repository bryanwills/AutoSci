---
title: Value-Driven Retrieval
aliases: [q-value-retrieval, learned-retrieval-policy]
tags: [retrieval, reinforcement-learning, memory-augmented, Q-value, context-selection]
maturity: emerging
definition: "Value-driven retrieval is a mechanism that learns stage-specific Q-values to quantify the utility of memory items for context selection, replacing traditional similarity-based retrieval with RL-trained value estimates."
key_papers: [towards-cold-start-drafting-continual-refining]
first_introduced: 2026
date_updated: 2026-05-14
related_concepts: [memory-based-mdp, cold-start-kernel-synthesis]
linked_ideas: []
---

## Definition

Value-driven retrieval is a context selection mechanism used in memory-augmented LLM agents. Instead of relying on semantic similarity to select relevant context items, it learns Q-value functions that estimate the expected benefit of including each memory item in the current context. These Q-values are updated via reinforcement learning from environment feedback (e.g., compilation success, correctness, latency).

## Intuition

Traditional retrieval asks "what looks similar?" while value-driven retrieval asks "what will actually help?" A code snippet that looks irrelevant by cosine similarity might contain a crucial pattern that enables the current task to succeed. The Q-value captures this utility signal through experience.

## Mechanism

1. **Dense Retrieval**: First, obtain a top-K candidate pool using standard embedding similarity
2. **Value Filtering**: Use stage-specific Q-values to filter K candidates down to final N items
3. **Q-Value Update**: After receiving reward r, update Q-values for all retrieved items:
   - Q(s, m) <- Q(s, m) + alpha * (r - Q(s, m))
4. **Stage Specificity**: Different Q-functions for different objectives:
   - Q1 (Drafting): Estimates contribution to functional correctness
   - Q2 (Refining): Estimates contribution to latency optimization

## Key Properties

- **Adaptive**: Values evolve as the agent's capabilities change
- **Stage-aware**: Different retrieval policies for different synthesis phases
- **Non-parametric**: No model weight updates required
- **Cross-task**: Values transfer across related tasks

## Theoretical Guarantees

- **Boundedness**: Value iterates remain in [-R_max, R_max] under bounded rewards
- **Convergence**: Bandit-style updates converge under Robbins-Monro conditions
- **Normalization Stability**: PopArt-style reward normalization stabilizes asymptotically

## Comparison with Other Retrieval Approaches

| Approach | Selection Criterion | Adapts to Feedback | Cross-task Transfer |
|----------|---------------------|-------------------|---------------------|
| Similarity-based | Cosine distance | No | Limited |
| Learned embedding | Trained similarity | Static | Moderate |
| Value-driven (this) | RL Q-values | Online | Strong |

## Relationship to foundations

Value-driven retrieval bridges retrieval-augmented generation (RAG) and reinforcement learning. It treats context selection as a decision problem, applying bandit-style learning to optimize the retrieval policy online.

## My understanding

The key insight is that semantic similarity is a poor proxy for utility in code generation tasks. A functionally relevant code snippet may share little surface-level similarity with the target task. By learning from actual outcomes (compilation, correctness), the system discovers which memory items genuinely help.
