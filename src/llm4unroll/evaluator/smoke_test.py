from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict

from llm4unroll.algorithms.base import RunBudget
from llm4unroll.utils import is_finite_number


@dataclass
class SmokeTestResult:
    ok: bool
    reason: str = ""
    runtime_s: float = 0.0
    diagnostics: Dict[str, object] = field(default_factory=dict)


def run_policy_smoke_test(runner, instance, policy, budget: RunBudget) -> SmokeTestResult:
    started = time.time()
    try:
        metrics = runner.run(instance=instance, policy=policy, budget=budget)
    except Exception as exc:
        return SmokeTestResult(ok=False, reason="runner_exception: %r" % exc, runtime_s=time.time() - started)

    runtime_s = time.time() - started
    if runtime_s > budget.time_limit_s * 1.25:
        return SmokeTestResult(
            ok=False,
            reason="smoke_timeout",
            runtime_s=runtime_s,
            diagnostics={"time_limit_s": budget.time_limit_s},
        )

    if metrics.failed:
        return SmokeTestResult(
            ok=False,
            reason=metrics.failure_reason or "runner_marked_failed",
            runtime_s=runtime_s,
            diagnostics={"iterations": metrics.iterations},
        )

    numeric_fields = {
        "objective": metrics.objective,
        "gap": metrics.gap,
        "primal_residual": metrics.primal_residual,
        "dual_residual": metrics.dual_residual,
        "violation": metrics.violation,
        "runtime": metrics.runtime,
    }
    for key, value in numeric_fields.items():
        if not is_finite_number(value):
            return SmokeTestResult(
                ok=False,
                reason="non_finite_%s" % key,
                runtime_s=runtime_s,
                diagnostics={"field": key, "value": value},
            )

    if metrics.iterations <= 0:
        return SmokeTestResult(
            ok=False,
            reason="zero_iterations",
            runtime_s=runtime_s,
            diagnostics={},
        )

    return SmokeTestResult(
        ok=True,
        runtime_s=runtime_s,
        diagnostics={
            "iterations": metrics.iterations,
            "gap": metrics.gap,
            "violation": metrics.violation,
            "runtime": metrics.runtime,
        },
    )
