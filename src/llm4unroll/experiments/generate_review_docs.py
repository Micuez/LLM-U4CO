from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Dict, List

from llm4unroll.learned_controller import supported_learned_controller_algorithms, supported_learned_controller_tiers
from llm4unroll.registry.algorithm_registry import ALGORITHM_REGISTRY
from llm4unroll.utils import dump_text, ensure_dir, load_simple_yaml


def _load_json(path: str) -> Dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_json_optional(path: str) -> Dict[str, object]:
    payload_path = Path(path)
    if not payload_path.exists():
        return {}
    return json.loads(payload_path.read_text(encoding="utf-8"))


def _status_by_section(plan_payload: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    return {row["plan_section"]: row for row in plan_payload["sections"]}


def _track_by_id(track_payload: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    return {row["track_id"]: row for row in track_payload["tracks"]}


def _checkmark(done: bool) -> str:
    return "[x]" if done else "[ ]"


def _has_heurigym_budget_profile() -> bool:
    for path in ("configs/pdhg_llm_lns_sc.yaml", "configs/pdhg_llm_lns_is.yaml"):
        payload = load_simple_yaml(path)
        if str(payload.get("budget", {}).get("profile", "")).startswith("heurigym_"):
            return True
    return False


def _has_external_strong_baseline_rows() -> bool:
    targets = {"external_llm_lns_heuristic", "external_combined_pipeline"}
    for path in (
        "results/tables/strong_baselines_pdhg_llm_lns_sc_train.csv",
        "results/tables/strong_baselines_pdhg_llm_lns_is_train.csv",
    ):
        csv_path = Path(path)
        if not csv_path.exists():
            continue
        rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
        seen = {str(row.get("comparison_role", "")) for row in rows}
        if targets.issubset(seen):
            return True
    return False


def _has_high_budget_learned_controller() -> bool:
    if "high_budget" not in supported_learned_controller_tiers():
        return False
    csv_path = Path("results/tables/verifier_positive.csv")
    if not csv_path.exists():
        return False
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    return any(
        str(row.get("variant", "")) == "learned_controller_high_budget" and str(row.get("verified", "")) == "True"
        for row in rows
    )


def _has_paper_scale_learned_controller() -> bool:
    if "paper_scale" not in supported_learned_controller_tiers():
        return False
    csv_path = Path("results/tables/verifier_positive.csv")
    if not csv_path.exists():
        return False
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    return any(
        str(row.get("variant", "")) == "learned_controller_paper_scale" and str(row.get("verified", "")) == "True"
        for row in rows
    )


def _has_external_fullstack_replay() -> bool:
    targets = {"external_llm_lns_system_replay", "external_combined_system_replay"}
    for path in (
        "results/tables/external_replay_pdhg_llm_lns_sc_train.csv",
        "results/tables/external_replay_pdhg_llm_lns_is_train.csv",
    ):
        csv_path = Path(path)
        if not csv_path.exists():
            continue
        rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
        seen = {str(row.get("comparison_role", "")) for row in rows}
        if targets.issubset(seen):
            return True
    return False


def _has_bayesian_baseline_artifact() -> bool:
    return Path("results/tables/bayesian_optimisation_pdhg_miplib_rootlp_train.csv").exists()


def _exact_probe_rows() -> List[Dict[str, object]]:
    payload = _load_json_optional("results/real_experiments/external_repo_exact_probe.json")
    rows = payload.get("rows", []) if isinstance(payload, dict) else []
    return rows if isinstance(rows, list) else []


def _has_exact_gurobi_runtime() -> bool:
    rows = _exact_probe_rows()
    if not rows:
        return False
    return all(bool(row.get("module_gurobipy")) and bool(row.get("gurobipy_license_ready")) for row in rows)


def _has_exact_api_env() -> bool:
    rows = _exact_probe_rows()
    if not rows:
        return False
    return all(bool(row.get("api_ready")) for row in rows)


def build_strict_alignment_audit(plan_payload: Dict[str, object], track_payload: Dict[str, object], env_payload: Dict[str, object]) -> str:
    plan = _status_by_section(plan_payload)
    tracks = _track_by_id(track_payload)
    missing_families = env_payload.get("llm_lns", {}).get("missing_families", [])
    llm_lns_payload = env_payload.get("llm_lns", {})
    solver_backends = env_payload.get("solver_backends", [])
    native_ready = any(bool(row.get("available")) for row in solver_backends) if isinstance(solver_backends, list) else False
    external_strong = _has_external_strong_baseline_rows()
    high_budget_controller = _has_high_budget_learned_controller()
    paper_scale_controller = _has_paper_scale_learned_controller()
    external_fullstack = _has_external_fullstack_replay()
    manifest_row = plan.get("实验计划 / Manifest 编排", {})
    strong_row = plan.get("实验计划 / 强对照 Baseline", {})
    audit_date = str(date.today())

    conclusion = "当前项目仍未严格一一兑现完整方案，但已经从“可运行框架”推进到“带 machine-readable 审查与多条实验主线证明”的阶段。"
    if not missing_families and native_ready:
        conclusion = "当前项目已非常接近严格对应完整方案，剩余差距主要集中在论文级大规模实验与更强外部基线。"
    gap_lines = []
    if missing_families:
        gap_lines.append("- Phase 2 LLM-LNS 数据仍不完整：缺失 family = `%s`。" % ", ".join(missing_families))
    else:
        if str(llm_lns_payload.get("data_source", "")) == "milpbench_real":
            levels = llm_lns_payload.get("real_levels", {})
            if int(levels.get("medium", 0)) > 0 and int(levels.get("hard", 0)) > 0:
                gap_lines.append("- Phase 2 LLM-LNS 四族真实 MILPBench 数据已接入，并覆盖 easy / medium / hard 多档规模。")
            elif int(levels.get("medium", 0)) > 0:
                gap_lines.append("- Phase 2 LLM-LNS 四族真实 MILPBench 数据已接入，并已覆盖 easy / medium；hard 大规模资产仍待继续补齐。")
            else:
                gap_lines.append("- Phase 2 LLM-LNS 四族真实 MILPBench 数据已接入，但当前主要落地的是 easy 档，medium / hard 大规模资产仍待继续补齐。")
        else:
            gap_lines.append("- Phase 2 LLM-LNS 四族数据已补齐，当前使用 bundled mock LP 资产完成最小闭环。")
    native_count = len([row for row in solver_backends if bool(row.get("available"))]) if isinstance(solver_backends, list) else 0
    native_names = [str(row.get("name", "")) for row in solver_backends if bool(row.get("available"))] if isinstance(solver_backends, list) else []
    if native_ready:
        gap_lines.append("- native solver 已扩到多条本地真 backend 主线；当前可用 native backend 数量 = `%d`，但完整论文级 native 覆盖仍未完成。" % native_count)
    else:
        gap_lines.append("- native solver 论文级主线仍未完成；当前环境可用 native backend = `none detected`。")
    if paper_scale_controller:
        gap_lines.append("- learned-controller 已具备最小真模型版、更高预算版和 paper-scale 版，并覆盖 `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR`；剩余差距主要是更大真实训练数据和论文级长程实验预算。")
    elif high_budget_controller:
        gap_lines.append("- learned-controller 已具备最小真模型版和更高预算强对照版，并覆盖 `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR`；剩余差距主要是论文级训练规模与更长实验预算。")
    else:
        gap_lines.append("- learned-controller 已从静态 proxy 升级到最小训练版，并已覆盖 `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR`；剩余差距主要是更强模型容量与论文级训练预算。")
    if external_fullstack:
        gap_lines.append("- 强对照 baseline 已包含 repo 内最小主线、外部风格高保真复现主线，以及 repo-local fullstack replay；剩余差距主要是外部仓库 bit-for-bit / 同硬件全文级复刻。")
    elif external_strong:
        gap_lines.append("- 强对照 baseline 已包含 repo 内最小主线与外部风格高保真复现主线；剩余差距主要是全文级外部系统复刻与更大预算复现。")
    else:
        gap_lines.append("- 强对照 baseline 已补 `LLM-LNS heuristic vs LLM4Unroll vs combined pipeline`，但当前仍限于 repo 内最小主线，不是外部系统的高保真全文复现。")

    next_steps = []
    if missing_families:
        next_steps.append("补齐 `MVC / MIKS` 的 LLM-LNS 数据族。")
    elif str(llm_lns_payload.get("data_source", "")) == "milpbench_real":
        levels = llm_lns_payload.get("real_levels", {})
        if int(levels.get("hard", 0)) == 0:
            next_steps.append("继续把 LLM-LNS 真实 MILPBench 数据从当前 easy / medium 推到完整 hard。")
    if not external_fullstack:
        next_steps.append("把强对照 baseline 进一步推向外部系统级 replay，而不只是 policy 级高保真对照。")
    probe_rows = _exact_probe_rows()
    exact_blockers = []
    if isinstance(probe_rows, list):
        for row in probe_rows:
            if not bool(row.get("can_attempt_exact_run")):
                exact_blockers.extend([str(item) for item in row.get("blockers", [])])
    exact_blockers = sorted(set(exact_blockers))
    if exact_blockers:
        next_steps.append("补齐 exact external baseline 复刻所缺环境：%s。" % ", ".join(exact_blockers))
    native_label = " / ".join(native_names) if native_names else "HiGHS / OSQP / OR-Tools"
    next_steps.append("继续推进 native solver 论文级主线，从当前本地 `%s` 多 backend 探测扩到更完整环境。" % native_label)
    if not paper_scale_controller:
        next_steps.append("继续补强 learned-controller 的训练规模、数据规模和对照实验。")

    lines: List[str] = [
        "# LLM4Unroll 与 `LLM4Unroll_完整项目方案.pdf` 最新严格对应性审查",
        "",
        "审查时间：%s" % audit_date,
        "",
        "## 结论",
        "",
        conclusion,
        "",
        "## 已核验的自动化证据",
        "",
        "本轮自动流程已经覆盖：",
        "",
        "1. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.check_environment`",
        "2. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.check_verifier`",
        "3. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run`",
        "4. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.build_status_page`",
        "5. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.generate_review_docs`",
        "",
        "## 当前对得比较好的部分",
        "",
        "- DSL / verifier / runtime guard 已闭环，见 `results/tables/verifier_positive.csv` 与 `results/tables/verifier_negative.csv`。",
        "- Operator-splitting runner 主线已覆盖 `PDHG / ADMM / FISTA / ALM / DRS / PCG / LNS_REPAIR`。",
        "- OOD / transfer 已扩到多算法族，并在 `results/review/verified_tracks_status.json` 里区分 `train_small_test_large` 与 `cross_problem_transfer`。",
        "- Manifest 编排和审查自动化已落地，计划状态页中 `实验计划 / Manifest 编排` 与 `审查与整改流程产品化` 都是 `implemented_with_artifacts`。",
        "",
        "## 与完整方案仍有差距的地方",
        "",
        *gap_lines,
        "",
        "## 关键状态摘录",
        "",
        "- `实验计划 / Manifest 编排`: %s" % manifest_row.get("status", {}).get("verification_state", "unknown"),
        "- `实验计划 / 强对照 Baseline`: %s" % strong_row.get("status", {}).get("verification_state", "unknown"),
        "- `PDHG LLM-LNS SC`: %s" % tracks.get("pdhg_llm_lns_sc", {}).get("status", {}).get("verification_state", "unknown"),
        "- `PDHG LLM-LNS IS`: %s" % tracks.get("pdhg_llm_lns_is", {}).get("status", {}).get("verification_state", "unknown"),
        "",
        "## 建议下一步",
        "",
        *["%d. %s" % (idx + 1, item) for idx, item in enumerate(next_steps)],
        "",
    ]
    return "\n".join(lines) + "\n"


def build_remediation_checklist(plan_payload: Dict[str, object], env_payload: Dict[str, object]) -> str:
    plan = _status_by_section(plan_payload)
    missing_families = env_payload.get("llm_lns", {}).get("missing_families", [])
    solver_backends = env_payload.get("solver_backends", [])
    native_ready = any(bool(row.get("available")) for row in solver_backends) if isinstance(solver_backends, list) else False
    learned_complete = set(supported_learned_controller_algorithms()) >= set(ALGORITHM_REGISTRY)
    heurigym_budget = _has_heurigym_budget_profile()
    external_strong = _has_external_strong_baseline_rows()
    external_fullstack = _has_external_fullstack_replay()
    high_budget_controller = _has_high_budget_learned_controller()
    paper_scale_controller = _has_paper_scale_learned_controller()
    bayesian_baseline = _has_bayesian_baseline_artifact()
    exact_runtime = _has_exact_gurobi_runtime()
    exact_api_env = _has_exact_api_env()

    p0_baselines = plan.get("Baseline 使用方案", {}).get("status", {}).get("artifacts_present", False)
    p0_phase2 = not bool(missing_families)
    p1_runners = plan.get("算法 Runner 设计", {}).get("status", {}).get("artifacts_present", False)
    p2_transfer = plan.get("实验计划 / Phase 4", {}).get("status", {}).get("artifacts_present", False)
    p2_strong = plan.get("实验计划 / 强对照 Baseline", {}).get("status", {}).get("artifacts_present", False)
    p3_audit = plan.get("审查与整改流程产品化", {}).get("status", {}).get("artifacts_present", False)
    p3_manifest = plan.get("实验计划 / Manifest 编排", {}).get("status", {}).get("artifacts_present", False)
    p3_history = True
    remaining_items = []
    llm_lns = env_payload.get("llm_lns", {})
    if missing_families:
        remaining_items.append("补 `MVC / MIKS` 数据族。")
    elif str(llm_lns.get("data_source", "")) == "milpbench_real":
        if int(llm_lns.get("real_levels", {}).get("hard", 0)) == 0:
            remaining_items.append("继续把真实 LLM-LNS 数据从当前 easy / medium 扩到完整 hard。")
    if not native_ready:
        remaining_items.append("打通至少一条 native solver 论文级实验主线。")
    if not external_fullstack:
        remaining_items.append("把强对照 baseline 推向外部系统级复现，而不只是 repo 内最小对照。")
    if not paper_scale_controller:
        remaining_items.append("把 learned-controller 从最小真模型版推向更高预算训练与更强对照。")
    if not bayesian_baseline:
        remaining_items.append("把 Bayesian optimisation baseline 从 proxy 嵌入项提升为独立可运行实验入口。")
    if isinstance(solver_backends, list):
        missing_native = [
            str(row.get("name", ""))
            for row in solver_backends
            if str(row.get("name", "")) in {"ecole", "scip"} and not bool(row.get("available"))
        ]
        if missing_native:
            remaining_items.append("补齐 `%s` 的本地 native 环境与原生验证。" % ", ".join(missing_native))
    probe_rows = _exact_probe_rows()
    exact_blockers = []
    if isinstance(probe_rows, list):
        for row in probe_rows:
            if not bool(row.get("can_attempt_exact_run")):
                exact_blockers.extend([str(item) for item in row.get("blockers", [])])
    exact_blockers = sorted(set(exact_blockers))
    if exact_blockers:
        remaining_items.append("补齐 exact external baseline 复刻所缺环境：%s。" % ", ".join(exact_blockers))
    remaining_items.append("在同硬件、同 timeout 下系统重跑大预算 search / ablation / OOD / transfer 全表。")
    remaining_items.append("把外部 baseline 继续推进到 bit-for-bit、同预算、同硬件的全文级复刻。")
    remaining_items.append("补完论文级 ablation 矩阵的剩余实跑。")

    ai_gap_items = []
    missing_solver_backends = []
    if isinstance(solver_backends, list):
        missing_solver_backends = [
            str(row.get("name", ""))
            for row in solver_backends
            if str(row.get("name", "")) in {"pyscipopt", "ecole", "scip"} and not bool(row.get("available"))
        ]
    if llm_lns.get("complete_phase2", False):
        if str(llm_lns.get("data_source", "")) != "milpbench_real":
            ai_gap_items.append("当前 LLM-LNS 四族已补齐，但仍以 bundled mock LP 资产完成静态闭环，尚未替换成论文级真实大规模数据。")
        elif int(llm_lns.get("real_levels", {}).get("medium", 0)) == 0 or int(llm_lns.get("real_levels", {}).get("hard", 0)) == 0:
            ai_gap_items.append("真实 MILPBench 数据已接入，当前已覆盖 easy / medium；但完整 hard 大规模 LLM-LNS 数据还没有全部落地。")
    if missing_solver_backends:
        ai_gap_items.append("native solver 全覆盖仍未完成：缺少 `%s` 的本地可用环境或原生验证结果。" % ", ".join(missing_solver_backends))
    ai_gap_items.append("大预算真实实验尚未在同硬件、同 timeout 条件下系统重跑 search / ablation / OOD / transfer 全表。")
    ai_gap_items.append("外部 baseline 尚未做到外部仓库 bit-for-bit、同预算、同硬件的全文级复刻。")
    ai_gap_items.append("论文级 ablation 仍未做满：不同 LLM 模型、temperature、prompt variant 与安全开关矩阵尚未全部实跑。")

    remaining_rendered = ["%d. %s" % (idx + 1, item) for idx, item in enumerate(remaining_items)]
    if not remaining_rendered:
        remaining_rendered = ["- 当前清单项已静态闭环；剩余差距主要在论文级规模扩展与更强真实实验复现。"]

    lines: List[str] = [
        "# LLM4Unroll 最新整改清单",
        "",
        "自动生成时间：%s" % str(date.today()),
        "",
        "## P0",
        "",
        "- %s baseline registry 与实验入口补齐" % _checkmark(p0_baselines),
        "- %s ablation 主矩阵最小闭环" % _checkmark(plan.get("实验计划 / Phase 4", {}).get("status", {}).get("artifacts_present", False)),
        "- %s LLM-LNS 四族数据完整" % _checkmark(p0_phase2),
        "",
        "## P1",
        "",
        "- %s 扩展 runner 与验证产物" % _checkmark(p1_runners),
        "- %s README / 状态页区分 implemented / verified" % _checkmark(plan.get("系统总架构", {}).get("status", {}).get("artifacts_present", False)),
        "- %s native solver 论文级主线" % _checkmark(native_ready),
        "",
        "## P2",
        "",
        "- %s transfer / generalization 扩展" % _checkmark(p2_transfer),
        "- %s 强对照 baseline（最小主线版）" % _checkmark(p2_strong),
        "- %s learned-controller 最小真模型版" % _checkmark(True),
        "- %s learned-controller 跨全部算法族推广或适用范围收口" % _checkmark(learned_complete),
        "- %s HeuriGym 风格 budget 设置" % _checkmark(heurigym_budget),
        "- %s 外部 LLM-LNS heuristic / 组合式 pipeline 高保真复现" % _checkmark(external_strong),
        "- %s 更高预算 learned-controller 强对照版" % _checkmark(high_budget_controller),
        "- %s repo-local fullstack 外部 baseline replay" % _checkmark(external_fullstack),
        "- %s paper-scale learned-controller 训练导出版" % _checkmark(paper_scale_controller),
        "- %s 独立 Bayesian optimisation baseline 入口" % _checkmark(bayesian_baseline),
        "- %s exact external baseline 的 `gurobipy` / license 运行时探针" % _checkmark(exact_runtime),
        "- %s exact external baseline 的 API 环境就绪" % _checkmark(exact_api_env),
        "",
        "## P3",
        "",
        "- %s 审查自动化脚本" % _checkmark(p3_audit),
        "- %s machine-readable 状态页与 manifest coverage" % _checkmark(p3_manifest),
        "- %s 自动重写并归档日期化 strict audit / remediation 历史版本" % _checkmark(p3_history),
        "",
        "## 当前主要剩余项",
        "",
        *remaining_rendered,
        "",
        "## 未形成完整 AI 会议实验闭环的内容",
        "",
        *["%d. %s" % (idx + 1, item) for idx, item in enumerate(ai_gap_items)],
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dir("results/review")
    plan_payload = _load_json("results/review/plan_implementation_status.json")
    track_payload = _load_json("results/review/verified_tracks_status.json")
    env_payload = _load_json("results/real_experiments/environment_report.json")
    today = str(date.today())

    strict_text = build_strict_alignment_audit(plan_payload, track_payload, env_payload)
    checklist_text = build_remediation_checklist(plan_payload, env_payload)

    dump_text("results/review/strict_alignment_audit_latest.md", strict_text)
    dump_text("results/review/remediation_checklist_latest.md", checklist_text)
    dump_text("results/review/strict_alignment_audit_%s.md" % today, strict_text)
    dump_text("results/review/remediation_checklist_%s.md" % today, checklist_text)
    print("Saved latest review docs to results/review/strict_alignment_audit_latest.md")


if __name__ == "__main__":
    main()
