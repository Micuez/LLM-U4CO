from __future__ import annotations

import re

from llm4unroll.dsl.transpiler import compile_policy
from llm4unroll.evaluator.optimisation_evaluator import OptimisationEvaluator
from llm4unroll.experiments.common import bootstrap, make_instances, parse_args
from llm4unroll.experiments.search_runtime import evaluate_candidate, write_search_outputs
from llm4unroll.policies import build_search_candidates
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.search.funsearch_adapter import FunSearchAdapter
from llm4unroll.search.llm_client import NullLLMClient, build_llm_client
from llm4unroll.search.population import PopulationArchive
from llm4unroll.search.prompts import SYSTEM_PROMPT, build_generation_prompt
from llm4unroll.search.reevo_adapter import ReEvoAdapter
from llm4unroll.search.population import CandidatePolicy


def _extract_policy_code(text: str) -> str:
    fence = re.search(r"```(?:python)?\s*(def\s+policy\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:.*?)(?:```|\Z)", text, re.DOTALL)
    if fence:
        return fence.group(1).strip() + "\n"
    start = re.search(r"def\s+policy\s*\(", text)
    if start:
        return text[start.start():].strip() + "\n"
    return text.strip() + "\n"


def _maybe_generate_llm_candidate(llm_cfg, algorithm_name, problem_family, spec, policy_id, parent_source="", diagnostics=""):
    if not llm_cfg:
        return None
    provider = str(llm_cfg.get("provider", "null"))
    if provider == "null":
        return None
    client = build_llm_client(llm_cfg)
    if isinstance(client, NullLLMClient):
        return None
    prompt = build_generation_prompt(
        algorithm_name=algorithm_name,
        problem_family=problem_family,
        spec=spec,
        parent_source=parent_source,
        diagnostics=diagnostics,
    )
    raw = client.generate(
        SYSTEM_PROMPT,
        prompt,
        temperature=float(llm_cfg.get("temperature", 0.2)),
        max_tokens=int(llm_cfg.get("max_tokens", 800)),
    )
    source = _extract_policy_code(raw)
    return CandidatePolicy(
        policy_id=policy_id,
        source=source,
        callable_policy=compile_policy(source),
        origin="llm_generated",
        metadata={"parent": policy_id.rsplit("_", 1)[0] if "_" in policy_id else ""},
    )


def main():
    args = parse_args("Run llm4unroll search.")
    config, runner, budget, instances = bootstrap(args.config, split=args.split)
    algorithm_name = str(config["algorithm"])
    problem_family = str(config["problem_family"])
    llm_cfg = config.get("llm", {})
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
    rows = []
    archive = PopulationArchive()
    funsearch = FunSearchAdapter()
    reevo = ReEvoAdapter()
    base_candidates = build_search_candidates(algorithm_name)
    llm_seed = _maybe_generate_llm_candidate(
        llm_cfg=llm_cfg,
        algorithm_name=algorithm_name,
        problem_family=problem_family,
        spec=spec,
        policy_id="llm_seed",
    )
    if llm_seed is not None:
        base_candidates.append(llm_seed)
    evaluated = []
    for candidate in base_candidates:
        verification, result = evaluate_candidate(
            candidate,
            spec,
            evaluator,
            budget,
            algorithm_name,
            problem_family,
            args.split,
            rows,
            archive,
            smoke_instance,
            smoke_budget,
        )
        evaluated.append((candidate, verification, result))

    second_generation = []
    for candidate, verification, result in evaluated:
        if candidate.policy_id in {"search_variant_1", "search_variant_2"} and verification.ok:
            mutated = funsearch.second_generation(algorithm_name, candidate)
            second_generation.append(mutated)
        if candidate.policy_id == "search_seed" and verification.ok and result is not None:
            reflection = reevo.propose_revision(candidate, result.aggregate)
            reflection.policy_id = "search_seed_reflect"
            reflection.metadata["parent"] = candidate.policy_id
            second_generation.append(reflection)
        if candidate.policy_id == "llm_seed" and verification.ok and result is not None:
            llm_reflect = _maybe_generate_llm_candidate(
                llm_cfg=llm_cfg,
                algorithm_name=algorithm_name,
                problem_family=problem_family,
                spec=spec,
                policy_id="llm_seed_reflect",
                parent_source=candidate.source,
                diagnostics=str(result.aggregate),
            )
            if llm_reflect is not None:
                llm_reflect.metadata["parent"] = candidate.policy_id
                second_generation.append(llm_reflect)

    for candidate in second_generation:
        evaluate_candidate(
            candidate,
            spec,
            evaluator,
            budget,
            algorithm_name,
            problem_family,
            args.split,
            rows,
            archive,
            smoke_instance,
            smoke_budget,
        )

    # One more half-step: automatically select the top-2 scored parents from the
    # candidates seen so far, then generate another mutation from each.
    seen = {candidate.policy_id for candidate, _, _ in evaluated}
    seen.update(candidate.policy_id for candidate in second_generation)
    top_parents = [record for record in archive.top_k(6) if record.verified][:2]
    third_generation = []
    candidate_by_id = {candidate.policy_id: candidate for candidate, _, _ in evaluated}
    candidate_by_id.update({candidate.policy_id: candidate for candidate in second_generation})
    for rank, parent_record in enumerate(top_parents, start=1):
        parent = candidate_by_id.get(parent_record.policy_id)
        if parent is None:
            continue
        child = funsearch.mutate_top_parent(algorithm_name, parent, rank)
        child.metadata["parent"] = parent.policy_id
        if child.policy_id not in seen:
            third_generation.append(child)
            seen.add(child.policy_id)

    for candidate in third_generation:
        evaluate_candidate(
            candidate,
            spec,
            evaluator,
            budget,
            algorithm_name,
            problem_family,
            args.split,
            rows,
            archive,
            smoke_instance,
            smoke_budget,
        )
    output_stub = "search_%s_%s_%s" % (algorithm_name.lower(), problem_family, args.split)
    write_search_outputs(output_stub, "Search Summary", rows, archive)
    print("Saved search results to results/tables/%s.csv" % output_stub)


if __name__ == "__main__":
    main()
