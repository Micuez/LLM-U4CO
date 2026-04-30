from __future__ import annotations

from llm4unroll.dsl.transpiler import compile_policy
from llm4unroll.search.population import CandidatePolicy


def build_baseline_policies(algorithm_name: str):
    return [
        CandidatePolicy("vanilla", _source_for(algorithm_name, "vanilla"), compile_policy(_source_for(algorithm_name, "vanilla")), "baseline"),
        CandidatePolicy("adaptive", _source_for(algorithm_name, "adaptive"), compile_policy(_source_for(algorithm_name, "adaptive")), "baseline"),
        CandidatePolicy("conservative", _source_for(algorithm_name, "conservative"), compile_policy(_source_for(algorithm_name, "conservative")), "baseline"),
    ]


def build_search_candidates(algorithm_name: str):
    return [
        CandidatePolicy("search_seed", _source_for(algorithm_name, "adaptive"), compile_policy(_source_for(algorithm_name, "adaptive")), "search_seed"),
        CandidatePolicy("search_variant_1", _source_for(algorithm_name, "search_variant_1"), compile_policy(_source_for(algorithm_name, "search_variant_1")), "mutation"),
        CandidatePolicy("search_variant_2", _source_for(algorithm_name, "search_variant_2"), compile_policy(_source_for(algorithm_name, "search_variant_2")), "mutation"),
    ]


def _vanilla_policy(algorithm_name: str):
    def policy(state):
        return {"actions": [{"name": "fallback"}], "metadata": {"kind": "vanilla", "algorithm": algorithm_name}}
    return policy


def _conservative_policy(algorithm_name: str):
    def policy(state):
        actions = [{"name": "fallback"}]
        if state.get("stagnation_count", 0) > 5:
            actions.append({"name": "restart"})
            if algorithm_name == "PDHG":
                actions.append({"name": "scale_tau", "value": 0.8})
                actions.append({"name": "scale_sigma", "value": 0.8})
            elif algorithm_name == "ADMM":
                actions.append({"name": "scale_rho", "value": 0.9})
            elif algorithm_name == "FISTA":
                actions.append({"name": "scale_tau", "value": 0.8})
                actions.append({"name": "set_momentum", "value": 0.0})
        actions.append({"name": "damp", "value": 0.7})
        return {"actions": actions, "metadata": {"kind": "conservative"}}
    return policy


def _adaptive_policy(algorithm_name: str):
    def policy(state):
        actions = [{"name": "fallback"}]
        if algorithm_name == "PDHG":
            ratio = (state.get("r_p_norm", 0.0) + 1e-9) / (state.get("r_d_norm", 0.0) + 1e-9)
            if ratio > 1.5:
                actions.extend([
                    {"name": "scale_tau", "value": 1.1},
                    {"name": "scale_sigma", "value": 0.9},
                ])
            elif ratio < 0.67:
                actions.extend([
                    {"name": "scale_tau", "value": 0.9},
                    {"name": "scale_sigma", "value": 1.1},
                ])
        elif algorithm_name == "ADMM":
            ratio = (state.get("r_p_norm", 0.0) + 1e-9) / (state.get("r_d_norm", 0.0) + 1e-9)
            if ratio > 1.2:
                actions.append({"name": "scale_rho", "value": 1.15})
            elif ratio < 0.8:
                actions.append({"name": "scale_rho", "value": 0.9})
        elif algorithm_name == "FISTA":
            if state.get("obj", 0.0) > state.get("obj_prev", 0.0):
                actions.append({"name": "restart"})
                actions.append({"name": "set_momentum", "value": 0.0})
            elif state.get("stagnation_count", 0) > 3:
                actions.append({"name": "set_momentum", "value": 0.5})
        actions.append({"name": "damp", "value": 1.0})
        return {"actions": actions, "metadata": {"kind": "adaptive"}}
    return policy


def _search_variant_1(algorithm_name: str):
    def policy(state):
        actions = [{"name": "fallback"}]
        if state.get("stagnation_count", 0) >= 2:
            actions.append({"name": "restart"})
        if algorithm_name == "PDHG":
            actions.append({"name": "scale_tau", "value": 1.05 if state.get("r_p_norm", 0.0) > state.get("r_d_norm", 0.0) else 0.95})
            actions.append({"name": "scale_sigma", "value": 0.95 if state.get("r_p_norm", 0.0) > state.get("r_d_norm", 0.0) else 1.05})
        elif algorithm_name == "ADMM":
            actions.append({"name": "scale_rho", "value": 1.05 if state.get("r_p_norm", 0.0) > state.get("r_d_norm", 0.0) else 0.95})
        else:
            actions.append({"name": "set_momentum", "value": 0.3 if state.get("stagnation_count", 0) else 0.9})
        actions.append({"name": "damp", "value": 0.9})
        return {"actions": actions, "metadata": {"kind": "search_variant_1"}}
    return policy


def _search_variant_2(algorithm_name: str):
    def policy(state):
        actions = [{"name": "fallback"}]
        if algorithm_name == "PDHG":
            actions.extend([
                {"name": "scale_tau", "value": 1.15 if state.get("violation", 0.0) > 0.05 else 0.98},
                {"name": "scale_sigma", "value": 0.85 if state.get("violation", 0.0) > 0.05 else 1.02},
            ])
        elif algorithm_name == "ADMM":
            if state.get("stagnation_count", 0) > 4:
                actions.append({"name": "restart"})
            actions.append({"name": "scale_rho", "value": 1.2 if state.get("r_p_norm", 0.0) > 0.02 else 0.97})
        else:
            if state.get("obj", 0.0) > state.get("obj_prev", 0.0):
                actions.append({"name": "restart"})
            actions.append({"name": "set_momentum", "value": 0.2 if state.get("gap", 1.0) < 0.1 else 0.85})
        actions.append({"name": "damp", "value": 0.8})
        return {"actions": actions, "metadata": {"kind": "search_variant_2"}}
    return policy


def _source_for(algorithm_name: str, variant: str) -> str:
    bodies = {
        "vanilla": _vanilla_source(),
        "adaptive": _adaptive_source(algorithm_name),
        "conservative": _conservative_source(algorithm_name),
        "search_variant_1": _search_variant_1_source(algorithm_name),
        "search_variant_2": _search_variant_2_source(algorithm_name),
    }
    return bodies[variant]


def _vanilla_source() -> str:
    return (
        "def policy(state):\n"
        "    actions = []\n"
        "    actions.append({'name': 'fallback'})\n"
        "    return {'actions': actions}\n"
    )


def _adaptive_source(algorithm_name: str) -> str:
    bodies = {
        "PDHG": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    ratio = (state.get('r_p_norm', 0.0) + 1e-9) / (state.get('r_d_norm', 0.0) + 1e-9)\n"
            "    if ratio > 1.5:\n"
            "        actions.append({'name': 'scale_tau', 'value': 1.12})\n"
            "        actions.append({'name': 'scale_sigma', 'value': 0.9})\n"
            "    elif ratio < 0.7:\n"
            "        actions.append({'name': 'scale_tau', 'value': 0.9})\n"
            "        actions.append({'name': 'scale_sigma', 'value': 1.12})\n"
            "    if state.get('stagnation_count', 0) >= 4:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.85})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    return {'actions': actions}\n"
        ),
        "ADMM": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    ratio = (state.get('r_p_norm', 0.0) + 1e-9) / (state.get('r_d_norm', 0.0) + 1e-9)\n"
            "    if ratio > 1.3:\n"
            "        actions.append({'name': 'scale_rho', 'value': 1.18})\n"
            "    elif ratio < 0.77:\n"
            "        actions.append({'name': 'scale_rho', 'value': 0.88})\n"
            "    if state.get('stagnation_count', 0) >= 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.8})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    return {'actions': actions}\n"
        ),
        "FISTA": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('obj', 0.0) > state.get('obj_prev', 0.0):\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'set_momentum', 'value': 0.0})\n"
            "        actions.append({'name': 'scale_tau', 'value': 0.92})\n"
            "    elif state.get('gap', 1.0) < 0.05:\n"
            "        actions.append({'name': 'set_momentum', 'value': 0.6})\n"
            "    elif state.get('stagnation_count', 0) >= 3:\n"
            "        actions.append({'name': 'set_momentum', 'value': 0.35})\n"
            "        actions.append({'name': 'scale_tau', 'value': 0.96})\n"
            "    actions.append({'name': 'damp', 'value': 1.0})\n"
            "    return {'actions': actions}\n"
        ),
        "ALM": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('violation', 0.0) > 0.05:\n"
            "        actions.append({'name': 'scale_rho', 'value': 1.25})\n"
            "    elif state.get('gap', 1.0) < 0.02:\n"
            "        actions.append({'name': 'scale_rho', 'value': 0.92})\n"
            "    if state.get('stagnation_count', 0) >= 4:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'set_rho', 'value': 0.8})\n"
            "    return {'actions': actions}\n"
        ),
        "DRS": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('residual_norm', 0.0) > 0.02:\n"
            "        actions.append({'name': 'damp', 'value': 0.9})\n"
            "    elif state.get('gap', 1.0) < 0.15:\n"
            "        actions.append({'name': 'damp', 'value': 0.65})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.8})\n"
            "    if state.get('stagnation_count', 0) >= 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
        "PCG": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('residual_ratio', 1.0) > 0.9:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.75})\n"
            "    elif state.get('residual_ratio', 1.0) < 0.2:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.9})\n"
            "    return {'actions': actions}\n"
        ),
        "LNS_REPAIR": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('violation', 0.0) > 0.0:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    elif state.get('fractionality', 0.0) > 0.22:\n"
            "        actions.append({'name': 'damp', 'value': 0.85})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.7})\n"
            "    if state.get('stagnation_count', 0) >= 4 and state.get('mip_gap', 0.0) > 0.05:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
    }
    return bodies[algorithm_name]


def _conservative_source(algorithm_name: str) -> str:
    bodies = {
        "PDHG": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('stagnation_count', 0) > 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'scale_tau', 'value': 0.82})\n"
            "        actions.append({'name': 'scale_sigma', 'value': 0.82})\n"
            "    actions.append({'name': 'damp', 'value': 0.7})\n"
            "    return {'actions': actions}\n"
        ),
        "ADMM": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('r_p_norm', 0.0) > 2.0 * (state.get('r_d_norm', 0.0) + 1e-9):\n"
            "        actions.append({'name': 'scale_rho', 'value': 1.08})\n"
            "    elif state.get('stagnation_count', 0) > 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'scale_rho', 'value': 0.92})\n"
            "    actions.append({'name': 'damp', 'value': 0.72})\n"
            "    return {'actions': actions}\n"
        ),
        "FISTA": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('obj', 0.0) > state.get('obj_prev', 0.0) or state.get('stagnation_count', 0) > 4:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'set_momentum', 'value': 0.0})\n"
            "        actions.append({'name': 'scale_tau', 'value': 0.85})\n"
            "    actions.append({'name': 'damp', 'value': 0.72})\n"
            "    return {'actions': actions}\n"
        ),
        "ALM": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('violation', 0.0) > 0.1:\n"
            "        actions.append({'name': 'set_rho', 'value': 1.2})\n"
            "    if state.get('stagnation_count', 0) > 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
        "DRS": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    actions.append({'name': 'damp', 'value': 0.65})\n"
            "    if state.get('stagnation_count', 0) > 5:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
        "PCG": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    actions.append({'name': 'damp', 'value': 0.8})\n"
            "    if state.get('stagnation_count', 0) > 3 or state.get('residual_ratio', 1.0) > 0.95:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
        "LNS_REPAIR": (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    actions.append({'name': 'damp', 'value': 0.78})\n"
            "    if state.get('stagnation_count', 0) > 5 and state.get('fractionality', 0.0) > 0.15:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        ),
    }
    return bodies[algorithm_name]


def _search_variant_1_source(algorithm_name: str) -> str:
    if algorithm_name == "ALM":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    rho = state.get('rho', 1.0)\n"
            "    violation = state.get('violation', 0.0)\n"
            "    gap = state.get('gap', 1.0)\n"
            "    if violation > 0.08 and gap > 0.04:\n"
            "        actions.append({'name': 'scale_rho', 'value': 1.3})\n"
            "    elif violation < 0.01 and gap < 0.015 and rho > 0.2:\n"
            "        actions.append({'name': 'scale_rho', 'value': 0.9})\n"
            "    if state.get('stagnation_count', 0) >= 3 and violation > 0.015:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'set_rho', 'value': 1.1})\n"
            "    if violation > 0.03:\n"
            "        actions.append({'name': 'damp', 'value': 0.9})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "DRS":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    residual = state.get('residual_norm', 0.0)\n"
            "    gap = state.get('gap', 1.0)\n"
            "    if residual > 0.01 and gap > 0.5:\n"
            "        actions.append({'name': 'damp', 'value': 0.95})\n"
            "    elif residual < 0.003 and gap < 0.3:\n"
            "        actions.append({'name': 'damp', 'value': 0.55})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.78})\n"
            "    if state.get('stagnation_count', 0) >= 3 and residual > 0.004:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "PCG":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    ratio = state.get('residual_ratio', 1.0)\n"
            "    curvature = state.get('direction_curvature', 1.0)\n"
            "    if curvature <= 1e-8:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.6})\n"
            "    elif ratio > 0.82:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.72})\n"
            "    elif ratio < 0.18:\n"
            "        actions.append({'name': 'damp', 'value': 1.0})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.9})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "LNS_REPAIR":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    mip_gap = state.get('mip_gap', 0.0)\n"
            "    fractionality = state.get('fractionality', 0.0)\n"
            "    lp_gap = state.get('lp_gap', 0.0)\n"
            "    if mip_gap > 0.18 and fractionality > 0.18:\n"
            "        actions.append({'name': 'damp', 'value': 0.98})\n"
            "    elif lp_gap < 0.08 and fractionality < 0.12:\n"
            "        actions.append({'name': 'damp', 'value': 0.62})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.84})\n"
            "    if state.get('stagnation_count', 0) >= 3 and mip_gap > 0.1:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        )
    return (
        "def policy(state):\n"
        "    actions = []\n"
        "    actions.append({'name': 'fallback'})\n"
        "    if state.get('stagnation_count', 0) >= 2:\n"
        "        actions.append({'name': 'restart'})\n"
        "    actions.append({'name': 'damp', 'value': 0.9})\n"
        "    return {'actions': actions}\n"
    )


def _search_variant_2_source(algorithm_name: str) -> str:
    if algorithm_name == "ALM":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    rho = state.get('rho', 1.0)\n"
            "    violation = state.get('violation', 0.0)\n"
            "    gap = state.get('gap', 1.0)\n"
            "    if violation > 0.12:\n"
            "        actions.append({'name': 'set_rho', 'value': 1.6 if rho < 1.6 else rho})\n"
            "    elif gap < 0.01 and violation < 0.015:\n"
            "        actions.append({'name': 'scale_rho', 'value': 0.82})\n"
            "    if state.get('stagnation_count', 0) > 4 and gap > 0.02:\n"
            "        actions.append({'name': 'restart'})\n"
            "        actions.append({'name': 'damp', 'value': 0.78})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.96})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "DRS":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    residual = state.get('residual_norm', 0.0)\n"
            "    gap = state.get('gap', 1.0)\n"
            "    if residual > 0.02:\n"
            "        actions.append({'name': 'damp', 'value': 0.98})\n"
            "    elif gap < 0.2:\n"
            "        actions.append({'name': 'damp', 'value': 0.5})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.72})\n"
            "    if state.get('obj', 0.0) > state.get('obj_prev', 0.0) or (state.get('stagnation_count', 0) > 4 and residual > 0.003):\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "PCG":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    ratio = state.get('residual_ratio', 1.0)\n"
            "    residual = state.get('residual_norm', 0.0)\n"
            "    curvature = state.get('direction_curvature', 1.0)\n"
            "    if ratio > 0.55:\n"
            "        actions.append({'name': 'damp', 'value': 0.68})\n"
            "    elif ratio < 0.08 and curvature > 1e-4:\n"
            "        actions.append({'name': 'damp', 'value': 0.98})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.84})\n"
            "    if state.get('stagnation_count', 0) > 2 or residual < 1e-10 or curvature <= 1e-10:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        )
    if algorithm_name == "LNS_REPAIR":
        return (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    fractionality = state.get('fractionality', 0.0)\n"
            "    mip_gap = state.get('mip_gap', 0.0)\n"
            "    incumbent = state.get('incumbent_obj', 0.0)\n"
            "    best_bound = state.get('best_bound', 0.0)\n"
            "    if fractionality > 0.24 and mip_gap > 0.08:\n"
            "        actions.append({'name': 'damp', 'value': 0.92})\n"
            "    elif fractionality < 0.1 and mip_gap < 0.04:\n"
            "        actions.append({'name': 'damp', 'value': 0.58})\n"
            "    else:\n"
            "        actions.append({'name': 'damp', 'value': 0.76})\n"
            "    if incumbent > best_bound * 1.18 and state.get('stagnation_count', 0) > 2:\n"
            "        actions.append({'name': 'restart'})\n"
            "    return {'actions': actions}\n"
        )
    return (
        "def policy(state):\n"
        "    actions = []\n"
        "    actions.append({'name': 'fallback'})\n"
        "    if state.get('obj', 0.0) > state.get('obj_prev', 0.0):\n"
        "        actions.append({'name': 'restart'})\n"
        "    actions.append({'name': 'damp', 'value': 0.8})\n"
        "    return {'actions': actions}\n"
    )
