from __future__ import annotations

from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.experiments.search_runtime import evaluate_candidate, write_search_outputs
from llm4unroll.policies import build_search_candidates
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.search.non_llm_baselines import NonLLMBaselineFactory
from llm4unroll.search.population import PopulationArchive


def main():
    args = parse_args("Run llm4unroll random-search baseline.")
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
    seeds = build_search_candidates(algorithm_name)
    factory = NonLLMBaselineFactory(int(config.get("seed", 0)) + 211)

    for candidate in seeds:
        evaluate_candidate(
            candidate, spec, evaluator, budget, algorithm_name, problem_family, args.split, rows, archive, smoke_instance, smoke_budget
        )

    num_random = int(config.get("random_search", {}).get("num_candidates", 8))
    depth_min = int(config.get("random_search", {}).get("min_depth", 1))
    depth_max = int(config.get("random_search", {}).get("max_depth", 3))
    for index in range(num_random):
        candidate = factory.random_walk(
            algorithm_name=algorithm_name,
            parents=seeds,
            policy_id="random_%02d" % index,
            origin="random_search",
            min_depth=depth_min,
            max_depth=max(depth_min, depth_max),
        )
        evaluate_candidate(
            candidate, spec, evaluator, budget, algorithm_name, problem_family, args.split, rows, archive, smoke_instance, smoke_budget
        )

    output_stub = "random_search_%s_%s_%s" % (algorithm_name.lower(), problem_family, args.split)
    write_search_outputs(output_stub, "Random Search Summary", rows, archive)
    print("Saved random-search results to results/tables/%s.csv" % output_stub)


if __name__ == "__main__":
    main()
