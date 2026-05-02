from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path
from typing import Dict, List

from llm4unroll.utils import dump_text, ensure_dir


def _probe_import(name: str) -> Dict[str, object]:
    try:
        importlib.import_module(name)
        return {"name": name, "available": True, "detail": "importable"}
    except Exception as exc:
        return {"name": name, "available": False, "detail": "%s: %s" % (type(exc).__name__, str(exc))}


def build_report() -> Dict[str, object]:
    ecole_import = _probe_import("ecole")
    pyscipopt_import = _probe_import("pyscipopt")
    scip_cmd = shutil.which("scip")
    highs_cmd = shutil.which("highs")
    ecole_stub = Path(".vendor/ecole-0.0.1.dist-info").exists() and not bool(ecole_import["available"])
    ecole_detail = str(ecole_import["detail"])
    if ecole_stub:
        ecole_detail += "; pip only left a same-name `ecole==0.0.1` dist-info stub, not the SCIP/Ecole module"

    rows: List[Dict[str, object]] = [
        {
            "component": "PySCIPOpt package",
            "status": "available" if pyscipopt_import["available"] else "missing",
            "detail": pyscipopt_import["detail"],
            "blocking": False,
        },
        {
            "component": "Ecole package",
            "status": "available" if ecole_import["available"] else "missing",
            "detail": ecole_detail,
            "blocking": not ecole_import["available"],
        },
        {
            "component": "SCIP command",
            "status": "available" if scip_cmd else "missing",
            "detail": scip_cmd or "not found on PATH",
            "blocking": scip_cmd is None,
        },
        {
            "component": "HiGHS command",
            "status": "available" if highs_cmd else "missing",
            "detail": highs_cmd or "not found on PATH",
            "blocking": False,
        },
    ]

    blockers: List[str] = []
    if not ecole_import["available"]:
        blockers.append(
            "Ecole is still not importable locally; the latest native install attempt fails in PEP517 metadata with missing `skbuild`, prior attempts also hit deeper CMake/xtl toolchain issues, and pip only left a non-importable same-name `ecole==0.0.1` stub."
        )
    if scip_cmd is None:
        blockers.append("SCIP command-line binary is still absent, so command-backed native SCIP validation cannot run even though PySCIPOpt is importable.")

    return {
        "rows": rows,
        "blockers": blockers,
    }


def write_report(report: Dict[str, object]) -> None:
    ensure_dir("results/real_experiments")
    dump_text(
        "results/real_experiments/native_installation_blockers.json",
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
    )
    lines = ["# Native Installation Blockers", ""]
    lines.append("| Component | Status | Blocking | Detail |")
    lines.append("| --- | --- | --- | --- |")
    for row in report["rows"]:
        lines.append(
            "| %s | %s | %s | %s |"
            % (
                row["component"],
                row["status"],
                row["blocking"],
                row["detail"],
            )
        )
    lines.append("")
    lines.append("## Remaining blockers")
    lines.append("")
    for item in report["blockers"]:
        lines.append("- %s" % item)
    if not report["blockers"]:
        lines.append("- none")
    dump_text("results/real_experiments/native_installation_blockers.md", "\n".join(lines) + "\n")


def main() -> None:
    report = build_report()
    write_report(report)
    print("Saved native installation blocker report to results/real_experiments/native_installation_blockers.json")


if __name__ == "__main__":
    main()
