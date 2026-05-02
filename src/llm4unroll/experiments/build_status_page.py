from __future__ import annotations

import json
import os
from typing import Dict, List

from llm4unroll.experiments.run_ood import default_transfer_scenarios
from llm4unroll.utils import dump_text, ensure_dir


STATUS_ENTRIES: List[Dict[str, object]] = [
    {
        "track_id": "pdhg_synthetic_lp",
        "algorithm": "PDHG",
        "problem_family": "pdhg_lp",
        "label": "PDHG synthetic LP",
        "section": "实验计划 / Phase 1",
        "runner": "PDHGRunner",
        "plan_section": "Phase 1 / minimal runnable demo",
        "code_modules": [
            "src/llm4unroll/algorithms/base.py",
            "src/llm4unroll/algorithms/pdhg.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/pdhg_synthetic_lp.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml",
            "python3 -m llm4unroll.experiments.run_search --config configs/pdhg_synthetic_lp.yaml",
        ],
        "key_state_actions": [
            "r_p_norm",
            "r_d_norm",
            "tau",
            "sigma",
            "restart",
            "scale_tau",
            "scale_sigma",
        ],
        "artifacts": [
            "results/tables/pdhg_pdhg_lp_train.csv",
            "results/tables/pdhg_pdhg_lp_train.md",
            "results/tables/ood_pdhg_pdhg_lp.csv",
        ],
    },
    {
        "track_id": "pdhg_miplib_rootlp",
        "algorithm": "PDHG",
        "problem_family": "miplib_rootlp",
        "label": "PDHG MIPLIB root-LP",
        "section": "与专业求解器结合 / 路线 A",
        "runner": "PDHGRunner",
        "plan_section": "Route A / root LP-QP relaxation accelerator",
        "code_modules": [
            "src/llm4unroll/algorithms/pdhg.py",
            "src/llm4unroll/benchmarks/miplib.py",
            "src/llm4unroll/solvers/highs_interface.py",
            "src/llm4unroll/experiments/check_native_backends.py",
        ],
        "config": "configs/pdhg_miplib_rootlp.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_miplib_rootlp.yaml --split train",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/pdhg_miplib_rootlp.yaml --split train",
        ],
        "key_state_actions": [
            "gap",
            "violation",
            "tau",
            "sigma",
            "native probe",
        ],
        "artifacts": [
            "results/tables/pdhg_miplib_rootlp_train.csv",
            "results/tables/native_probe_pdhg_miplib_rootlp_train.csv",
            "results/tables/ood_pdhg_miplib_rootlp.csv",
        ],
    },
    {
        "track_id": "pdhg_llm_lns_sc",
        "algorithm": "PDHG",
        "problem_family": "llm_lns_sc",
        "label": "PDHG LLM-LNS SC",
        "section": "实验计划 / Phase 2",
        "runner": "PDHGRunner",
        "plan_section": "Phase 2 / LLM-LNS set cover",
        "code_modules": [
            "src/llm4unroll/algorithms/pdhg.py",
            "src/llm4unroll/benchmarks/llm_lns_data.py",
            "src/llm4unroll/experiments/run_ood.py",
        ],
        "config": "configs/pdhg_llm_lns_sc.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_sc.yaml --split train",
            "python3 -m llm4unroll.experiments.run_external_baseline_replay --config configs/pdhg_llm_lns_sc.yaml --split train",
        ],
        "key_state_actions": [
            "mip-style LP relaxation",
            "residual balancing",
            "solver baseline",
        ],
        "artifacts": [
            "results/tables/pdhg_llm_lns_sc_train.csv",
            "results/tables/pdhg_llm_lns_sc_train.md",
            "results/tables/ood_pdhg_llm_lns_sc.csv",
            "results/tables/external_replay_pdhg_llm_lns_sc_train.csv",
        ],
    },
    {
        "track_id": "pdhg_llm_lns_is",
        "algorithm": "PDHG",
        "problem_family": "llm_lns_is",
        "label": "PDHG LLM-LNS IS",
        "section": "实验计划 / Phase 2",
        "runner": "PDHGRunner",
        "plan_section": "Phase 2 / LLM-LNS independent set",
        "code_modules": [
            "src/llm4unroll/algorithms/pdhg.py",
            "src/llm4unroll/benchmarks/llm_lns_data.py",
            "src/llm4unroll/experiments/run_ood.py",
        ],
        "config": "configs/pdhg_llm_lns_is.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_is.yaml --split train",
            "python3 -m llm4unroll.experiments.run_external_baseline_replay --config configs/pdhg_llm_lns_is.yaml --split train",
        ],
        "key_state_actions": [
            "instance_features",
            "residual balancing",
            "solver baseline",
        ],
        "artifacts": [
            "results/tables/pdhg_llm_lns_is_train.csv",
            "results/tables/pdhg_llm_lns_is_train.md",
            "results/tables/external_replay_pdhg_llm_lns_is_train.csv",
        ],
    },
    {
        "track_id": "admm_synthetic_qp",
        "algorithm": "ADMM",
        "problem_family": "admm_qp",
        "label": "ADMM synthetic QP",
        "section": "实验计划 / Phase 1",
        "runner": "ADMMRunner",
        "plan_section": "Phase 1 / minimal runnable demo",
        "code_modules": [
            "src/llm4unroll/algorithms/admm.py",
            "src/llm4unroll/registry/algorithm_registry.py",
            "src/llm4unroll/solvers/osqp_interface.py",
            "src/llm4unroll/experiments/check_native_backends.py",
        ],
        "config": "configs/admm_synthetic_qp.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/admm_synthetic_qp.yaml",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/admm_synthetic_qp.yaml --split train",
        ],
        "key_state_actions": [
            "r_p_norm",
            "r_d_norm",
            "rho",
            "scale_rho",
            "restart",
        ],
        "artifacts": [
            "results/tables/admm_admm_qp_train.csv",
            "results/tables/admm_admm_qp_train.md",
            "results/tables/native_probe_admm_admm_qp_train.csv",
            "results/tables/ood_admm_admm_qp.csv",
        ],
    },
    {
        "track_id": "fista_lasso",
        "algorithm": "FISTA",
        "problem_family": "fista_lasso",
        "label": "FISTA LASSO",
        "section": "实验计划 / Phase 1",
        "runner": "FISTARunner",
        "plan_section": "Phase 1 / minimal runnable demo",
        "code_modules": [
            "src/llm4unroll/algorithms/fista.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/fista_lasso.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/fista_lasso.yaml",
        ],
        "key_state_actions": [
            "obj",
            "obj_prev",
            "gap",
            "momentum",
            "restart",
            "scale_tau",
        ],
        "artifacts": [
            "results/tables/fista_fista_lasso_train.csv",
            "results/tables/fista_fista_lasso_train.md",
            "results/tables/ood_fista_fista_lasso.csv",
        ],
    },
    {
        "track_id": "alm_eq_qp",
        "algorithm": "ALM",
        "problem_family": "alm_eq_qp",
        "label": "ALM equality-QP",
        "section": "算法 Runner 设计 / 扩展线",
        "runner": "ALMRunner",
        "plan_section": "Algorithm runner expansion / ALM",
        "code_modules": [
            "src/llm4unroll/algorithms/alm.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/alm_eq_qp.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/alm_eq_qp.yaml",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/alm_eq_qp.yaml --split train",
        ],
        "key_state_actions": [
            "violation",
            "rho",
            "dual_residual",
            "grad_norm",
            "clip_update",
        ],
        "artifacts": [
            "results/tables/alm_alm_eq_qp_train.csv",
            "results/tables/alm_alm_eq_qp_train.md",
            "results/tables/native_probe_alm_alm_eq_qp_train.csv",
            "results/tables/ood_alm_alm_eq_qp.csv",
        ],
    },
    {
        "track_id": "drs_feasibility",
        "algorithm": "DRS",
        "problem_family": "drs_feasibility",
        "label": "DRS feasibility",
        "section": "算法 Runner 设计 / 扩展线",
        "runner": "DouglasRachfordRunner",
        "plan_section": "Algorithm runner expansion / DRS",
        "code_modules": [
            "src/llm4unroll/algorithms/douglas_rachford.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/drs_feasibility.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/drs_feasibility.yaml",
        ],
        "key_state_actions": [
            "residual_norm",
            "lambda_relax",
            "dual_residual",
            "set_lambda_relax",
            "clip_update",
        ],
        "artifacts": [
            "results/tables/drs_drs_feasibility_train.csv",
            "results/tables/drs_drs_feasibility_train.md",
            "results/tables/ood_drs_drs_feasibility.csv",
        ],
    },
    {
        "track_id": "pcg_linear_system",
        "algorithm": "PCG",
        "problem_family": "pcg_linear_system",
        "label": "PCG linear system",
        "section": "算法 Runner 设计 / 扩展线",
        "runner": "PCGRunner",
        "plan_section": "Algorithm runner expansion / PCG",
        "code_modules": [
            "src/llm4unroll/algorithms/pcg.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/pcg_linear_system.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pcg_linear_system.yaml",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/pcg_linear_system.yaml --split train",
        ],
        "key_state_actions": [
            "residual_ratio",
            "direction_curvature",
            "gap",
            "clip_update",
            "restart",
        ],
        "artifacts": [
            "results/tables/pcg_pcg_linear_system_train.csv",
            "results/tables/pcg_pcg_linear_system_train.md",
            "results/tables/native_probe_pcg_pcg_linear_system_train.csv",
            "results/tables/ood_pcg_pcg_linear_system.csv",
        ],
    },
    {
        "track_id": "lns_repair_cover",
        "algorithm": "LNS_REPAIR",
        "problem_family": "lns_repair_cover",
        "label": "LNS repair cover",
        "section": "与专业求解器结合 / 路线 B",
        "runner": "LNSRepairRunner",
        "plan_section": "Route B / relaxation-guided LNS repair",
        "code_modules": [
            "src/llm4unroll/algorithms/lns_repair.py",
            "src/llm4unroll/registry/algorithm_registry.py",
        ],
        "config": "configs/lns_repair_cover.yaml",
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/lns_repair_cover.yaml",
            "python3 -m llm4unroll.experiments.run_solver_tracks --config configs/lns_repair_cover.yaml --split train",
        ],
        "key_state_actions": [
            "mip_gap",
            "fractionality",
            "neighbourhood_size",
            "repair_progress",
            "set_neighbourhood_size",
        ],
        "artifacts": [
            "results/tables/lns_repair_lns_repair_cover_train.csv",
            "results/tables/lns_repair_lns_repair_cover_train.md",
            "results/tables/ood_lns_repair_lns_repair_cover.csv",
            "results/tables/solver_tracks_lns_repair_lns_repair_cover_train.csv",
        ],
    },
]

PLAN_STATUS_ENTRIES: List[Dict[str, object]] = [
    {
        "plan_section": "系统总架构",
        "module_group": "Core pipeline",
        "code_modules": [
            "src/llm4unroll/registry/algorithm_registry.py",
            "src/llm4unroll/dsl/verifier.py",
            "src/llm4unroll/evaluator/optimisation_evaluator.py",
            "src/llm4unroll/experiments/build_status_page.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.check_verifier",
            "python3 -m llm4unroll.experiments.build_status_page",
        ],
        "artifacts": [
            "results/review/verified_tracks_status.json",
            "results/review/plan_implementation_status.json",
        ],
    },
    {
        "plan_section": "DSL 设计",
        "module_group": "DSL + parser + runtime guard",
        "code_modules": [
            "src/llm4unroll/dsl/schema.py",
            "src/llm4unroll/dsl/parser.py",
            "src/llm4unroll/dsl/verifier.py",
            "src/llm4unroll/dsl/guards.py",
            "src/llm4unroll/dsl/transpiler.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.check_verifier",
        ],
        "artifacts": [
            "results/tables/verifier_positive.csv",
            "results/tables/verifier_negative.csv",
            "results/figures/verifier_report.html",
        ],
    },
    {
        "plan_section": "Baseline 使用方案",
        "module_group": "Policy baselines + non-LLM baselines",
        "code_modules": [
            "src/llm4unroll/registry/baseline_registry.py",
            "src/llm4unroll/policies.py",
            "src/llm4unroll/search/non_llm_baselines.py",
            "src/llm4unroll/experiments/run_baselines.py",
            "src/llm4unroll/experiments/run_bayesian_baseline.py",
            "src/llm4unroll/experiments/run_random_search.py",
            "src/llm4unroll/experiments/run_evolution_baseline.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml",
            "python3 -m llm4unroll.experiments.run_bayesian_baseline --config configs/pdhg_miplib_rootlp.yaml --split train",
            "python3 -m llm4unroll.experiments.run_random_search --config configs/pdhg_miplib_rootlp.yaml --split train",
            "python3 -m llm4unroll.experiments.run_evolution_baseline --config configs/pdhg_miplib_rootlp.yaml --split train",
        ],
        "artifacts": [
            "results/tables/pdhg_pdhg_lp_train.csv",
            "results/tables/bayesian_optimisation_pdhg_miplib_rootlp_train.csv",
            "results/tables/random_search_pdhg_miplib_rootlp_train.csv",
            "results/tables/evolution_no_llm_pdhg_miplib_rootlp_train.csv",
        ],
    },
    {
        "plan_section": "Verifier 与 Safety Guard",
        "module_group": "Static verifier + runtime guard",
        "code_modules": [
            "src/llm4unroll/dsl/verifier.py",
            "src/llm4unroll/dsl/guards.py",
            "src/llm4unroll/evaluator/smoke_test.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.check_verifier",
        ],
        "artifacts": [
            "results/tables/verifier_positive.md",
            "results/tables/verifier_negative.md",
        ],
    },
    {
        "plan_section": "算法 Runner 设计",
        "module_group": "Operator-splitting runners",
        "code_modules": [
            "src/llm4unroll/algorithms/pdhg.py",
            "src/llm4unroll/algorithms/admm.py",
            "src/llm4unroll/algorithms/fista.py",
            "src/llm4unroll/algorithms/alm.py",
            "src/llm4unroll/algorithms/douglas_rachford.py",
            "src/llm4unroll/algorithms/pcg.py",
            "src/llm4unroll/algorithms/lns_repair.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/alm_eq_qp.yaml",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/drs_feasibility.yaml",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pcg_linear_system.yaml",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/lns_repair_cover.yaml",
        ],
        "artifacts": [
            "results/tables/alm_alm_eq_qp_train.csv",
            "results/tables/drs_drs_feasibility_train.csv",
            "results/tables/pcg_pcg_linear_system_train.csv",
            "results/tables/lns_repair_lns_repair_cover_train.csv",
        ],
    },
    {
        "plan_section": "与专业求解器结合的三条路线",
        "module_group": "Solver interfaces + native probe",
        "code_modules": [
            "src/llm4unroll/solvers/highs_interface.py",
            "src/llm4unroll/solvers/osqp_interface.py",
            "src/llm4unroll/solvers/pyscipopt_interface.py",
            "src/llm4unroll/solvers/ortools_interface.py",
            "src/llm4unroll/solvers/ecole_interface.py",
            "src/llm4unroll/solvers/common.py",
            "src/llm4unroll/experiments/check_native_backends.py",
            "src/llm4unroll/experiments/run_solver_tracks.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.check_environment",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/pdhg_miplib_rootlp.yaml --split train",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/admm_synthetic_qp.yaml --split train",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/alm_eq_qp.yaml --split train",
            "python3 -m llm4unroll.experiments.check_native_backends --config configs/pcg_linear_system.yaml --split train",
            "python3 -m llm4unroll.experiments.run_solver_tracks --config configs/lns_repair_cover.yaml --split train",
        ],
        "artifacts": [
            "results/real_experiments/environment_report.json",
            "results/tables/native_probe_pdhg_miplib_rootlp_train.csv",
            "results/tables/native_probe_admm_admm_qp_train.csv",
            "results/tables/native_probe_alm_alm_eq_qp_train.csv",
            "results/tables/native_probe_pcg_pcg_linear_system_train.csv",
            "results/tables/solver_tracks_lns_repair_lns_repair_cover_train.csv",
        ],
    },
    {
        "plan_section": "实验计划 / Phase 1",
        "module_group": "Minimal runnable demo",
        "code_modules": [
            "src/llm4unroll/experiments/run_baselines.py",
            "src/llm4unroll/experiments/run_search.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/admm_synthetic_qp.yaml",
            "python3 -m llm4unroll.experiments.run_search --config configs/pdhg_synthetic_lp.yaml",
        ],
        "artifacts": [
            "results/tables/pdhg_pdhg_lp_train.csv",
            "results/tables/admm_admm_qp_train.csv",
            "results/tables/search_pdhg_pdhg_lp_train.csv",
        ],
    },
    {
        "plan_section": "实验计划 / Phase 2",
        "module_group": "LLM-LNS + MIPLIB",
        "code_modules": [
            "src/llm4unroll/benchmarks/llm_lns_data.py",
            "src/llm4unroll/benchmarks/miplib.py",
            "src/llm4unroll/experiments/check_environment.py",
        ],
        "experiment_entrypoints": [
            "bash scripts/prepare_llm_lns_data.sh",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_sc.yaml --split train",
            "python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_miplib_rootlp.yaml --split train",
        ],
        "artifacts": [
            "results/tables/pdhg_llm_lns_sc_train.csv",
            "results/tables/pdhg_miplib_rootlp_train.csv",
            "results/real_experiments/environment_report.md",
        ],
    },
    {
        "plan_section": "实验计划 / Phase 4",
        "module_group": "Ablation + OOD/transfer",
        "code_modules": [
            "src/llm4unroll/experiments/run_ablation.py",
            "src/llm4unroll/experiments/run_ood.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_synthetic_lp.yaml",
            "python3 -m llm4unroll.experiments.run_ood --config configs/pdhg_miplib_rootlp.yaml",
            "python3 -m llm4unroll.experiments.run_ood --config configs/pdhg_llm_lns_sc.yaml",
        ],
        "artifacts": [
            "results/tables/ablation_pdhg_pdhg_lp_train.csv",
            "results/tables/ood_pdhg_miplib_rootlp.csv",
            "results/tables/ood_pdhg_llm_lns_sc.csv",
        ],
    },
    {
        "plan_section": "实验计划 / 强对照 Baseline",
        "module_group": "LLM-LNS heuristic vs LLM4Unroll vs combined pipeline",
        "code_modules": [
            "src/llm4unroll/experiments/run_strong_baselines.py",
            "src/llm4unroll/experiments/run_external_baseline_replay.py",
            "src/llm4unroll/policies.py",
            "src/llm4unroll/benchmarks/llm_lns_data.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_sc.yaml --split train",
            "python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_is.yaml --split train",
            "python3 -m llm4unroll.experiments.run_external_baseline_replay --config configs/pdhg_llm_lns_sc.yaml --split train",
            "python3 -m llm4unroll.experiments.run_external_baseline_replay --config configs/pdhg_llm_lns_is.yaml --split train",
        ],
        "artifacts": [
            "results/tables/strong_baselines_pdhg_llm_lns_sc_train.csv",
            "results/tables/strong_baselines_pdhg_llm_lns_is_train.csv",
            "results/tables/external_replay_pdhg_llm_lns_sc_train.csv",
            "results/tables/external_replay_pdhg_llm_lns_is_train.csv",
        ],
    },
    {
        "plan_section": "实验计划 / Manifest 编排",
        "module_group": "Manifest coverage + staged generalization jobs",
        "code_modules": [
            "src/llm4unroll/experiments/run_manifest.py",
            "configs/real_experiment_manifest.json",
            "src/llm4unroll/experiments/run_ood.py",
        ],
        "experiment_entrypoints": [
            "python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --stage generalization --dry-run",
            "python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --stage generalization",
        ],
        "artifacts": [
            "results/real_experiments/manifest_status.json",
            "results/real_experiments/manifest_status.md",
            "results/tables/bayesian_optimisation_pdhg_miplib_rootlp_train.csv",
            "results/tables/solver_tracks_lns_repair_lns_repair_cover_train.csv",
            "results/tables/external_replay_pdhg_llm_lns_sc_train.csv",
            "results/tables/external_replay_pdhg_llm_lns_is_train.csv",
            "results/tables/ood_pdhg_miplib_rootlp.csv",
            "results/tables/ood_pdhg_pdhg_lp.csv",
            "results/tables/ood_pdhg_llm_lns_sc.csv",
            "results/tables/ood_pdhg_llm_lns_is.csv",
            "results/tables/ood_admm_admm_qp.csv",
            "results/tables/ood_fista_fista_lasso.csv",
            "results/tables/ood_alm_alm_eq_qp.csv",
            "results/tables/ood_drs_drs_feasibility.csv",
            "results/tables/ood_pcg_pcg_linear_system.csv",
            "results/tables/ood_lns_repair_lns_repair_cover.csv",
        ],
    },
    {
        "plan_section": "审查与整改流程产品化",
        "module_group": "Alignment audit automation",
        "code_modules": [
            "scripts/audit_alignment.sh",
            "src/llm4unroll/experiments/check_environment.py",
            "src/llm4unroll/experiments/check_verifier.py",
            "src/llm4unroll/experiments/run_manifest.py",
            "src/llm4unroll/experiments/build_status_page.py",
            "src/llm4unroll/experiments/generate_review_docs.py",
        ],
        "experiment_entrypoints": [
            "bash scripts/audit_alignment.sh",
            "bash scripts/audit_alignment.sh --dynamic-generalization",
        ],
        "artifacts": [
            "results/real_experiments/environment_report.md",
            "results/real_experiments/manifest_status.md",
            "results/review/verified_tracks_status.md",
            "results/review/plan_implementation_status.md",
            "results/review/strict_alignment_audit_latest.md",
            "results/review/remediation_checklist_latest.md",
        ],
    },
]


def _entry_status(entry: Dict[str, object]) -> Dict[str, object]:
    config_path = str(entry["config"])
    artifact_paths = [str(path) for path in entry["artifacts"]]
    artifact_rows = [{"path": path, "exists": os.path.exists(path)} for path in artifact_paths]
    all_artifacts_present = all(item["exists"] for item in artifact_rows)
    eval_cfg = {"train_instances": 3, "test_instances": 3}
    ood_scenarios = default_transfer_scenarios(str(entry["problem_family"]), eval_cfg)
    ood_rows = []
    for scenario in ood_scenarios:
        ood_rows.append({
            "name": str(scenario["name"]),
            "type": "train_small_test_large"
            if str(scenario["name"]) == "train_small_test_large"
            else "cross_problem_transfer",
            "source_problem_family": str(entry["problem_family"]),
            "target_problem_family": str(scenario.get("target_problem_family", entry["problem_family"])),
            "source_scale": str(scenario.get("source_scale", "source")),
            "target_scale": str(scenario.get("target_scale", "target")),
        })
    ood_types = sorted({row["type"] for row in ood_rows})
    return {
        "track_id": entry["track_id"],
        "algorithm": entry["algorithm"],
        "problem_family": entry["problem_family"],
        "label": entry["label"],
        "section": entry["section"],
        "runner": entry["runner"],
        "plan_section": entry["plan_section"],
        "code_modules": [{"path": path, "exists": os.path.exists(path)} for path in entry["code_modules"]],
        "config": {
            "path": config_path,
            "exists": os.path.exists(config_path),
        },
        "experiment_entrypoints": list(entry["experiment_entrypoints"]),
        "key_state_actions": list(entry["key_state_actions"]),
        "artifacts": artifact_rows,
        "ood_coverage": {
            "artifact_paths": [row for row in artifact_rows if "/ood_" in row["path"]],
            "scenario_types": ood_types,
            "scenarios": ood_rows,
        },
        "status": {
            "implemented": True,
            "config_present": os.path.exists(config_path),
            "artifacts_present": all_artifacts_present,
            "verification_state": "verified_artifacts_present" if all_artifacts_present else "implemented_missing_artifacts",
        },
    }


def build_status_payload() -> Dict[str, object]:
    tracks = [_entry_status(entry) for entry in STATUS_ENTRIES]
    return {
        "schema_version": 1,
        "name": "llm4unroll_verified_tracks",
        "tracks": tracks,
        "sections": [
            {
                "section": section,
                "tracks": [track["track_id"] for track in tracks if track["section"] == section],
            }
            for section in sorted({track["section"] for track in tracks})
        ],
        "summary": {
            "track_count": len(tracks),
            "tracks_with_artifacts": len([track for track in tracks if track["status"]["artifacts_present"]]),
            "tracks_missing_artifacts": len([track for track in tracks if not track["status"]["artifacts_present"]]),
        },
    }


def build_plan_status_payload() -> Dict[str, object]:
    rows = []
    for entry in PLAN_STATUS_ENTRIES:
        module_rows = [{"path": path, "exists": os.path.exists(path)} for path in entry["code_modules"]]
        artifact_rows = [{"path": path, "exists": os.path.exists(path)} for path in entry["artifacts"]]
        rows.append({
            "plan_section": entry["plan_section"],
            "module_group": entry["module_group"],
            "code_modules": module_rows,
            "experiment_entrypoints": list(entry["experiment_entrypoints"]),
            "artifacts": artifact_rows,
            "status": {
                "modules_present": all(item["exists"] for item in module_rows),
                "artifacts_present": all(item["exists"] for item in artifact_rows),
                "verification_state": "implemented_with_artifacts"
                if all(item["exists"] for item in module_rows) and all(item["exists"] for item in artifact_rows)
                else "implemented_missing_artifacts",
            },
        })
    return {
        "schema_version": 1,
        "name": "llm4unroll_plan_implementation_status",
        "sections": rows,
        "summary": {
            "section_count": len(rows),
            "sections_with_artifacts": len([row for row in rows if row["status"]["artifacts_present"]]),
            "sections_missing_artifacts": len([row for row in rows if not row["status"]["artifacts_present"]]),
        },
    }


def write_status_outputs(payload: Dict[str, object]) -> None:
    ensure_dir("results/review")
    dump_text(
        "results/review/verified_tracks_status.json",
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )

    lines = ["# Verified Track Status", ""]
    lines.append("| Section | Track | Runner | Code Modules | Config | Artifacts | Train-small-test-large | Cross-problem transfer | Status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for track in payload["tracks"]:
        artifact_summary = "%d/%d" % (
            len([item for item in track["artifacts"] if item["exists"]]),
            len(track["artifacts"]),
        )
        train_small = [
            row["target_problem_family"]
            for row in track["ood_coverage"]["scenarios"]
            if row["type"] == "train_small_test_large"
        ]
        cross_problem = [
            "%s->%s" % (row["source_problem_family"], row["target_problem_family"])
            for row in track["ood_coverage"]["scenarios"]
            if row["type"] == "cross_problem_transfer"
        ]
        module_summary = "%d/%d" % (
            len([item for item in track["code_modules"] if item["exists"]]),
            len(track["code_modules"]),
        )
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                track["section"],
                track["label"],
                track["runner"],
                module_summary,
                "OK" if track["config"]["exists"] else "MISSING",
                artifact_summary,
                "<br>".join(train_small) if train_small else "None",
                "<br>".join(cross_problem) if cross_problem else "None",
                track["status"]["verification_state"],
            )
        )
    dump_text("results/review/verified_tracks_status.md", "\n".join(lines) + "\n")


def write_plan_status_outputs(payload: Dict[str, object]) -> None:
    ensure_dir("results/review")
    dump_text(
        "results/review/plan_implementation_status.json",
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    lines = ["# Plan Implementation Status", ""]
    lines.append("| Plan Section | Module Group | Modules | Artifacts | Status |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in payload["sections"]:
        module_summary = "%d/%d" % (
            len([item for item in row["code_modules"] if item["exists"]]),
            len(row["code_modules"]),
        )
        artifact_summary = "%d/%d" % (
            len([item for item in row["artifacts"] if item["exists"]]),
            len(row["artifacts"]),
        )
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                row["plan_section"],
                row["module_group"],
                module_summary,
                artifact_summary,
                row["status"]["verification_state"],
            )
        )
    dump_text("results/review/plan_implementation_status.md", "\n".join(lines) + "\n")


def main() -> None:
    payload = build_status_payload()
    plan_payload = build_plan_status_payload()
    write_status_outputs(payload)
    write_plan_status_outputs(plan_payload)
    print("Saved verified track status to results/review/verified_tracks_status.json")


if __name__ == "__main__":
    main()
