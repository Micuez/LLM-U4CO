from __future__ import annotations

import json
import sys
import time

from llm4unroll.benchmarks.llm_lns_data import parse_lp_file
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.solvers.common import CommandBackedSolverInterface, make_solver_metrics


class EcoleInterface(CommandBackedSolverInterface):
    solver_name = "Ecole"
    python_package = "ecole"
    runtime_bias = 0.0014

    def supports(self, problem_family: str) -> bool:
        return problem_family in {"lns_repair_cover", "llm_lns_sc", "llm_lns_is", "llm_lns_mvc", "llm_lns_miks"}

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        metadata = instance.payload.get("metadata", {})
        source_path = metadata.get("source_path")
        if status.available and status.mode == "python_package" and source_path:
            probe = self.run_command_probe(
                [sys.executable, "-c", _ECOLE_SOLVE_SCRIPT, str(source_path), str(float(budget.time_limit_s))],
                timeout_s=max(1.0, float(budget.time_limit_s) + 1.0),
            )
            if probe.get("ok"):
                try:
                    payload = json.loads(probe.get("stdout", "").strip() or "{}")
                    return _metrics_from_ecole_payload(
                        parsed=parse_lp_file(str(source_path)),
                        ecole_payload=payload,
                        status=status,
                        runtime_bias=self.runtime_bias,
                    )
                except Exception as exc:
                    probe["ok"] = False
                    probe["stderr"] = "%s: %s" % (type(exc).__name__, str(exc))
            return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias, command_probe=probe)
        return make_solver_metrics(instance, self.solver_name, status, runtime_bias=self.runtime_bias)


def _metrics_from_ecole_payload(parsed, ecole_payload, status, runtime_bias: float) -> EvalMetrics:
    x = {str(key): float(value) for key, value in ecole_payload.get("x", {}).items()}
    objective = float(ecole_payload.get("objective", float("inf")))
    best_bound = ecole_payload.get("best_bound")
    if best_bound is not None:
        best_bound = float(best_bound)
    violations = []
    if x:
        for _, coeffs, sense_token, rhs in parsed.constraints:
            activity = sum(float(coeff) * float(x.get(name, 0.0)) for name, coeff in coeffs.items())
            if sense_token == "<=":
                violations.append(max(0.0, activity - float(rhs)))
            elif sense_token == ">=":
                violations.append(max(0.0, float(rhs) - activity))
            else:
                violations.append(abs(activity - float(rhs)))
    violation = sum(violations)
    status_text = str(ecole_payload.get("status", "unknown"))
    failed = not bool(ecole_payload.get("ok", False)) or status_text.upper() not in {"OPTIMAL", "FEASIBLE", "TIMELIMIT"}
    return EvalMetrics(
        objective=objective,
        best_bound=best_bound,
        gap=0.0 if best_bound is None else abs(objective - best_bound) / max(abs(best_bound), 1e-9),
        primal_residual=violation,
        dual_residual=0.0,
        violation=violation,
        integrality_gap=0.0 if parsed.binaries or parsed.generals else None,
        runtime=float(ecole_payload.get("runtime_s", 0.0)) + runtime_bias,
        iterations=int(ecole_payload.get("nodes", 0)),
        memory_mb=None,
        failed=failed,
        failure_reason="" if not failed else status_text,
        diagnostics={
            "solver_name": "Ecole",
            "available": True,
            "mode": "native",
            "backend_mode": status.mode,
            "backend_detail": status.detail,
            "package": status.package,
            "ecole_status": status_text,
            "raw_payload": ecole_payload,
        },
    )


_ECOLE_SOLVE_SCRIPT = r"""
import json
import sys
import time

import ecole

path = sys.argv[1]
time_limit = float(sys.argv[2])
started = time.time()
payload = {"ok": False, "path": path}

def safe_call(obj, name, *args):
    attr = getattr(obj, name, None)
    if attr is None:
        return None
    try:
        return attr(*args) if callable(attr) else attr
    except Exception:
        return None

model = ecole.scip.Model.from_file(path)
safe_call(model, "set_params", {"limits/time": time_limit})
backend = None
for name in ("as_pyscipopt", "scip_model"):
    attr = getattr(model, name, None)
    if attr is None:
        continue
    try:
        backend = attr() if callable(attr) else attr
    except Exception:
        backend = None
    if backend is not None:
        break
if backend is None:
    backend = model

safe_call(backend, "hideOutput")
safe_call(backend, "setIntParam", "display/verblevel", 0)
safe_call(backend, "setRealParam", "limits/time", time_limit)
optimize = getattr(backend, "optimize", None) or getattr(backend, "solve", None)
if optimize is None:
    raise RuntimeError("No optimize/solve method exposed by Ecole backend")
optimize()

status = safe_call(backend, "getStatus")
payload["status"] = str(status)
payload["objective"] = safe_call(backend, "getObjVal")
payload["best_bound"] = safe_call(backend, "getDualbound")
payload["runtime_s"] = safe_call(backend, "getSolvingTime") or (time.time() - started)
payload["nodes"] = safe_call(backend, "getNNodes") or 0
payload["n_vars"] = safe_call(backend, "getNVars")
payload["n_conss"] = safe_call(backend, "getNConss")

solution = safe_call(backend, "getBestSol")
get_vars = getattr(backend, "getVars", None)
get_sol_val = getattr(backend, "getSolVal", None)
values = {}
if solution is not None and callable(get_vars) and callable(get_sol_val):
    for var in get_vars():
        name = getattr(var, "name", None)
        if name is None:
            get_name = getattr(var, "getName", None)
            name = get_name() if callable(get_name) else None
        if not name:
            continue
        try:
            values[str(name)] = float(get_sol_val(solution, var))
        except Exception:
            continue
payload["x"] = values
payload["ok"] = True
print(json.dumps(payload))
"""
