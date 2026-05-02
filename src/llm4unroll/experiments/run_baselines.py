from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.smoke_test import run_policy_smoke_test
from llm4unroll.evaluator.report import (
    write_table_chart,
    write_candidate_archive,
    write_failure_analysis,
    write_markdown_summary,
    write_minimal_pdf,
    write_phase1_table,
)
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.policies import build_baseline_policies
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.solvers.catalog import build_solver_interfaces
from llm4unroll.utils import dump_text, ensure_dir


def _solver_backend_columns(diagnostics):
    mode = str(diagnostics.get("mode", ""))
    native_used = mode == "native"
    native_backend = ""
    if native_used:
        package = str(diagnostics.get("package", "")).strip()
        command = str(diagnostics.get("command", "")).strip()
        backend_mode = str(diagnostics.get("backend_mode", "")).strip()
        if package:
            native_backend = package
        elif command:
            native_backend = command.rsplit("/", 1)[-1]
        else:
            native_backend = backend_mode
    return {
        "native_used": native_used,
        "native_backend": native_backend,
        "support_level": diagnostics.get("support_level", ""),
        "supports_native": diagnostics.get("supports_native", False),
        "supports_surrogate": diagnostics.get("supports_surrogate", False),
        "paper_scale_pending": diagnostics.get("paper_scale_pending", True),
    }


def main():
    args = parse_args("Run llm4unroll baselines.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    policies = build_baseline_policies(str(config["algorithm"]))
    spec = ALGORITHM_REGISTRY[str(config["algorithm"])]
    smoke_instance = make_instances(
        str(config["problem_family"]),
        "train",
        1,
        int(config.get("seed", 0)) + 97,
        dataset_cfg=config.get("dataset", {}),
    )[0]
    smoke_budget = type(budget)(max_iters=max(3, min(8, budget.max_iters // 4 or 3)), time_limit_s=min(0.5, budget.time_limit_s))

    rows = []
    summary_lines = ["algorithm=%s problem=%s split=%s" % (config["algorithm"], config["problem_family"], args.split)]
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
        row = {
            "algorithm": config["algorithm"],
            "problem_family": config["problem_family"],
            "policy_id": candidate.policy_id,
            "origin": candidate.origin,
            "budget_profile": budget.profile,
            "budget_max_iters": budget.max_iters,
            "budget_time_limit_s": budget.time_limit_s,
            "native_used": "",
            "native_backend": "",
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
        archive_path = "results/candidates/%s_%s_%s.txt" % (config["algorithm"].lower(), config["problem_family"], candidate.policy_id)
        write_candidate_archive(archive_path, {
            "policy_id": candidate.policy_id,
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

    for solver in build_solver_interfaces():
        if not solver.supports(str(config["problem_family"])):
            continue
        result = evaluator.evaluate_solver(solver, budget, solver_id=solver.solver_name)
        diagnostics = result.metrics_by_instance[next(iter(result.metrics_by_instance))].diagnostics
        row = {
            "algorithm": config["algorithm"],
            "problem_family": config["problem_family"],
            "policy_id": solver.solver_name,
            "origin": "solver_baseline",
            "budget_profile": budget.profile,
            "budget_max_iters": budget.max_iters,
            "budget_time_limit_s": budget.time_limit_s,
            "backend_mode": diagnostics.get("backend_mode", ""),
            "backend_detail": diagnostics.get("backend_detail", ""),
            "score": round(result.score, 6),
            "median_gap": round(result.aggregate["median_gap"], 6),
            "median_violation": round(result.aggregate["median_violation"], 6),
            "median_runtime": round(result.aggregate["median_runtime"], 6),
            "median_primal_residual": round(result.aggregate["median_primal_residual"], 6),
            "median_dual_residual": round(result.aggregate["median_dual_residual"], 6),
            "median_iterations": int(result.aggregate["median_iterations"]),
            "fail_rate": round(result.aggregate["fail_rate"], 6),
        }
        row.update(_solver_backend_columns(diagnostics))
        rows.append(row)
        summary_lines.append(str(row))
        archive_path = "results/candidates/%s_%s_%s.txt" % (
            str(config["algorithm"]).lower(),
            str(config["problem_family"]),
            solver.solver_name.lower().replace(" ", "_"),
        )
        write_candidate_archive(archive_path, {
            "policy_id": solver.solver_name,
            "origin": "solver_baseline",
            "split": args.split,
            "score": result.score,
            "aggregate": result.aggregate,
            "available": solver.available(),
            "backend_status": diagnostics,
            "native_used": row["native_used"],
            "native_backend": row["native_backend"],
            "source": solver.solver_name,
        })

    ensure_dir("results/tables")
    output_name = "%s_%s_%s.csv" % (str(config["algorithm"]).lower(), str(config["problem_family"]), args.split)
    table_path = "results/tables/%s" % output_name
    write_phase1_table(table_path, rows)
    write_table_chart(table_path)
    dump_text("results/logs/%s.log" % output_name[:-4], "\n".join(summary_lines) + "\n")
    write_minimal_pdf("results/figures/convergence_curves.pdf", "Phase 1 Summary", summary_lines[:12])
    write_markdown_summary("results/tables/%s.md" % output_name[:-4], "Baseline Summary", rows)
    write_failure_analysis("results/logs/%s_failures.md" % output_name[:-4], rows)
    print("Saved baseline table to %s" % table_path)


if __name__ == "__main__":
    main()
