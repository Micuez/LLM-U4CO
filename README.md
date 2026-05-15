# llm4unroll

Runnable research framework for the `LLM4Unroll_完整项目方案.tex` blueprint.

This version now includes:

- a safe policy DSL and static verifier
- a stricter DSL semantic verifier with action-schema and state-schema checks
- PDHG, ADMM, FISTA, ALM, DRS, PCG, and LNS_REPAIR runners
- synthetic Phase 1 and small Phase 2 benchmarks
- optimisation evaluator and result archival
- baseline, search, ablation, and OOD entrypoints
- a lightweight multi-generation search loop
- pluggable LLM client stubs for `mock` and `openai_compatible` providers

## Code structure

The repository follows a clear split between the runnable package under `src/`, experiment configs under `configs/`, helper scripts under `scripts/`, and generated artifacts under `results/`.

```text
LLM-U4CO/
├── README.md
├── README_zh.md
├── pyproject.toml
├── configs/                  # YAML experiment configs and manifest examples
├── data/                     # Bundled synthetic and small benchmark assets
├── results/                  # Generated tables, review docs, and real-run reports
├── scripts/                  # One-shot reproduction and setup helpers
└── src/llm4unroll/           # Core Python package
    ├── algorithms/           # Unrolled runners: PDHG, ADMM, FISTA, ALM, DRS, PCG, LNS_REPAIR
    ├── benchmarks/           # Synthetic generators and real-data loaders
    ├── dsl/                  # Policy DSL schema, parser, transpiler, verifier, runtime guards
    ├── evaluator/            # Metrics, smoke tests, scoring, reports, budget handling
    ├── experiments/          # CLI entrypoints for baselines, search, ablation, OOD, manifests
    ├── registry/             # Algorithm/problem/baseline registries
    ├── search/               # LLM client, prompts, population archive, search adapters
    ├── solvers/              # Native-or-surrogate solver interfaces
    ├── learned_controller.py # Learned-controller baseline export
    ├── policies.py           # Handwritten baseline/search seed policies
    ├── math_utils.py
    └── utils.py
```

### What each layer does

- `src/llm4unroll/experiments/`: the operational entry layer. Most runs start here, especially `run_baselines.py`, `run_search.py`, `run_ablation.py`, `run_ood.py`, and `run_manifest.py`.
- `src/llm4unroll/experiments/common.py`: the shared bootstrap path. It loads config, picks the algorithm runner, builds the run budget, and creates instances from the selected problem family.
- `src/llm4unroll/registry/algorithm_registry.py`: the central contract table. Each algorithm is described here by allowed state features, required features, legal actions, and safety constraints.
- `src/llm4unroll/dsl/`: the safety and policy layer. `schema.py` defines the contract, `verifier.py` statically checks generated policies, `transpiler.py` compiles policy code, and `guards.py` enforces runtime safety.
- `src/llm4unroll/algorithms/`: algorithm-specific runners. Each runner inherits from `algorithms/base.py` and implements how a policy interacts with one optimisation loop.
- `src/llm4unroll/benchmarks/`: instance construction layer. Synthetic problems come from `synthetic_lp_qp.py` and graph relaxations; small real-style data comes from `miplib.py` and `llm_lns_data.py`.
- `src/llm4unroll/evaluator/`: execution scoring and reporting. `optimisation_evaluator.py` runs policies or solver baselines on instances and aggregates metrics into comparable scores.
- `src/llm4unroll/search/`: policy search layer. It contains prompt templates, the OpenAI-compatible client, population management, and adapters such as FunSearch/ReEvo-style mutations.
- `src/llm4unroll/solvers/`: baseline solver layer. These files wrap HiGHS, OSQP, OR-Tools, PySCIPOpt, and Ecole, and fall back to surrogate behavior when native backends are unavailable.
- `configs/`: reproducible experiment recipes. The config selects the algorithm, problem family, budget profile, dataset roots, evaluation split sizes, and LLM provider settings.
- `scripts/`: coarse-grained automation for setup, data prep, environment checks, and end-to-end reproduction.
- `results/`: output sink for tables, logs, review reports, environment probes, and real-experiment summaries.

### Core execution flow

For most runs, the code path is:

`configs/*.yaml`
-> `experiments/common.py`
-> `registry/algorithm_registry.py`
-> `benchmarks/*` + `algorithms/*`
-> `dsl/verifier.py` and `dsl/guards.py`
-> `evaluator/optimisation_evaluator.py`
-> `evaluator/report.py`
-> `results/tables/*` and `results/logs/*`

Search runs add one more layer:

`experiments/run_search.py`
-> `search/prompts.py`
-> `search/llm_client.py`
-> `search/population.py`
-> `search/funsearch_adapter.py` / `search/reevo_adapter.py`

### Suggested reading order

If you want to understand the repository quickly, this order works well:

1. `src/llm4unroll/experiments/common.py`: see how config, runner, budget, and instances are assembled.
2. `src/llm4unroll/registry/algorithm_registry.py`: understand the state/action/safety contract for each algorithm family.
3. `src/llm4unroll/dsl/schema.py` and `src/llm4unroll/dsl/verifier.py`: see how candidate policies are constrained.
4. `src/llm4unroll/algorithms/base.py` plus one concrete runner such as `algorithms/pdhg.py`: understand the runtime loop.
5. `src/llm4unroll/experiments/run_baselines.py`: see the baseline evaluation pipeline end to end.
6. `src/llm4unroll/experiments/run_search.py` and `src/llm4unroll/search/`: see how LLM-guided search is added on top.
7. `src/llm4unroll/solvers/` and `src/llm4unroll/benchmarks/`: fill in native backend and dataset details as needed.

## Quick start

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/admm_synthetic_qp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/fista_lasso.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/pdhg_synthetic_lp.yaml
```

Install the package itself:

```bash
python3 -m pip install -e .
```

To reproduce the bundled sanity check:

```bash
bash scripts/reproduce_phase1.sh
bash scripts/reproduce_phase2.sh
bash scripts/reproduce_framework.sh
bash scripts/reproduce_real_experiments.sh --dry-run
```

## External repos and LLM-LNS data

Prepare local external repo links:

```bash
bash scripts/setup_external.sh
```

Inspect LLM-LNS and MILPBench availability:

```bash
bash scripts/prepare_llm_lns_data.sh
```

## Real experiment workflow

The repository is fully runnable in surrogate/small-benchmark mode out of the box.
For paper-grade real experiments, the intended workflow is:

1. Prepare external repositories and local data links.

```bash
bash scripts/setup_external.sh
bash scripts/prepare_llm_lns_data.sh
```

2. Install native solver backends that you want the baseline layer to use.

```bash
python3 -m pip install highspy osqp ortools
python3 -m pip install pyscipopt
python3 -m pip install ecole
```

3. Prepare benchmark data.

- `data/miplib/miplib_small.txt`: maintain a local list of root-LP `.lp` files
- `data/llm_lns/...`: place small or full LLM-LNS LP assets here
- optional: extend `configs/*.yaml` with larger `train/validation/test_instances`

4. Choose the LLM mode for search.

- `configs/search_mock_llm.yaml`: framework smoke test
- `configs/search_openai_compatible.example.yaml`: local deployed model or remote API

5. Run the real baselines and search loops.

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_sc.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_sc.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_is.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_evolution_baseline --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_random_search --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/search_openai_compatible.example.yaml --split train
```

6. Run ablation, OOD, and reporting.

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ood --config configs/pdhg_miplib_rootlp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

For the full paper-grade scaffold, you can also use the manifest runner:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_environment
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json
PYTHONPATH=src python3 -m llm4unroll.experiments.aggregate_real_experiments
```

Or use the helper script:

```bash
bash scripts/reproduce_real_experiments.sh --dry-run
bash scripts/reproduce_real_experiments.sh
```

7. Inspect outputs.

- tables: `results/tables/`
- candidate archives: `results/candidates/`
- logs: `results/logs/`
- paper figures and appendix pages: `results/figures/`
- manifest and environment status: `results/real_experiments/`

For a native backend run, check that solver rows show:

- `native_used=True`
- `native_backend=highspy|osqp|ortools|pyscipopt|ecole|...`

If the environment is incomplete, the same commands still run, but solver rows fall back to `backend_mode=surrogate`.

## LLM entrypoints

Smoke-test the configured LLM client:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_llm_client --config configs/search_mock_llm.yaml
```

To call a local or remote OpenAI-compatible endpoint, copy:

- `configs/search_openai_compatible.example.yaml`

and set:

- `llm.base_url`
- `llm.model`
- `llm.api_key` if needed

This works with local deployment stacks that expose an OpenAI-compatible `/v1/chat/completions` API.

## Native solver backends

The solver baseline layer now auto-switches between `native` and `surrogate` mode.
No extra runtime flag is required: if a backend package or command is available, the corresponding interface will use the real solve path automatically.

Current native backends:

- `HiGHS`: prefers `highspy`, falls back to the `highs` command
- `OSQP`: uses the Python `osqp` package
- `OR-Tools`: uses the Python `ortools` package
- `PySCIPOpt`: uses the Python `pyscipopt` package, with `scip` command as secondary fallback
- `Ecole`: uses the Python `ecole` package and a SCIP bridge subprocess

Recommended installs:

```bash
python3 -m pip install highspy osqp ortools
python3 -m pip install pyscipopt
python3 -m pip install ecole
```

For a repo-local setup, installing into `.vendor/` also works because `src/llm4unroll/__init__.py` prepends that directory to `sys.path` when present.

The bundled configs now also support budget presets through `budget.profile`, including `heurigym_small`, `heurigym_medium`, and `paper_native`.

Notes:

- `PySCIPOpt` and `Ecole` usually need a working SCIP installation or compatible binary environment.
- `HiGHS` can be enabled either by `pip install highspy` or by exposing a `highs` executable in `PATH`.
- If a backend is missing, the framework keeps running and records `backend_mode=surrogate` in the result tables.

To verify which mode is active, inspect the solver rows in:

- `results/tables/*.csv`
- `results/candidates/*_highs.txt`
- `results/candidates/*_pyscipopt.txt`
- `results/candidates/*_or-tools.txt`
- `results/candidates/*_ecole.txt`

Example configs:

- `configs/default.yaml`
- `configs/backend_native.example.yaml`
- `configs/search_openai_compatible.example.yaml`
- `configs/real_experiment_manifest.json`

Check the policy semantic verifier:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_verifier
```

## Report figures

The report layer can now render real SVG charts directly from the generated CSV tables, without `matplotlib` or `pandas`:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

It writes baseline, search, ablation, and OOD figures under `results/figures/`, plus a simple `results/figures/index.md` manifest.
It also writes a standalone verifier appendix page at `results/figures/verifier_report.html`.
For a denser paper-style appendix layout, it also writes `results/figures/verifier_appendix.html`.

For machine-readable implementation and verification coverage, inspect:

- `results/review/verified_tracks_status.json`
- `results/review/verified_tracks_status.md`
- `results/review/plan_implementation_status.json`
- `results/review/plan_implementation_status.md`

## Verified track map

The table below only lists tracks that already have a runner, config, and result artifacts wired together in the current repository.

| Track | Runner | Representative config | Key state/actions | Verified outputs | train-small-test-large | cross-problem transfer |
| --- | --- | --- | --- | --- | --- | --- |
| PDHG synthetic LP | `PDHGRunner` | `configs/pdhg_synthetic_lp.yaml` | `r_p_norm / r_d_norm / tau / sigma / restart / scale_tau / scale_sigma` | `results/tables/pdhg_pdhg_lp_train.csv` | `pdhg_lp` | `pdhg_lp -> setcover_relaxation`, `pdhg_lp -> miplib_rootlp` |
| PDHG MIPLIB root-LP | `PDHGRunner` | `configs/pdhg_miplib_rootlp.yaml` | `gap / violation / tau / sigma / native probe` | `results/tables/pdhg_miplib_rootlp_train.csv`, `results/tables/native_probe_pdhg_miplib_rootlp_train.csv` | `miplib_rootlp` | `miplib_rootlp -> llm_lns_sc` |
| PDHG LLM-LNS SC | `PDHGRunner` | `configs/pdhg_llm_lns_sc.yaml` | `mip-style LP relaxation / residual balancing / solver baseline` | `results/tables/pdhg_llm_lns_sc_train.csv` | `llm_lns_sc` | `llm_lns_sc -> llm_lns_is` |
| PDHG LLM-LNS IS | `PDHGRunner` | `configs/pdhg_llm_lns_is.yaml` | `instance_features / residual balancing / solver baseline` | `results/tables/pdhg_llm_lns_is_train.csv` | `llm_lns_is` | `llm_lns_is -> llm_lns_sc` |
| ADMM synthetic QP | `ADMMRunner` | `configs/admm_synthetic_qp.yaml` | `r_p_norm / r_d_norm / rho / scale_rho / restart / native probe` | `results/tables/admm_admm_qp_train.csv`, `results/tables/native_probe_admm_admm_qp_train.csv` | `admm_qp` | `admm_qp -> admm_qp_relaxation` |
| FISTA LASSO | `FISTARunner` | `configs/fista_lasso.yaml` | `obj / obj_prev / gap / momentum / restart / scale_tau` | `results/tables/fista_fista_lasso_train.csv` | `fista_lasso` | `fista_lasso -> fista_sparse_coding` |
| ALM equality-QP | `ALMRunner` | `configs/alm_eq_qp.yaml` | `violation / rho / dual_residual / grad_norm / clip_update / native probe` | `results/tables/alm_alm_eq_qp_train.csv`, `results/tables/native_probe_alm_alm_eq_qp_train.csv` | `alm_eq_qp` | `alm_eq_qp -> alm_cover_relaxation` |
| DRS feasibility | `DouglasRachfordRunner` | `configs/drs_feasibility.yaml` | `residual_norm / lambda_relax / dual_residual / set_lambda_relax / clip_update` | `results/tables/drs_drs_feasibility_train.csv` | `drs_feasibility` | `drs_feasibility -> drs_affine_box_shifted` |
| PCG linear system | `PCGRunner` | `configs/pcg_linear_system.yaml` | `residual_ratio / direction_curvature / gap / clip_update / restart / native probe` | `results/tables/pcg_pcg_linear_system_train.csv`, `results/tables/native_probe_pcg_pcg_linear_system_train.csv` | `pcg_linear_system` | `pcg_linear_system -> pcg_graph_laplacian` |
| LNS repair cover | `LNSRepairRunner` | `configs/lns_repair_cover.yaml` | `mip_gap / fractionality / neighbourhood_size / repair_progress / set_neighbourhood_size` | `results/tables/lns_repair_lns_repair_cover_train.csv` | `lns_repair_cover` | `lns_repair_cover -> lns_repair_cover_dense` |

## Current status

Implemented and statically closed:

- DSL schema, transpiler, static verifier, and runtime safety guard
- PDHG, ADMM, FISTA, ALM, DRS, PCG, and LNS_REPAIR runners
- synthetic Phase 1 benchmarks and small Phase 2 LLM-LNS / MIPLIB-style loaders
- optimisation evaluator, candidate archive, failure logs, and report generation
- baseline, search, ablation, OOD, random-search, and evolution-without-LLM entrypoints
- direct strong-baseline entrypoints for LLM-LNS heuristic vs LLM4Unroll vs combined pipeline
- standalone Bayesian-optimisation-style baseline, and minimal + high-budget + paper-scale learned-controller exports
- mock LLM, local OpenAI-compatible model, and remote API search entrypoints
- native-or-fallback solver interfaces for HiGHS, OSQP, OR-Tools, PySCIPOpt, and Ecole
- verifier appendix pages, native backend usage report, and SVG figure pipeline

Implemented with surrogate fallback:

- solver baselines still run when native backends are missing
- the Phase 2 data path still keeps a bundled mock LP fallback, but the local setup now prefers real MILPBench-backed LLM-LNS LP assets when present
- search still runs when only `mock` LLM is available

## Remaining work

Real-experiment-only work:

- install full native solver environments and rerun the same entrypoints in `native` mode
- continue expanding the real LLM-LNS data path from the current easy / medium MILPBench assets to full hard coverage, plus larger real MIPLIB subsets
- run large-budget search, ablation, and OOD experiments for paper tables
- compare against true external baselines under the same hardware and timeout budget

Framework extensions not fully implemented yet:

- larger-budget Bayesian optimisation and grid-search sweeps beyond the new standalone baseline entrypoint
- native solver coverage beyond the new local `highspy / osqp / ortools / pyscipopt` multi-track probes, with `ecole / scip` still missing locally
- stronger learned-controller baselines beyond the new minimal + high-budget + paper-scale trained `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR` coverage
- explicit `LLM one-shot without verifier` runner as a first-class experiment
- full paper-grade ablation matrix:
  - without verifier
  - without reflection
  - without evolution
  - safe fallback only
  - different LLM models / temperatures / prompt variants
- deep professional solver pipeline integration:
  - PySCIPOpt callback-level primal heuristic / LNS callback insertion
  - Ecole-generated train-small-test-large benchmark mainline
  - OR-Tools-specific PDLP / CP-SAT / routing baseline track
- full-strength external-system reproduction beyond the new high-fidelity `LLM-LNS heuristic` / `combined pipeline` contrast tracks and repo-local fullstack replay

In short: the framework itself is already end-to-end runnable, while the main unfinished items are large real experiments and a few paper-grade baseline/ablation extensions.
