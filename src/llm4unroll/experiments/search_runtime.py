from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.report import write_candidate_archive, write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.evaluator.smoke_test import run_policy_smoke_test
from llm4unroll.search.population import CandidateRecord


def evaluate_candidate(candidate, spec, evaluator, budget, algorithm_name, problem_family, split, rows, archive, smoke_instance, smoke_budget):
    verification = verify_policy_source(candidate.source, spec)
    smoke = run_policy_smoke_test(
        runner=evaluator.algorithm_runner,
        instance=smoke_instance,
        policy=candidate.callable_policy,
        budget=smoke_budget,
    ) if verification.ok else None
    result = evaluator.evaluate(
        policy=candidate.callable_policy,
        budget=budget,
        policy_id=candidate.policy_id,
        policy_source=candidate.source,
    ) if verification.ok and smoke is not None and smoke.ok else None
    row = {
        "algorithm": algorithm_name,
        "policy_id": candidate.policy_id,
        "verified": verification.ok,
        "smoke_ok": None if smoke is None else smoke.ok,
        "smoke_reason": "" if smoke is None else smoke.reason,
        "errors": " | ".join(verification.errors),
        "warnings": " | ".join(verification.warnings),
        "feature_coverage": round(verification.feature_coverage, 4),
        "proof_count": len(verification.proof_obligations),
        "score": round(result.score, 6) if result else None,
        "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
        "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
        "origin": candidate.origin,
        "parent": candidate.metadata.get("parent", ""),
    }
    rows.append(row)
    archive.add(CandidateRecord(
        policy_id=candidate.policy_id,
        origin=candidate.origin,
        score=float(result.score if result else -1e9),
        verified=verification.ok,
        problem_family=problem_family,
        algorithm=algorithm_name,
        metadata={"split": split, "parent": candidate.metadata.get("parent", "")},
    ))
    write_candidate_archive("results/candidates/search_%s_%s_%s.txt" % (
        algorithm_name.lower(),
        problem_family,
        candidate.policy_id,
    ), {
        "policy_id": candidate.policy_id,
        "problem_family": problem_family,
        "verified": verification.ok,
        "smoke_ok": None if smoke is None else smoke.ok,
        "smoke_reason": "" if smoke is None else smoke.reason,
        "smoke_diagnostics": {} if smoke is None else smoke.diagnostics,
        "errors": verification.errors,
        "warnings": verification.warnings,
        "feature_coverage": verification.feature_coverage,
        "proof_obligations": verification.proof_obligations,
        "source": candidate.source,
        "origin": candidate.origin,
        "parent": candidate.metadata.get("parent", ""),
        "score": None if result is None else result.score,
    })
    return verification, result


def write_search_outputs(output_stub: str, summary_title: str, rows, archive) -> None:
    output_path = "results/tables/%s.csv" % output_stub
    archive_path = "results/tables/%s_archive.csv" % output_stub
    write_phase1_table(output_path, rows)
    archive.write_csv(archive_path)
    write_table_chart(output_path)
    write_table_chart(archive_path)
    write_markdown_summary(output_path[:-4] + ".md", summary_title, rows)
