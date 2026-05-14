---
name: "AscendOptimizer"
slug: ascendoptimizer-method
type: optimization
tags: [ascend-npu, operator-optimization, llm-agent, evolutionary-search, optimization-rewind, retrieval-augmented-generation]
source_papers: [ascendoptimizer]
parent_methods: []
child_methods: []
code_repo: "https://github.com/KernelHive"
date_updated: 2026-05-14
---

## Problem setting

Optimize AscendC operators on Huawei Ascend NPUs under severe knowledge scarcity. The optimization target is a coupled pair (tiling function, kernel code) where performance depends on both data movement orchestration and instruction scheduling.

## Mechanism

Two alternating stages that exploit different search-space structures:

1. **Stage I (Tiling):** Evolutionary search with LLM mutation over tiling functions. Hardware execution is the fitness function with zero-tolerance for compilation/correctness failures.

2. **Stage II (Kernel):** Optimization-Rewind constructs an experience bank by de-optimizing expert kernels. Online optimization uses bottleneck diagnosis + retrieval-augmented rewriting.

The stages alternate: Stage I optimizes tiling with kernel fixed, Stage II optimizes kernel with tiling fixed. Each improvement reshapes the feasible region for the other.

## Procedure

1. Synthesize evolvable tiling template from operator specification
2. Run evolutionary tiling search (Stage I) for U steps with hardware feedback
3. Run optimization-rewind experience bank construction (offline)
4. For each inner loop iteration (Stage II):
   a. Diagnose bottleneck in current kernel
   b. Retrieve top-k optimization tuples from experience bank
   c. Refiner LLM rewrites kernel using retrieved patterns
   d. Compile and evaluate on real hardware
5. After S Stage II steps, return to Stage I with updated kernel
6. Repeat for R outer rounds

## Assumptions

- A small set of expert-level seed kernels is available
- Hardware compilation and profiling infrastructure is accessible
- LLMs have sufficient code understanding to perform meaningful mutations and de-optimizations
- The tiling landscape, while discontinuous, has exploitable structure

## Limitations

- Hardware-in-the-loop overhead (each evaluation requires compilation + execution)
- Not adapted for dynamic shapes
- Experience bank patterns may be hardware-generation specific
- Seed kernels from same benchmark set (transductive setting)

## Tradeoff profile

| Dimension | Rating |
|-----------|--------|
| Performance gain | High (1.19x GM, up to 20x on individual ops) |
| Automation level | High (no hand-crafted rules) |
| Compute cost | High (hardware-in-the-loop) |
| Generalizability | Medium (Ascend-specific, transductive) |
| Training required | None (training-free) |
