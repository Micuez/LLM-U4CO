from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Dict, List

from llm4unroll.utils import dump_text, ensure_dir


def _has_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def _probe_gurobi_license() -> Dict[str, object]:
    try:
        import gurobipy as gp

        version = tuple(int(item) for item in gp.gurobi.version())
        model = gp.Model()
        model.dispose()
        return {
            "available": True,
            "version": ".".join(str(item) for item in version),
            "detail": "model_create_ok",
        }
    except Exception as exc:
        return {
            "available": False,
            "version": "",
            "detail": "%s: %s" % (type(exc).__name__, str(exc)),
        }


def _repo_head(repo_root: str) -> str:
    head = Path(repo_root) / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    text = head.read_text(encoding="utf-8").strip()
    if not text.startswith("ref: "):
        return text
    ref = text.split(" ", 1)[1].strip()
    ref_path = Path(repo_root) / ".git" / ref
    return ref_path.read_text(encoding="utf-8").strip() if ref_path.exists() else ref


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return path.read_text(encoding="utf-8", errors="ignore")


def build_probe_rows() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    api_ready = bool(os.environ.get("LLM_API_KEY")) and bool(os.environ.get("LLM_API_ENDPOINT"))
    openai_ready = bool(os.environ.get("OPENAI_API_KEY")) and bool(os.environ.get("OPENAI_BASE_URL"))
    gurobi_license = _probe_gurobi_license()
    shared_modules = {
        "numpy": _has_module("numpy"),
        "joblib": _has_module("joblib"),
        "gurobipy": _has_module("gurobipy"),
    }
    targets = [
        {
            "label": "LLM-LNS SC exact repo script",
            "repo_root": "baselines/LLM-LNS",
            "entrypoint": "src/MILP Problems/SC_eoh_change_prompt_ACP.py",
            "problem_family": "llm_lns_sc",
        },
        {
            "label": "LLM-LNS IS exact repo script",
            "repo_root": "baselines/LLM-LNS",
            "entrypoint": "src/MILP Problems/IS_eoh_change_prompt_ACP.py",
            "problem_family": "llm_lns_is",
        },
        {
            "label": "LLM-LNS MVC exact repo script",
            "repo_root": "baselines/LLM-LNS",
            "entrypoint": "src/MILP Problems/MVC_eoh_change_prompt_ACP.py",
            "problem_family": "llm_lns_mvc",
        },
        {
            "label": "LLM-LNS MIKS exact repo script",
            "repo_root": "baselines/LLM-LNS",
            "entrypoint": "src/MILP Problems/MIKS_eoh_change_prompt_ACP.py",
            "problem_family": "llm_lns_miks",
        },
    ]
    for target in targets:
        repo_root = str(target["repo_root"])
        entrypoint = str(target["entrypoint"])
        abs_entry = os.path.join(repo_root, entrypoint)
        entry_path = Path(abs_entry)
        blockers: List[str] = []
        contains_placeholder_endpoint = False
        contains_placeholder_key = False
        if not entry_path.exists():
            blockers.append("entrypoint missing")
        else:
            text = _read_text(entry_path)
            contains_placeholder_endpoint = "your_llm_endpoint" in text
            contains_placeholder_key = "your_api_key" in text
            if contains_placeholder_endpoint or contains_placeholder_key:
                blockers.append("upstream script still contains placeholder API credentials")
        if not shared_modules["gurobipy"]:
            blockers.append("missing gurobipy")
        if shared_modules["gurobipy"] and not gurobi_license["available"]:
            blockers.append("gurobipy import works but license/model creation is unavailable")
        if not api_ready:
            blockers.append("missing LLM_API_KEY / LLM_API_ENDPOINT")
        rows.append(
            {
                "label": target["label"],
                "repo_root": repo_root,
                "repo_head": _repo_head(repo_root),
                "entrypoint": abs_entry,
                "problem_family": target["problem_family"],
                "exact_command": "python3 %s" % abs_entry,
                "api_ready": api_ready,
                "openai_compatible_ready": openai_ready,
                "module_numpy": shared_modules["numpy"],
                "module_joblib": shared_modules["joblib"],
                "module_gurobipy": shared_modules["gurobipy"],
                "gurobipy_license_ready": gurobi_license["available"],
                "gurobipy_version": gurobi_license["version"],
                "gurobipy_detail": gurobi_license["detail"],
                "contains_placeholder_endpoint": contains_placeholder_endpoint,
                "contains_placeholder_key": contains_placeholder_key,
                "can_attempt_exact_run": len(blockers) == 0,
                "blockers": blockers,
            }
        )
    return rows


def write_probe(rows: List[Dict[str, object]]) -> None:
    ensure_dir("results/real_experiments")
    payload = {"rows": rows}
    dump_text(
        "results/real_experiments/external_repo_exact_probe.json",
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    lines = ["# External Repo Exact Probe", ""]
    lines.append("| Target | Problem | Can Attempt Exact Run | Repo Head | Main Blockers |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in rows:
        blockers = ", ".join(row["blockers"]) if row["blockers"] else "none"
        lines.append(
            "| %s | %s | %s | %s | %s |"
            % (
                row["label"],
                row["problem_family"],
                row["can_attempt_exact_run"],
                row["repo_head"],
                blockers,
            )
        )
    lines.append("")
    lines.append("## Probe notes")
    lines.append("")
    lines.append("- `gurobipy` probe checks both importability and `gp.Model()` creation.")
    lines.append("- `can_attempt_exact_run=True` requires real `LLM_API_KEY` / `LLM_API_ENDPOINT` and no placeholder API credentials left in the upstream script body.")
    lines.append("")
    lines.append("## Exact commands")
    lines.append("")
    for row in rows:
        lines.append("- `%s`" % row["exact_command"])
    dump_text("results/real_experiments/external_repo_exact_probe.md", "\n".join(lines) + "\n")


def main() -> None:
    rows = build_probe_rows()
    write_probe(rows)
    print("Saved external repo exact probe to results/real_experiments/external_repo_exact_probe.json")


if __name__ == "__main__":
    main()
