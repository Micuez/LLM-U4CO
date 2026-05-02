from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Dict, List

from llm4unroll.utils import dump_text, ensure_dir


def parse_args():
    parser = argparse.ArgumentParser(description="Run a real-experiment manifest for llm4unroll.")
    parser.add_argument("--manifest", default="configs/real_experiment_manifest.json", help="Path to the JSON manifest.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the jobs without executing them.")
    parser.add_argument("--stage", default="", help="Only run jobs from one stage.")
    return parser.parse_args()


def load_manifest(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run_job(job: Dict[str, object], timeout_s: float) -> Dict[str, object]:
    command = list(job["command"])
    env = dict(os.environ)
    extra_paths = ["src", ".vendor"]
    if env.get("PYTHONPATH"):
        extra_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(extra_paths)
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
            check=False,
        )
        return {
            "job_id": job["job_id"],
            "stage": job.get("stage", ""),
            "description": job.get("description", ""),
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "runtime_s": time.time() - started,
            "stdout": completed.stdout[-2000:],
            "stderr": completed.stderr[-2000:],
            "artifacts": job.get("artifacts", []),
        }
    except subprocess.TimeoutExpired:
        return {
            "job_id": job["job_id"],
            "stage": job.get("stage", ""),
            "description": job.get("description", ""),
            "command": command,
            "ok": False,
            "returncode": None,
            "runtime_s": time.time() - started,
            "stdout": "",
            "stderr": "timeout",
            "artifacts": job.get("artifacts", []),
        }


def write_manifest_report(manifest: Dict[str, object], rows: List[Dict[str, object]]) -> None:
    ensure_dir("results/real_experiments")
    payload = {
        "manifest_name": manifest.get("name", ""),
        "description": manifest.get("description", ""),
        "rows": rows,
    }
    dump_text("results/real_experiments/manifest_status.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    lines = ["# Manifest Status", ""]
    lines.append("- manifest: %s" % manifest.get("name", ""))
    lines.append("- description: %s" % manifest.get("description", ""))
    lines.append("")
    lines.append("| Job | Stage | OK | Runtime(s) | Return | Artifacts |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(
            "| %s | %s | %s | %.2f | %s | %s |"
            % (
                row["job_id"],
                row["stage"],
                row["ok"],
                float(row["runtime_s"]),
                row["returncode"],
                ", ".join(row.get("artifacts", [])),
            )
        )
    dump_text("results/real_experiments/manifest_status.md", "\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    jobs = list(manifest.get("jobs", []))
    if args.stage:
        jobs = [job for job in jobs if str(job.get("stage", "")) == args.stage]
    if args.dry_run:
        for job in jobs:
            print("[%s] %s" % (job.get("stage", ""), " ".join(job["command"])))
        return
    rows = []
    timeout_s = float(manifest.get("default_timeout_s", 7200))
    for job in jobs:
        print("Running job:", job["job_id"])
        row = run_job(job, timeout_s=timeout_s)
        rows.append(row)
        if row["stdout"]:
            print(row["stdout"][-400:])
        if not row["ok"]:
            print("Job failed:", job["job_id"], file=sys.stderr)
    write_manifest_report(manifest, rows)
    failures = [row for row in rows if not row["ok"]]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
