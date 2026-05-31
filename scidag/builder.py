"""Build SampledDAGs from specs, and load stage DAG libraries.

A DAG template is a YAML doc with light metadata plus a `nodes:` list in layer
order:

    name: explore-debate-test
    stage: ideation
    complexity: 3            # 1 (simple) .. 5 (complex)
    paper_figure: true       # the architecture shown in the paper figure
    description: "..."
    nodes:
      - op: MultiGenerate
        parents: [root]      # "root" or 0-based indices of earlier nodes
      - op: Variation
        parents: [0]
      - op: Debate
        parents: [0]
      - op: Test
        parents: [1, 2]

`parents` entries are either the literal "root" or integer indices of earlier
nodes in the spec (0-based, in spec order). Each module keeps its own library
directory under `scidag/templates/<stage>/`, with one file per architecture
(filename prefixed `1-`..`5-` so listing is simple→complex).
"""
from __future__ import annotations

import os
from typing import List, Optional

from .dag import SampledDAG

# Stage libraries live here. A "stage" is one of: ideation, experiment, writing.
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STAGES = ("ideation", "experiment", "writing")


# ---------------------------------------------------------------- build

def build_dag(spec) -> SampledDAG:
    """Build a SampledDAG from a node list (or a doc dict carrying `nodes`)."""
    nodes_spec = spec["nodes"] if isinstance(spec, dict) else spec
    dag = SampledDAG()
    root = dag.add_root()
    spec_to_nid = {}  # spec index -> node id

    for i, node_spec in enumerate(nodes_spec):
        op = node_spec["op"]
        raw_parents = node_spec.get("parents", ["root"])
        parent_ids = []
        for p in raw_parents:
            if p == "root":
                parent_ids.append(root)
            else:
                parent_ids.append(spec_to_nid[int(p)])
        # layer = 1 + max parent layer (root is -1, so producers land at layer 0)
        layer = 1 + max(dag.nodes[pid].layer_idx for pid in parent_ids)
        nid = dag.add_node(op_name=op, layer_idx=layer, parent_ids=parent_ids)
        spec_to_nid[i] = nid

    dag.finalize_leaves()
    return dag


def is_nonlinear(dag: SampledDAG) -> bool:
    """True if the DAG genuinely branches (some fan-out or fan-in), i.e. it is
    not a pure chain. A node with >=2 children (fan-out) or >=2 parents (fan-in)
    — counting the root's children — makes it a real DAG rather than linear."""
    for nid in dag.nodes:
        if len(dag.get_children(nid)) >= 2:
            return True
        if len(dag.nodes[nid].parent_ids) >= 2:
            return True
    return False


# ---------------------------------------------------------------- load docs

def read_doc(path: str) -> dict:
    """Read a template YAML into a dict {name, stage, complexity, paper_figure,
    description, nodes}. Falls back to a tiny parser if PyYAML is missing."""
    try:
        import yaml  # type: ignore
        with open(path) as f:
            doc = yaml.safe_load(f)
        if "nodes" not in doc:
            raise ValueError(f"template {path} has no `nodes`")
        return doc
    except ImportError:
        return _parse_doc_no_yaml(path)


def load_template(path: str) -> SampledDAG:
    """Load a single template file into a SampledDAG."""
    return build_dag(read_doc(path))


def _parse_doc_no_yaml(path: str) -> dict:
    """Minimal parser for the template subset (scalars + a `nodes:` list)."""
    doc: dict = {"nodes": []}
    in_nodes = False
    cur: Optional[dict] = None
    with open(path) as f:
        for line in f:
            raw = line.rstrip("\n")
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            if s == "nodes:":
                in_nodes = True
                continue
            if not in_nodes:
                if ":" in s:
                    k, v = s.split(":", 1)
                    v = v.strip().strip('"').strip("'")
                    if v.lower() in ("true", "false"):
                        doc[k.strip()] = (v.lower() == "true")
                    elif v.isdigit():
                        doc[k.strip()] = int(v)
                    else:
                        doc[k.strip()] = v
                continue
            # inside nodes
            if s.startswith("- "):
                if cur is not None:
                    doc["nodes"].append(cur)
                cur = {}
                s = s[2:].strip()
            if cur is None:
                continue
            if s.startswith("op:"):
                cur["op"] = s.split(":", 1)[1].strip().strip('"').strip("'")
            elif s.startswith("parents:"):
                val = s.split(":", 1)[1].strip().strip("[]")
                parts = [p.strip().strip('"').strip("'") for p in val.split(",") if p.strip()]
                cur["parents"] = [p if p == "root" else int(p) for p in parts]
    if cur is not None:
        doc["nodes"].append(cur)
    return doc


# ---------------------------------------------------------------- library

def _stage_dir(stage: str, base_dir: Optional[str] = None) -> str:
    return os.path.join(base_dir or TEMPLATES_DIR, stage)


def list_library(stage: str, base_dir: Optional[str] = None) -> List[dict]:
    """List a module's DAG library, sorted simple→complex (by filename prefix).

    Returns one dict per architecture:
    {name, path, complexity, paper_figure, n_nodes, description}.
    """
    sdir = _stage_dir(stage, base_dir)
    if not os.path.isdir(sdir):
        raise FileNotFoundError(f"no DAG library for stage {stage!r} at {sdir}")
    out = []
    for fname in sorted(os.listdir(sdir)):
        if not fname.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(sdir, fname)
        doc = read_doc(path)
        out.append({
            "name": doc.get("name", os.path.splitext(fname)[0]),
            "path": path,
            "complexity": doc.get("complexity"),
            "paper_figure": bool(doc.get("paper_figure", False)),
            "n_nodes": len(doc.get("nodes", [])),
            "description": doc.get("description", ""),
        })
    return out


def load_from_library(stage: str, name: str, base_dir: Optional[str] = None) -> SampledDAG:
    """Load one architecture from a module's library by `name` (or filename stem)."""
    for entry in list_library(stage, base_dir):
        stem = os.path.splitext(os.path.basename(entry["path"]))[0]
        if name in (entry["name"], stem):
            return load_template(entry["path"])
    available = ", ".join(e["name"] for e in list_library(stage, base_dir))
    raise KeyError(f"no DAG named {name!r} in {stage} library. Available: {available}")
