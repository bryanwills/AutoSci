---
title: Memory-based Markov Decision Process
aliases: [M-MDP, memory-augmented-mdp]
tags: [reinforcement-learning, MDP, memory-augmented, decision-process, agentic-framework]
maturity: emerging
definition: "A Memory-based Markov Decision Process (M-MDP) extends the standard MDP formulation by incorporating a dynamic, self-evolving memory bank that accumulates interaction history and influences the agent's policy through learned retrieval."
key_papers: [towards-cold-start-drafting-continual-refining]
first_introduced: 2026
date_updated: 2026-05-14
related_concepts: [value-driven-retrieval]
linked_ideas: []
---

## Definition

An M-MDP augments the standard MDP tuple (S, A, P, R) with a memory component M that evolves over time. The memory bank accumulates the agent's interaction history (state-action-reward triples) and serves as an external knowledge base that the retrieval policy can query to construct context for the generator.

## Formal Definition

An M-MDP is defined by the tuple (S, A, M, P, R) where:

- **State Space (S)**: A state s_t = (x, xi_t) where x is the static task and xi_t is the dynamic generation state
- **Action Space (A)**: Actions correspond to generated outputs (e.g., kernel code)
- **Memory (M)**: A dynamic knowledge base that evolves as M_{t+1} <- M_t union {(s_t, a_t, r_t)}
- **Transition Dynamics (P)**: Deterministic updates conditioned on verifier outcomes
- **Reward Function (R)**: Scalar feedback from environment evaluation

## Policy Factorization

The agent's policy is factored into two components:

1. **Retrieval Policy (mu)**: Selects context c_t from memory M based on current state
2. **Generator Policy (G_theta)**: Produces output conditioned on state and retrieved context

pi(y_t | s_t, M_t) = G_theta(a_t | s_t, c_t) * mu(c_t | s_t, M_t)

This factorization allows optimizing the retrieval policy via RL while keeping the generator (LLM) fixed.

## Key Properties

- **Self-evolving**: Memory grows with each interaction, accumulating diverse experiences
- **Non-parametric learning**: Learning happens in the memory bank, not in model weights
- **Compositional**: Different retrieval strategies can be plugged in (similarity, value-driven, hybrid)
- **Persistent**: Unlike context-window-based approaches, memory persists across episodes

## Applications

- **Kernel Synthesis**: EvoKernel uses M-MDP for cold-start kernel generation with value-driven retrieval
- **Code Generation**: General framework for memory-augmented code agents
- **Procedural Memory**: Foundation for agents that learn reusable skills and patterns

## Relationship to foundations

M-MDP extends classical reinforcement learning by treating memory as a first-class component of the decision process. It connects to work on memory-augmented neural networks, experience replay, and retrieval-augmented generation.

## My understanding

The M-MDP formulation is elegant because it separates "what to generate" (generator policy) from "what to remember" (retrieval policy). This allows the system to improve its context selection through RL without modifying the underlying LLM, making it applicable to any pre-trained model.
