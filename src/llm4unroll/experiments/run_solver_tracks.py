from __future__ import annotations

from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, parse_args
from llm4unroll.solvers.catalog import build_solver_interfaces


def _solver_track_label(solver_name: str, problem_family: str) -> str:
    if solver_name == "OSQP":
        return "qp_native_inner_loop"
    if solver_name == "HiGHS":
        return "root_lp_relaxation"
    if solver_name == "OR-Tools":
        if problem_family.startswith("llm_lns_") or problem_family == "lns_repair_cover":
            return "ortools_mip_relaxation_track"
        return "ortools_lp_specialist_track"
    if solver_name == "PySCIPOpt":
        return "callback_ready_primal_heuristic_track"
    if solver_name == "Ecole":
        return "ecole_benchmark_bridge_track"
    return "generic_solver_track"


def main():
    args = parse_args("Run solver specialist tracks for one benchmark configuration.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
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
            "origin": "solver_specialist",
            "specialist_track": _solver_track_label(solver.solver_name, str(config["problem_family"])),
            "available": diagnostics.get("available", False),
            "native_used": diagnostics.get("mode", "") == "native",
            "support_level": diagnostics.get("support_level", ""),
            "supports_native": diagnostics.get("supports_native", False),
            "supports_surrogate": diagnostics.get("supports_surrogate", False),
            "paper_scale_pending": diagnostics.get("paper_scale_pending", True),
            "backend_mode": diagnostics.get("backend_mode", ""),
            "backend_detail": diagnostics.get("backend_detail", ""),
            "score": round(result.score, 6),
            "median_gap": round(result.aggregate["median_gap"], 6),
            "median_violation": round(result.aggregate["median_violation"], 6),
            "median_runtime": round(result.aggregate["median_runtime"], 6),
            "median_iterations": int(result.aggregate["median_iterations"]),
            "fail_rate": round(result.aggregate["fail_rate"], 6),
        })

    out = "results/tables/solver_tracks_%s_%s_%s.csv" % (
        str(config["algorithm"]).lower(),
        str(config["problem_family"]),
        args.split,
    )
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "Solver Specialist Track Summary", rows)
    print("Saved solver track table to %s" % out)


if __name__ == "__main__":
    main()
