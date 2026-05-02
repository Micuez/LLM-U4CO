from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import (
    write_candidate_archive,
    write_failure_analysis,
    write_markdown_summary,
    write_phase1_table,
    write_table_chart,
)
from llm4unroll.evaluator.smoke_test import run_policy_smoke_test
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.policies import build_strong_contrast_policies
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.utils import dump_text, ensure_dir


def main():
    args = parse_args("Run llm4unroll strong-contrast baselines.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    algorithm = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    policies = build_strong_contrast_policies(algorithm, problem_family)
    spec = ALGORITHM_REGISTRY[algorithm]

    smoke_instance = make_instances(
        problem_family,
        "train",
        1,
        int(config.get("seed", 0)) + 131,
        dataset_cfg=config.get("dataset", {}),
    )[0]
    smoke_budget = type(budget)(max_iters=max(3, min(8, budget.max_iters // 4 or 3)), time_limit_s=min(0.5, budget.time_limit_s))

    rows = []
    summary_lines = ["algorithm=%s problem=%s split=%s" % (algorithm, problem_family, args.split)]
    for candidate in policies:
        verification = verify_policy_source(candidate.source, spec)
        smoke = run_policy_smoke_test(
            runner=evaluator.algorithm_runner,
            instance=smoke_instance,
            policy=candidate.callable_policy,
            budget=smoke_budget,
        ) if verification.ok else None
        result = evaluator.evaluate(
            policy=candidate.callable_policy,
            budget=budget,
            policy_id=candidate.policy_id,
            policy_source=candidate.source,
        ) if verification.ok and smoke is not None and smoke.ok else None

        comparison_role_map = {
            "adaptive": "llm4unroll_reference",
            "llm_lns_heuristic_external": "external_llm_lns_heuristic",
            "llm_lns_plus_llm4unroll_external": "external_combined_pipeline",
        }
        comparison_role = comparison_role_map.get(candidate.policy_id, candidate.policy_id)
        row = {
            "algorithm": algorithm,
            "problem_family": problem_family,
            "policy_id": candidate.policy_id,
            "comparison_role": comparison_role,
            "origin": candidate.origin,
            "budget_profile": budget.profile,
            "budget_max_iters": budget.max_iters,
            "budget_time_limit_s": budget.time_limit_s,
            "same_budget_candidates": budget.same_budget_candidates,
            "verified": verification.ok,
            "smoke_ok": None if smoke is None else smoke.ok,
            "smoke_reason": "" if smoke is None else smoke.reason,
            "errors": " | ".join(verification.errors),
            "warnings": " | ".join(verification.warnings),
            "feature_coverage": round(verification.feature_coverage, 4),
            "proof_count": len(verification.proof_obligations),
            "score": round(result.score, 6) if result else None,
            "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
            "median_violation": round(result.aggregate["median_violation"], 6) if result else None,
            "median_runtime": round(result.aggregate["median_runtime"], 6) if result else None,
            "median_primal_residual": round(result.aggregate["median_primal_residual"], 6) if result else None,
            "median_dual_residual": round(result.aggregate["median_dual_residual"], 6) if result else None,
            "median_iterations": int(result.aggregate["median_iterations"]) if result else None,
            "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
        }
        rows.append(row)
        summary_lines.append(str(row))
        archive_path = "results/candidates/strong_%s_%s_%s.txt" % (algorithm.lower(), problem_family, candidate.policy_id)
        write_candidate_archive(archive_path, {
            "policy_id": candidate.policy_id,
            "comparison_role": comparison_role,
            "origin": candidate.origin,
            "split": args.split,
            "score": None if result is None else result.score,
            "aggregate": None if result is None else result.aggregate,
            "source": candidate.source,
            "verified": verification.ok,
            "errors": verification.errors,
            "warnings": verification.warnings,
            "smoke_ok": None if smoke is None else smoke.ok,
            "smoke_reason": "" if smoke is None else smoke.reason,
            "smoke_diagnostics": {} if smoke is None else smoke.diagnostics,
            "feature_coverage": verification.feature_coverage,
            "proof_obligations": verification.proof_obligations,
        })

    ensure_dir("results/tables")
    output_name = "strong_baselines_%s_%s_%s.csv" % (algorithm.lower(), problem_family, args.split)
    table_path = "results/tables/%s" % output_name
    write_phase1_table(table_path, rows)
    write_table_chart(table_path)
    dump_text("results/logs/%s.log" % output_name[:-4], "\n".join(summary_lines) + "\n")
    write_markdown_summary("results/tables/%s.md" % output_name[:-4], "Strong Baseline Summary", rows)
    write_failure_analysis("results/logs/%s_failures.md" % output_name[:-4], rows)
    print("Saved strong baseline table to %s" % table_path)


if __name__ == "__main__":
    main()
