#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p results/logs results/candidates results/tables results/figures

PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/admm_synthetic_qp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/fista_lasso.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.combine_phase1

echo "Phase 1 sanity checks finished. Tables are under results/tables."
