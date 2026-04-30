from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class EvalMetrics:
    objective: float
    best_bound: Optional[float]
    gap: float
    primal_residual: float
    dual_residual: float
    violation: float
    integrality_gap: Optional[float]
    runtime: float
    iterations: int
    memory_mb: Optional[float]
    failed: bool
    failure_reason: str = ""
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricWeights:
    gap: float = 1.0
    violation: float = 0.7
    runtime: float = 0.15
    primal_residual: float = 0.5
    dual_residual: float = 0.5
    fail: float = 4.0
    complexity: float = 0.05
