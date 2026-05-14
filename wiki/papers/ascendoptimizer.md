---
title: "AscendOptimizer: Episodic Agent for Ascend NPU Operator Optimization"
slug: ascendoptimizer
arxiv: ""
venue: "ICML 2026 (submitted)"
year: 2026
tags: [ascend-npu, operator-optimization, llm-agent, evolutionary-search, optimization-rewind, kernel-optimization, tiling]
importance: 4
date_added: 2026-05-14
source_type: tex
contribution_type: [system, method]
datasets: [cann-ops-benchmark-127]
code_url: "https://github.com/KernelHive"
cited_by: []
tldr: "An episodic agent that bootstraps missing AscendC operator optimization expertise via two alternating stages: evolutionary-guided tiling search with hardware-in-the-loop feedback, and optimization-rewind based kernel rewriting with retrieval-augmented refinement."
---

## Problem & Context

AscendC operator optimization on Huawei Ascend NPUs faces a severe knowledge bottleneck: unlike the CUDA ecosystem with abundant open-source code, there are few public reference implementations to learn from. Performance depends on a coupled two-part artifact -- a host-side tiling program (data partitioning and movement) and a device-side kernel program (instruction scheduling and pipelining). LLMs achieve ~50% Pass@1 on CUDA operators but less than 2.1% on AscendC, a two-orders-of-magnitude gap rooted in knowledge scarcity rather than syntax differences.

## Key idea

When external training data are insufficient, bootstrap experience internally by exploiting the structured nature of code. Tiling parameters can be optimized via evolutionary search with hardware execution as ground-truth fitness feedback. Kernel optimizations can be bootstrapped by deliberately "rewinding" (de-optimizing) expert kernels to create synthetic bad-to-good trajectories, then distilling these into a retrievable experience bank.

## Method

**Stage I -- Evolutionary-Guided Program Search (Tiling):** The LLM synthesizes an evolvable tiling template with mutation markers, then performs evolutionary search over tiling functions. Hardware-in-the-loop evaluation acts as a zero-tolerance fitness function -- any configuration that fails compilation or has precision errors is immediately discarded. This forces convergence to valid, high-performance regions of the discontinuous tiling landscape.

**Stage II -- Optimization-Rewind based Experience Bootstrapping (Kernel):** Starting from expert-level seed kernels, an LLM systematically removes optimization motifs (unrolling, pipelining, vectorization) step by step, creating degradation trajectories. Each degraded variant is executed on real NPU hardware. Significant performance drops between adjacent pairs are captured as structured Optimization Tuples (Title, Description, Bottleneck, Code Diff) and stored in an Experience Bank. During online optimization, bottleneck diagnosis retrieves relevant tuples, and a Refiner LLM applies them as structured rewrites.

**Alternating Loop:** The two stages alternate -- Stage I optimizes tiling with kernel fixed, Stage II optimizes kernel with tiling fixed. Improvements in one stage reshape the feasible region for the other, analogous to block coordinate descent.

## Experiment & Results

Evaluated on 127 real AscendC operators from the official cann-ops repository on Ascend 910B4 NPUs with CANN 8.3. AscendOptimizer achieves 1.19x geometric-mean speedup over the open-source baseline, with 49.61% of operators outperforming references. On level-3 (complex) operators, it achieves 1.81x GM speedup with 71.43% surpassing baseline. Uses heterogeneous model deployment: GPT-5.2 for offline structural tasks, DeepSeek-V3.2 for online optimization loops. The experience bank contains 412 optimization tuples.

## Limitations

- Not yet adapted for dynamic shapes
- Cross-stack variability not fully addressed
- Hardware-in-the-loop overhead remains significant
- Noise tolerance and correctness assurance need strengthening
- Seed kernels come from the same benchmark set (transductive, not zero-shot)

## Open questions

- Can the experience bank transfer across different Ascend hardware generations?
- How to reduce the profiling overhead for the evolutionary search?
- Can optimization rewind generalize to other DSA architectures?
- Dynamic shape handling for real-world deployment scenarios

## My take

The core insight -- using code structure to self-supervise when external data is scarce -- is elegant and broadly applicable. The "optimization rewind" technique of deliberately de-optimizing to create training pairs is a clever workaround for the data scarcity problem on niche hardware. The alternating tiling/kernel optimization is well-motivated by the AscendC two-part architecture.

## Related

- [[gpu-kernel]]
- [[kernel-benchmark]]
- [[ascend-npu]]
- [[optimization-rewind]]
- [[evolutionary-guided-program-search]]
- [[ascendoptimizer-method]]
