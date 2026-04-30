from __future__ import annotations

from typing import Any, Dict, Iterable, List

from llm4unroll.utils import clamp


ALLOWED_ACTIONS = {
    "set_tau",
    "set_sigma",
    "scale_tau",
    "scale_sigma",
    "set_rho",
    "scale_rho",
    "set_momentum",
    "restart",
    "damp",
    "clip_update",
    "switch_operator",
    "fallback",
}


def normalize_actions(raw_actions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for item in raw_actions or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name not in ALLOWED_ACTIONS:
            continue
        actions.append({"name": name, "value": item.get("value")})
    return actions


def apply_numeric_bound(value: float, lower: float, upper: float) -> float:
    return clamp(float(value), lower, upper)
