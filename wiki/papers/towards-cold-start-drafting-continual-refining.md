---
title: "Towards Cold-Start Drafting and Continual Refining: A Value-Driven Memory Approach with Application to NPU Kernel Synthesis"
slug: towards-cold-start-drafting-continual-refining
venue: ICLR
year: 2026
tags: [kernel-synthesis, cold-start, reinforcement-learning, memory-augmented, NPU, value-driven-retrieval, agentic-framework]
importance: 4
date_added: 2026-05-14
source_type: tex
tldr: "EvoKernel is a self-evolving agentic framework that formulates kernel synthesis as a memory-based RL task, using value-driven retrieval with stage-specific Q-values to bootstrap correct kernels from scratch and iteratively optimize latency on data-scarce NPU platforms."
contribution_type: [method, benchmark, system]
datasets: [ascend-c-kernelbench, attention-set, mhc-kernels]
code_url: https://evokernel.zhuo.li
cited_by: []
---

## Abstract

Deploying Large Language Models to data-scarce programming domains poses significant challenges, particularly for kernel synthesis on emerging Domain-Specific Architectures where a "Data Wall" limits available training data. While models excel on data-rich platforms like CUDA, they suffer catastrophic performance drops on data-scarce ecosystems such as NPU programming. To overcome this cold-start barrier without expensive fine-tuning, we introduce EvoKernel, a self-evolving agentic framework that automates the lifecycle of kernel synthesis from initial drafting to continual refining. EvoKernel addresses this by formulating the synthesis process as a memory-based reinforcement learning task. Through a novel value-driven retrieval mechanism, it learns stage-specific Q-values that prioritize experiences based on their contribution to the current objective -- whether bootstrapping a feasible draft or iteratively refining latency. Furthermore, by enabling cross-task memory sharing, the agent generalizes insights from simple to complex operators. By building an NPU variant of KernelBench and evaluating on it, EvoKernel improves frontier models' correctness from 11.0% to 83.0% and achieves a median speedup of 3.60x over initial drafts through iterative refinement.

## Key Contributions

- **Unified Drafting-Refining Pipeline:** A two-stage framework over a shared memory that transitions from feasibility-driven drafting to latency-driven refining to bootstrap and optimize NPU kernels.
- **Evolving Value-Driven Retrieval:** A retrieval mechanism that learns stage-specific Q-values to quantify memory utility, with a unified Monte-Carlo update that adapts the policy from verifier feedback without updating model weights.
- **Comprehensive Evaluation:** Boosts performance on NPU benchmarks from 11.0% to 83.0% correctness, with in-depth analysis of cross-task transfer, emergent curricula, and scaling to out-of-distribution workloads.

## Method Summary

EvoKernel formulates kernel synthesis as a Memory-based Markov Decision Process (M-MDP). The framework consists of:

1. **Memory Architecture**: A heterogeneous knowledge base containing API templates, summarized success/failure experiences, generation traces, and best practices.
2. **Value-Driven Retrieval**: Stage-specific Q-value functions (Q1 for drafting feasibility, Q2 for latency optimization) that filter a dense-retrieval candidate pool to select high-utility context items.
3. **Cold-Start Drafting (Stage 1)**: Iterative retrieval-and-generation with binary feasibility rewards, using epsilon-greedy exploration over Q1 values.
4. **Continual Refining (Stage 2)**: Maintains optimization start points, uses Q2 for start-point and context selection, with relative latency rewards normalized via PopArt-style statistics.
5. **Multi-Gate Verification**: Anti-hacking screening, compilation checking, correctness validation, and latency profiling.

## Main Results

- With GPT-5.2: 98.5% compilation rate, 83.0% correctness (vs. 11.0% baseline)
- Median 3.60x speedup over first feasible draft through iterative refinement
- Cross-task memory transfer: L1 memory bootstraps L2, achieving 64% L2 correctness at iteration 17 (vs. 34% from scratch)
- Cross-backbone transfer: GPT-5.2 memory improves DeepSeek-V3.2 from 6% to 58% correctness
- Scaling to Attention Set (CUDA): 100% correctness on 250 operators
- Scaling to mHC kernels (Ascend): 66.7% correctness on 15 DeepSeek architectural kernels

## Related

- [[value-driven-retrieval]]
- [[memory-based-mdp]]
- [[cold-start-kernel-synthesis]]
- [[kernel-benchmark]]
- [[gpu-kernel]]

## Notes

### Key Insight
Frontier LLMs' enhanced in-context learning capabilities make memory-based, non-parametric approaches practically viable for cold-start kernel synthesis. The value-driven retrieval mechanism induces adaptive curriculum learning without explicit task ordering.

### Limitations
- Level 2 accuracy remains 0% for weaker models (Qwen3-Coder-30B, DeepSeek-V3.2)
- Optimal candidate pool size multiplier remains an open question
- Framework primarily instantiated on Ascend C; cross-architecture universality needs verification
