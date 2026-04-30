#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

bash scripts/reproduce_phase1.sh
bash scripts/reproduce_phase2.sh
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ood --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures

echo "Framework reproduction finished."
