from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, load_config, make_budget, make_instances, make_runner, parse_args
from llm4unroll.policies import build_baseline_policies
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY


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

    rows = []
    for split in ("train", "validation", "test"):
        count = int(eval_cfg.get("%s_instances" % split, eval_cfg.get("train_instances", 3)))
        instances = make_instances(problem_family, split, count, seed, dataset_cfg=dataset_cfg)
        evaluator = OptimisationEvaluator(runner, instances)
        for candidate in build_baseline_policies(algorithm):
            verification = verify_policy_source(candidate.source, spec)
            result = evaluator.evaluate(candidate.callable_policy, budget, candidate.policy_id, candidate.source) if verification.ok else None
            rows.append({
                "split": split,
                "policy_id": candidate.policy_id,
                "verified": verification.ok,
                "errors": " | ".join(verification.errors),
                "feature_coverage": round(verification.feature_coverage, 4),
                "score": round(result.score, 6) if result else None,
                "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
                "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
            })

    out = "results/tables/ood_%s_%s.csv" % (algorithm.lower(), problem_family)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "OOD Summary", rows)
    print("Saved OOD table to %s" % out)


if __name__ == "__main__":
    main()
