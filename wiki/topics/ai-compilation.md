---
title: "AI-Driven Compilation"
tags: [ai, compilers, llm, optimization, code-generation]
key_venues: []
related_topics: [llm-kernel-synthesis, gpu-kernel-optimization]
key_people: []
linked_ideas: []
---

## Overview

The integration of AI techniques — particularly large language models — with compiler infrastructure. This includes using LLMs for compiler pass optimization, code transformation, hardware-specific lowering, and the emerging paradigm of "the new compiler stack" where LLMs augment or replace traditional compiler components.

## Timeline

- 2017-2020: ML-based compiler optimization (MLGO, learned index structures)
- 2021-2023: LLMs for code understanding and transformation
- 2024-2026: LLM-compiler co-design, agent-based compilation

## Seminal works

- [[new-compiler-stack-survey-synergy-llms]] — comprehensive survey

## SOTA tracker

| System | Approach | Year |
|--------|----------|------|
| TVM | Auto-tuning | 2018+ |
| MLGO | ML-guided optimization | 2021 |
| LLM+Compiler | Co-design | 2025+ |

## Key benchmarks

- Standard compiler benchmark suites (Polybench, Rodinia)

## Open problems

### Known gaps

- Formal verification of LLM-transformed code
- Handling compiler IRs that are unfamiliar to LLMs
- Scaling to full application compilation (not just kernels)

### Methodological gaps

- Principled integration of LLM suggestions with existing optimization passes
- Training data curation for compiler-specific tasks
- Evaluation of correctness guarantees in AI-assisted compilation
