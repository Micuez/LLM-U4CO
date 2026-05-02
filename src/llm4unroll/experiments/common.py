from __future__ import annotations

import argparse
from typing import Dict, Optional

from llm4unroll.algorithms import (
    ADMMRunner,
    ALMRunner,
    DouglasRachfordRunner,
    FISTARunner,
    LNSRepairRunner,
    PCGRunner,
    PDHGRunner,
)
from llm4unroll.algorithms.base import RunBudget
from llm4unroll.benchmarks.graph_relaxations import build_graph_relaxation_instances
from llm4unroll.benchmarks.llm_lns_data import load_llm_lns_instances
from llm4unroll.benchmarks.miplib import load_miplib_rootlp_instances
from llm4unroll.benchmarks.synthetic_lp_qp import build_synthetic_instances
from llm4unroll.dsl.guards import RuntimeSafetyGuard
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.utils import load_simple_yaml, seed_everything

HEURIGYM_BUDGET_PRESETS: Dict[str, Dict[str, object]] = {
    "default": {
        "max_iters": 60,
        "time_limit_s": 10.0,
        "same_budget_candidates": 8,
        "controller_train_multiplier": 1.0,
    },
    "heurigym_small": {
        "max_iters": 96,
        "time_limit_s": 12.0,
        "same_budget_candidates": 12,
        "controller_train_multiplier": 1.5,
    },
    "heurigym_medium": {
        "max_iters": 128,
        "time_limit_s": 18.0,
        "same_budget_candidates": 16,
        "controller_train_multiplier": 2.0,
    },
    "paper_native": {
        "max_iters": 160,
        "time_limit_s": 24.0,
        "same_budget_candidates": 20,
        "controller_train_multiplier": 2.5,
    },
}


def parse_args(default_description: str):
    parser = argparse.ArgumentParser(description=default_description)
    parser.add_argument("--config", required=True, help="Path to the YAML config.")
    parser.add_argument("--split", default="train", choices=["train", "validation", "test"], help="Benchmark split to run.")
    return parser.parse_args()


def load_config(path: str) -> Dict[str, object]:
    return load_simple_yaml(path)


def make_runner(algorithm_name: str):
    spec = ALGORITHM_REGISTRY[algorithm_name]
    guard = RuntimeSafetyGuard(spec.safety)
    mapping = {
        "PDHG": PDHGRunner,
        "ADMM": ADMMRunner,
        "FISTA": FISTARunner,
        "ALM": ALMRunner,
        "DRS": DouglasRachfordRunner,
        "PCG": PCGRunner,
        "LNS_REPAIR": LNSRepairRunner,
    }
    return mapping[algorithm_name](guard)


def make_instances(problem_family: str, split: str, count: int, seed: int, dataset_cfg: Optional[Dict[str, object]] = None):
    dataset_cfg = dataset_cfg or {}
    if problem_family in {
        "pdhg_lp",
        "admm_qp",
        "admm_qp_relaxation",
        "fista_lasso",
        "fista_sparse_coding",
        "alm_eq_qp",
        "alm_cover_relaxation",
        "drs_feasibility",
        "drs_affine_box_shifted",
        "pcg_linear_system",
        "pcg_graph_laplacian",
        "lns_repair_cover",
        "lns_repair_cover_dense",
    }:
        return build_synthetic_instances(problem_family, split, count, seed)
    if problem_family.startswith("llm_lns_"):
        return load_llm_lns_instances(
            problem_family,
            split,
            count,
            seed,
            root=str(dataset_cfg.get("llm_lns_root", dataset_cfg.get("root", "data/llm_lns"))),
        )
    if problem_family == "miplib_rootlp":
        return load_miplib_rootlp_instances(
            split,
            count,
            seed,
            list_path=str(dataset_cfg.get("list_path", "data/miplib/miplib_small.txt")),
            benchmark_group=str(dataset_cfg.get("benchmark_group", "miplib_small")),
        )
    return build_graph_relaxation_instances(problem_family, split, count, seed)


def make_budget(config: Dict[str, object]) -> RunBudget:
    budget = config["budget"]
    profile = str(budget.get("profile", "default"))
    preset = dict(HEURIGYM_BUDGET_PRESETS.get(profile, HEURIGYM_BUDGET_PRESETS["default"]))
    preset.update({key: value for key, value in budget.items() if key != "profile"})
    native_probe_time_limit_s = float(preset.get("native_probe_time_limit_s", preset.get("time_limit_s", 30.0)))
    return RunBudget(
        max_iters=int(preset["max_iters"]),
        time_limit_s=float(preset.get("time_limit_s", 30.0)),
        profile=profile,
        same_budget_candidates=int(preset.get("same_budget_candidates", 8)),
        controller_train_multiplier=float(preset.get("controller_train_multiplier", 1.0)),
        native_probe_time_limit_s=native_probe_time_limit_s,
    )


def bootstrap(config_path: str, split: str = "train"):
    config = load_config(config_path)
    seed_everything(int(config.get("seed", 0)))
    algorithm_name = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    runner = make_runner(algorithm_name)
    budget = make_budget(config)
    eval_cfg = config["evaluation"]
    dataset_cfg = config.get("dataset", {})
    count_key = {
        "train": "train_instances",
        "validation": "validation_instances",
        "test": "test_instances",
    }[split]
    fallback = int(eval_cfg.get("train_instances", 3))
    instances = make_instances(
        problem_family,
        split,
        int(eval_cfg.get(count_key, fallback)),
        int(config.get("seed", 0)),
        dataset_cfg=dataset_cfg,
    )
    return config, runner, budget, instances
