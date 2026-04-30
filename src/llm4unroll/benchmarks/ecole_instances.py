from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class EcoleInstanceDescriptor:
    family: str
    size: str
    metadata: Dict[str, object]


def build_ecole_descriptors() -> List[EcoleInstanceDescriptor]:
    return [
        EcoleInstanceDescriptor("setcover", "small", {"rows": 32, "cols": 64}),
        EcoleInstanceDescriptor("indset", "small", {"nodes": 48, "edge_prob": 0.1}),
    ]
