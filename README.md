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

## Current status

Implemented and statically closed:

- DSL schema, transpiler, static verifier, and runtime safety guard
- PDHG, ADMM, FISTA, ALM, DRS, PCG, and LNS_REPAIR runners
- synthetic Phase 1 benchmarks and small Phase 2 LLM-LNS / MIPLIB-style loaders
- optimisation evaluator, candidate archive, failure logs, and report generation
- baseline, search, ablation, OOD, random-search, and evolution-without-LLM entrypoints
- mock LLM, local OpenAI-compatible model, and remote API search entrypoints
- native-or-fallback solver interfaces for HiGHS, OSQP, OR-Tools, PySCIPOpt, and Ecole
- verifier appendix pages, native backend usage report, and SVG figure pipeline

Implemented with surrogate fallback:

- solver baselines still run when native backends are missing
- Phase 2 data path still runs when only bundled mock LP assets are available
- search still runs when only `mock` LLM is available

## Remaining work

Real-experiment-only work:

- install full native solver environments and rerun the same entrypoints in `native` mode
- replace bundled mock/small benchmark assets with real MIPLIB subsets and larger LLM-LNS assets
- run large-budget search, ablation, and OOD experiments for paper tables
- compare against true external baselines under the same hardware and timeout budget

Framework extensions not fully implemented yet:

- Bayesian optimisation or grid-search baseline
- learned-controller baseline
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
- full-strength LLM-LNS heuristic vs. LLM4Unroll vs. combined pipeline comparison
- HeuriGym-style agentic heuristic benchmark integration

In short: the framework itself is already end-to-end runnable, while the main unfinished items are large real experiments and a few paper-grade baseline/ablation extensions.
