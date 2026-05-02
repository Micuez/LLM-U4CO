from __future__ import annotations

from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, parse_args
from llm4unroll.solvers.catalog import build_solver_interfaces


def main():
    args = parse_args("Probe native solver backends for one benchmark configuration.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    budget = type(budget)(
        max_iters=budget.max_iters,
        time_limit_s=budget.native_probe_time_limit_s,
        profile=budget.profile,
        same_budget_candidates=budget.same_budget_candidates,
        controller_train_multiplier=budget.controller_train_multiplier,
        native_probe_time_limit_s=budget.native_probe_time_limit_s,
    )
    evaluator = OptimisationEvaluator(runner, instances)
    rows = []

    for solver in build_solver_interfaces():
        if not solver.supports(str(config["problem_family"])):
            continue
        result = evaluator.evaluate_solver(solver, budget, solver_id=solver.solver_name)
        first_metrics = result.metrics_by_instance[next(iter(result.metrics_by_instance))]
        diagnostics = dict(first_metrics.diagnostics)
        rows.append({
            "algorithm": config["algorithm"],
            "problem_family": config["problem_family"],
            "split": args.split,
            "solver_name": solver.solver_name,
            "score": round(result.score, 6),
            "median_gap": round(result.aggregate["median_gap"], 6),
            "median_runtime": round(result.aggregate["median_runtime"], 6),
            "fail_rate": round(result.aggregate["fail_rate"], 6),
            "native_used": diagnostics.get("mode", "") == "native",
            "support_level": diagnostics.get("support_level", ""),
            "supports_native": diagnostics.get("supports_native", False),
            "supports_surrogate": diagnostics.get("supports_surrogate", False),
            "paper_scale_pending": diagnostics.get("paper_scale_pending", True),
            "backend_mode": diagnostics.get("backend_mode", ""),
            "backend_detail": diagnostics.get("backend_detail", ""),
        })

    out = "results/tables/native_probe_%s_%s_%s.csv" % (
        str(config["algorithm"]).lower(),
        str(config["problem_family"]),
        args.split,
    )
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "Native Backend Probe", rows)
    print("Saved native probe table to %s" % out)


if __name__ == "__main__":
    main()
