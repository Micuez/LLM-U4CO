from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.policies import build_strong_contrast_policies
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY


def _pipeline_shape(policy_id: str) -> tuple[str, int, bool, bool]:
    if policy_id == "llm_lns_heuristic_external":
        return "external_heuristic_replay", 2, True, False
    if policy_id == "llm_lns_plus_llm4unroll_external":
        return "external_combined_replay", 3, True, True
    return "internal_reference", 1, False, False


def main():
    args = parse_args("Run repo-local fullstack replay for external-style baselines.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    algorithm = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    spec = ALGORITHM_REGISTRY[algorithm]
    policies = [
        candidate
        for candidate in build_strong_contrast_policies(algorithm, problem_family)
        if candidate.policy_id in {"adaptive", "llm_lns_heuristic_external", "llm_lns_plus_llm4unroll_external"}
    ]

    smoke_instance = make_instances(
        problem_family,
        "train",
        1,
        int(config.get("seed", 0)) + 191,
        dataset_cfg=config.get("dataset", {}),
    )[0]
    smoke_budget = type(budget)(max_iters=max(3, min(8, budget.max_iters // 4 or 3)), time_limit_s=min(0.5, budget.time_limit_s))

    rows = []
    for candidate in policies:
        verification = verify_policy_source(candidate.source, spec)
        result = evaluator.evaluate(
            policy=candidate.callable_policy,
            budget=budget,
            policy_id=candidate.policy_id,
            policy_source=candidate.source,
        ) if verification.ok else None
        pipeline_type, stage_count, uses_external_heuristic, uses_llm4unroll_refine = _pipeline_shape(candidate.policy_id)
        rows.append({
            "algorithm": algorithm,
            "problem_family": problem_family,
            "policy_id": candidate.policy_id,
            "origin": "external_fullstack_replay",
            "comparison_role": {
                "adaptive": "llm4unroll_reference",
                "llm_lns_heuristic_external": "external_llm_lns_system_replay",
                "llm_lns_plus_llm4unroll_external": "external_combined_system_replay",
            }.get(candidate.policy_id, candidate.policy_id),
            "reproduction_mode": "repo_local_fullstack_replay",
            "pipeline_type": pipeline_type,
            "pipeline_stage_count": stage_count,
            "uses_external_heuristic": uses_external_heuristic,
            "uses_llm4unroll_refine": uses_llm4unroll_refine,
            "budget_profile": budget.profile,
            "budget_max_iters": budget.max_iters,
            "budget_time_limit_s": budget.time_limit_s,
            "same_budget_candidates": budget.same_budget_candidates,
            "smoke_reference": smoke_instance.name,
            "smoke_budget_iters": smoke_budget.max_iters,
            "verified": verification.ok,
            "feature_coverage": round(verification.feature_coverage, 4),
            "proof_count": len(verification.proof_obligations),
            "score": round(result.score, 6) if result else None,
            "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
            "median_violation": round(result.aggregate["median_violation"], 6) if result else None,
            "median_runtime": round(result.aggregate["median_runtime"], 6) if result else None,
            "median_iterations": int(result.aggregate["median_iterations"]) if result else None,
            "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
        })

    out = "results/tables/external_replay_%s_%s_%s.csv" % (algorithm.lower(), problem_family, args.split)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "External Fullstack Replay Summary", rows)
    print("Saved external replay table to %s" % out)


if __name__ == "__main__":
    main()
