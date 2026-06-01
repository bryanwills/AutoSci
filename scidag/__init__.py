"""SciDAG — DAG-based multi-agent augmentation for AutoSci.

SciDAG represents a hard skill's execution as a directed acyclic graph of
reusable research operators. Given a stage task `z`, it runs an operator graph
G = (V, E) and returns a single artifact (a research idea / scheme as text),
so the calling SciFlow skill keeps its artifact contract unchanged.

This package is self-contained Python (no MetaGPT dependency). The operator
and DAG-execution logic is adapted from the user's MaAS repository; the LLM
call layer is rewired to AutoSci's OpenAI-compatible endpoint
(LLM_API_KEY / LLM_BASE_URL / LLM_MODEL, the same env the llm-review MCP uses).

Three sub-repositories mirror the paper's three SciDAG method modules:
  - operators/   §1  the operator library (reusable agents)
  - templates/   §2  stage-specific DAG architectures (ideation / experiment / writing)
  - traces/      §1+§3  evaluated DAG samples + quality scores (added later)

Current scope: the 7 operators ported from MaAS
(generate[+cot/multi], variation, refine, debate, test, ensemble, early-stop),
the DAG data structure, and the topological executor. The learned controller
and the review / polish operators come in later steps.
"""

from .dag import DAGNode, SampledDAG
from .llm import LLMClient, MockLLMClient
from .executor import DAGExecutor

__all__ = [
    "DAGNode",
    "SampledDAG",
    "LLMClient",
    "MockLLMClient",
    "DAGExecutor",
]

__version__ = "0.1.0"
