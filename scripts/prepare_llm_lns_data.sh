#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data/llm_lns

if [ -d "external/MILPBench/Benchmark Datasets" ]; then
  echo "Found external/MILPBench/Benchmark Datasets."
  echo "You can map or copy the benchmark folders into data/llm_lns as needed."
else
  echo "MILPBench not available locally. Using bundled mock LP data under data/llm_lns."
fi

find data/llm_lns -maxdepth 3 -type f | sort
