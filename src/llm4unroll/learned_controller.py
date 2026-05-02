from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List


@dataclass(frozen=True)
class ControllerConfig:
    feature_names: tuple[str, ...]
    feature_scales: tuple[float, ...]
    hidden_units: int
    epochs: int
    lr: float
    sample_count: int


CONTROLLER_CONFIGS: Dict[str, ControllerConfig] = {
    "PDHG": ControllerConfig(
        feature_names=("r_p_norm", "r_d_norm", "gap", "violation", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=180,
        lr=0.04,
        sample_count=192,
    ),
    "ADMM": ControllerConfig(
        feature_names=("r_p_norm", "r_d_norm", "gap", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=180,
        lr=0.04,
        sample_count=192,
    ),
    "FISTA": ControllerConfig(
        feature_names=("obj", "obj_prev", "gap", "stagnation_count"),
        feature_scales=(2.0, 2.0, 1.0, 6.0),
        hidden_units=4,
        epochs=220,
        lr=0.035,
        sample_count=192,
    ),
    "DRS": ControllerConfig(
        feature_names=("residual_norm", "dual_residual", "gap", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=200,
        lr=0.038,
        sample_count=192,
    ),
    "ALM": ControllerConfig(
        feature_names=("violation", "dual_residual", "grad_norm", "gap", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=200,
        lr=0.038,
        sample_count=192,
    ),
    "PCG": ControllerConfig(
        feature_names=("residual_ratio", "direction_curvature", "gap", "precond_quality", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=220,
        lr=0.035,
        sample_count=192,
    ),
    "LNS_REPAIR": ControllerConfig(
        feature_names=("fractionality", "mip_gap", "violation", "repair_progress", "stagnation_count"),
        feature_scales=(1.0, 1.0, 1.0, 1.0, 6.0),
        hidden_units=4,
        epochs=220,
        lr=0.035,
        sample_count=192,
    ),
}


def supported_learned_controller_algorithms() -> List[str]:
    return sorted(CONTROLLER_CONFIGS)


def supported_learned_controller_tiers() -> List[str]:
    return ["minimal", "high_budget", "paper_scale"]


def has_true_learned_controller(algorithm_name: str) -> bool:
    return algorithm_name in CONTROLLER_CONFIGS


def learned_controller_training_note(algorithm_name: str, tier: str = "minimal") -> str:
    if not has_true_learned_controller(algorithm_name):
        return "heuristic fallback"
    config = _controller_config(algorithm_name, tier)
    return "%s trained_mlp_distillation hidden=%d epochs=%d samples=%d" % (
        tier,
        config.hidden_units,
        config.epochs,
        config.sample_count,
    )


def build_learned_controller_source(algorithm_name: str, tier: str = "minimal") -> str:
    if not has_true_learned_controller(algorithm_name):
        raise KeyError("No trained learned-controller config for %s" % algorithm_name)
    weights = _fit_exportable_controller(algorithm_name, tier)
    renderers = {
        "PDHG": _render_pdhg_source,
        "ADMM": _render_admm_source,
        "FISTA": _render_fista_source,
        "DRS": _render_drs_source,
        "ALM": _render_alm_source,
        "PCG": _render_pcg_source,
        "LNS_REPAIR": _render_lns_repair_source,
    }
    return renderers[algorithm_name](weights)


def build_high_budget_learned_controller_source(algorithm_name: str) -> str:
    return build_learned_controller_source(algorithm_name, tier="high_budget")


def _controller_config(algorithm_name: str, tier: str) -> ControllerConfig:
    base = CONTROLLER_CONFIGS[algorithm_name]
    if tier == "minimal":
        return base
    if tier == "high_budget":
        return ControllerConfig(
            feature_names=base.feature_names,
            feature_scales=base.feature_scales,
            hidden_units=base.hidden_units + 2,
            epochs=base.epochs * 2,
            lr=max(0.02, base.lr * 0.8),
            sample_count=base.sample_count * 2,
        )
    if tier == "paper_scale":
        return ControllerConfig(
            feature_names=base.feature_names,
            feature_scales=base.feature_scales,
            hidden_units=base.hidden_units + 2,
            epochs=base.epochs * 4,
            lr=max(0.015, base.lr * 0.6),
            sample_count=base.sample_count * 4,
        )
    raise KeyError("Unsupported learned-controller tier %s" % tier)


@lru_cache(maxsize=None)
def _fit_exportable_controller(algorithm_name: str, tier: str) -> Dict[str, object]:
    config = _controller_config(algorithm_name, tier)
    samples = _sample_training_rows(algorithm_name, config)
    hidden = config.hidden_units
    input_dim = len(config.feature_names)
    rng = random.Random(17 + len(algorithm_name))

    w1 = [[rng.uniform(-0.25, 0.25) for _ in range(input_dim)] for _ in range(hidden)]
    b1 = [0.0] * hidden
    w2 = [[rng.uniform(-0.2, 0.2) for _ in range(hidden)] for _ in range(3)]
    b2 = [0.0] * 3

    for _ in range(config.epochs):
        for row in samples:
            x = row["inputs"]
            target = row["targets"]

            hidden_pre = [sum(w1[j][i] * x[i] for i in range(input_dim)) + b1[j] for j in range(hidden)]
            hidden_act = [value if value > 0.0 else 0.0 for value in hidden_pre]
            outputs = [sum(w2[k][j] * hidden_act[j] for j in range(hidden)) + b2[k] for k in range(3)]

            grad_out = [2.0 * (outputs[k] - target[k]) for k in range(3)]
            grad_hidden = [0.0] * hidden
            for j in range(hidden):
                upstream = sum(grad_out[k] * w2[k][j] for k in range(3))
                grad_hidden[j] = upstream if hidden_pre[j] > 0.0 else 0.0

            for k in range(3):
                for j in range(hidden):
                    w2[k][j] -= config.lr * grad_out[k] * hidden_act[j]
                b2[k] -= config.lr * grad_out[k]

            for j in range(hidden):
                for i in range(input_dim):
                    w1[j][i] -= config.lr * grad_hidden[j] * x[i]
                b1[j] -= config.lr * grad_hidden[j]

    return {
        "feature_names": config.feature_names,
        "feature_scales": config.feature_scales,
        "w1": _round_matrix(w1),
        "b1": _round_vector(b1),
        "w2": _round_matrix(w2),
        "b2": _round_vector(b2),
    }


def _sample_training_rows(algorithm_name: str, config: ControllerConfig) -> List[Dict[str, object]]:
    rng = random.Random(211 + len(algorithm_name))
    rows = []
    for _ in range(config.sample_count):
        state = _sample_state(algorithm_name, rng)
        inputs = [float(state[name]) / scale for name, scale in zip(config.feature_names, config.feature_scales)]
        rows.append({"inputs": inputs, "targets": _teacher_targets(algorithm_name, state)})
    return rows


def _sample_state(algorithm_name: str, rng: random.Random) -> Dict[str, float]:
    if algorithm_name == "PDHG":
        return {
            "r_p_norm": rng.uniform(0.0, 1.8),
            "r_d_norm": rng.uniform(0.0, 1.8),
            "gap": rng.uniform(0.0, 1.0),
            "violation": rng.uniform(0.0, 0.12),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "ADMM":
        return {
            "r_p_norm": rng.uniform(0.0, 1.8),
            "r_d_norm": rng.uniform(0.0, 1.8),
            "gap": rng.uniform(0.0, 1.0),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "FISTA":
        obj_prev = rng.uniform(0.1, 1.8)
        obj = obj_prev + rng.uniform(-0.4, 0.4)
        return {
            "obj": obj,
            "obj_prev": obj_prev,
            "gap": rng.uniform(0.0, 1.0),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "DRS":
        obj_prev = rng.uniform(0.1, 1.2)
        obj = obj_prev + rng.uniform(-0.2, 0.2)
        return {
            "obj": obj,
            "obj_prev": obj_prev,
            "gap": rng.uniform(0.0, 1.0),
            "residual_norm": rng.uniform(0.0, 0.08),
            "dual_residual": rng.uniform(0.0, 0.08),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "ALM":
        obj_prev = rng.uniform(0.2, 1.6)
        obj = obj_prev + rng.uniform(-0.25, 0.25)
        return {
            "obj": obj,
            "obj_prev": obj_prev,
            "gap": rng.uniform(0.0, 0.3),
            "violation": rng.uniform(0.0, 0.16),
            "dual_residual": rng.uniform(0.0, 0.08),
            "grad_norm": rng.uniform(0.0, 0.8),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "PCG":
        return {
            "gap": rng.uniform(0.0, 0.5),
            "residual_ratio": rng.uniform(0.2, 1.2),
            "direction_curvature": rng.uniform(-1e-8, 0.5),
            "precond_quality": rng.uniform(0.0, 1.0),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    if algorithm_name == "LNS_REPAIR":
        return {
            "fractionality": rng.uniform(0.0, 0.4),
            "mip_gap": rng.uniform(0.0, 0.3),
            "violation": rng.uniform(0.0, 0.18),
            "repair_progress": rng.uniform(0.0, 1.0),
            "stagnation_count": float(rng.randint(0, 6)),
        }
    raise KeyError("Unsupported learned-controller algorithm %s" % algorithm_name)


def _teacher_targets(algorithm_name: str, state: Dict[str, float]) -> List[float]:
    if algorithm_name == "PDHG":
        ratio = (state["r_p_norm"] + 1e-9) / (state["r_d_norm"] + 1e-9)
        direction = 1.0 if ratio > 1.35 or state["violation"] > 0.05 else -1.0 if ratio < 0.78 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 4.0 else 0.0
        damp = 0.82 if restart > 0.0 else 0.94 if state["gap"] < 0.08 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "ADMM":
        ratio = (state["r_p_norm"] + 1e-9) / (state["r_d_norm"] + 1e-9)
        direction = 1.0 if ratio > 1.25 else -1.0 if ratio < 0.82 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 4.0 else 0.0
        damp = 0.86 if restart > 0.0 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "FISTA":
        direction = 1.0 if state["obj"] > state["obj_prev"] else -1.0 if state["gap"] < 0.08 else 0.0
        restart = 1.0 if direction > 0.0 or state["stagnation_count"] >= 4.0 else 0.0
        damp = 0.9 if restart > 0.0 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "DRS":
        direction = 1.0 if state["residual_norm"] > 0.02 else -1.0 if state["gap"] < 0.08 and state["dual_residual"] < 0.01 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 5.0 or state["obj"] > state["obj_prev"] else 0.0
        damp = 0.82 if restart > 0.0 else 0.92 if state["residual_norm"] > 0.01 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "ALM":
        direction = 1.0 if state["violation"] > 0.08 else -1.0 if state["violation"] < 0.015 and state["dual_residual"] < 0.02 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 4.0 or state["gap"] > 0.12 else 0.0
        damp = 0.82 if restart > 0.0 else 0.9 if state["grad_norm"] > 0.2 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "PCG":
        direction = 1.0 if state["residual_ratio"] > 0.92 or state["direction_curvature"] <= 1e-8 else -1.0 if state["residual_ratio"] < 0.45 and state["precond_quality"] > 0.7 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 3.0 or state["direction_curvature"] <= 1e-8 else 0.0
        damp = 0.78 if restart > 0.0 else 0.9 if state["gap"] < 0.08 else 1.0
        return [direction, restart, damp]
    if algorithm_name == "LNS_REPAIR":
        direction = 1.0 if state["fractionality"] > 0.22 and state["mip_gap"] > 0.08 else -1.0 if state["repair_progress"] > 0.7 and state["violation"] < 0.02 else 0.0
        restart = 1.0 if state["stagnation_count"] >= 4.0 and state["mip_gap"] > 0.05 else 0.0
        damp = 0.86 if state["violation"] > 0.0 else 0.94 if direction < 0.0 else 1.0
        return [direction, restart, damp]
    raise KeyError("Unsupported learned-controller algorithm %s" % algorithm_name)


def _round_matrix(matrix: List[List[float]]) -> List[List[float]]:
    return [[round(value, 4) for value in row] for row in matrix]


def _round_vector(values: List[float]) -> List[float]:
    return [round(value, 4) for value in values]


def _render_feature_block(weights: Dict[str, object]) -> List[str]:
    lines = []
    feature_names = list(weights["feature_names"])
    feature_scales = list(weights["feature_scales"])
    for idx, (name, scale) in enumerate(zip(feature_names, feature_scales)):
        lines.append("    x%d = state.get('%s', 0.0) / %.4f" % (idx, name, float(scale)))
    return lines


def _render_hidden_block(weights: Dict[str, object]) -> List[str]:
    lines = []
    w1 = weights["w1"]
    b1 = weights["b1"]
    for hid, row in enumerate(w1):
        expr = " + ".join("%.4f * x%d" % (float(coeff), idx) for idx, coeff in enumerate(row))
        lines.append("    h%d = %s + %.4f" % (hid, expr, float(b1[hid])))
        lines.append("    if h%d < 0.0:" % hid)
        lines.append("        h%d = 0.0" % hid)
    return lines


def _render_output_expr(weights: Dict[str, object], out_idx: int) -> str:
    w2 = weights["w2"][out_idx]
    b2 = float(weights["b2"][out_idx])
    terms = ["%.4f * h%d" % (float(coeff), hid) for hid, coeff in enumerate(w2)]
    return " + ".join(terms) + " + %.4f" % b2


def _render_pdhg_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    tau = state.get('tau', 1.0)")
    lines.append("    sigma = state.get('sigma', 1.0)")
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.18:")
    lines.append("        actions.append({'name': 'scale_tau', 'value': 1.08 if tau <= sigma else 1.04})")
    lines.append("        actions.append({'name': 'scale_sigma', 'value': 0.92 if sigma <= tau else 0.96})")
    lines.append("    elif direction < -0.18:")
    lines.append("        actions.append({'name': 'scale_tau', 'value': 0.92 if tau >= sigma else 0.96})")
    lines.append("        actions.append({'name': 'scale_sigma', 'value': 1.08 if sigma >= tau else 1.04})")
    lines.append("    if restart_score > 0.35 or k > 6:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.86:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.82})")
    lines.append("    elif damp_score < 0.97:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.9})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_admm_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    rho = state.get('rho', 1.0)")
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.16:")
    lines.append("        actions.append({'name': 'scale_rho', 'value': 1.12 if rho < 1.6 else 1.04})")
    lines.append("    elif direction < -0.16:")
    lines.append("        actions.append({'name': 'scale_rho', 'value': 0.9 if rho > 0.5 else 0.96})")
    lines.append("    if restart_score > 0.35 or k > 6:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.9:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.86})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_fista_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.18:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("        actions.append({'name': 'set_momentum', 'value': 0.0})")
    lines.append("        actions.append({'name': 'scale_tau', 'value': 0.92})")
    lines.append("    elif direction < -0.18:")
    lines.append("        actions.append({'name': 'set_momentum', 'value': 0.52})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'set_momentum', 'value': 0.82})")
    lines.append("    if restart_score > 0.38:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.92:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.9})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_drs_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.18:")
    lines.append("        actions.append({'name': 'set_lambda_relax', 'value': 1.22})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.8})")
    lines.append("    elif direction < -0.18:")
    lines.append("        actions.append({'name': 'set_lambda_relax', 'value': 0.92})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.55})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.0})")
    lines.append("    if restart_score > 0.38 or k > 6:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.88:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.82})")
    lines.append("    elif damp_score < 0.97:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.92})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_alm_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    rho = state.get('rho', 1.0)")
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.16:")
    lines.append("        actions.append({'name': 'scale_rho', 'value': 1.18 if rho < 1.4 else 1.06})")
    lines.append("    elif direction < -0.16:")
    lines.append("        actions.append({'name': 'scale_rho', 'value': 0.9 if rho > 0.4 else 0.96})")
    lines.append("    if restart_score > 0.34 or k > 6:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.88:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.82})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.7})")
    lines.append("    elif damp_score < 0.97:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.92})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.0})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.4})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_pcg_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.18:")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.55})")
    lines.append("    elif direction < -0.18:")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.35})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.92})")
    lines.append("    if restart_score > 0.34 or k > 5:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.84:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.72})")
    lines.append("    elif damp_score < 0.95:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.88})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"


def _render_lns_repair_source(weights: Dict[str, object]) -> str:
    lines = ["def policy(state):", "    actions = []", "    actions.append({'name': 'fallback'})"]
    lines.extend(_render_feature_block(weights))
    lines.append("    k = state.get('k', 0)")
    lines.extend(_render_hidden_block(weights))
    lines.append("    direction = %s" % _render_output_expr(weights, 0))
    lines.append("    restart_score = %s" % _render_output_expr(weights, 1))
    lines.append("    damp_score = %s" % _render_output_expr(weights, 2))
    lines.append("    if direction > 0.18:")
    lines.append("        actions.append({'name': 'scale_neighbourhood_size', 'value': 1.18})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 0.75})")
    lines.append("    elif direction < -0.18:")
    lines.append("        actions.append({'name': 'scale_neighbourhood_size', 'value': 0.82})")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.15})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'clip_update', 'value': 1.0})")
    lines.append("    if restart_score > 0.38 or k > 6:")
    lines.append("        actions.append({'name': 'restart'})")
    lines.append("    if damp_score < 0.9:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.88})")
    lines.append("    elif damp_score < 0.97:")
    lines.append("        actions.append({'name': 'damp', 'value': 0.96})")
    lines.append("    else:")
    lines.append("        actions.append({'name': 'damp', 'value': 1.0})")
    lines.append("    return {'actions': actions}")
    return "\n".join(lines) + "\n"
