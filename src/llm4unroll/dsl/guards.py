from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from llm4unroll.dsl.schema import SafetySpec
from llm4unroll.utils import is_finite_number


@dataclass
class GuardStatus:
    ok: bool
    reason: str = ""
    fallback: bool = False


class RuntimeSafetyGuard:
    def __init__(self, safety_spec: SafetySpec):
        self.safety_spec = safety_spec

    def check_state(self, state: Dict[str, float], previous: Dict[str, float] | None = None) -> GuardStatus:
        for key in ("obj", "gap", "r_p_norm", "r_d_norm", "violation", "tau", "sigma", "rho", "momentum"):
            if key in state and state[key] is not None and not is_finite_number(state[key]):
                return GuardStatus(ok=False, reason="Non-finite value in state: %s" % key, fallback=True)

        if previous:
            for key in ("r_p_norm", "r_d_norm", "violation"):
                if key in state and key in previous and is_finite_number(previous[key]) and previous[key] > 0:
                    if state[key] > previous[key] * self.safety_spec.residual_explosion_factor:
                        return GuardStatus(ok=False, reason="Residual explosion on %s" % key, fallback=True)
        return GuardStatus(ok=True)

    def clip_named(self, name: str, value: float) -> float:
        bounds: Tuple[float | None, float | None]
        bounds = {
            "tau": (self.safety_spec.min_tau, self.safety_spec.max_tau),
            "sigma": (self.safety_spec.min_sigma, self.safety_spec.max_sigma),
            "rho": (self.safety_spec.min_rho, self.safety_spec.max_rho),
        }.get(name, (None, None))
        lower, upper = bounds
        if lower is not None:
            value = max(lower, value)
        if upper is not None:
            value = min(upper, value)
        return value
