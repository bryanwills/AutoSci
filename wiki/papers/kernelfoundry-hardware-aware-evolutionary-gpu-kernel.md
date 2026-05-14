---
title: "KernelFoundry: Hardware-Aware Evolutionary GPU Kernel Optimization"
slug: kernelfoundry-hardware-aware-evolutionary-gpu-kernel
arxiv: ""
venue: ""
year: 2026
tags: [kernel-generation, evolutionary-algorithms, code-generation, gpu-programming, llm, sycl, map-elites, quality-diversity]
importance: 4
date_added: 2026-05-14
source_type: tex
s2_id: ""
tldr: "An evolutionary framework using MAP-Elites quality-diversity search, meta-prompt co-evolution, and templated parameter optimization to generate high-performance GPU kernels in SYCL and CUDA."
contribution_type: [method, system, benchmark]
datasets: [kernelbench, robust-kbench]
code_url: ""
cited_by: []
---

## Problem & Context

Optimizing GPU kernels presents a significantly greater challenge for large language models than standard code generation tasks. It requires understanding hardware architecture, parallel optimization strategies, and performance profiling outputs. Most existing LLM-based approaches to kernel generation rely on simple prompting and feedback loops, incorporating hardware awareness only indirectly through profiling feedback. These approaches suffer from two key problems: (1) mode collapse, where iterative searches prematurely converge because LLMs repeatedly propose variants close to recent successes, and (2) context degradation, where failed attempts dominate the prompt context as optimization histories grow.

## Key idea

KernelFoundry addresses these limitations through three key mechanisms:
1. **MAP-Elites quality-diversity search** with kernel-specific behavioral dimensions (memory access patterns, algorithmic structure, parallelism coordination) to sustain exploration across diverse optimization strategies
2. **Meta-prompt evolution** that co-evolves prompts with kernels to uncover task-specific optimization strategies and mitigate context degradation
3. **Template-based parameter optimization** to tune hardware-dependent values like tile and block sizes separately from algorithmic transformations

## Method

### System Architecture
The framework comprises five tightly-coupled components:
- **Task specification layer**: Accepts kernel generation problems in flexible format (PyTorch references, natural language, existing kernels)
- **Prompt construction engine**: Assembles context-aware prompts combining task specification with hardware-specific guidance, parent programs, gradient-derived mutation hints, and evolved prompt components
- **LLM inference backend**: Unified interface to API-based and local models
- **Compilation & evaluation pipeline**: Compiles to target backend (SYCL via Intel DPC++, CUDA via nvcc, Triton), validates correctness, measures execution time
- **Evolutionary archive**: Implements MAP-Elites organizing kernels by behavioral coordinates

### MAP-Elites with Kernel-Specific Behavioral Descriptors
Three-dimensional optimization feature space with discrete levels:
- **Memory Access Pattern** (d_mem in {0,1,2,3}): Scalar/strided -> Coalesced/vectorized -> Shared/local memory with tiling -> Multi-level hierarchy
- **Algorithmic Structure** (d_algo in {0,1,2,3}): Direct translation -> Fused operations -> Reformulated algorithm -> Novel/asymptotically improved
- **Parallelism Coordination** (d_sync in {0,1,2,3}): No synchronization -> Work-group barriers -> Sub-group primitives -> Global coordination

This yields 4^3 = 64 behavioral cells. Coordinates are computed deterministically via static pattern matching on SYCL and CUDA constructs.

### Gradient-Informed Evolution
Augments MAP-Elites with gradient-like signals from evolutionary transition history:
- **Fitness gradient**: Estimates which directions in behavioral space improve fitness
- **Improvement-rate gradient**: Estimates which directions yield higher improvement probability
- **Exploration gradient**: Points to empty or low-quality cells

Gradients inform parent selection (cells with strong positive gradient magnitudes receive higher sampling probability) and prompt construction (gradient directions translated into natural-language mutation hints).

### Meta-Prompt Evolution
Prompts are mutable and co-evolve with kernels. Four evolvable prompt sections:
1. Optimization philosophy (high-level principles)
2. Optimization strategies (concrete techniques by category)
3. Common pitfalls (anti-patterns to avoid)
4. Analysis guidance (pre-coding reasoning scaffold)

A dedicated meta-prompter LLM analyzes generation outcomes and proposes prompt modifications as SEARCH/REPLACE diffs restricted to evolvable regions.

### Templated Kernels
LLMs optionally produce templated kernels with configurable parameters alongside a dispatch function enumerating valid parameter combinations. The evaluation pipeline detects templated kernels, extracts parameter configurations, and evaluates each instantiation independently.

## Experiment & Results

Evaluated on KernelBench, robust-kbench, and custom tasks, generating both SYCL and CUDA kernels. Key results:
- Average speedup of 2.3x on KernelBench for SYCL
- Consistently outperforms baseline methods
- Implemented as a distributed framework with remote access to diverse hardware
- Flexible user input layer supporting kernel generation for real-world use cases beyond benchmarking

## Limitations

- Benchmarking challenges: spurious speedups can arise from incorrect kernels that pass test cases
- Generalization across GPU architectures remains challenging
- Performance gap between LLM-generated and expert-optimized kernels may be significant for some kernel types

## Open questions

- Can templated kernel generation achieve consistent speedups across input ranges and tensor shapes?
- How can formal verification be improved to eliminate reward hacking?
- What is the potential for deeper hardware specialization within the framework?

## My take

KernelFoundry represents a significant advance in LLM-based kernel optimization by explicitly addressing mode collapse and context degradation through quality-diversity search and meta-prompt co-evolution. The use of kernel-specific behavioral descriptors (memory access patterns, algorithmic structure, parallelism coordination) is particularly insightful, as it leverages the structured nature of kernel optimization space. The 2.3x average speedup on KernelBench for SYCL demonstrates practical value. The distributed architecture and SYCL focus make it relevant for cross-platform deployment.

## Related

- [[gpu-kernel]]
- [[kernel-benchmark]]
- [[triton-language]]
- [[llm-agent-gpu-kernel-optimization]]
- [[map-elites]]
- [[quality-diversity-search]]
- [[meta-prompt-evolution]]
- [[sycl]]
