---
title: "StitchCUDA: An Automated Multi-Agents End-to-End GPU Programming Framework with Rubric-based Agentic Reinforcement Learning"
slug: stitchcuda
arxiv: ""
venue: ICML 2026
year: 2026
tags: [gpu-programming, multi-agent, reinforcement-learning, cuda, code-generation, end-to-end-optimization]
importance: 4
date_added: 2026-05-14
source_type: tex
s2_id: ""
tldr: "A multi-agent framework (Planner, Coder, Verifier) with rubric-based agentic RL for end-to-end GPU program generation, achieving near-100% success rate on KernelBench Level 3."
contribution_type: [framework, method, system]
datasets: [kernelbench]
code_url: ""
cited_by: []
---

## Summary

StitchCUDA addresses the challenge of automated end-to-end GPU program generation, moving beyond single-kernel optimization to full program-level systems. It uses three specialized agents -- Planner, Coder, and Verifier -- in an iterative plan-code-profile-refine loop. The Coder is further enhanced via rubric-based agentic reinforcement learning that decomposes multi-turn RL into two atomic skills (from-scratch generation and feedback-driven optimization), combined with rubric rewards to prevent reward hacking and degenerate behaviors.

## Key contributions

1. **Multi-agent framework for end-to-end GPU programming**: Three specialized agents (Planner, Coder, Verifier) with expert CoT prompts and RAG-augmented CUDA documentation.
2. **Rubric-based agentic RL**: Decomposes multi-turn agentic RL into atomic skills with combined rubric reward and rule-based reward, preventing reward hacking while improving Coder capability.
3. **Strong empirical results**: Near-100% success rate on KernelBench Level 3 with 1.5x average speedup over PyTorch eager, 1.72x over multi-agent baselines, and 2.73x over RL model baselines.

## Method

### Multi-agent workflow
- **Planner**: Parses reference PyTorch code, profiles with Nsys, generates structured to-do list with kernel fusion boundaries, tensor shape/layout contracts, and CPU-GPU overlapping specs.
- **Coder**: Implements CUDA code for each subtask, compiles with nvcc, refines based on Verifier feedback.
- **Verifier**: Validates correctness, profiles with Nsys (system-level) and NCU (kernel-level), classifies kernels as memory-bound or compute-bound, generates actionable optimization suggestions.

### Rubric-based agentic RL
- Decomposes multi-turn agentic RL into two atomic skills: (1) from-scratch generation, (2) feedback-driven optimization.
- Rubric reward scored on four dimensions: Anti-Hacking, CUDA Engineering, Operator Coverage, Skill Compliance.
- Combined reward: rule-based (correctness + speedup) with rubric shaping, using GRPO training on Qwen3-32B.
- Single-turn RL training is substantially more efficient than multi-turn agentic RL.

## Results

- KernelBench Level 3 (10 end-to-end tasks): StitchCUDA achieves 10/10 correctness with 1.50x speedup on H200.
- Outperforms CUDAForge (6/10, 0.87x) and Kevin-32B (2/10, 0.34x) on Level 3.
- RL-trained Coder (StitchCUDA) vs untrained (StitchCUDA-Q): correctness 3/10 -> 9/10, speedup 0.24x -> 1.50x on Level 3.
- Rubric reward reduces reward hacking: 8/50 partial hackings vs 22/50 for Kevin-32B backbone.

## Related

- [[kernel-benchmark]]
- [[gpu-kernel]]
- [[multi-agent-gpu-programming]]
- [[rubric-based-reinforcement-learning]]
- [[reward-hacking-prevention]]
