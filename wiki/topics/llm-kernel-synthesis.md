---
title: "LLM-based Kernel Synthesis"
tags: [llm, kernel-synthesis, code-generation, gpu]
key_venues: []
related_topics: [gpu-kernel-optimization, ai-compilation]
key_people: []
linked_ideas: [llm-agent-gpu-kernel-optimization]
---

## Overview

Using large language models to automatically generate GPU kernel code from natural language descriptions, mathematical specifications, or reference implementations. This topic covers the full pipeline from prompt engineering to code validation and performance optimization.

## Timeline

- 2023-2024: Early explorations of LLM code generation for GPU kernels
- 2024-2025: Emergence of specialized benchmarks (KernelBench, TritonBench)
- 2025-2026: Agent-based frameworks with iterative refinement and hardware awareness

## Seminal works

- [[kernelbench-llms-write-efficient-gpu-kernels]] — first comprehensive benchmark
- [[tritonbench-benchmarking-large-language-model-capabilities]] — Triton-focused evaluation
- [[kernelbench-comprehensive-benchmark-evaluating-llm-generated]] — extended benchmark coverage

## SOTA tracker

| Method | Approach | Year |
|--------|----------|------|
| KernelFoundry | Evolutionary search + LLM | 2026 |
| StitchCUDA | Multi-agent + RL | 2026 |
| AscendOptimizer | Episodic agent memory | 2026 |

## Key benchmarks

- [[kernelbench-llms-write-efficient-gpu-kernels]]
- [[tritonbench-benchmarking-large-language-model-capabilities]]
- [[kernelbench-comprehensive-benchmark-evaluating-llm-generated]]

## Open problems

### Known gaps

- Generalization across GPU architectures (NVIDIA, AMD, Ascend)
- Handling complex multi-kernel programs and memory management
- Bridging the gap between functional correctness and performance optimization

### Methodological gaps

- Lack of standardized evaluation metrics beyond speedup
- Limited understanding of failure modes in LLM-generated kernels
- Need for better feedback mechanisms (profiling, hardware counters) in the generation loop
