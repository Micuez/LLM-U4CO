from __future__ import annotations

from llm4unroll.dsl.verifier import verify_policy_source
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart
from llm4unroll.experiments.common import bootstrap, parse_args
from llm4unroll.policies import build_baseline_policies, build_search_candidates
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY


def main():
    args = parse_args("Run llm4unroll ablations.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    evaluator = OptimisationEvaluator(runner, instances)
    spec = ALGORITHM_REGISTRY[str(config["algorithm"])]
    rows = []

    for candidate in build_baseline_policies(str(config["algorithm"])):
        verification = verify_policy_source(candidate.source, spec)
        result = evaluator.evaluate(candidate.callable_policy, budget, candidate.policy_id, candidate.source) if verification.ok else None
        rows.append({
            "family": config["problem_family"],
            "split": args.split,
            "variant": "baseline",
            "policy_id": candidate.policy_id,
            "verified": verification.ok,
            "errors": " | ".join(verification.errors),
            "feature_coverage": round(verification.feature_coverage, 4),
            "score": round(result.score, 6) if result else None,
            "median_gap": round(result.aggregate["median_gap"], 6) if result else None,
            "fail_rate": round(result.aggregate["fail_rate"], 6) if result else None,
        })

    for candidate in build_search_candidates(str(config["algorithm"])):
        verification = verify_policy_source(candidate.source, spec)
        if verification.ok:
            result = evaluator.evaluate(candidate.callable_policy, budget, candidate.policy_id, candidate.source)
            score = round(result.score, 6)
            gap = round(result.aggregate["median_gap"], 6)
            fail_rate = round(result.aggregate["fail_rate"], 6)
        else:
            score = None
            gap = None
            fail_rate = None
        rows.append({
            "family": config["problem_family"],
            "split": args.split,
            "variant": "search",
            "policy_id": candidate.policy_id,
            "verified": verification.ok,
            "errors": " | ".join(verification.errors),
            "feature_coverage": round(verification.feature_coverage, 4),
            "score": score,
            "median_gap": gap,
            "fail_rate": fail_rate,
        })

    out = "results/tables/ablation_%s_%s_%s.csv" % (str(config["algorithm"]).lower(), str(config["problem_family"]), args.split)
    write_phase1_table(out, rows)
    write_table_chart(out)
    write_markdown_summary(out[:-4] + ".md", "Ablation Summary", rows)
    print("Saved ablation table to %s" % out)


if __name__ == "__main__":
    main()
