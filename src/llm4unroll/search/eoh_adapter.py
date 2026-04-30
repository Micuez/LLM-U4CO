from __future__ import annotations

from typing import List

from llm4unroll.search.population import CandidatePolicy


class EoHAdapter:
    def __init__(self, templates):
        self.templates = templates

    def seed_population(self) -> List[CandidatePolicy]:
        return list(self.templates)

    def evolve_population(self) -> List[CandidatePolicy]:
        evolved = []
        for candidate in self.templates:
            evolved.append(candidate)
        return evolved
