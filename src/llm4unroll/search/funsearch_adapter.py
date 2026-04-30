from __future__ import annotations

from typing import List, Tuple

from llm4unroll.dsl.transpiler import compile_policy
from llm4unroll.search.population import CandidatePolicy


class FunSearchAdapter:
    """A tiny deterministic mutator for small benchmark experiments."""

    def mutate_thresholds(self, candidate: CandidatePolicy, suffix: str, replacements):
        source = candidate.source
        for old, new in replacements:
            source = source.replace(old, new)
        return CandidatePolicy(
            policy_id="%s_%s" % (candidate.policy_id, suffix),
            source=source,
            callable_policy=compile_policy(source),
            origin="funsearch_mutation",
            metadata={"parent": candidate.policy_id},
        )

    def second_generation(self, algorithm_name: str, candidate: CandidatePolicy) -> CandidatePolicy:
        replacements = _mutation_recipe(algorithm_name, candidate.policy_id)
        return self.mutate_thresholds(candidate, "g2", replacements)

    def mutate_top_parent(self, algorithm_name: str, candidate: CandidatePolicy, rank: int) -> CandidatePolicy:
        replacements = _top_parent_recipe(algorithm_name, rank)
        return self.mutate_thresholds(candidate, "top%d" % rank, replacements)


def _mutation_recipe(algorithm_name: str, policy_id: str) -> List[Tuple[str, str]]:
    recipes = {
        "ALM": {
            "search_variant_1": [
                ("0.08", "0.06"),
                ("1.3", "1.22"),
                ("0.9", "0.94"),
                ("1.1", "0.95"),
            ],
            "search_variant_2": [
                ("0.12", "0.09"),
                ("1.6", "1.35"),
                ("0.82", "0.88"),
                ("0.78", "0.84"),
            ],
        },
        "DRS": {
            "search_variant_1": [
                ("0.01", "0.008"),
                ("0.95", "0.88"),
                ("0.55", "0.6"),
                ("0.78", "0.74"),
            ],
            "search_variant_2": [
                ("0.02", "0.016"),
                ("0.98", "0.9"),
                ("0.5", "0.58"),
                ("0.72", "0.68"),
            ],
        },
        "PCG": {
            "search_variant_1": [
                ("0.82", "0.7"),
                ("0.72", "0.8"),
                ("0.18", "0.12"),
                ("0.9", "0.94"),
            ],
            "search_variant_2": [
                ("0.55", "0.45"),
                ("0.68", "0.74"),
                ("0.98", "1.0"),
                ("0.84", "0.9"),
            ],
        },
        "LNS_REPAIR": {
            "search_variant_1": [
                ("0.18", "0.14"),
                ("0.98", "0.9"),
                ("0.08", "0.06"),
                ("0.84", "0.8"),
            ],
            "search_variant_2": [
                ("0.24", "0.2"),
                ("0.92", "0.86"),
                ("0.58", "0.64"),
                ("1.18", "1.12"),
            ],
        },
    }
    return recipes.get(algorithm_name, {}).get(policy_id, [("0.9", "0.87")])


def _top_parent_recipe(algorithm_name: str, rank: int) -> List[Tuple[str, str]]:
    recipes = {
        "ALM": [
            [("1.25", "1.18"), ("0.92", "0.95"), ("0.8", "0.9"), ("0.85", "0.9")],
            [("1.25", "1.32"), ("0.92", "0.88"), ("0.8", "1.05"), ("0.85", "0.8")],
        ],
        "DRS": [
            [("0.9", "0.86"), ("0.65", "0.6"), ("0.8", "0.74"), ("0.55", "0.58")],
            [("0.9", "0.93"), ("0.65", "0.55"), ("0.8", "0.7"), ("0.55", "0.52")],
        ],
        "PCG": [
            [("0.75", "0.82"), ("1.0", "0.98"), ("0.9", "0.94"), ("0.35", "0.42")],
            [("0.75", "0.68"), ("1.0", "1.0"), ("0.9", "0.88"), ("0.35", "0.28")],
        ],
        "LNS_REPAIR": [
            [("1.0", "0.94"), ("0.85", "0.8"), ("0.7", "0.66"), ("0.05", "0.08")],
            [("1.0", "0.98"), ("0.85", "0.88"), ("0.7", "0.74"), ("0.05", "0.03")],
        ],
    }
    indexed = recipes.get(algorithm_name, [[("0.9", "0.88")], [("0.9", "0.92")]])
    idx = 0 if rank <= 1 else 1
    return indexed[idx]
