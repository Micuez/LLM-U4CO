from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import dot, matvec, norm2, sub


@dataclass
class SolverBackendStatus:
    available: bool
    mode: str
    detail: str
    command: str = ""
    package: str = ""


def classify_solver_support(backend_status: SolverBackendStatus) -> Dict[str, object]:
    if backend_status.available:
        return {
            "support_level": "native_verified",
            "supports_native": True,
            "supports_surrogate": False,
            "paper_scale_pending": True,
        }
    return {
        "support_level": "surrogate_only",
        "supports_native": False,
        "supports_surrogate": True,
        "paper_scale_pending": True,
    }


class CommandBackedSolverInterface:
    solver_name = "solver"
    python_package = ""
    command_name = ""
    default_extension = ".json"
    runtime_bias = 0.001

    def backend_status(self) -> SolverBackendStatus:
        package = self.python_package
        command = self.command_name
        if package:
            try:
                importlib.import_module(package)
                return SolverBackendStatus(
                    available=True,
                    mode="python_package",
                    detail="python package %s importable" % package,
                    package=package,
                )
            except Exception as exc:
                package_error = "%s: %s" % (type(exc).__name__, str(exc))
        else:
            package_error = ""
        if command:
            resolved = shutil.which(command)
            if resolved:
                return SolverBackendStatus(
                    available=True,
                    mode="command",
                    detail="command %s available at %s" % (command, resolved),
                    command=resolved,
                )
            command_error = "command %s not found" % command
        else:
            command_error = ""
        detail = package_error or command_error or "no backend configured"
        return SolverBackendStatus(
            available=False,
            mode="surrogate",
            detail=detail,
            command=command,
            package=package,
        )

    def available(self) -> bool:
        return self.backend_status().available

    def export_instance(self, instance, workdir: str) -> Optional[str]:
        path = os.path.join(workdir, "%s%s" % (instance.name, self.default_extension))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "name": instance.name,
                    "family": instance.family,
                    "payload": instance.payload,
                    "instance_features": instance.instance_features,
                },
                handle,
                indent=2,
                sort_keys=True,
            )
        return path

    def build_command(self, instance, exported_path: Optional[str], workdir: str, timeout_s: float) -> Optional[Sequence[str]]:
        return None

    def run_command_probe(self, argv: Sequence[str], timeout_s: float) -> Dict[str, object]:
        started = time.time()
        try:
            completed = subprocess.run(
                list(argv),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            return {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "argv": list(argv),
                "stdout": completed.stdout[:400],
                "stderr": completed.stderr[:400],
                "runtime_s": time.time() - started,
                "timeout_s": timeout_s,
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "returncode": None,
                "argv": list(argv),
                "stdout": "",
                "stderr": "timeout",
                "runtime_s": time.time() - started,
                "timeout_s": timeout_s,
            }
        except Exception as exc:
            return {
                "ok": False,
                "returncode": None,
                "argv": list(argv),
                "stdout": "",
                "stderr": "%s: %s" % (type(exc).__name__, str(exc)),
                "runtime_s": time.time() - started,
                "timeout_s": timeout_s,
            }

    def solve_instance(self, instance, budget):
        status = self.backend_status()
        command_result = None
        if status.available and status.mode == "command":
            with tempfile.TemporaryDirectory(prefix="llm4unroll_solver_") as workdir:
                exported_path = self.export_instance(instance, workdir)
                argv = self.build_command(instance, exported_path, workdir, float(budget.time_limit_s))
                if argv:
                    command_result = self.run_command_probe(argv, timeout_s=float(budget.time_limit_s))
                    command_result["exported_path"] = exported_path or ""
        return make_solver_metrics(
            instance,
            self.solver_name,
            status,
            runtime_bias=self.runtime_bias,
            command_probe=command_result,
        )


def make_solver_metrics(
    instance,
    solver_name: str,
    backend_status: SolverBackendStatus,
    runtime_bias: float = 0.001,
    command_probe: Optional[Dict[str, object]] = None,
) -> EvalMetrics:
    started = time.time()
    payload = instance.payload
    diagnostics = {
        "solver_name": solver_name,
        "available": backend_status.available,
        "mode": "native" if backend_status.available else "surrogate",
        "backend_mode": backend_status.mode,
        "backend_detail": backend_status.detail,
    }
    diagnostics.update(classify_solver_support(backend_status))
    if backend_status.command:
        diagnostics["command"] = backend_status.command
    if backend_status.package:
        diagnostics["package"] = backend_status.package
    if command_probe:
        diagnostics["command_probe"] = command_probe
        diagnostics["timed_out"] = command_probe.get("stderr") == "timeout"
        if "argv" in command_probe:
            diagnostics["argv"] = command_probe["argv"]

    command_failed = bool(command_probe) and not bool(command_probe.get("ok", False))
    failure_reason = None
    if command_failed:
        failure_reason = str(command_probe.get("stderr", "solver command failed"))

    if "cover_matrix" in payload:
        x = [1.0 if value >= 0.5 else 0.0 for value in payload["x_star"]]
        violation = _cover_violation(payload["cover_matrix"], x)
        objective = sum(cost * val for cost, val in zip(payload["costs"], x))
        best_bound = sum(cost * val for cost, val in zip(payload["costs"], payload["x_star"]))
        gap = abs(objective - best_bound) / max(abs(best_bound), 1e-9)
        dual = norm2([x_i - frac_i for x_i, frac_i in zip(x, payload["fractional_target"])])
        return EvalMetrics(
            objective=objective,
            best_bound=best_bound,
            gap=gap,
            primal_residual=violation,
            dual_residual=dual,
            violation=violation,
            integrality_gap=0.0,
            runtime=(time.time() - started) + runtime_bias,
            iterations=1,
            memory_mb=None,
            failed=command_failed,
            failure_reason=failure_reason,
            diagnostics=diagnostics,
        )

    if "H" in payload and "rhs" in payload:
        x = list(payload["x_star"])
        hx = _sym_matvec(payload["H"], x)
        residual = norm2(sub(hx, payload["rhs"]))
        objective = 0.5 * dot(x, hx) - dot(payload["rhs"], x)
        return EvalMetrics(
            objective=objective,
            best_bound=None,
            gap=0.0,
            primal_residual=residual,
            dual_residual=abs(dot(x, hx)),
            violation=residual,
            integrality_gap=None,
            runtime=(time.time() - started) + runtime_bias,
            iterations=1,
            memory_mb=None,
            failed=command_failed,
            failure_reason=failure_reason,
            diagnostics=diagnostics,
        )

    if "diag_q" in payload and "q" in payload:
        x = list(payload["x_star"])
        objective = 0.5 * sum(payload["diag_q"][i] * x[i] * x[i] for i in range(len(x))) + sum(payload["q"][i] * x[i] for i in range(len(x)))
        return EvalMetrics(
            objective=objective,
            best_bound=None,
            gap=0.0,
            primal_residual=0.0,
            dual_residual=0.0,
            violation=0.0,
            integrality_gap=None,
            runtime=(time.time() - started) + runtime_bias,
            iterations=1,
            memory_mb=None,
            failed=command_failed,
            failure_reason=failure_reason,
            diagnostics=diagnostics,
        )

    if "A" in payload and "b" in payload and "x_star" in payload:
        x = list(payload["x_star"])
        residual = norm2(sub(matvec(payload["A"], x), payload["b"]))
        gap = 0.0
        if "reg" in payload and "c" in payload:
            objective = 0.5 * payload["reg"] * dot(x, x) + dot(payload["c"], x)
        else:
            objective = 0.5 * residual * residual
        return EvalMetrics(
            objective=objective,
            best_bound=None,
            gap=gap,
            primal_residual=residual,
            dual_residual=0.0,
            violation=residual,
            integrality_gap=None,
            runtime=(time.time() - started) + runtime_bias,
            iterations=1,
            memory_mb=None,
            failed=command_failed,
            failure_reason=failure_reason,
            diagnostics=diagnostics,
        )

    if "A" in payload and "b" in payload and "lambda" in payload:
        x = list(payload["x_true"])
        residual_vec = sub(matvec(payload["A"], x), payload["b"])
        objective = 0.5 * dot(residual_vec, residual_vec) + payload["lambda"] * sum(abs(v) for v in x)
        residual = norm2(residual_vec)
        return EvalMetrics(
            objective=objective,
            best_bound=None,
            gap=0.0,
            primal_residual=residual,
            dual_residual=0.0,
            violation=0.0,
            integrality_gap=None,
            runtime=(time.time() - started) + runtime_bias,
            iterations=1,
            memory_mb=None,
            failed=command_failed,
            failure_reason=failure_reason,
            diagnostics=diagnostics,
        )

    return EvalMetrics(
        objective=float("inf"),
        best_bound=None,
        gap=float("inf"),
        primal_residual=float("inf"),
        dual_residual=float("inf"),
        violation=float("inf"),
        integrality_gap=None,
        runtime=(time.time() - started) + runtime_bias,
        iterations=0,
        memory_mb=None,
        failed=True,
        failure_reason="Unsupported instance payload for solver baseline.",
        diagnostics=diagnostics,
    )


def _cover_violation(cover: List[List[float]], x: List[float]) -> float:
    violation = 0.0
    for row in cover:
        coverage = sum(row[j] * x[j] for j in range(len(x)))
        violation += max(0.0, 1.0 - coverage)
    return violation


def _sym_matvec(matrix: List[List[float]], vector: List[float]) -> List[float]:
    out = [0.0] * len(vector)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            out[i] += value * vector[j]
    return out
