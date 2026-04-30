from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FeatureSpec:
    name: str
    kind: str = "number"
    default_kind: str = "number"
    description: str = ""


@dataclass
class StateSpec:
    allowed_features: List[str]
    required_features: List[str]
    feature_types: Dict[str, FeatureSpec] = field(default_factory=dict)


@dataclass
class ActionSpec:
    name: str
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    arity: int = 1
    value_kind: str = "number"
    conflicts_with: List[str] = field(default_factory=list)
    category: str = ""


@dataclass
class SafetySpec:
    require_fallback: bool = True
    require_state_get_default: bool = True
    require_explicit_return: bool = True
    max_actions_per_call: int = 8
    forbid_conflicting_actions: bool = True
    require_parameter_guardrails: bool = True
    residual_explosion_factor: float = 1e3
    max_stagnation: int = 25
    min_tau: Optional[float] = None
    max_tau: Optional[float] = None
    min_sigma: Optional[float] = None
    max_sigma: Optional[float] = None
    min_rho: Optional[float] = None
    max_rho: Optional[float] = None


@dataclass
class PolicySpec:
    algorithm: str
    description: str
    state: StateSpec
    actions: List[ActionSpec]
    safety: SafetySpec = field(default_factory=SafetySpec)


@dataclass
class PolicyOutput:
    actions: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
