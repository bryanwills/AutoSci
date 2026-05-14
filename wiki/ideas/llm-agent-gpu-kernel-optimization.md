---
title: "LLM/Agent-based GPU Kernel Optimization"
slug: llm-agent-gpu-kernel-optimization
status: proposed
origin: "User research direction: LLM/agent for GPU kernel optimization"
origin_gaps: [llm-kernel-synthesis, gpu-kernel-optimization]
tags: [llm, agents, gpu, kernel-optimization, code-generation]
target_venue: ""
novelty_score: 0
priority: 3
pilot_result: ""
failure_reason: ""
linked_experiments: []
date_proposed: 2026-05-14
date_resolved: ""
---

## Motivation

GPU kernel optimization remains a bottleneck in high-performance computing and ML systems. Despite advances in auto-tuning and compiler frameworks, writing high-performance GPU kernels still requires deep hardware expertise. The recent success of LLMs in code generation, combined with agent-based iterative refinement, opens a path toward automating this process end-to-end.

## Hypothesis

LLM-based agents with access to profiling feedback, hardware specifications, and iterative refinement loops can generate GPU kernels that match or approach expert-level performance across diverse kernel types and hardware targets.

## Approach sketch

1. Use an LLM to generate initial kernel code from specifications
2. Deploy agents that test, profile, and iteratively refine the kernel
3. Incorporate hardware-aware features (memory hierarchy, thread block sizing)
4. Evaluate against expert-written baselines and existing benchmarks

## Novelty argument

While individual components exist (LLM code generation, agent frameworks, kernel optimization), the integration of these into a cohesive system with hardware-aware feedback loops and comprehensive benchmarking represents a frontier research direction. See [[new-compiler-stack-survey-synergy-llms]] for the broader context.

## Target venue



## Risks

- LLM-generated kernels may have subtle correctness issues under edge cases
- Performance gap between LLM-generated and expert-optimized kernels may be significant
- Generalization across GPU architectures remains challenging

## Pilot results



## Lessons learned

