from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProblemInstance:
    name: str
    family: str
    payload: Dict[str, object]
    instance_features: Dict[str, float] = field(default_factory=dict)


def _rand_matrix(rng: random.Random, m: int, n: int, scale: float = 1.0) -> List[List[float]]:
    return [[scale * (rng.random() - 0.5) for _ in range(n)] for _ in range(m)]


def build_synthetic_instances(family: str, split: str, count: int, seed: int) -> List[ProblemInstance]:
    rng = random.Random(seed + _split_offset(split))
    builders = {
        "pdhg_lp": _build_pdhg_lp,
        "admm_qp": _build_admm_qp,
        "fista_lasso": _build_fista_lasso,
        "setcover_relaxation": _build_setcover_relaxation,
        "alm_eq_qp": _build_alm_eq_qp,
        "drs_feasibility": _build_drs_feasibility,
        "pcg_linear_system": _build_pcg_linear_system,
        "lns_repair_cover": _build_lns_repair_cover,
    }
    if family not in builders:
        raise ValueError("Unknown synthetic family: %s" % family)
    return [builders[family](rng, idx, split) for idx in range(count)]


def _split_offset(split: str) -> int:
    return {"train": 0, "validation": 10_000, "test": 20_000}.get(split, 30_000)


def _build_pdhg_lp(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 12 if split == "train" else 20 if split == "validation" else 28
    m = max(4, n // 3)
    x_star = [0.3 + rng.random() for _ in range(n)]
    y_star = [rng.random() - 0.5 for _ in range(m)]
    a = _rand_matrix(rng, m, n, scale=0.8)
    b = [sum(a_i_j * x_j for a_i_j, x_j in zip(row, x_star)) for row in a]
    reg = 0.1
    at_y = [sum(a[i][j] * y_star[i] for i in range(m)) for j in range(n)]
    c = [-(reg * x_star[j] + at_y[j]) for j in range(n)]
    return ProblemInstance(
        name="pdhg_%s_%02d" % (split, idx),
        family="pdhg_lp",
        payload={"A": a, "b": b, "c": c, "reg": reg, "x_star": x_star},
        instance_features={"n": float(n), "m": float(m), "density": 1.0},
    )


def _build_admm_qp(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 16 if split == "train" else 24 if split == "validation" else 32
    x_star = [(rng.random() - 0.5) * 1.2 for _ in range(n)]
    diag_q = [0.5 + rng.random() * 2.0 for _ in range(n)]
    q = [-diag_q[i] * x_star[i] for i in range(n)]
    return ProblemInstance(
        name="admm_%s_%02d" % (split, idx),
        family="admm_qp",
        payload={"diag_q": diag_q, "q": q, "lower": -1.0, "upper": 1.0, "x_star": x_star},
        instance_features={"n": float(n), "box_width": 2.0},
    )


def _build_fista_lasso(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 18 if split == "train" else 28 if split == "validation" else 36
    m = n + n // 2
    a = _rand_matrix(rng, m, n, scale=0.4)
    x_true = [0.0] * n
    for pos in range(max(2, n // 6)):
        x_true[pos] = (rng.random() - 0.5) * 2.0
    noise = [0.01 * (rng.random() - 0.5) for _ in range(m)]
    b = [sum(a_i_j * x_j for a_i_j, x_j in zip(row, x_true)) + noise_i for row, noise_i in zip(a, noise)]
    lam = 0.08
    return ProblemInstance(
        name="fista_%s_%02d" % (split, idx),
        family="fista_lasso",
        payload={"A": a, "b": b, "lambda": lam, "x_true": x_true},
        instance_features={"n": float(n), "m": float(m), "sparsity": float(sum(1 for x in x_true if x == 0.0)) / n},
    )


def _build_setcover_relaxation(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    rows = 10 if split == "train" else 15 if split == "validation" else 20
    cols = 20 if split == "train" else 28 if split == "validation" else 36
    matrix = []
    for _ in range(rows):
        row = [1.0 if rng.random() < 0.25 else 0.0 for _ in range(cols)]
        if sum(row) == 0:
            row[rng.randrange(cols)] = 1.0
        matrix.append(row)
    costs = [0.2 + rng.random() for _ in range(cols)]
    # Reuse the PDHG runner on an equality-style relaxation after creating a feasible target.
    x_star = [0.0] * cols
    for j in range(cols):
        if rng.random() < 0.15:
            x_star[j] = 0.5 + 0.5 * rng.random()
    b = [sum(row[j] * x_star[j] for j in range(cols)) for row in matrix]
    return ProblemInstance(
        name="setcover_%s_%02d" % (split, idx),
        family="pdhg_lp",
        payload={"A": matrix, "b": b, "c": costs, "reg": 0.05, "x_star": x_star},
        instance_features={"n": float(cols), "m": float(rows), "density": 0.25},
    )


def _build_alm_eq_qp(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 12 if split == "train" else 18 if split == "validation" else 24
    m = max(3, n // 4)
    x_star = [(rng.random() - 0.5) * 1.0 for _ in range(n)]
    a = _rand_matrix(rng, m, n, scale=0.5)
    b = [sum(row[j] * x_star[j] for j in range(n)) for row in a]
    reg = 0.8
    c = [-reg * value for value in x_star]
    return ProblemInstance(
        name="alm_%s_%02d" % (split, idx),
        family="alm_eq_qp",
        payload={"A": a, "b": b, "c": c, "reg": reg, "x_star": x_star},
        instance_features={"n": float(n), "m": float(m)},
    )


def _build_drs_feasibility(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 10 if split == "train" else 16 if split == "validation" else 22
    m = max(2, n // 5)
    x_star = [0.2 + 0.6 * rng.random() for _ in range(n)]
    a = _rand_matrix(rng, m, n, scale=0.4)
    b = [sum(row[j] * x_star[j] for j in range(n)) for row in a]
    return ProblemInstance(
        name="drs_%s_%02d" % (split, idx),
        family="drs_feasibility",
        payload={"A": a, "b": b, "x_star": x_star, "lower": 0.0, "upper": 1.0},
        instance_features={"n": float(n), "m": float(m)},
    )


def _build_pcg_linear_system(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    n = 14 if split == "train" else 20 if split == "validation" else 28
    base = _rand_matrix(rng, n, n, scale=0.25)
    h = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            value = sum(base[k][i] * base[k][j] for k in range(n))
            h[i][j] = value + (1.0 if i == j else 0.0)
    x_star = [(rng.random() - 0.5) * 0.8 for _ in range(n)]
    rhs = [sum(h[i][j] * x_star[j] for j in range(n)) for i in range(n)]
    return ProblemInstance(
        name="pcg_%s_%02d" % (split, idx),
        family="pcg_linear_system",
        payload={"H": h, "rhs": rhs, "x_star": x_star},
        instance_features={"n": float(n)},
    )


def _build_lns_repair_cover(rng: random.Random, idx: int, split: str) -> ProblemInstance:
    rows = 8 if split == "train" else 12 if split == "validation" else 16
    cols = 14 if split == "train" else 20 if split == "validation" else 26
    cover = []
    for _ in range(rows):
        row = [1.0 if rng.random() < 0.3 else 0.0 for _ in range(cols)]
        if sum(row) == 0:
            row[rng.randrange(cols)] = 1.0
        cover.append(row)
    costs = [0.5 + rng.random() for _ in range(cols)]
    x_star = [0.0] * cols
    for i in range(cols):
        if rng.random() < 0.2:
            x_star[i] = 1.0
    for row in cover:
        if sum(row[j] * x_star[j] for j in range(cols)) < 1.0:
            picks = [j for j in range(cols) if row[j] > 0]
            x_star[min(picks, key=lambda j: costs[j])] = 1.0
    fractional_target = [0.85 * value + 0.15 * rng.random() for value in x_star]
    return ProblemInstance(
        name="lns_%s_%02d" % (split, idx),
        family="lns_repair_cover",
        payload={
            "cover_matrix": cover,
            "costs": costs,
            "x_star": x_star,
            "fractional_target": fractional_target,
        },
        instance_features={"n": float(cols), "m": float(rows)},
    )
