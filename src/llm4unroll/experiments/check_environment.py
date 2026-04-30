from __future__ import annotations

import importlib
import json
import os
import shutil
from typing import Dict, List

from llm4unroll.benchmarks.llm_lns_data import summarize_llm_lns_assets
from llm4unroll.benchmarks.miplib import load_miplib_paths
from llm4unroll.utils import dump_text, ensure_dir


def _probe_python_package(name: str) -> Dict[str, object]:
    try:
        importlib.import_module(name)
        return {"name": name, "available": True, "mode": "python_package", "detail": "importable"}
    except Exception as exc:
        return {"name": name, "available": False, "mode": "python_package", "detail": "%s: %s" % (type(exc).__name__, str(exc))}


def _probe_command(name: str) -> Dict[str, object]:
    resolved = shutil.which(name)
    if resolved:
        return {"name": name, "available": True, "mode": "command", "detail": resolved}
    return {"name": name, "available": False, "mode": "command", "detail": "not found"}


def build_environment_report() -> Dict[str, object]:
    solver_backends = [
        _probe_python_package("highspy"),
        _probe_python_package("osqp"),
        _probe_python_package("ortools"),
        _probe_python_package("pyscipopt"),
        _probe_python_package("ecole"),
        _probe_command("highs"),
        _probe_command("scip"),
    ]
    llm_backends = [
        {"mode": "mock", "available": True, "detail": "always available"},
        {"mode": "openai_compatible", "available": True, "detail": "requires configured base_url/model/api_key"},
    ]
    miplib_report: Dict[str, object] = {"list_path": "data/miplib/miplib_small.txt", "configured": False, "existing_files": 0, "missing_files": 0}
    list_path = miplib_report["list_path"]
    if os.path.exists(str(list_path)):
        miplib_report["configured"] = True
        paths = load_miplib_paths(str(list_path))
        miplib_report["listed_files"] = len(paths)
        miplib_report["existing_files"] = len([path for path in paths if os.path.exists(path)])
        miplib_report["missing_files"] = len(paths) - int(miplib_report["existing_files"])
    llm_lns_report = summarize_llm_lns_assets("data/llm_lns")
    return {
        "solver_backends": solver_backends,
        "llm_backends": llm_backends,
        "miplib": miplib_report,
        "llm_lns": llm_lns_report,
    }


def write_environment_report(report: Dict[str, object]) -> None:
    ensure_dir("results/real_experiments")
    dump_text("results/real_experiments/environment_report.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    lines: List[str] = ["# Environment Report", ""]
    lines.append("## Solver backends")
    lines.append("")
    lines.append("| Name | Mode | Available | Detail |")
    lines.append("| --- | --- | --- | --- |")
    for item in report["solver_backends"]:
        lines.append("| %s | %s | %s | %s |" % (item["name"], item["mode"], item["available"], item["detail"]))
    lines.append("")
    lines.append("## LLM backends")
    lines.append("")
    lines.append("| Mode | Available | Detail |")
    lines.append("| --- | --- | --- |")
    for item in report["llm_backends"]:
        lines.append("| %s | %s | %s |" % (item["mode"], item["available"], item["detail"]))
    miplib = report["miplib"]
    lines.append("")
    lines.append("## MIPLIB")
    lines.append("")
    lines.append("- list_path: %s" % miplib["list_path"])
    lines.append("- configured: %s" % miplib["configured"])
    lines.append("- existing_files: %s" % miplib["existing_files"])
    lines.append("- missing_files: %s" % miplib["missing_files"])
    llm_lns = report["llm_lns"]
    lines.append("")
    lines.append("## LLM-LNS")
    lines.append("")
    lines.append("- root: %s" % llm_lns["root"])
    lines.append("- lp_files: %s" % llm_lns["lp_files"])
    lines.append("- families: %s" % llm_lns["families"])
    dump_text("results/real_experiments/environment_report.md", "\n".join(lines) + "\n")


def main() -> None:
    report = build_environment_report()
    write_environment_report(report)
    print("Saved environment report to results/real_experiments/environment_report.json")


if __name__ == "__main__":
    main()
