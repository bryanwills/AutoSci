---
title: "TritonBench: Benchmarking Large Language Model Capabilities for Generating Triton Operators"
slug: tritonbench
arxiv: "2502.14752"
venue: "ACL 2024"
year: 2024
tags: [benchmark, triton, llm, code-generation, gpu, operator-generation]
importance: 4
date_added: 2026-05-14
source_type: tex
tldr: "First benchmark for evaluating LLMs on generating Triton GPU operators, covering both Git-sourced and PyTorch-based tasks"
contribution_type: [benchmark, evaluation]
datasets: [tritonbench]
code_url: ""
---

## Problem & Context

Evaluating LLM-generated GPU kernels requires standardized benchmarks. While KernelBench focused on CUDA, Triton has emerged as a more LLM-friendly kernel language. TritonBench fills the gap by providing a comprehensive evaluation framework for Triton operator generation.

## Key Idea

Create a dual-track benchmark: (1) Git-sourced tasks from real Triton repositories, and (2) PyTorch-to-Triton translation tasks. This captures both realistic code generation and cross-language translation capabilities.

## Method

- **Task construction**: Collected Triton operators from GitHub and converted PyTorch operators to Triton reference implementations
- **Difficulty levels**: Progressive difficulty from simple element-wise operations to complex reductions and convolutions
- **Evaluation**: Correctness testing + performance comparison against reference implementations
- **Filtering pipeline**: Automated filtering to ensure task quality and testability

## Experiment & Results

- Evaluated multiple LLMs including GPT-4, Claude, and open-source models
- Found significant performance gaps between models on different difficulty levels
- Git-sourced tasks proved more challenging than PyTorch translation tasks
- Current SOTA models achieve limited success on complex Triton operators

## Limitations

- Benchmark focuses on single-operator generation, not multi-operator programs
- Performance evaluation is hardware-specific
- Limited coverage of advanced Triton features (e.g., complex memory patterns)

## Open Questions

- How well do LLMs generalize across Triton operator types?
- Can fine-tuning on Triton-specific data improve generation quality?
- What is the role of hardware-aware prompting in Triton generation?

## My Take

TritonBench is essential for the LLM kernel generation community because Triton is more accessible to LLMs than raw CUDA. The dual-track design (Git + PyTorch) is well-motivated. The benchmark reveals that even strong LLMs struggle with complex Triton patterns, highlighting the need for specialized training or agent-based approaches.

## Related

- [[kernel-benchmark]]
- [[triton-language]]
- [[gpu-kernel]]
- [[kernelbench-llms-write-efficient-gpu-kernels]]
