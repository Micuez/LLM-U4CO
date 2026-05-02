from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from llm4unroll.dsl.guards import RuntimeSafetyGuard


@dataclass
class RunBudget:
    max_iters: int
    time_limit_s: float = 30.0
    profile: str = "default"
    same_budget_candidates: int = 8
    controller_train_multiplier: float = 1.0
    native_probe_time_limit_s: float = 30.0


@dataclass
class RunTrace:
    objectives: List[float] = field(default_factory=list)
    gaps: List[float] = field(default_factory=list)
    primal_residuals: List[float] = field(default_factory=list)
    dual_residuals: List[float] = field(default_factory=list)


class UnrolledAlgorithmRunner:
    algorithm_name = "BASE"

    def __init__(self, guard: RuntimeSafetyGuard):
        self.guard = guard

    def run(self, instance, policy, budget: RunBudget):
        raise NotImplementedError

    @staticmethod
    def default_policy(state: Dict[str, Any]) -> Dict[str, Any]:
        return {"actions": [{"name": "fallback"}], "metadata": {"kind": "default"}}
