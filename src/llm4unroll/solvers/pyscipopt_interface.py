from __future__ import annotations

import time

from llm4unroll.benchmarks.llm_lns_data import ParsedLP, parse_lp_file
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import norm2
from llm4unroll.solvers.common import CommandBackedSolverInterface, make_solver_metrics


class PyScipOptInterface(CommandBackedSolverInterface):
    solver_name = "PySCIPOpt"
    python_package = "pyscipopt"
    command_name = "scip"
    default_extension = ".lp"
    runtime_bias = 0.0015

    def supports(self, problem_family: str) -> bool:
        return problem_family in {"lns_repair_cover", "llm_lns_sc", "llm_lns_is", "llm_lns_mvc", "llm_lns_miks"}

    def export_instance(self, instance, workdir: str):
        metadata = instance.payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if source_path:
            return str(source_path)
        return None

    def build_command(self, instance, exported_path, workdir: str, timeout_s: float):
        status = self.backend_status()
        if not exported_path:
            return [status.command, "-v"]
        return [
            status.command,
            "-c",
            "set limits time %s" % max(0.1, timeout_s),
            "-c",
            "read %s" % exported_path,
            "-c",
            "optimize",
            "-c",
            "display statistics",
            "-c",
            "quit",
        ]

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        metadata = instance.payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if status.available and status.mode == "python_package":
            try:
                if source_path:
                    return self._solve_file_backed(str(source_path), float(budget.time_limit_s), status)
                if "cover_matrix" in instance.payload:
                    return self._solve_cover_payload(instance.payload, float(budget.time_limit_s), status)
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

    def _solve_file_backed(self, source_path: str, time_limit_s: float, status) -> EvalMetrics:
        from pyscipopt import Model

        parsed = parse_lp_file(source_path)
        started = time.time()
        model = Model()
        model.hideOutput()
        model.readProblem(source_path)
        model.setRealParam("limits/time", max(0.1, time_limit_s))
        model.optimize()
        return _metrics_from_scip_model(
            model=model,
            parsed=parsed,
            runtime=time.time() - started + self.runtime_bias,
            diagnostics={
                "solver_name": self.solver_name,
                "available": True,
                "mode": "native",
                "backend_mode": status.mode,
                "backend_detail": status.detail,
                "package": status.package,
                "source_path": source_path,
            },
        )

    def _solve_cover_payload(self, payload, time_limit_s: float, status) -> EvalMetrics:
        from pyscipopt import Model, quicksum

        started = time.time()
        model = Model()
        model.hideOutput()
        model.setRealParam("limits/time", max(0.1, time_limit_s))
        variables = [model.addVar(name="x_%d" % j, vtype="B") for j in range(len(payload["costs"]))]
        for row in payload["cover_matrix"]:
            model.addCons(quicksum(float(row[j]) * variables[j] for j in range(len(variables)) if row[j]) >= 1.0)
        model.setObjective(quicksum(float(payload["costs"][j]) * variables[j] for j in range(len(variables))), "minimize")
        model.optimize()
        status_text = str(model.getStatus())
        solution = model.getBestSol()
        x = [0.0] * len(variables)
        if solution is not None:
            for j, var in enumerate(variables):
                x[j] = float(model.getSolVal(solution, var))
        violation = 0.0
        for row in payload["cover_matrix"]:
            violation += max(0.0, 1.0 - sum(float(row[j]) * x[j] for j in range(len(x))))
        objective = sum(float(payload["costs"][j]) * x[j] for j in range(len(x)))
        best_bound = float(model.getDualbound()) if hasattr(model, "getDualbound") else None
        failed = status_text.lower() not in {"optimal", "timelimit", "gaplimit", "bestsollimit"}
        return EvalMetrics(
            objective=objective,
            best_bound=best_bound,
            gap=0.0 if best_bound is None else abs(objective - best_bound) / max(abs(best_bound), 1e-9),
            primal_residual=violation,
            dual_residual=norm2([x[j] - float(payload["fractional_target"][j]) for j in range(len(x))]),
            violation=violation,
            integrality_gap=0.0,
            runtime=time.time() - started + self.runtime_bias,
            iterations=int(model.getNNodes()),
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
                "scip_status": status_text,
            },
        )


def _metrics_from_scip_model(model, parsed: ParsedLP, runtime: float, diagnostics) -> EvalMetrics:
    status_text = str(model.getStatus())
    solution = model.getBestSol()
    x = {}
    if solution is not None:
        for var in model.getVars():
            x[str(var.name)] = float(model.getSolVal(solution, var))
    violations = []
    for _, coeffs, sense_token, rhs in parsed.constraints:
        activity = sum(float(coeff) * float(x.get(name, 0.0)) for name, coeff in coeffs.items())
        if sense_token == "<=":
            violations.append(max(0.0, activity - float(rhs)))
        elif sense_token == ">=":
            violations.append(max(0.0, float(rhs) - activity))
        else:
            violations.append(abs(activity - float(rhs)))
    objective = float(model.getObjVal()) if solution is not None else float("inf")
    best_bound = float(model.getDualbound()) if hasattr(model, "getDualbound") else None
    diagnostics["scip_status"] = status_text
    return EvalMetrics(
        objective=objective,
        best_bound=best_bound,
        gap=0.0 if best_bound is None or solution is None else abs(objective - best_bound) / max(abs(best_bound), 1e-9),
        primal_residual=sum(violations),
        dual_residual=0.0,
        violation=sum(violations),
        integrality_gap=0.0 if parsed.binaries or parsed.generals else None,
        runtime=runtime,
        iterations=int(model.getNNodes()),
        memory_mb=None,
        failed=status_text.lower() not in {"optimal", "timelimit", "gaplimit", "bestsollimit"},
        failure_reason="" if status_text.lower() in {"optimal", "timelimit", "gaplimit", "bestsollimit"} else status_text,
        diagnostics=diagnostics,
    )
