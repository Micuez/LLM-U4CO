from __future__ import annotations

import time

from llm4unroll.benchmarks.llm_lns_data import parse_lp_file
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.solvers.common import CommandBackedSolverInterface, make_solver_metrics


class HighsInterface(CommandBackedSolverInterface):
    solver_name = "HiGHS"
    python_package = "highspy"
    command_name = "highs"
    default_extension = ".lp"
    runtime_bias = 0.0012

    def supports(self, problem_family: str) -> bool:
        return problem_family in {"pdhg_lp", "setcover_relaxation", "miplib_rootlp", "llm_lns_sc", "llm_lns_is", "llm_lns_mvc", "llm_lns_miks", "admm_qp", "alm_eq_qp"}

    def export_instance(self, instance, workdir: str):
        metadata = instance.payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if source_path:
            return str(source_path)
        return None

    def build_command(self, instance, exported_path, workdir: str, timeout_s: float):
        status = self.backend_status()
        if not exported_path:
            return [status.command, "--version"]
        solution_path = "%s.sol" % exported_path
        return [
            status.command,
            exported_path,
            "--time_limit",
            str(max(0.1, timeout_s)),
            "--presolve",
            "on",
            "--solver",
            "simplex",
            "--write_solution_to_file",
            solution_path,
        ]

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        metadata = instance.payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if status.available and status.mode == "python_package" and source_path:
            try:
                return self._solve_with_highspy(str(source_path), float(budget.time_limit_s), status)
            except Exception as exc:
                probe = {
                    "ok": False,
                    "returncode": None,
                    "stdout": "",
                    "stderr": "%s: %s" % (type(exc).__name__, str(exc)),
                    "runtime_s": 0.0,
                    "timeout_s": float(budget.time_limit_s),
                }
                return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias, command_probe=probe)
        if status.available and status.mode == "command":
            probe = self.run_command_probe(self.build_command(instance, source_path, "", float(budget.time_limit_s)), timeout_s=float(budget.time_limit_s))
            return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias, command_probe=probe)
        return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias)

    def _solve_with_highspy(self, source_path: str, time_limit_s: float, status) -> EvalMetrics:
        from highspy import Highs

        parsed = parse_lp_file(source_path)
        started = time.time()
        solver = Highs()
        solver.setOptionValue("output_flag", False)
        solver.setOptionValue("time_limit", max(0.1, time_limit_s))
        read_status = solver.readModel(source_path)
        run_status = solver.run()
        model_status = str(solver.getModelStatus())
        solution = solver.getSolution()
        variable_names = _highs_variable_names(solver, parsed)
        x = {}
        col_values = list(getattr(solution, "col_value", []) or [])
        for index, name in enumerate(variable_names):
            if index < len(col_values):
                x[name] = float(col_values[index])
        objective = float(solver.getObjectiveValue())
        violations = []
        for _, coeffs, sense_token, rhs in parsed.constraints:
            activity = sum(float(coeff) * float(x.get(name, 0.0)) for name, coeff in coeffs.items())
            if sense_token == "<=":
                violations.append(max(0.0, activity - float(rhs)))
            elif sense_token == ">=":
                violations.append(max(0.0, float(rhs) - activity))
            else:
                violations.append(abs(activity - float(rhs)))
        info = solver.getInfo()
        simplex_iters = int(getattr(info, "simplex_iteration_count", 0) or 0)
        mip_nodes = int(getattr(info, "mip_node_count", 0) or 0)
        dual_bound = getattr(info, "objective_function_value", None)
        if dual_bound is not None:
            dual_bound = float(dual_bound)
        status_text = "%s / %s / %s" % (read_status, run_status, model_status)
        failed = not any(token in model_status.lower() for token in ("optimal", "feasible"))
        violation = sum(violations)
        return EvalMetrics(
            objective=objective,
            best_bound=dual_bound,
            gap=0.0 if dual_bound is None else abs(objective - dual_bound) / max(abs(dual_bound), 1e-9),
            primal_residual=violation,
            dual_residual=0.0,
            violation=violation,
            integrality_gap=0.0 if parsed.binaries or parsed.generals else None,
            runtime=time.time() - started + self.runtime_bias,
            iterations=max(simplex_iters, mip_nodes),
            memory_mb=None,
            failed=failed,
            failure_reason="" if not failed else status_text,
            diagnostics={
                "solver_name": self.solver_name,
                "available": True,
                "mode": "native",
                "backend_mode": status.mode,
                "backend_detail": status.detail,
                "package": status.package,
                "highs_model_status": model_status,
                "read_status": str(read_status),
                "run_status": str(run_status),
                "source_path": source_path,
            },
        )


def _highs_variable_names(solver, parsed):
    names = []
    lp = getattr(solver, "getLp", None)
    if callable(lp):
        try:
            model = lp()
            col_names = getattr(model, "col_names_", None)
            if col_names:
                names = [str(name) for name in col_names]
        except Exception:
            names = []
    if names:
        return names
    return sorted(parsed.bounds)
