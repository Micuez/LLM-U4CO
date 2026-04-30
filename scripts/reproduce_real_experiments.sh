#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PYTHONPATH=src python3 -m llm4unroll.experiments.check_environment

if [[ "${1:-}" == "--dry-run" ]]; then
  PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
  exit 0
fi

PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json
PYTHONPATH=src python3 -m llm4unroll.experiments.aggregate_real_experiments

echo "Real experiment scaffold finished. See results/real_experiments and results/tables/real_experiment_summary.csv"
