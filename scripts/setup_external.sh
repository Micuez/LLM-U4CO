#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p external data/llm_lns results/logs results/candidates results/tables results/figures

link_repo() {
  local src="$1"
  local dst="$2"
  if [ -e "$dst" ]; then
    echo "skip existing $dst"
    return
  fi
  if [ -e "$src" ]; then
    ln -s "../$src" "$dst"
    echo "linked $dst -> ../$src"
  else
    echo "missing source repo: $src"
  fi
}

link_repo "baselines/LLM-LNS" "external/LLM-LNS"
link_repo "baselines/MILPBench" "external/MILPBench"
link_repo "baselines/EoH" "external/EoH"
link_repo "baselines/ReEvo" "external/reevo"
link_repo "baselines/OSQP" "external/osqp"
link_repo "baselines/HiGHS" "external/HiGHS"
link_repo "baselines/PySCIPOpt" "external/PySCIPOpt"
link_repo "baselines/Ecole" "external/ecole"
link_repo "baselines/OR-Tools" "external/or-tools"
link_repo "baselines/HeuriGym" "external/heurigym"

echo "External workspace prepared under $ROOT_DIR/external"
