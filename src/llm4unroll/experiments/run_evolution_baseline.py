from __future__ import annotations

from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.experiments.search_runtime import evaluate_candidate, write_search_outputs
from llm4unroll.policies import build_search_candidates
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.search.non_llm_baselines import NonLLMBaselineFactory
from llm4unroll.search.population import PopulationArchive


def main():
    args = parse_args("Run llm4unroll non-LLM evolutionary baseline.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    algorithm_name = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    evaluator = OptimisationEvaluator(runner, instances)
    spec = ALGORITHM_REGISTRY[algorithm_name]
    smoke_instance = make_instances(
        problem_family,
        "train",
        1,
        int(config.get("seed", 0)) + 97,
        dataset_cfg=config.get("dataset", {}),
    )[0]
    smoke_budget = type(budget)(max_iters=max(3, min(8, budget.max_iters // 4 or 3)), time_limit_s=min(0.5, budget.time_limit_s))
    archive = PopulationArchive()
    rows = []
    candidate_by_id = {}
    factory = NonLLMBaselineFactory(int(config.get("seed", 0)) + 503)
    evo_cfg = config.get("evolution_baseline", {})
    generations = int(evo_cfg.get("generations", 2))
    children_per_parent = int(evo_cfg.get("children_per_parent", 2))
    top_k = int(evo_cfg.get("top_k", 2))

    for candidate in build_search_candidates(algorithm_name):
        verification, result = evaluate_candidate(
            candidate, spec, evaluator, budget, algorithm_name, problem_family, args.split, rows, archive, smoke_instance, smoke_budget
        )
        if verification.ok and result is not None:
            candidate_by_id[candidate.policy_id] = candidate

    for generation in range(1, generations + 1):
        parents = [record for record in archive.top_k(max(top_k * 2, top_k)) if record.verified and record.score > -1e8]
        parents = parents[:top_k]
        if not parents:
            break
        for parent_rank, parent_record in enumerate(parents):
            parent = candidate_by_id.get(parent_record.policy_id)
            if parent is None:
                continue
            for child_idx in range(children_per_parent):
                candidate = factory.random_mutation(
                    algorithm_name=algorithm_name,
                    parent=parent,
                    policy_id="evo_g%02d_p%02d_c%02d" % (generation, parent_rank, child_idx),
                    origin="evolution_no_llm",
                )
                verification, result = evaluate_candidate(
                    candidate, spec, evaluator, budget, algorithm_name, problem_family, args.split, rows, archive, smoke_instance, smoke_budget
                )
                if verification.ok and result is not None:
                    candidate_by_id[candidate.policy_id] = candidate

    output_stub = "evolution_no_llm_%s_%s_%s" % (algorithm_name.lower(), problem_family, args.split)
    write_search_outputs(output_stub, "Evolution Without LLM Summary", rows, archive)
    print("Saved evolution baseline results to results/tables/%s.csv" % output_stub)


if __name__ == "__main__":
    main()
