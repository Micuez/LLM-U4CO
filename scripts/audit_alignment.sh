#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="src:.vendor${PYTHONPATH:+:$PYTHONPATH}"

DYNAMIC_GENERALIZATION=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dynamic-generalization)
      DYNAMIC_GENERALIZATION=1
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: bash scripts/audit_alignment.sh [--dynamic-generalization]" >&2
      exit 1
      ;;
  esac
done

echo "[audit] checking LLM-LNS data coverage"
bash scripts/prepare_llm_lns_data.sh

echo "[audit] running environment check"
python3 -m llm4unroll.experiments.check_environment

echo "[audit] checking native installation blockers"
python3 -m llm4unroll.experiments.check_native_installation_blockers

echo "[audit] probing external exact-repo reproduction readiness"
python3 -m llm4unroll.experiments.run_external_repo_exact_probe

echo "[audit] running verifier check"
python3 -m llm4unroll.experiments.check_verifier

echo "[audit] validating manifest wiring (dry-run)"
python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --stage generalization --dry-run

if [[ "$DYNAMIC_GENERALIZATION" -eq 1 ]]; then
  echo "[audit] running small dynamic generalization stage"
  python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --stage generalization
fi

echo "[audit] rebuilding machine-readable status pages"
python3 -m llm4unroll.experiments.build_status_page

echo "[audit] generating latest review docs"
python3 -m llm4unroll.experiments.generate_review_docs

echo "[audit] refreshing status pages after review-doc generation"
python3 -m llm4unroll.experiments.build_status_page
python3 -m llm4unroll.experiments.generate_review_docs

echo
echo "[audit] alignment audit complete"
echo "  - environment: results/real_experiments/environment_report.md"
echo "  - manifest status: results/real_experiments/manifest_status.md"
echo "  - verified tracks: results/review/verified_tracks_status.md"
echo "  - plan status: results/review/plan_implementation_status.md"
echo "  - strict audit: results/review/strict_alignment_audit_latest.md"
echo "  - remediation checklist: results/review/remediation_checklist_latest.md"
