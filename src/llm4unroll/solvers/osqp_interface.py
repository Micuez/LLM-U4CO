from __future__ import annotations

import time
from typing import List, Sequence

from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import dot, matvec, norm2, sub
from llm4unroll.solvers.common import CommandBackedSolverInterface, make_solver_metrics


class OSQPInterface(CommandBackedSolverInterface):
    solver_name = "OSQP"
    python_package = "osqp"
    command_name = "osqp"
    runtime_bias = 0.0010

    def supports(self, problem_family: str) -> bool:
        return problem_family in {"admm_qp", "alm_eq_qp", "pcg_linear_system"}

    def build_command(self, instance, exported_path, workdir: str, timeout_s: float):
        status = self.backend_status()
        if status.command:
            return [status.command, "--help"]
        return None

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        if status.available and status.mode == "python_package":
            try:
                return self._solve_with_osqp(instance, float(budget.time_limit_s), int(budget.max_iters), status)
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
        probe = None
        if status.available and status.mode == "command":
            probe = self.run_command_probe(self.build_command(instance, None, "", float(budget.time_limit_s)), timeout_s=min(1.0, budget.time_limit_s))
        return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias, command_probe=probe)

    def _solve_with_osqp(self, instance, time_limit_s: float, max_iters: int, status) -> EvalMetrics:
        import numpy as np
        import osqp
        from scipy import sparse

        payload = instance.payload
        started = time.time()
        solver = osqp.OSQP()
        setup = self._build_problem(payload, np, sparse)
        solver.setup(
            P=setup["P"],
            q=setup["q"],
            A=setup["A"],
            l=setup["l"],
            u=setup["u"],
            verbose=False,
            max_iter=max(25, max_iters * 20),
            time_limit=max(0.05, time_limit_s),
            eps_abs=1e-5,
            eps_rel=1e-5,
            polish=True,
        )
        result = solver.solve()
        x = [float(value) for value in getattr(result, "x", [])]
        info = getattr(result, "info", None)
        status_text = str(getattr(info, "status", "unknown"))
        runtime = float(getattr(info, "run_time", time.time() - started)) + self.runtime_bias
        iterations = int(getattr(info, "iter", 0))
        prim_res = _to_float(getattr(info, "prim_res", None), default=0.0)
        dual_res = _to_float(getattr(info, "dual_res", None), default=0.0)
        diagnostics = {
            "solver_name": self.solver_name,
            "available": True,
            "mode": "native",
            "backend_mode": status.mode,
            "backend_detail": status.detail,
            "package": status.package,
            "osqp_status": status_text,
            "iterations": iterations,
        }
        if not x:
            return EvalMetrics(
                objective=float("inf"),
                best_bound=None,
                gap=float("inf"),
                primal_residual=float("inf"),
                dual_residual=float("inf"),
                violation=float("inf"),
                integrality_gap=None,
                runtime=runtime,
                iterations=iterations,
                memory_mb=None,
                failed=True,
                failure_reason=status_text,
                diagnostics=diagnostics,
            )
        objective, violation = self._objective_and_violation(payload, x)
        failed = "solved" not in status_text.lower()
        return EvalMetrics(
            objective=objective,
            best_bound=None,
            gap=0.0,
            primal_residual=max(violation, prim_res),
            dual_residual=dual_res,
            violation=violation,
            integrality_gap=None,
            runtime=runtime,
            iterations=iterations,
            memory_mb=None,
            failed=failed,
            failure_reason="" if not failed else status_text,
            diagnostics=diagnostics,
        )

    def _build_problem(self, payload, np, sparse):
        if "diag_q" in payload and "q" in payload:
            n = len(payload["diag_q"])
            lower = _expand_bounds(payload.get("lower", -1.0), n)
            upper = _expand_bounds(payload.get("upper", 1.0), n)
            return {
                "P": sparse.diags([float(value) for value in payload["diag_q"]], format="csc"),
                "q": np.array([float(value) for value in payload["q"]], dtype=float),
                "A": sparse.identity(n, format="csc"),
                "l": np.array(lower, dtype=float),
                "u": np.array(upper, dtype=float),
            }
        if "A" in payload and "b" in payload and "c" in payload and "reg" in payload:
            n = len(payload["c"])
            matrix = sparse.csc_matrix(payload["A"], dtype=float)
            p = sparse.diags([float(payload["reg"])] * n, format="csc")
            return {
                "P": p,
                "q": np.array([float(value) for value in payload["c"]], dtype=float),
                "A": matrix,
                "l": np.array([float(value) for value in payload["b"]], dtype=float),
                "u": np.array([float(value) for value in payload["b"]], dtype=float),
            }
        if "H" in payload and "rhs" in payload:
            n = len(payload["rhs"])
            return {
                "P": sparse.csc_matrix(payload["H"], dtype=float),
                "q": np.array([-float(value) for value in payload["rhs"]], dtype=float),
                "A": sparse.csc_matrix((0, n), dtype=float),
                "l": np.array([], dtype=float),
                "u": np.array([], dtype=float),
            }
        raise ValueError("Unsupported payload for OSQP real solve path")

    def _objective_and_violation(self, payload, x: Sequence[float]):
        if "diag_q" in payload and "q" in payload:
            objective = 0.5 * sum(float(payload["diag_q"][i]) * x[i] * x[i] for i in range(len(x))) + sum(float(payload["q"][i]) * x[i] for i in range(len(x)))
            lower = _expand_bounds(payload.get("lower", -1.0), len(x))
            upper = _expand_bounds(payload.get("upper", 1.0), len(x))
            violation = 0.0
            for i, value in enumerate(x):
                violation += max(0.0, lower[i] - value) + max(0.0, value - upper[i])
            return objective, violation
        if "A" in payload and "b" in payload and "c" in payload and "reg" in payload:
            residual = sub(matvec(payload["A"], list(x)), payload["b"])
            objective = 0.5 * float(payload["reg"]) * dot(list(x), list(x)) + dot(payload["c"], list(x))
            return objective, norm2(residual)
        if "H" in payload and "rhs" in payload:
            hx = matvec(payload["H"], list(x))
            residual = sub(hx, payload["rhs"])
            objective = 0.5 * dot(list(x), hx) - dot(payload["rhs"], list(x))
            return objective, norm2(residual)
        return float("inf"), float("inf")


def _expand_bounds(bound, size: int) -> List[float]:
    if isinstance(bound, (list, tuple)):
        return [float(value) for value in bound]
    return [float(bound)] * size


def _to_float(value, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default
