#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

bash scripts/prepare_llm_lns_data.sh
PYTHONPATH=src python3 -m llm4unroll.experiments.inspect_llm_lns
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_sc.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_is.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/pdhg_llm_lns_sc.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.combine_phase2

echo "Phase 2 LLM-LNS surrogate checks finished. Summary table: results/tables/phase2_llm_lns.csv"
