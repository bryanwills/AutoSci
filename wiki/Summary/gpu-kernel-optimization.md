---
title: "GPU Kernel Optimization with LLMs and Agents"
tags: [gpu, kernel-optimization, llm, agents, code-generation]
date_updated: 2026-05-14
---

## Overview

The intersection of large language models (LLMs), autonomous agents, and GPU kernel optimization represents a rapidly evolving research area. The core challenge is automating the generation of high-performance GPU kernels — programs that run on massively parallel hardware — using AI-driven approaches rather than manual expert tuning.

## Core areas

- **LLM-based kernel synthesis**: Using LLMs to generate CUDA, Triton, or other GPU kernel code from high-level specifications
- **Agent-based optimization**: Multi-agent frameworks that iteratively refine kernel code through testing, profiling, and feedback
- **Benchmarks and evaluation**: Standardized testbeds for measuring LLM-generated kernel quality (KernelBench, TritonBench, KernelBench-X)
- **Compiler-LLM synergy**: Integrating LLMs with compiler infrastructure for hardware-aware optimization
- **Evolutionary and search-based methods**: Combining LLMs with evolutionary search for kernel design space exploration

## Evolution

The field progressed from traditional auto-tuning (OpenCL, CUDA autotuners) through ML-based approaches (TVM, Halide) to the current wave of LLM-driven methods. Key milestones include the emergence of Triton as an LLM-friendly kernel language and the development of agent frameworks that can iteratively debug and optimize generated code.

## Current frontiers

- Hardware-aware kernel generation that adapts to specific GPU architectures
- Multi-agent systems combining code generation, testing, and profiling agents
- Agentic reinforcement learning for program optimization (e.g., StitchCUDA)
- Cold-start kernel synthesis with memory-augmented agents
- Comprehensive benchmarking across diverse kernel types and hardware targets

## Key references

- [[kernelfoundry-hardware-aware-evolutionary-gpu-kernel]] — evolutionary approach to kernel optimization
- [[kernelbench-llms-write-efficient-gpu-kernels]] — foundational benchmark for LLM kernel generation
- [[stitchcuda-automated-multi-agents-end-end]] — multi-agent GPU programming framework
- [[new-compiler-stack-survey-synergy-llms]] — survey on LLM-compiler synergy

## Related

- [[llm-kernel-synthesis]]
- [[gpu-kernel-optimization]]
- [[ai-compilation]]
