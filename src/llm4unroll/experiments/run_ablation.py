from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, parse_args
from llm4unroll.policies import build_candidate_policy
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.search.non_llm_baselines import NonLLMBaselineFactory


def _ablation_specs(algorithm_name: str):
    factory = NonLLMBaselineFactory(701)
    adaptive_parent = build_candidate_policy(algorithm_name, "adaptive", policy_id="adaptive_parent", origin="baseline")
    grid_parent = build_candidate_policy(algorithm_name, "grid_candidate_1", policy_id="grid_parent", origin="grid_search")
    evo_candidate = factory.random_mutation(
        algorithm_name=algorithm_name,
        parent=adaptive_parent,
        policy_id="evolution_no_llm_ablation",
        origin="evolution_without_llm",
    )
    bo_candidate = factory.random_mutation(
        algorithm_name=algorithm_name,
        parent=grid_parent,
        policy_id="bayes_proxy_ablation",
        origin="bayesian_optimisation",
    )
    bo_candidate_2 = factory.random_walk(
        algorithm_name=algorithm_name,
        parents=[grid_parent, adaptive_parent],
        policy_id="bayes_proxy_ablation_deep",
        origin="bayesian_optimisation",
        min_depth=2,
        max_depth=3,
    )
    temp_candidate = factory.random_mutation(
        algorithm_name=algorithm_name,
        parent=adaptive_parent,
        policy_id="temperature_0p3_variant",
        origin="temperature_variant",
    )
    temp_candidate_2 = factory.random_walk(
        algorithm_name=algorithm_name,
        parents=[adaptive_parent, grid_parent],
        policy_id="temperature_0p7_variant",
        origin="temperature_variant",
        min_depth=1,
        max_depth=2,
    )
    return [
        {"ablation": "baseline", "candidate": build_candidate_policy(algorithm_name, "vanilla", origin="baseline"), "verify": True},
        {"ablation": "baseline", "candidate": build_candidate_policy(algorithm_name, "adaptive", origin="baseline"), "verify": True},
        {"ablation": "baseline", "candidate": build_candidate_policy(algorithm_name, "conservative", origin="baseline"), "verify": True},
        {
            "ablation": "safe_fallback_only",
            "candidate": build_candidate_policy(algorithm_name, "safe_fallback_only", origin="safe_fallback_only"),
            "verify": True,
        },
        {
            "ablation": "llm_only_one_shot",
            "candidate": build_candidate_policy(algorithm_name, "llm_one_shot", origin="llm_one_shot"),
            "verify": True,
        },
        {
            "ablation": "without_reflection",
            "candidate": build_candidate_policy(algorithm_name, "prompt_variant", origin="without_reflection"),
            "verify": True,
        },
        {
            "ablation": "without_evolution",
            "candidate": build_candidate_policy(algorithm_name, "model_variant", origin="without_evolution"),
            "verify": True,
        },
        {"ablation": "prompt_variant", "candidate": build_candidate_policy(algorithm_name, "prompt_variant", origin="prompt_variant"), "verify": True},
        {"ablation": "llm_model_variant", "candidate": build_candidate_policy(algorithm_name, "model_variant", origin="llm_model_variant"), "verify": True},
        {
            "ablation": "random_search_same_budget",
            "candidate": build_candidate_policy(algorithm_name, "grid_candidate_1", origin="grid_search"),
            "verify": True,
        },
        {
            "ablation": "bo_same_budget",
            "candidate": bo_candidate,
            "verify": True,
        },
        {
            "ablation": "bo_same_budget_deep",
            "candidate": bo_candidate_2,
            "verify": True,
        },
        {
            "ablation": "evolution_without_llm",
            "candidate": evo_candidate,
            "verify": True,
        },
        {
            "ablation": "learned_controller_high_budget",
            "candidate": build_candidate_policy(algorithm_name, "learned_controller_high_budget", origin="learned_controller"),
            "verify": True,
        },
        {
            "ablation": "learned_controller_paper_scale",
            "candidate": build_candidate_policy(algorithm_name, "learned_controller_paper_scale", origin="learned_controller"),
            "verify": True,
        },
        {
            "ablation": "temperature_0p3",
            "candidate": temp_candidate,
            "verify": True,
        },
        {
            "ablation": "temperature_0p7",
            "candidate": temp_candidate_2,
            "verify": True,
        },
        {
            "ablation": "without_verifier",
            "candidate": build_candidate_policy(algorithm_name, "unsafe_no_verifier", origin="without_verifier"),
            "verify": False,
        },
    ]


def main():
    args = parse_args("Run llm4unroll ablations.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    algorithm_name = str(config["algorithm"])
    spec = ALGORITHM_REGISTRY[algorithm_name]
    rows = []

    for item in _ablation_specs(algorithm_name):
        candidate = item["candidate"]
        verify = bool(item["verify"])
        verification = verify_policy_source(candidate.source, spec) if verify else None
        can_evaluate = verification.ok if verification is not None else True
        result = evaluator.evaluate(candidate.callable_policy, budget, candidate.policy_id, candidate.source) if can_evaluate else None
        rows.append({
            "algorithm": algorithm_name,
            "family": config["problem_family"],
            "split": args.split,
            "variant": item["ablation"],
            "ablation": item["ablation"],
            "policy_id": candidate.policy_id,
            "policy_variant": candidate.metadata.get("variant", ""),
            "origin": candidate.origin,
            "verification_mode": "strict" if verify else "bypassed",
            "verified": None if verification is None else verification.ok,
            "errors": "" if verification is None else " | ".join(verification.errors),
            "warnings": "" if verification is None else " | ".join(verification.warnings),
            "feature_coverage": None if verification is None else round(verification.feature_coverage, 4),
            "proof_count": 0 if verification is None else len(verification.proof_obligations),
            "score": round(result.score, 6) if result else None,
            "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
            "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
            "median_runtime": round(result.aggregate["median_runtime"], 6) if result else None,
            "median_primal_residual": round(result.aggregate["median_primal_residual"], 6) if result else None,
            "median_dual_residual": round(result.aggregate["median_dual_residual"], 6) if result else None,
        })

    out = "results/tables/ablation_%s_%s_%s.csv" % (algorithm_name.lower(), str(config["problem_family"]), args.split)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "Ablation Summary", rows)
    print("Saved ablation table to %s" % out)


if __name__ == "__main__":
    main()
