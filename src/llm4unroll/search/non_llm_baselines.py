from __future__ import annotations

import random
from typing import Iterable, List

from llm4unroll.dsl.transpiler import compile_policy
from llm4unroll.search.population import CandidatePolicy


class NonLLMBaselineFactory:
    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)

    def random_mutation(
        self,
        algorithm_name: str,
        parent: CandidatePolicy,
        policy_id: str,
        origin: str,
    ) -> CandidatePolicy:
        source = parent.source
        replacements = _mutation_specs(algorithm_name)
        changed = False
        for token, lower, upper, digits in replacements:
            if token not in source:
                continue
            mutated = _format_float(self.rng.uniform(lower, upper), digits)
            if mutated == token:
                continue
            source = source.replace(token, mutated, 1)
            changed = True
        if not changed:
            source = source.replace("0.9", _format_float(self.rng.uniform(0.78, 0.98), 2), 1)
        return CandidatePolicy(
            policy_id=policy_id,
            source=source,
            callable_policy=compile_policy(source),
            origin=origin,
            metadata={"parent": parent.policy_id},
        )

    def random_walk(
        self,
        algorithm_name: str,
        parents: Iterable[CandidatePolicy],
        policy_id: str,
        origin: str,
        min_depth: int = 1,
        max_depth: int = 3,
    ) -> CandidatePolicy:
        parent_list: List[CandidatePolicy] = list(parents)
        if not parent_list:
            raise ValueError("random_walk requires at least one parent policy")
        current = self.rng.choice(parent_list)
        lineage = [current.policy_id]
        depth = self.rng.randint(min_depth, max_depth)
        candidate = current
        for step in range(depth):
            candidate = self.random_mutation(
                algorithm_name=algorithm_name,
                parent=candidate,
                policy_id="%s_s%d" % (policy_id, step),
                origin=origin,
            )
            lineage.append(candidate.metadata.get("parent", ""))
        candidate.policy_id = policy_id
        candidate.origin = origin
        candidate.metadata["seed_parent"] = current.policy_id
        candidate.metadata["lineage_depth"] = depth
        candidate.metadata["lineage"] = "->".join(item for item in lineage if item)
        return candidate


def _format_float(value: float, digits: int) -> str:
    text = ("%0." + str(digits) + "f") % value
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _mutation_specs(algorithm_name: str):
    recipes = {
        "PDHG": [
            ("1.12", 1.03, 1.22, 2),
            ("0.9", 0.78, 0.97, 2),
            ("0.7", 0.6, 0.85, 2),
            ("0.85", 0.78, 0.96, 2),
            ("1.15", 1.0, 1.26, 2),
            ("1.02", 0.95, 1.1, 2),
        ],
        "ADMM": [
            ("1.18", 1.02, 1.28, 2),
            ("0.88", 0.78, 0.96, 2),
            ("0.8", 0.68, 0.92, 2),
            ("1.2", 1.05, 1.32, 2),
            ("0.97", 0.86, 1.02, 2),
        ],
        "FISTA": [
            ("0.92", 0.82, 0.98, 2),
            ("0.6", 0.45, 0.82, 2),
            ("0.35", 0.15, 0.55, 2),
            ("0.96", 0.86, 0.99, 2),
            ("0.85", 0.7, 0.95, 2),
        ],
        "ALM": [
            ("1.25", 1.05, 1.4, 2),
            ("0.92", 0.8, 1.02, 2),
            ("0.8", 0.65, 1.0, 2),
            ("1.3", 1.08, 1.45, 2),
            ("1.1", 0.9, 1.25, 2),
            ("0.9", 0.74, 0.98, 2),
        ],
        "DRS": [
            ("0.9", 0.78, 0.98, 2),
            ("0.65", 0.48, 0.82, 2),
            ("0.8", 0.65, 0.92, 2),
            ("0.95", 0.82, 0.99, 2),
            ("0.55", 0.4, 0.72, 2),
            ("0.78", 0.62, 0.88, 2),
        ],
        "PCG": [
            ("0.75", 0.6, 0.9, 2),
            ("1.0", 0.92, 1.08, 2),
            ("0.9", 0.75, 0.98, 2),
            ("0.72", 0.55, 0.84, 2),
            ("0.6", 0.45, 0.75, 2),
        ],
        "LNS_REPAIR": [
            ("1.0", 0.88, 1.08, 2),
            ("0.85", 0.72, 0.96, 2),
            ("0.7", 0.56, 0.84, 2),
            ("0.98", 0.86, 1.05, 2),
            ("0.62", 0.48, 0.78, 2),
            ("0.84", 0.7, 0.94, 2),
        ],
    }
    return recipes.get(algorithm_name, [("0.9", 0.78, 0.98, 2)])
