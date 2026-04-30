from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List

from llm4unroll.algorithms.base import RunBudget
from llm4unroll.evaluator.metrics import EvalMetrics, MetricWeights
from llm4unroll.utils import median


@dataclass
class EvalResult:
    score: float
    metrics_by_instance: Dict[str, EvalMetrics]
    aggregate: Dict[str, float]
    policy_id: str
    policy_source: str


class OptimisationEvaluator:
    def __init__(self, algorithm_runner, instances, metric_config=None):
        self.algorithm_runner = algorithm_runner
        self.instances = instances
        self.metric_config = metric_config or MetricWeights()

    def evaluate(self, policy, budget: RunBudget, policy_id: str = "unknown", policy_source: str = "") -> EvalResult:
        results = {}
        for instance in self.instances:
            try:
                metrics = self.algorithm_runner.run(instance=instance, policy=policy, budget=budget)
            except Exception as exc:
                metrics = EvalMetrics(
                    objective=float("inf"),
                    best_bound=None,
                    gap=float("inf"),
                    primal_residual=float("inf"),
                    dual_residual=float("inf"),
                    violation=float("inf"),
                    integrality_gap=None,
                    runtime=budget.time_limit_s,
                    iterations=0,
                    memory_mb=None,
                    failed=True,
                    failure_reason=repr(exc),
                    diagnostics={},
                )
            results[instance.name] = metrics

        aggregate = self._aggregate(list(results.values()))
        score = self._score(aggregate, complexity=self._policy_complexity(policy_source))
        return EvalResult(
            score=score,
            metrics_by_instance=results,
            aggregate=aggregate,
            policy_id=policy_id,
            policy_source=policy_source,
        )

    def evaluate_solver(self, solver, budget: RunBudget, solver_id: str | None = None) -> EvalResult:
        results = {}
        for instance in self.instances:
            try:
                metrics = solver.solve_instance(instance=instance, budget=budget)
            except Exception as exc:
                metrics = EvalMetrics(
                    objective=float("inf"),
                    best_bound=None,
                    gap=float("inf"),
                    primal_residual=float("inf"),
                    dual_residual=float("inf"),
                    violation=float("inf"),
                    integrality_gap=None,
                    runtime=budget.time_limit_s,
                    iterations=0,
                    memory_mb=None,
                    failed=True,
                    failure_reason=repr(exc),
                    diagnostics={},
                )
            results[instance.name] = metrics
        aggregate = self._aggregate(list(results.values()))
        score = self._score(aggregate, complexity=0.0)
        return EvalResult(
            score=score,
            metrics_by_instance=results,
            aggregate=aggregate,
            policy_id=solver_id or getattr(solver, "solver_name", "solver"),
            policy_source=getattr(solver, "solver_name", "solver"),
        )

    def _aggregate(self, metrics_list: List[EvalMetrics]) -> Dict[str, float]:
        fail_rate = sum(1.0 for m in metrics_list if m.failed) / max(len(metrics_list), 1)
        return {
            "median_gap": median([m.gap for m in metrics_list]),
            "median_violation": median([m.violation for m in metrics_list]),
            "median_runtime": median([m.runtime for m in metrics_list]),
            "median_primal_residual": median([m.primal_residual for m in metrics_list]),
            "median_dual_residual": median([m.dual_residual for m in metrics_list]),
            "median_iterations": median([float(m.iterations) for m in metrics_list], default=0.0),
            "fail_rate": fail_rate,
        }

    def _score(self, aggregate: Dict[str, float], complexity: float) -> float:
        weights = self.metric_config
        return -(
            weights.gap * _log1p_safe(aggregate["median_gap"])
            + weights.violation * _log1p_safe(aggregate["median_violation"])
            + weights.runtime * _log1p_safe(aggregate["median_runtime"])
            + weights.primal_residual * _log1p_safe(aggregate["median_primal_residual"])
            + weights.dual_residual * _log1p_safe(aggregate["median_dual_residual"])
            + weights.fail * aggregate["fail_rate"]
            + weights.complexity * complexity
        )

    def _policy_complexity(self, source: str) -> float:
        if not source:
            return 1.0
        lines = [line for line in source.splitlines() if line.strip()]
        branches = sum(1 for line in lines if line.strip().startswith(("if ", "elif ", "for ")))
        return float(len(lines) + branches)


def _log1p_safe(value: float) -> float:
    if value is None or not math.isfinite(value):
        return 1e6
    return math.log1p(max(0.0, value))
