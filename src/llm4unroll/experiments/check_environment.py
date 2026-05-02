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
        return {
            "name": name,
            "available": True,
            "mode": "python_package",
            "detail": "importable",
            "support_level": "native_verified",
            "paper_scale_pending": True,
        }
    except Exception as exc:
        return {
            "name": name,
            "available": False,
            "mode": "python_package",
            "detail": "%s: %s" % (type(exc).__name__, str(exc)),
            "support_level": "surrogate_only",
            "paper_scale_pending": True,
        }


def _probe_command(name: str) -> Dict[str, object]:
    resolved = shutil.which(name)
    if resolved:
        return {
            "name": name,
            "available": True,
            "mode": "command",
            "detail": resolved,
            "support_level": "native_verified",
            "paper_scale_pending": True,
        }
    return {
        "name": name,
        "available": False,
        "mode": "command",
        "detail": "not found",
        "support_level": "surrogate_only",
        "paper_scale_pending": True,
    }


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
    external_repos = [
        {"name": "LLM-LNS", "present": os.path.isdir("external/LLM-LNS")},
        {"name": "MILPBench", "present": os.path.isdir("external/MILPBench")},
        {"name": "HeuriGym", "present": os.path.isdir("external/heurigym")},
    ]
    return {
        "solver_backends": solver_backends,
        "llm_backends": llm_backends,
        "miplib": miplib_report,
        "llm_lns": llm_lns_report,
        "external_repos": external_repos,
    }


def write_environment_report(report: Dict[str, object]) -> None:
    ensure_dir("results/real_experiments")
    dump_text("results/real_experiments/environment_report.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    lines: List[str] = ["# Environment Report", ""]
    lines.append("## Solver backends")
    lines.append("")
    lines.append("| Name | Mode | Available | Support | Paper Pending | Detail |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for item in report["solver_backends"]:
        lines.append(
            "| %s | %s | %s | %s | %s | %s |"
            % (
                item["name"],
                item["mode"],
                item["available"],
                item.get("support_level", ""),
                item.get("paper_scale_pending", True),
                item["detail"],
            )
        )
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
    lines.append("- data_source: %s" % llm_lns.get("data_source", "unknown"))
    lines.append("- real_lp_files: %s" % llm_lns.get("real_lp_files", 0))
    lines.append("- real_levels: %s" % llm_lns.get("real_levels", {}))
    lines.append("- mock_lp_files: %s" % llm_lns.get("mock_lp_files", 0))
    lines.append("- families: %s" % llm_lns["families"])
    lines.append("- complete_phase2: %s" % llm_lns.get("complete_phase2", False))
    if llm_lns.get("missing_families"):
        lines.append("- missing_families: %s" % ", ".join(llm_lns["missing_families"]))
    lines.append("")
    lines.append("## External repos")
    lines.append("")
    for item in report.get("external_repos", []):
        lines.append("- %s: %s" % (item["name"], item["present"]))
    dump_text("results/real_experiments/environment_report.md", "\n".join(lines) + "\n")


def main() -> None:
    report = build_environment_report()
    write_environment_report(report)
    print("Saved environment report to results/real_experiments/environment_report.json")


if __name__ == "__main__":
    main()
