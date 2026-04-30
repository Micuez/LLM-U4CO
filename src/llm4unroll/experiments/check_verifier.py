from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table
from llm4unroll.policies import _source_for
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY


def build_verifier_tables() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    variants = ["vanilla", "adaptive", "conservative", "search_variant_1", "search_variant_2"]
    positive_rows: list[dict[str, object]] = []
    negative_rows: list[dict[str, object]] = []

    for algorithm, spec in ALGORITHM_REGISTRY.items():
        for variant in variants:
            try:
                source = _source_for(algorithm, variant)
            except KeyError:
                continue
            result = verify_policy_source(source, spec)
            positive_rows.append({
                "algorithm": algorithm,
                "variant": variant,
                "policy_id": variant,
                "verified": result.ok,
                "feature_coverage": round(result.feature_coverage, 4),
                "proof_count": len(result.proof_obligations),
                "max_actions": result.max_actions_per_path,
                "used_features": ",".join(result.used_features),
                "emitted_actions": ",".join(result.emitted_actions),
                "warnings": " | ".join(result.warnings),
                "primary_proof": result.proof_obligations[0] if result.proof_obligations else "",
                "path_count": len(result.diagnostics.get("paths", [])),
            })

    negative_cases = [
        (
            "missing_fallback",
            "PDHG",
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'scale_tau', 'value': 1.1})\n"
            "    return {'actions': actions}\n",
        ),
        (
            "forbidden_import",
            "ADMM",
            "import os\n"
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    return {'actions': actions}\n",
        ),
        (
            "illegal_feature",
            "PCG",
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    if state.get('sigma', 1.0) > 0.5:\n"
            "        actions.append({'name': 'damp', 'value': 0.8})\n"
            "    return {'actions': actions}\n",
        ),
        (
            "illegal_action",
            "LNS_REPAIR",
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    actions.append({'name': 'set_tau', 'value': 1.0})\n"
            "    return {'actions': actions}\n",
        ),
        (
            "conflicting_actions",
            "PDHG",
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    actions.append({'name': 'set_tau', 'value': 1.0})\n"
            "    actions.append({'name': 'scale_tau', 'value': 0.9})\n"
            "    return {'actions': actions}\n",
        ),
        (
            "wrong_default_kind",
            "PDHG",
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    payload = state.get('instance_features', 0.0)\n"
            "    return {'actions': actions, 'metadata': payload}\n",
        ),
    ]

    for name, algorithm, source in negative_cases:
        result = verify_policy_source(source, ALGORITHM_REGISTRY[algorithm])
        blocked = not result.ok
        negative_rows.append({
            "case_id": name,
            "algorithm": algorithm,
            "status": "BLOCKED" if blocked else "MISSED",
            "blocked_flag": 1 if blocked else 0,
            "error_count": len(result.errors),
            "primary_error": result.errors[0] if result.errors else "",
            "all_errors": " | ".join(result.errors),
        })

    write_phase1_table("results/tables/verifier_positive.csv", positive_rows)
    write_phase1_table("results/tables/verifier_negative.csv", negative_rows)
    write_markdown_summary("results/tables/verifier_positive.md", "Verifier Positive Cases", positive_rows)
    write_markdown_summary("results/tables/verifier_negative.md", "Verifier Negative Cases", negative_rows)
    return positive_rows, negative_rows


def main():
    positive_rows, negative_rows = build_verifier_tables()
    passed = len([row for row in positive_rows if bool(row["verified"])])
    total = len(positive_rows)
    blocked = len([row for row in negative_rows if int(row["blocked_flag"]) == 1])

    for row in positive_rows:
        print(
            "%s %s/%s actions=%s features=%s coverage=%.2f max_actions=%d" % (
                "PASS" if bool(row["verified"]) else "FAIL",
                row["algorithm"],
                row["variant"],
                row["emitted_actions"],
                row["used_features"],
                float(row["feature_coverage"]),
                int(row["max_actions"]),
            )
        )
        if row["primary_proof"]:
            print("  proof: %s" % row["primary_proof"])

    for row in negative_rows:
        print("%s negative/%s errors=%s" % (row["status"], row["case_id"], row["all_errors"]))

    print("Verifier summary: positive_pass=%d/%d negative_blocked=%d/%d" % (passed, total, blocked, len(negative_rows)))


if __name__ == "__main__":
    main()
