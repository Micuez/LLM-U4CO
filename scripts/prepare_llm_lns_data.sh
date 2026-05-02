#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data/llm_lns

if [ -d "external/MILPBench/Benchmark Datasets" ]; then
  echo "Found external/MILPBench/Benchmark Datasets."
  if find data/llm_lns -maxdepth 3 -type f \( -name '*_easy_*.lp' -o -name '*_medium_*.lp' -o -name '*_hard_*.lp' \) | grep -q .; then
    echo "Real MILPBench-derived LP assets detected under data/llm_lns."
  else
    echo "MILPBench repo is available, but hydrated real LP assets are not present yet."
    echo "Run: PYTHONPATH=src python3 -m llm4unroll.experiments.hydrate_llm_lns_real_data --levels easy"
  fi
else
  echo "MILPBench not available locally. Using bundled mock LP data under data/llm_lns."
fi

find data/llm_lns -maxdepth 3 -type f | sort

echo
echo "Coverage check:"
missing=0
for family in SC_easy_instance IS_easy_instance MVC_easy_instance MIKS_easy_instance; do
  family_dir="data/llm_lns/${family}/LP"
  if [ -d "$family_dir" ]; then
    count=$(find "$family_dir" -maxdepth 1 -type f -name '*.lp' | wc -l | tr -d ' ')
  else
    count=0
  fi
  echo "  ${family}: ${count} LP files"
  if [ "$count" -eq 0 ]; then
    missing=1
  fi
done

if [ "$missing" -eq 1 ]; then
  echo
  echo "WARNING: Phase 2 LLM-LNS coverage is incomplete. Expected non-empty SC/IS/MVC/MIKS families."
else
  echo
  echo "Phase 2 LLM-LNS coverage looks complete."
fi
