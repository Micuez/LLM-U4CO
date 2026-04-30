from __future__ import annotations

import math
from typing import Iterable, List


def zeros(n: int) -> List[float]:
    return [0.0] * n


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def add(a: Iterable[float], b: Iterable[float]) -> List[float]:
    return [x + y for x, y in zip(a, b)]


def sub(a: Iterable[float], b: Iterable[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def scale(a: Iterable[float], alpha: float) -> List[float]:
    return [alpha * x for x in a]


def norm2(a: Iterable[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def matvec(matrix: List[List[float]], vector: List[float]) -> List[float]:
    return [dot(row, vector) for row in matrix]


def t_matvec(matrix: List[List[float]], vector: List[float]) -> List[float]:
    if not matrix:
        return []
    cols = len(matrix[0])
    result = [0.0] * cols
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            result[j] += value * vector[i]
    return result


def soft_threshold(vector: List[float], lam: float) -> List[float]:
    out = []
    for value in vector:
        if value > lam:
            out.append(value - lam)
        elif value < -lam:
            out.append(value + lam)
        else:
            out.append(0.0)
    return out


def clip(vector: List[float], lower: float, upper: float) -> List[float]:
    return [max(lower, min(upper, value)) for value in vector]
