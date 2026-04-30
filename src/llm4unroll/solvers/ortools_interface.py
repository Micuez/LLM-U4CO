from __future__ import annotations

import time

from llm4unroll.benchmarks.llm_lns_data import parse_lp_file
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import dot, matvec, norm2, sub
from llm4unroll.solvers.common import CommandBackedSolverInterface, make_solver_metrics


class ORToolsInterface(CommandBackedSolverInterface):
    solver_name = "OR-Tools"
    python_package = "ortools"
    runtime_bias = 0.0013

    def supports(self, problem_family: str) -> bool:
        return problem_family in {"setcover_relaxation", "lns_repair_cover", "miplib_rootlp", "llm_lns_sc", "llm_lns_is", "pdhg_lp"}

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        if status.available and status.mode == "python_package":
            try:
                return self._solve_with_ortools(instance, float(budget.time_limit_s), status)
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
        return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias)

    def _solve_with_ortools(self, instance, time_limit_s: float, status) -> EvalMetrics:
        from ortools.linear_solver import pywraplp

        payload = instance.payload
        started = time.time()
        metadata = payload.get("metadata", {})
        source_path = metadata.get("source_path")

        if source_path:
            parsed = parse_lp_file(str(source_path))
            solver = pywraplp.Solver.CreateSolver("GLOP")
            if solver is None:
                raise RuntimeError("OR-Tools GLOP backend unavailable")
            solver.SetTimeLimit(int(max(1.0, time_limit_s) * 1000.0))
            variables = {}
            relaxed = set(parsed.binaries) | set(parsed.generals)
            for name, (lower, upper) in parsed.bounds.items():
                lower_bound = float(lower)
                upper_bound = float(upper)
                variables[name] = solver.NumVar(lower_bound, upper_bound, name)
            for _, coeffs, sense_token, rhs in parsed.constraints:
                constraint = _make_constraint(solver, sense_token, float(rhs))
                for name, coeff in coeffs.items():
                    constraint.SetCoefficient(variables[name], float(coeff))
            objective = solver.Objective()
            for name, coeff in parsed.objective.items():
                objective.SetCoefficient(variables[name], float(coeff))
            if parsed.sense == "max":
                objective.SetMaximization()
            else:
                objective.SetMinimization()
            status_code = solver.Solve()
            x = {name: variables[name].solution_value() for name in variables}
            return _metrics_from_parsed_lp(
                parsed=parsed,
                x=x,
                runtime=time.time() - started + self.runtime_bias,
                iterations=simplex_iterations(solver),
                status_code=status_code,
                status_lookup={
                    pywraplp.Solver.OPTIMAL: "OPTIMAL",
                    pywraplp.Solver.FEASIBLE: "FEASIBLE",
                    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
                    pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
                    pywraplp.Solver.ABNORMAL: "ABNORMAL",
                    pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
                },
                diagnostics={
                    "solver_name": self.solver_name,
                    "available": True,
                    "mode": "native",
                    "backend_mode": status.mode,
                    "backend_detail": status.detail,
                    "package": status.package,
                    "relaxed_integrality": bool(relaxed),
                    "source_path": str(source_path),
                },
            )

        if "cover_matrix" in payload:
            solver = pywraplp.Solver.CreateSolver("CBC")
            if solver is None:
                solver = pywraplp.Solver.CreateSolver("SCIP")
            if solver is None:
                raise RuntimeError("OR-Tools MIP backend unavailable")
            solver.SetTimeLimit(int(max(1.0, time_limit_s) * 1000.0))
            x_vars = [solver.BoolVar("x_%d" % j) for j in range(len(payload["costs"]))]
            for row in payload["cover_matrix"]:
                constraint = solver.RowConstraint(1.0, solver.infinity(), "")
                for j, coeff in enumerate(row):
                    if coeff:
                        constraint.SetCoefficient(x_vars[j], float(coeff))
            objective = solver.Objective()
            for j, cost in enumerate(payload["costs"]):
                objective.SetCoefficient(x_vars[j], float(cost))
            objective.SetMinimization()
            status_code = solver.Solve()
            x = [var.solution_value() for var in x_vars]
            cover_violation = 0.0
            for row in payload["cover_matrix"]:
                cover_violation += max(0.0, 1.0 - sum(float(row[j]) * x[j] for j in range(len(x))))
            objective_value = sum(float(payload["costs"][j]) * x[j] for j in range(len(x)))
            best_bound = sum(float(payload["costs"][j]) * float(payload["x_star"][j]) for j in range(len(x)))
            dual = norm2([x[j] - float(payload["fractional_target"][j]) for j in range(len(x))])
            status_text = {
                pywraplp.Solver.OPTIMAL: "OPTIMAL",
                pywraplp.Solver.FEASIBLE: "FEASIBLE",
                pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
                pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
                pywraplp.Solver.ABNORMAL: "ABNORMAL",
                pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
            }.get(status_code, str(status_code))
            failed = status_code not in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}
            return EvalMetrics(
                objective=objective_value,
                best_bound=best_bound,
                gap=abs(objective_value - best_bound) / max(abs(best_bound), 1e-9),
                primal_residual=cover_violation,
                dual_residual=dual,
                violation=cover_violation,
                integrality_gap=0.0,
                runtime=time.time() - started + self.runtime_bias,
                iterations=simplex_iterations(solver),
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
                    "ortools_status": status_text,
                },
            )

        if "A" in payload and "b" in payload and "c" in payload:
            solver = pywraplp.Solver.CreateSolver("GLOP")
            if solver is None:
                raise RuntimeError("OR-Tools GLOP backend unavailable")
            solver.SetTimeLimit(int(max(1.0, time_limit_s) * 1000.0))
            n = len(payload["c"])
            x_vars = [solver.NumVar(-solver.infinity(), solver.infinity(), "x_%d" % j) for j in range(n)]
            for i, row in enumerate(payload["A"]):
                rhs = float(payload["b"][i])
                constraint = solver.RowConstraint(rhs, rhs, "")
                for j, coeff in enumerate(row):
                    if coeff:
                        constraint.SetCoefficient(x_vars[j], float(coeff))
            objective = solver.Objective()
            for j, coeff in enumerate(payload["c"]):
                objective.SetCoefficient(x_vars[j], float(coeff))
            objective.SetMinimization()
            status_code = solver.Solve()
            x = [var.solution_value() for var in x_vars]
            residual = norm2(sub(matvec(payload["A"], x), payload["b"]))
            objective_value = 0.5 * float(payload.get("reg", 0.0)) * dot(x, x) + dot(payload["c"], x)
            status_text = {
                pywraplp.Solver.OPTIMAL: "OPTIMAL",
                pywraplp.Solver.FEASIBLE: "FEASIBLE",
                pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
                pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
                pywraplp.Solver.ABNORMAL: "ABNORMAL",
                pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
            }.get(status_code, str(status_code))
            failed = status_code not in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}
            return EvalMetrics(
                objective=objective_value,
                best_bound=None,
                gap=0.0,
                primal_residual=residual,
                dual_residual=0.0,
                violation=residual,
                integrality_gap=None,
                runtime=time.time() - started + self.runtime_bias,
                iterations=simplex_iterations(solver),
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
                    "ortools_status": status_text,
                },
            )

        raise ValueError("Unsupported payload for OR-Tools real solve path")


def _make_constraint(solver, sense_token: str, rhs: float):
    if sense_token == "<=":
        return solver.RowConstraint(-solver.infinity(), rhs, "")
    if sense_token == ">=":
        return solver.RowConstraint(rhs, solver.infinity(), "")
    return solver.RowConstraint(rhs, rhs, "")


def _metrics_from_parsed_lp(parsed, x, runtime: float, iterations: int, status_code: int, status_lookup, diagnostics) -> EvalMetrics:
    activity_violations = []
    objective = sum(float(coeff) * float(x[name]) for name, coeff in parsed.objective.items())
    best_bound = objective
    for _, coeffs, sense_token, rhs in parsed.constraints:
        activity = sum(float(coeff) * float(x[name]) for name, coeff in coeffs.items())
        if sense_token == "<=":
            activity_violations.append(max(0.0, activity - float(rhs)))
        elif sense_token == ">=":
            activity_violations.append(max(0.0, float(rhs) - activity))
        else:
            activity_violations.append(abs(activity - float(rhs)))
    status_text = status_lookup.get(status_code, str(status_code))
    diagnostics["ortools_status"] = status_text
    return EvalMetrics(
        objective=objective,
        best_bound=best_bound,
        gap=0.0,
        primal_residual=sum(activity_violations),
        dual_residual=0.0,
        violation=sum(activity_violations),
        integrality_gap=0.0 if parsed.binaries or parsed.generals else None,
        runtime=runtime,
        iterations=iterations,
        memory_mb=None,
        failed=status_text not in {"OPTIMAL", "FEASIBLE"},
        failure_reason="" if status_text in {"OPTIMAL", "FEASIBLE"} else status_text,
        diagnostics=diagnostics,
    )


def simplex_iterations(solver) -> int:
    try:
        return int(solver.Iterations())
    except Exception:
        return 0
