from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, parse_args
from llm4unroll.policies import build_candidate_policy
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.search.non_llm_baselines import NonLLMBaselineFactory


def _evaluate_candidate(evaluator, budget, spec, config, candidate):
    verification = verify_policy_source(candidate.source, spec)
    result = evaluator.evaluate(
        policy=candidate.callable_policy,
        budget=budget,
        policy_id=candidate.policy_id,
        policy_source=candidate.source,
    ) if verification.ok else None
    score = None if result is None else float(result.score)
    feature_coverage = float(verification.feature_coverage)
    acquisition = None if score is None else round(score + 0.05 * feature_coverage, 6)
    return {
        "algorithm": config["algorithm"],
        "problem_family": config["problem_family"],
        "policy_id": candidate.policy_id,
        "origin": candidate.origin,
        "variant": candidate.metadata.get("variant", ""),
        "parent": candidate.metadata.get("parent", ""),
        "seed_parent": candidate.metadata.get("seed_parent", ""),
        "lineage_depth": candidate.metadata.get("lineage_depth", 0),
        "verified": verification.ok,
        "errors": " | ".join(verification.errors),
        "warnings": " | ".join(verification.warnings),
        "feature_coverage": round(feature_coverage, 4),
        "proof_count": len(verification.proof_obligations),
        "acquisition_score": acquisition,
        "score": None if score is None else round(score, 6),
        "median_gap": None if result is None else round(result.aggregate["median_gap"], 6),
        "median_violation": None if result is None else round(result.aggregate["median_violation"], 6),
        "median_runtime": None if result is None else round(result.aggregate["median_runtime"], 6),
        "median_iterations": None if result is None else int(result.aggregate["median_iterations"]),
        "fail_rate": None if result is None else round(result.aggregate["fail_rate"], 6),
    }


def main():
    args = parse_args("Run llm4unroll Bayesian-optimisation-style baseline.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    algorithm_name = str(config["algorithm"])
    spec = ALGORITHM_REGISTRY[algorithm_name]
    factory = NonLLMBaselineFactory(int(config.get("seed", 0)) + 404)

    seeds = [
        build_candidate_policy(algorithm_name, "grid_candidate_1", policy_id="bo_seed_grid_1", origin="grid_search"),
        build_candidate_policy(algorithm_name, "grid_candidate_2", policy_id="bo_seed_grid_2", origin="grid_search"),
        build_candidate_policy(algorithm_name, "adaptive", policy_id="bo_seed_adaptive", origin="baseline"),
    ]
    rows = []
    ranked = []
    for candidate in seeds:
        row = _evaluate_candidate(evaluator, budget, spec, config, candidate)
        row["iteration"] = 0
        row["selection_stage"] = "seed"
        rows.append(row)
        ranked.append(row)

    for iteration in range(1, max(3, budget.same_budget_candidates) + 1):
        ranked = sorted(
            [row for row in ranked if row.get("acquisition_score") is not None],
            key=lambda item: float(item["acquisition_score"]),
            reverse=True,
        )
        parent_ids = [row["policy_id"] for row in ranked[:2]] or ["bo_seed_adaptive"]
        parents = [build_candidate_policy(algorithm_name, "adaptive", policy_id=policy_id, origin="bayesian_parent") for policy_id in parent_ids]
        candidate = factory.random_walk(
            algorithm_name=algorithm_name,
            parents=parents,
            policy_id="bayes_iter_%02d" % iteration,
            origin="bayesian_optimisation",
            min_depth=1,
            max_depth=2,
        )
        row = _evaluate_candidate(evaluator, budget, spec, config, candidate)
        row["iteration"] = iteration
        row["selection_stage"] = "acquisition"
        rows.append(row)
        ranked.append(row)

    out = "results/tables/bayesian_optimisation_%s_%s_%s.csv" % (algorithm_name.lower(), str(config["problem_family"]), args.split)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "Bayesian Optimisation Baseline Summary", rows)
    print("Saved Bayesian baseline table to %s" % out)


if __name__ == "__main__":
    main()
