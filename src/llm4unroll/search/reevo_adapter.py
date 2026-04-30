from __future__ import annotations

from llm4unroll.dsl.transpiler import compile_policy
from llm4unroll.search.population import CandidatePolicy


class ReEvoAdapter:
    def reflect(self, diagnostics):
        return {
            "summary": "Phase 1 reflection placeholder.",
            "diagnostics": diagnostics,
        }

    def propose_revision(self, candidate: CandidatePolicy, diagnostics) -> CandidatePolicy:
        source = candidate.source
        if "0.9" in source:
            source = source.replace("0.9", "0.85", 1)
        return CandidatePolicy(
            policy_id="%s_reflect" % candidate.policy_id,
            source=source,
            callable_policy=compile_policy(source),
            origin="reflection",
            metadata={"diagnostics": str(diagnostics)[:120]},
        )
