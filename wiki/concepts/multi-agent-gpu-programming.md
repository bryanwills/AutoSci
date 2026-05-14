---
title: "Multi-Agent GPU Programming"
aliases: [multi-agent-cuda-generation, agentic-gpu-programming]
tags: [multi-agent, gpu, cuda, code-generation, llm, automation]
maturity: emerging
definition: "A paradigm where multiple specialized LLM agents collaborate to generate, optimize, and verify GPU programs, with each agent handling a distinct subtask in the development pipeline."
key_papers: [stitchcuda]
first_introduced: "2026"
date_updated: 2026-05-14
related_concepts: [gpu-kernel, kernel-benchmark]
linked_ideas: [llm-agent-gpu-kernel-optimization]
---

## Definition

Multi-agent GPU programming decomposes the GPU code development pipeline into specialized roles (e.g., planning, coding, verification/profiling) assigned to distinct LLM agents. These agents iteratively communicate through shared state to produce correct and optimized GPU programs.

## Intuition

Just as a human GPU programming team might have an architect designing the system, a developer writing kernels, and a performance engineer profiling and suggesting optimizations, multi-agent systems mirror this division of labor with LLM agents.

## Key design patterns

- **Planner-Coder-Verifier**: Decomposes tasks at the system level, implements code, and validates with profiling tools.
- **Coder-Feedback loop**: Iterative refinement where a feedback agent provides structured suggestions based on compilation errors and profiling data.
- **RAG-augmented agents**: Agents retrieve relevant hardware documentation and library guides during planning and verification.

## Comparison to single-agent approaches

| Aspect | Single-agent | Multi-agent |
|--------|-------------|-------------|
| Task scope | Single kernel | End-to-end program |
| Feedback integration | Limited | Structured per-role |
| Optimization depth | Local | System-level |
| Failure recovery | Self-refine | Role-specific repair |

## Known limitations

- Local optima and specification drift in iterative refinement
- Long code context and tool traces degrade agent consistency
- Cross-kernel optimization requires global coordination that simple agent loops may miss

## Open problems

- Scaling to very large multi-kernel programs (10+ kernels)
- Automated agent role assignment and specialization
- Efficient communication protocols between agents
- Integration with compiler-driven optimization passes

## Relationship to foundations

Multi-agent GPU programming builds on GPU kernels and LLM code generation, extending single-kernel synthesis to full program-level automation.

## My understanding

