from __future__ import annotations

from llm4unroll.benchmarks.synthetic_lp_qp import build_synthetic_instances


def build_graph_relaxation_instances(family: str, split: str, count: int, seed: int):
    if family == "setcover_relaxation":
        return build_synthetic_instances(family, split, count, seed)
    raise ValueError("Phase 1 only includes setcover_relaxation in this loader.")
