from __future__ import annotations

import ast
import csv
import os
import random
from typing import Any, Dict, Iterable, List


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def seed_everything(seed: int) -> None:
    random.seed(seed)


def is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and value == value and value not in (float("inf"), float("-inf"))


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def median(values: Iterable[float], default: float = float("inf")) -> float:
    filtered = sorted(v for v in values if is_finite_number(v))
    if not filtered:
        return default
    mid = len(filtered) // 2
    if len(filtered) % 2:
        return filtered[mid]
    return 0.5 * (filtered[mid - 1] + filtered[mid])


def mean(values: Iterable[float], default: float = float("inf")) -> float:
    vals = [v for v in values if is_finite_number(v)]
    if not vals:
        return default
    return sum(vals) / len(vals)


def write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    ensure_dir(os.path.dirname(path))
    headers = sorted({key for row in rows for key in row})
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def dump_text(path: str, text: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def load_simple_yaml(path: str) -> Dict[str, Any]:
    """Parse the limited YAML used by the bundled configs.

    Supported:
    - nested dicts by indentation
    - numbers, booleans, strings
    - inline lists like [a, b, c]
    """

    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    root: Dict[str, Any] = {}
    stack = [(-1, root)]

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        key, sep, value = stripped.partition(":")
        if not sep:
            raise ValueError("Invalid config line: %s" % stripped)

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        key = key.strip()
        value = value.strip()
        if not value:
            parent[key] = {}
            stack.append((indent, parent[key]))
            continue
        parent[key] = _parse_scalar(value)
    return root


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    try:
        return ast.literal_eval(value)
    except Exception:
        return value.strip("'\"")
