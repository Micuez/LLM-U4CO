from __future__ import annotations

import os
import random
from typing import List

from llm4unroll.benchmarks.llm_lns_data import parse_lp_file, parsed_lp_to_surrogate
from llm4unroll.benchmarks.synthetic_lp_qp import ProblemInstance


def load_miplib_paths(list_path: str) -> List[str]:
    with open(list_path, "r", encoding="utf-8") as handle:
        base_dir = os.path.dirname(os.path.abspath(list_path))
        paths = []
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            candidate = line if os.path.isabs(line) else os.path.join(base_dir, line)
            paths.append(os.path.normpath(candidate))
        return paths


def load_miplib_rootlp_instances(
    split: str,
    count: int,
    seed: int,
    list_path: str = "data/miplib/miplib_small.txt",
    benchmark_group: str = "miplib_small",
) -> List[ProblemInstance]:
    all_paths = load_miplib_paths(list_path)
    if not all_paths:
        raise FileNotFoundError("No MIPLIB paths configured in %s" % list_path)
    missing = [path for path in all_paths if not os.path.exists(path)]
    if missing:
        raise FileNotFoundError("Missing MIPLIB files: %s" % ", ".join(missing[:3]))
    selected = _split_paths(all_paths, split, count, seed)
    instances = []
    for path in selected:
        suffix = os.path.splitext(path)[1].lower()
        if suffix != ".lp":
            raise ValueError("Only .lp root-relaxation files are supported in the minimal loader: %s" % path)
        parsed = parse_lp_file(path)
        instance = parsed_lp_to_surrogate(parsed, "miplib_rootlp")
        instance.name = "miplib_%s" % parsed.name
        instance.family = "miplib_rootlp"
        instance.payload.setdefault("metadata", {})
        instance.payload["metadata"].update({
            "source_path": path,
            "source_format": suffix[1:],
            "benchmark_group": benchmark_group,
            "split": split,
        })
        instances.append(instance)
    return instances


def _split_paths(paths: List[str], split: str, count: int, seed: int) -> List[str]:
    shuffled = list(paths)
    random.Random(seed).shuffle(shuffled)
    if len(shuffled) <= count:
        return shuffled
    third = max(1, len(shuffled) // 3)
    if split == "train":
        pool = shuffled[:third]
    elif split == "validation":
        pool = shuffled[third: 2 * third]
    else:
        pool = shuffled[2 * third:]
    if not pool:
        pool = shuffled
    return pool[:count]
