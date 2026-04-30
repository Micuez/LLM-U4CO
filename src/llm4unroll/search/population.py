from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from llm4unroll.utils import write_csv


@dataclass
class CandidatePolicy:
    policy_id: str
    source: str
    callable_policy: Callable
    origin: str = "manual"
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class CandidateRecord:
    policy_id: str
    origin: str
    score: float
    verified: bool
    problem_family: str
    algorithm: str
    metadata: Dict[str, object] = field(default_factory=dict)


class PopulationArchive:
    def __init__(self) -> None:
        self.records: List[CandidateRecord] = []

    def add(self, record: CandidateRecord) -> None:
        self.records.append(record)

    def top_k(self, k: int = 3) -> List[CandidateRecord]:
        return sorted(self.records, key=lambda item: item.score, reverse=True)[:k]

    def by_origin(self, origin: str) -> List[CandidateRecord]:
        return [record for record in self.records if record.origin == origin]

    def write_csv(self, path: str) -> None:
        write_csv(path, [self._to_row(record) for record in self.records])

    def summary(self) -> Dict[str, object]:
        return {
            "count": len(self.records),
            "top_policy_ids": [record.policy_id for record in self.top_k()],
        }

    @staticmethod
    def _to_row(record: CandidateRecord) -> Dict[str, object]:
        row = {
            "policy_id": record.policy_id,
            "origin": record.origin,
            "score": record.score,
            "verified": record.verified,
            "problem_family": record.problem_family,
            "algorithm": record.algorithm,
        }
        for key, value in record.metadata.items():
            row["meta_%s" % key] = value
        return row
