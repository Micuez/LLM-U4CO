from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, load_config, make_budget, make_instances, make_runner, parse_args
from llm4unroll.policies import build_baseline_policies
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY


def default_transfer_scenarios(problem_family: str, eval_cfg):
    default_count = int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 3)))
    defaults = {
        "pdhg_lp": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "pdhg_lp",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "synthetic_to_setcover_relaxation",
                "target_problem_family": "setcover_relaxation",
                "target_split": "test",
                "count": default_count,
                "source_scale": "synthetic_lp",
                "target_scale": "setcover_relaxation",
            },
            {
                "name": "synthetic_to_miplib",
                "target_problem_family": "miplib_rootlp",
                "target_split": "test",
                "count": 2,
                "target_dataset": {"list_path": "data/miplib/miplib_small.txt", "benchmark_group": "miplib_small"},
                "source_scale": "synthetic",
                "target_scale": "miplib",
            },
        ],
        "admm_qp": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "admm_qp",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "box_qp_to_relaxation",
                "target_problem_family": "admm_qp_relaxation",
                "target_split": "test",
                "count": default_count,
                "source_scale": "box_qp",
                "target_scale": "relaxation_shift",
            },
        ],
        "fista_lasso": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "fista_lasso",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "lasso_to_sparse_coding",
                "target_problem_family": "fista_sparse_coding",
                "target_split": "test",
                "count": default_count,
                "source_scale": "lasso",
                "target_scale": "sparse_coding",
            },
        ],
        "alm_eq_qp": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "alm_eq_qp",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "equality_qp_to_cover_relaxation",
                "target_problem_family": "alm_cover_relaxation",
                "target_split": "test",
                "count": default_count,
                "source_scale": "equality_qp",
                "target_scale": "cover_relaxation",
            },
        ],
        "drs_feasibility": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "drs_feasibility",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "affine_box_to_shifted_box",
                "target_problem_family": "drs_affine_box_shifted",
                "target_split": "test",
                "count": default_count,
                "source_scale": "affine_box",
                "target_scale": "shifted_box",
            },
        ],
        "pcg_linear_system": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "pcg_linear_system",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "linear_system_to_graph_laplacian",
                "target_problem_family": "pcg_graph_laplacian",
                "target_split": "test",
                "count": default_count,
                "source_scale": "dense_spd",
                "target_scale": "graph_laplacian",
            },
        ],
        "lns_repair_cover": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "lns_repair_cover",
                "target_split": "test",
                "count": default_count,
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "cover_repair_to_dense_cover",
                "target_problem_family": "lns_repair_cover_dense",
                "target_split": "test",
                "count": default_count,
                "source_scale": "sparse_cover",
                "target_scale": "dense_cover",
            },
        ],
        "miplib_rootlp": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "miplib_rootlp",
                "target_split": "test",
                "count": int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 2))),
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "miplib_to_llm_lns_sc",
                "target_problem_family": "llm_lns_sc",
                "target_split": "test",
                "count": 2,
                "source_scale": "miplib",
                "target_scale": "llm_lns_sc",
            },
        ],
        "llm_lns_sc": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "llm_lns_sc",
                "target_split": "test",
                "count": int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 2))),
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "setcover_to_independent_set",
                "target_problem_family": "llm_lns_is",
                "target_split": "test",
                "count": int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 2))),
                "source_scale": "set_cover",
                "target_scale": "independent_set",
            },
        ],
        "llm_lns_is": [
            {
                "name": "train_small_test_large",
                "target_problem_family": "llm_lns_is",
                "target_split": "test",
                "count": int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 2))),
                "source_scale": "small_train",
                "target_scale": "large_test",
            },
            {
                "name": "independent_set_to_setcover",
                "target_problem_family": "llm_lns_sc",
                "target_split": "test",
                "count": int(eval_cfg.get("test_instances", eval_cfg.get("train_instances", 2))),
                "source_scale": "independent_set",
                "target_scale": "set_cover",
            },
        ],
    }
    return [dict(item) for item in defaults.get(problem_family, [])]


def _evaluate_rows(evaluator, budget, candidates, spec, split: str, evaluation_mode: str, source_problem_family: str, target_problem_family: str, scenario: str):
    rows = []
    for candidate in candidates:
        verification = verify_policy_source(candidate.source, spec)
        result = evaluator.evaluate(candidate.callable_policy, budget, candidate.policy_id, candidate.source) if verification.ok else None
        rows.append({
            "split": split,
            "evaluation_mode": evaluation_mode,
            "scenario": scenario,
            "source_problem_family": source_problem_family,
            "target_problem_family": target_problem_family,
            "policy_id": candidate.policy_id,
            "verified": verification.ok,
            "errors": " | ".join(verification.errors),
            "feature_coverage": round(verification.feature_coverage, 4),
            "score": round(result.score, 6) if result else None,
            "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
            "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
        })
    return rows


def main():
    args = parse_args("Run llm4unroll OOD evaluation.")
    config = load_config(args.config)
    algorithm = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    budget = make_budget(config)
    runner = make_runner(algorithm)
    spec = ALGORITHM_REGISTRY[algorithm]
    seed = int(config.get("seed", 0))
    eval_cfg = config["evaluation"]
    dataset_cfg = config.get("dataset", {})
    ood_cfg = config.get("ood", {})
    candidates = build_baseline_policies(algorithm)

    rows = []
    for split in ("train", "validation", "test"):
        count = int(eval_cfg.get("%s_instances" % split, eval_cfg.get("train_instances", 3)))
        instances = make_instances(problem_family, split, count, seed, dataset_cfg=dataset_cfg)
        evaluator = OptimisationEvaluator(runner, instances)
        rows.extend(_evaluate_rows(
            evaluator=evaluator,
            budget=budget,
            candidates=candidates,
            spec=spec,
            split=split,
            evaluation_mode="standard_split",
            source_problem_family=problem_family,
            target_problem_family=problem_family,
            scenario=split,
        ))

    transfer_scenarios = list(ood_cfg.get("transfer_scenarios", []))
    if not transfer_scenarios:
        transfer_scenarios = default_transfer_scenarios(problem_family, eval_cfg)

    for scenario in transfer_scenarios:
        scenario_name = str(scenario.get("name", "transfer"))
        target_problem_family = str(scenario.get("target_problem_family", problem_family))
        target_split = str(scenario.get("target_split", "test"))
        target_count = int(scenario.get("count", eval_cfg.get("test_instances", eval_cfg.get("train_instances", 3))))
        target_dataset_cfg = dict(dataset_cfg)
        target_dataset_cfg.update(scenario.get("target_dataset", {}))
        instances = make_instances(target_problem_family, target_split, target_count, seed, dataset_cfg=target_dataset_cfg)
        evaluator = OptimisationEvaluator(runner, instances)
        mode = "train_small_test_large" if scenario_name == "train_small_test_large" else "cross_problem_transfer"
        transfer_rows = _evaluate_rows(
            evaluator=evaluator,
            budget=budget,
            candidates=candidates,
            spec=spec,
            split=target_split,
            evaluation_mode=mode,
            source_problem_family=problem_family,
            target_problem_family=target_problem_family,
            scenario=scenario_name,
        )
        for row in transfer_rows:
            row["source_scale"] = str(scenario.get("source_scale", "source"))
            row["target_scale"] = str(scenario.get("target_scale", "target"))
        rows.extend(transfer_rows)

    out = "results/tables/ood_%s_%s.csv" % (algorithm.lower(), problem_family)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "OOD Summary", rows)
    print("Saved OOD table to %s" % out)


if __name__ == "__main__":
    main()
