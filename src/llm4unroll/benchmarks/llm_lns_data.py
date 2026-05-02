from __future__ import annotations

import os
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from llm4unroll.benchmarks.synthetic_lp_qp import ProblemInstance


@dataclass
class ParsedLP:
    name: str
    sense: str
    objective: Dict[str, float]
    constraints: List[Tuple[str, Dict[str, float], str, float]]
    bounds: Dict[str, Tuple[float, float]]
    binaries: List[str] = field(default_factory=list)
    generals: List[str] = field(default_factory=list)


def discover_llm_lns_files(root: str = "data/llm_lns") -> List[str]:
    discovered = []
    for current_root, _, files in os.walk(root):
        for filename in files:
            if filename.endswith(".lp"):
                discovered.append(os.path.join(current_root, filename))
    return sorted(discovered)


def summarize_llm_lns_assets(root: str = "data/llm_lns") -> Dict[str, object]:
    files = discover_llm_lns_files(root)
    expected_families = ("SC_easy_instance", "IS_easy_instance", "MVC_easy_instance", "MIKS_easy_instance")
    summary = {
        "root": root,
        "lp_files": len(files),
        "families": {},
        "real_lp_files": 0,
        "mock_lp_files": 0,
        "real_levels": {"easy": 0, "medium": 0, "hard": 0},
        "data_source": "mock_only",
        "missing_families": [],
        "complete_phase2": True,
    }
    summary["real_lp_files"] = len([path for path in files if any(token in os.path.basename(path) for token in ("_easy_", "_medium_", "_hard_"))])
    for level in ("easy", "medium", "hard"):
        summary["real_levels"][level] = len([path for path in files if ("_%s_" % level) in os.path.basename(path)])
    summary["mock_lp_files"] = len(files) - int(summary["real_lp_files"])
    if summary["real_lp_files"] > 0:
        summary["data_source"] = "milpbench_real"
    for family in expected_families:
        path = os.path.join(root, family, "LP")
        count = len([name for name in os.listdir(path) if name.endswith(".lp")]) if os.path.isdir(path) else 0
        summary["families"][family] = count
        if count == 0:
            summary["missing_families"].append(family)
    summary["complete_phase2"] = len(summary["missing_families"]) == 0
    return summary


def load_llm_lns_instances(family: str, split: str, count: int, seed: int, root: str = "data/llm_lns") -> List[ProblemInstance]:
    family_dir = _family_directory(family, root)
    all_files = sorted(
        os.path.join(family_dir, filename)
        for filename in os.listdir(family_dir)
        if filename.endswith(".lp")
    )
    real_files = [
        path for path in all_files
        if any(token in os.path.basename(path) for token in ("_easy_", "_medium_", "_hard_"))
    ]
    if real_files:
        all_files = real_files
    if not all_files:
        raise FileNotFoundError("No .lp files found under %s" % family_dir)

    selected = _split_files(all_files, split, count, seed)
    instances = []
    for path in selected:
        parsed = parse_lp_file(path)
        instances.append(parsed_lp_to_surrogate(parsed, family))
    return instances


def parse_lp_file(path: str) -> ParsedLP:
    with open(path, "r", encoding="utf-8") as handle:
        raw_lines = [line.strip() for line in handle if line.strip() and not line.strip().startswith("\\")]

    sections: Dict[str, List[str]] = {}
    current = None
    mapping = {
        "minimize": "objective",
        "maximize": "objective",
        "subject to": "constraints",
        "such that": "constraints",
        "bounds": "bounds",
        "binary": "binary",
        "binaries": "binary",
        "general": "general",
        "generals": "general",
        "end": "end",
    }
    sense = "min"
    for line in raw_lines:
        lowered = line.lower()
        if lowered in mapping:
            current = mapping[lowered]
            if lowered == "minimize":
                sense = "min"
            elif lowered == "maximize":
                sense = "max"
            sections.setdefault(current, [])
            continue
        if current:
            sections.setdefault(current, []).append(line)

    objective_lines = sections.get("objective", [])
    objective_expr = " ".join(part.split(":", 1)[1] if ":" in part else part for part in objective_lines)
    objective = _parse_linear_expression(objective_expr)

    constraints = []
    for line in sections.get("constraints", []):
        label, expr = (line.split(":", 1) + [""])[:2] if ":" in line else ("c%d" % len(constraints), line)
        lhs, sense_token, rhs = _split_constraint(expr or label)
        if expr:
            label = label.strip()
        else:
            label = "c%d" % len(constraints)
        constraints.append((label, _parse_linear_expression(lhs), sense_token, float(rhs)))

    binaries = _collect_symbol_block(sections.get("binary", []))
    generals = _collect_symbol_block(sections.get("general", []))
    bounds = {}
    for var in set(objective) | {name for _, coeffs, _, _ in constraints for name in coeffs} | set(binaries) | set(generals):
        bounds[var] = (0.0, 1.0 if var in binaries else 10.0)
    for line in sections.get("bounds", []):
        _apply_bound_line(line, bounds)

    return ParsedLP(
        name=os.path.splitext(os.path.basename(path))[0],
        sense=sense,
        objective=objective,
        constraints=constraints,
        bounds=bounds,
        binaries=binaries,
        generals=generals,
    )


def parsed_lp_to_surrogate(parsed: ParsedLP, family: str) -> ProblemInstance:
    variables = sorted(parsed.bounds)
    index = {name: idx for idx, name in enumerate(variables)}
    a = []
    rhs = []
    sense_list = []
    for _, coeffs, sense_token, bound in parsed.constraints:
        row = [0.0] * len(variables)
        for var, coeff in coeffs.items():
            row[index[var]] = coeff
        a.append(row)
        rhs.append(bound)
        sense_list.append(sense_token)

    c = [parsed.objective.get(var, 0.0) for var in variables]
    if parsed.sense == "max":
        c = [-value for value in c]

    lower = [parsed.bounds[var][0] for var in variables]
    upper = [parsed.bounds[var][1] for var in variables]
    x_star = _greedy_relaxed_solution(a, rhs, sense_list, c, lower, upper)
    surrogate_b = [sum(row[j] * x_star[j] for j in range(len(variables))) for row in a]
    metadata = {
        "source_family": family,
        "original_rhs_mean": sum(rhs) / max(len(rhs), 1),
        "constraint_count": len(a),
    }
    return ProblemInstance(
        name=parsed.name,
        family="pdhg_lp",
        payload={"A": a, "b": surrogate_b, "c": c, "reg": 0.05, "x_star": x_star, "metadata": metadata},
        instance_features={
            "n": float(len(variables)),
            "m": float(len(a)),
            "binary_ratio": float(len(parsed.binaries)) / max(len(variables), 1),
        },
    )


def _family_directory(family: str, root: str) -> str:
    mapping = {
        "llm_lns_sc": os.path.join(root, "SC_easy_instance", "LP"),
        "llm_lns_is": os.path.join(root, "IS_easy_instance", "LP"),
        "llm_lns_mvc": os.path.join(root, "MVC_easy_instance", "LP"),
        "llm_lns_miks": os.path.join(root, "MIKS_easy_instance", "LP"),
    }
    if family not in mapping:
        raise ValueError("Unknown LLM-LNS family: %s" % family)
    path = mapping[family]
    if not os.path.isdir(path):
        raise FileNotFoundError("Expected LLM-LNS directory %s" % path)
    return path


def _split_files(paths: List[str], split: str, count: int, seed: int) -> List[str]:
    shuffled = list(paths)
    random.Random(seed).shuffle(shuffled)
    if len(shuffled) <= count:
        return shuffled
    third = max(1, len(shuffled) // 3)
    if split == "train":
        pool = shuffled[:third]
    elif split == "validation":
        pool = shuffled[third: 2 * third]
    else:
        pool = shuffled[2 * third:]
    if not pool:
        pool = shuffled
    return pool[:count]


def _collect_symbol_block(lines: List[str]) -> List[str]:
    symbols = []
    for line in lines:
        symbols.extend(part for part in line.split() if part)
    return symbols


def _split_constraint(expr: str) -> Tuple[str, str, str]:
    for token in ("<=", ">=", "="):
        if token in expr:
            lhs, rhs = expr.split(token, 1)
            return lhs.strip(), token, rhs.strip()
    raise ValueError("Unsupported constraint expression: %s" % expr)


def _apply_bound_line(line: str, bounds: Dict[str, Tuple[float, float]]) -> None:
    if " free" in line:
        var = line.split()[0]
        bounds[var] = (-10.0, 10.0)
        return
    match = re.match(r"([+\-]?\d+(?:\.\d+)?)\s*<=\s*([A-Za-z_][A-Za-z0-9_]*)\s*<=\s*([+\-]?\d+(?:\.\d+)?)", line)
    if match:
        lower, var, upper = match.groups()
        bounds[var] = (float(lower), float(upper))
        return
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*<=\s*([+\-]?\d+(?:\.\d+)?)", line)
    if match:
        var, upper = match.groups()
        lower = bounds.get(var, (0.0, 10.0))[0]
        bounds[var] = (lower, float(upper))
        return
    match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*>=\s*([+\-]?\d+(?:\.\d+)?)", line)
    if match:
        var, lower = match.groups()
        upper = bounds.get(var, (0.0, 10.0))[1]
        bounds[var] = (float(lower), upper)


def _parse_linear_expression(expr: str) -> Dict[str, float]:
    expr = expr.replace("-", " - ").replace("+", " + ")
    tokens = [token for token in expr.split() if token]
    coeffs: Dict[str, float] = {}
    sign = 1.0
    pending_number = None
    for token in tokens:
        if token == "+":
            sign = 1.0
            pending_number = None
            continue
        if token == "-":
            sign = -1.0
            pending_number = None
            continue
        if re.match(r"^[+\-]?\d+(?:\.\d+)?$", token):
            pending_number = sign * float(token)
            sign = 1.0
            continue
        coeff = pending_number if pending_number is not None else sign * 1.0
        coeffs[token] = coeffs.get(token, 0.0) + coeff
        pending_number = None
        sign = 1.0
    return coeffs


def _greedy_relaxed_solution(
    a: List[List[float]],
    rhs: List[float],
    senses: List[str],
    objective: List[float],
    lower: List[float],
    upper: List[float],
) -> List[float]:
    x = [
        min(max((upper_i if coeff < 0 else lower_i), lower_i), upper_i)
        for coeff, lower_i, upper_i in zip(objective, lower, upper)
    ]
    if not a:
        return [min(max(0.0, x_i), up) for x_i, up in zip(x, upper)]

    preferred = sorted(range(len(objective)), key=lambda idx: objective[idx])
    for row, bound, sense in zip(a, rhs, senses):
        activity = sum(row[j] * x[j] for j in range(len(x)))
        if sense == ">=":
            for j in preferred:
                if activity >= bound - 1e-9:
                    break
                coeff = row[j]
                if coeff <= 0 or x[j] >= upper[j]:
                    continue
                delta = min(upper[j] - x[j], (bound - activity) / max(coeff, 1e-9))
                x[j] += delta
                activity += coeff * delta
        elif sense == "<=":
            for j in reversed(preferred):
                if activity <= bound + 1e-9:
                    break
                coeff = row[j]
                if coeff <= 0 or x[j] <= lower[j]:
                    continue
                delta = min(x[j] - lower[j], (activity - bound) / max(coeff, 1e-9))
                x[j] -= delta
                activity -= coeff * delta
        else:
            target = bound
            for j in preferred:
                coeff = row[j]
                if coeff <= 0:
                    continue
                needed = target - activity
                if abs(needed) <= 1e-9:
                    break
                if needed > 0 and x[j] < upper[j]:
                    delta = min(upper[j] - x[j], needed / coeff)
                    x[j] += delta
                    activity += coeff * delta
    return [min(max(x_i, lower_i), upper_i) for x_i, lower_i, upper_i in zip(x, lower, upper)]
