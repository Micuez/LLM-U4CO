from __future__ import annotations

import csv
import glob
import math
from string import Template
from typing import Dict, Iterable, List, Sequence, Tuple

from llm4unroll.utils import dump_text, ensure_dir, write_csv

SVG_WIDTH = 1080
SVG_HEIGHT = 640
CHART_LEFT = 84
CHART_RIGHT = 28
CHART_TOP = 80
CHART_BOTTOM = 112
PALETTE = [
    "#2563eb",
    "#f97316",
    "#16a34a",
    "#dc2626",
    "#7c3aed",
    "#0891b2",
    "#ca8a04",
    "#db2777",
]


def write_phase1_table(path: str, rows: List[Dict[str, object]]) -> None:
    write_csv(path, rows)


def write_candidate_archive(path: str, payload: Dict[str, object]) -> None:
    lines = []
    for key, value in payload.items():
        lines.append("%s: %s" % (key, value))
    dump_text(path, "\n".join(lines) + "\n")


def write_markdown_summary(path: str, title: str, rows: List[Dict[str, object]]) -> None:
    if not rows:
        dump_text(path, "# %s\n\nNo rows.\n" % title)
        return
    headers = _collect_headers(rows)
    lines = ["# %s" % title, "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    dump_text(path, "\n".join(lines) + "\n")


def write_failure_analysis(path: str, rows: List[Dict[str, object]]) -> None:
    failed = [row for row in rows if float(row.get("fail_rate", 0.0) or 0.0) > 0.0]
    lines = ["# Failure Analysis", ""]
    if not failed:
        lines.append("No failing candidates in this run.")
    else:
        for row in failed:
            lines.append("- %s / %s fail_rate=%s" % (row.get("problem_family"), row.get("policy_id"), row.get("fail_rate")))
    dump_text(path, "\n".join(lines) + "\n")


def write_minimal_pdf(path: str, title: str, body_lines: List[str]) -> None:
    ensure_dir(path.rsplit("/", 1)[0])
    text = "%s\n%s" % (title, "\n".join(body_lines))
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = "BT /F1 12 Tf 50 760 Td (%s) Tj ET" % safe.replace("\n", ") Tj T* (")
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        "5 0 obj << /Length %d >> stream\n%s\nendstream endobj" % (len(content), content),
    ]
    pdf = ["%PDF-1.4"]
    offsets = [0]
    for obj in objects:
        offsets.append(sum(len(part) + 1 for part in pdf))
        pdf.append(obj)
    xref_pos = sum(len(part) + 1 for part in pdf)
    pdf.append("xref")
    pdf.append("0 6")
    pdf.append("0000000000 65535 f ")
    for offset in offsets[1:]:
        pdf.append("%010d 00000 n " % offset)
    pdf.append("trailer << /Root 1 0 R /Size 6 >>")
    pdf.append("startxref")
    pdf.append(str(xref_pos))
    pdf.append("%%EOF")
    dump_text(path, "\n".join(pdf))


def load_table_rows(path: str) -> List[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as handle:
        return [_coerce_row(row) for row in csv.DictReader(handle)]


def write_table_chart(path: str) -> List[str]:
    figure_paths = []
    if not path.endswith(".csv"):
        return figure_paths
    rows = load_table_rows(path)
    if not rows:
        return figure_paths
    basename = path.rsplit("/", 1)[-1][:-4]
    out_dir = "results/figures"
    ensure_dir(out_dir)

    if basename == "verifier_positive":
        coverage_path = "%s/%s_feature_coverage.svg" % (out_dir, basename)
        proof_path = "%s/%s_proof_count.svg" % (out_dir, basename)
        _write_categorical_bar_figure(coverage_path, "Verifier Feature Coverage", rows, "policy_id", "feature_coverage", "algorithm")
        _write_categorical_bar_figure(proof_path, "Verifier Proof Count", rows, "policy_id", "proof_count", "algorithm")
        return [coverage_path, proof_path]
    if basename == "verifier_negative":
        summary_path = "%s/%s_summary.svg" % (out_dir, basename)
        _write_categorical_bar_figure(summary_path, "Verifier Negative Cases", rows, "case_id", "blocked_flag", "status")
        return [summary_path]

    if (
        basename.startswith("search_archive_")
        or (basename.startswith("random_search_") and basename.endswith("_archive"))
        or (basename.startswith("evolution_no_llm_") and basename.endswith("_archive"))
    ):
        figure_path = "%s/%s_score_trend.svg" % (out_dir, basename)
        _write_search_archive_figure(figure_path, basename, rows)
        return [figure_path]
    if basename.startswith("search_") or basename.startswith("random_search_") or basename.startswith("evolution_no_llm_"):
        score_path = "%s/%s_score.svg" % (out_dir, basename)
        gap_path = "%s/%s_gap.svg" % (out_dir, basename)
        _write_categorical_bar_figure(score_path, "Search Score", rows, "policy_id", "score", "origin")
        _write_categorical_bar_figure(gap_path, "Search Median Gap", rows, "policy_id", "median_gap", "origin")
        figure_paths.extend([score_path, gap_path])
        figure_paths.extend(_maybe_write_verifier_metric_figures(out_dir, basename, rows, "policy_id", "origin"))
        return figure_paths
    if basename.startswith("ood_"):
        score_path = "%s/%s_score.svg" % (out_dir, basename)
        gap_path = "%s/%s_gap.svg" % (out_dir, basename)
        _write_grouped_bar_figure(score_path, "OOD Score", rows, "split", "policy_id", "score")
        _write_grouped_bar_figure(gap_path, "OOD Median Gap", rows, "split", "policy_id", "median_gap")
        figure_paths.extend([score_path, gap_path])
        figure_paths.extend(_maybe_write_verifier_metric_figures(out_dir, basename, rows, "policy_id", "split"))
        return figure_paths
    if basename.startswith("ablation_"):
        score_path = "%s/%s_score.svg" % (out_dir, basename)
        gap_path = "%s/%s_gap.svg" % (out_dir, basename)
        _write_grouped_bar_figure(score_path, "Ablation Score", rows, "variant", "policy_id", "score")
        _write_grouped_bar_figure(gap_path, "Ablation Median Gap", rows, "variant", "policy_id", "median_gap")
        figure_paths.extend([score_path, gap_path])
        figure_paths.extend(_maybe_write_verifier_metric_figures(out_dir, basename, rows, "policy_id", "variant"))
        return figure_paths
    if basename in {"phase1", "phase2_llm_lns"} or basename.endswith("_train") or basename in {
        "admm_admm_qp",
        "fista_fista_lasso",
        "pdhg_pdhg_lp",
        "pdhg_llm_lns_is",
        "pdhg_llm_lns_sc",
    }:
        score_path = "%s/%s_score.svg" % (out_dir, basename)
        gap_path = "%s/%s_gap.svg" % (out_dir, basename)
        category_key = "policy_id"
        if basename in {"phase1", "phase2_llm_lns"}:
            category_key = "problem_family"
        _write_categorical_bar_figure(score_path, "Baseline Score", rows, category_key, "score", "origin")
        _write_categorical_bar_figure(gap_path, "Baseline Median Gap", rows, category_key, "median_gap", "origin")
        figure_paths.extend([score_path, gap_path])
        figure_paths.extend(_maybe_write_verifier_metric_figures(out_dir, basename, rows, category_key, "origin"))
        return figure_paths
    return figure_paths


def build_report_figures(table_glob: str = "results/tables/*.csv") -> List[str]:
    outputs = []
    backend_tables: List[Tuple[str, List[Dict[str, object]]]] = []
    for path in sorted(glob.glob(table_glob)):
        outputs.extend(write_table_chart(path))
        rows = load_table_rows(path)
        if _has_solver_backend_rows(rows):
            backend_tables.append((path, rows))
    if backend_tables:
        backend_report_path = "results/figures/native_backend_report.html"
        write_native_backend_report_html(backend_report_path, backend_tables)
        outputs.append(backend_report_path)
    if outputs:
        _write_figure_index("results/figures/index.md", outputs)
    return outputs


def write_native_backend_report_html(path: str, table_rows: Sequence[Tuple[str, List[Dict[str, object]]]]) -> None:
    summaries = []
    total_solver_rows = 0
    total_native_rows = 0
    for table_path, rows in table_rows:
        solver_rows = [row for row in rows if _label(row.get("origin")) == "solver_baseline"]
        native_rows = [row for row in solver_rows if bool(row.get("native_used"))]
        total_solver_rows += len(solver_rows)
        total_native_rows += len(native_rows)
        summaries.append({
            "name": table_path.rsplit("/", 1)[-1][:-4],
            "solver_rows": solver_rows,
            "native_rows": native_rows,
        })

    html = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Native Backend Usage</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }
    .page { max-width: 1180px; margin: 0 auto; padding: 28px 24px 40px; }
    h1, h2 { margin: 0; font-weight: 600; }
    h1 { font-size: 30px; margin-bottom: 10px; }
    h2 { font-size: 18px; margin: 0 0 10px; }
    p { margin: 0; color: #334155; line-height: 1.5; }
    .stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 22px 0 28px; }
    .stat { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 18px; }
    .label { font-size: 12px; color: #64748b; margin-bottom: 8px; }
    .value { font-size: 24px; color: #0f172a; }
    .panel { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-top: 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { padding: 9px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; vertical-align: top; font-size: 13px; }
    th { background: #f1f5f9; color: #0f172a; }
    tr:last-child td { border-bottom: 0; }
    .mono { font-family: Menlo, Consolas, monospace; }
    .ok { color: #166534; font-weight: 600; }
    .no { color: #991b1b; font-weight: 600; }
    @media (max-width: 900px) { .stats { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="page">
    <h1>Native Backend Usage</h1>
    <p>Summary of which solver baseline rows used real native backends versus surrogate fallback. This page is intended for appendix screenshots and experiment bookkeeping.</p>
    <div class="stats">
      <div class="stat"><div class="label">Baseline Tables</div><div class="value">$table_count</div></div>
      <div class="stat"><div class="label">Solver Rows</div><div class="value">$solver_rows</div></div>
      <div class="stat"><div class="label">Native Active</div><div class="value">$native_rows</div></div>
    </div>
    $panels
  </div>
</body>
</html>
""").substitute(
        table_count=len(summaries),
        solver_rows=total_solver_rows,
        native_rows=total_native_rows,
        panels="".join(_native_backend_panel_html(item) for item in summaries),
    )
    dump_text(path, html)


def write_verifier_report_html(path: str) -> None:
    positive_rows = load_table_rows("results/tables/verifier_positive.csv")
    negative_rows = load_table_rows("results/tables/verifier_negative.csv")
    positive_count = len(positive_rows)
    verified_count = len([row for row in positive_rows if bool(row.get("verified"))])
    mean_coverage = 0.0
    coverage_values = [_to_float(row.get("feature_coverage")) for row in positive_rows]
    coverage_values = [value for value in coverage_values if value is not None]
    if coverage_values:
        mean_coverage = sum(coverage_values) / float(len(coverage_values))
    blocked_count = len([row for row in negative_rows if int(_to_float(row.get("blocked_flag")) or 0.0) == 1])

    top_positive = sorted(
        positive_rows,
        key=lambda row: (
            -float(_to_float(row.get("feature_coverage")) or 0.0),
            -float(_to_float(row.get("proof_count")) or 0.0),
            _label(row.get("algorithm")),
        ),
    )[:8]

    html = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Verifier Report</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }
    .page { max-width: 1180px; margin: 0 auto; padding: 32px 24px 48px; }
    h1, h2, h3 { margin: 0; font-weight: 600; }
    p { margin: 0; line-height: 1.5; color: #334155; }
    .hero { padding: 20px 0 28px; }
    .hero h1 { font-size: 30px; margin-bottom: 10px; }
    .hero p { max-width: 820px; }
    .stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 24px 0 30px; }
    .stat { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 18px; }
    .stat .label { font-size: 12px; color: #64748b; margin-bottom: 8px; }
    .stat .value { font-size: 24px; color: #0f172a; }
    .section { margin-top: 28px; }
    .figure-grid { display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 16px; }
    .figure { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; }
    .figure h3 { font-size: 16px; margin-bottom: 10px; }
    .figure img { width: 100%; height: auto; display: block; background: #fff; }
    .two-col { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 18px; }
    table { width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
    th, td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: left; vertical-align: top; font-size: 13px; }
    th { background: #f1f5f9; color: #0f172a; }
    tr:last-child td { border-bottom: 0; }
    .mono { font-family: Menlo, Consolas, monospace; }
    .muted { color: #64748b; font-size: 12px; }
    @media (max-width: 960px) {
      .stats, .two-col { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <h1>Verifier Report</h1>
      <p>Static semantic validation summary for the typed policy DSL, including feature coverage, proof-carrying diagnostics, and blocked negative-case checks.</p>
    </div>

    <div class="stats">
      <div class="stat"><div class="label">Positive Cases</div><div class="value">$positive_count</div></div>
      <div class="stat"><div class="label">Verified</div><div class="value">$verified_count</div></div>
      <div class="stat"><div class="label">Mean Coverage</div><div class="value">$mean_coverage</div></div>
      <div class="stat"><div class="label">Blocked Negatives</div><div class="value">$blocked_count/$negative_total</div></div>
    </div>

    <div class="section">
      <h2>Core Figures</h2>
      <div class="figure-grid">
        <div class="figure">
          <h3>Feature Coverage</h3>
          <img src="verifier_positive_feature_coverage.svg" alt="Verifier feature coverage chart" />
        </div>
        <div class="two-col">
          <div class="figure">
            <h3>Proof Count</h3>
            <img src="verifier_positive_proof_count.svg" alt="Verifier proof count chart" />
          </div>
          <div class="figure">
            <h3>Blocked Negative Cases</h3>
            <img src="verifier_negative_summary.svg" alt="Verifier negative case summary chart" />
          </div>
        </div>
      </div>
    </div>

    <div class="section two-col">
      <div>
        <h2>High-Coverage Policies</h2>
        <table>
          <thead>
            <tr><th>Algorithm</th><th>Policy</th><th>Coverage</th><th>Proofs</th><th>Primary Proof</th></tr>
          </thead>
          <tbody>
            $positive_rows_html
          </tbody>
        </table>
      </div>
      <div>
        <h2>Negative Cases</h2>
        <table>
          <thead>
            <tr><th>Case</th><th>Status</th><th>Error Count</th><th>Primary Error</th></tr>
          </thead>
          <tbody>
            $negative_rows_html
          </tbody>
        </table>
        <p class="muted" style="margin-top: 10px;">Generated from <span class="mono">results/tables/verifier_positive.csv</span> and <span class="mono">results/tables/verifier_negative.csv</span>.</p>
      </div>
    </div>
  </div>
</body>
</html>
""").substitute(
        positive_count=positive_count,
        verified_count=verified_count,
        mean_coverage=_fmt_number(mean_coverage),
        blocked_count=blocked_count,
        negative_total=len(negative_rows),
        positive_rows_html="".join(_verifier_positive_row_html(row) for row in top_positive),
        negative_rows_html="".join(_verifier_negative_row_html(row) for row in negative_rows),
    )
    dump_text(path, html)


def write_verifier_appendix_html(path: str) -> None:
    positive_rows = load_table_rows("results/tables/verifier_positive.csv")
    negative_rows = load_table_rows("results/tables/verifier_negative.csv")
    top_positive = sorted(
        positive_rows,
        key=lambda row: (
            -float(_to_float(row.get("feature_coverage")) or 0.0),
            -float(_to_float(row.get("proof_count")) or 0.0),
            _label(row.get("algorithm")),
        ),
    )[:12]
    warning_rows = [row for row in positive_rows if _label(row.get("warnings"))][:8]
    mean_coverage = 0.0
    coverage_values = [_to_float(row.get("feature_coverage")) for row in positive_rows]
    coverage_values = [value for value in coverage_values if value is not None]
    if coverage_values:
        mean_coverage = sum(coverage_values) / float(len(coverage_values))

    html = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Verifier Appendix</title>
  <style>
    body { font-family: "Times New Roman", Times, serif; margin: 0; background: #ffffff; color: #111111; }
    .page { max-width: 1120px; margin: 0 auto; padding: 20px 26px 28px; }
    h1, h2, h3 { margin: 0; font-weight: 700; }
    h1 { font-size: 24px; margin-bottom: 8px; }
    h2 { font-size: 16px; margin-bottom: 8px; border-bottom: 1px solid #111111; padding-bottom: 4px; }
    h3 { font-size: 14px; margin-bottom: 6px; }
    p { margin: 0; line-height: 1.35; font-size: 13px; }
    .lede { margin-bottom: 12px; }
    .meta { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 12px 0 18px; }
    .meta div { border: 1px solid #111111; padding: 8px 10px; }
    .meta .k { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
    .meta .v { font-size: 18px; margin-top: 4px; }
    .section { margin-top: 16px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
    .three-col { display: grid; grid-template-columns: 1.05fr 1.05fr 0.9fr; gap: 14px; align-items: start; }
    .panel { border: 1px solid #111111; padding: 10px; }
    .panel img { width: 100%; height: auto; display: block; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #111111; padding: 6px 7px; text-align: left; vertical-align: top; font-size: 12px; line-height: 1.25; }
    th { background: #f3f3f3; }
    .mono { font-family: Menlo, Consolas, monospace; }
    .small { font-size: 11px; color: #333333; }
    .caption { font-size: 11px; margin-top: 6px; color: #333333; }
    @media print {
      body { background: #ffffff; }
      .page { max-width: none; padding: 10mm 10mm 12mm; }
      .panel, .meta div, th, td { break-inside: avoid; }
    }
    @media (max-width: 980px) {
      .meta, .two-col, .three-col { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <h1>Appendix: Verifier Diagnostics</h1>
    <p class="lede">Compact appendix view for the typed policy DSL verifier. This page emphasises print clarity, figure placement, and high-density summaries for thesis appendices and paper supplements.</p>

    <div class="meta">
      <div><div class="k">Positive cases</div><div class="v">$positive_total</div></div>
      <div><div class="k">Negative cases</div><div class="v">$negative_total</div></div>
      <div><div class="k">Mean coverage</div><div class="v">$mean_coverage</div></div>
      <div><div class="k">All negatives blocked</div><div class="v">$blocked_summary</div></div>
    </div>

    <div class="section three-col">
      <div class="panel">
        <h3>Feature Coverage</h3>
        <img src="verifier_positive_feature_coverage.svg" alt="Verifier feature coverage chart" />
        <div class="caption">Coverage over required typed state features for each algorithm-specific policy.</div>
      </div>
      <div class="panel">
        <h3>Proof Count</h3>
        <img src="verifier_positive_proof_count.svg" alt="Verifier proof count chart" />
        <div class="caption">Path-wise proof obligations discharged by the semantic verifier.</div>
      </div>
      <div class="panel">
        <h3>Blocked Negative Cases</h3>
        <img src="verifier_negative_summary.svg" alt="Verifier negative case summary chart" />
        <div class="caption">Sanity-check adversarial cases blocked by static analysis.</div>
      </div>
    </div>

    <div class="section two-col">
      <div>
        <h2>Highest-Coverage Policies</h2>
        <table>
          <thead>
            <tr><th>Alg.</th><th>Policy</th><th>Coverage</th><th>Proofs</th><th>Paths</th></tr>
          </thead>
          <tbody>
            $top_positive_rows
          </tbody>
        </table>
      </div>
      <div>
        <h2>Negative-Case Blocking Summary</h2>
        <table>
          <thead>
            <tr><th>Case</th><th>Status</th><th>Errors</th><th>Primary Error</th></tr>
          </thead>
          <tbody>
            $negative_rows
          </tbody>
        </table>
      </div>
    </div>

    <div class="section two-col">
      <div>
        <h2>Representative Proof Obligations</h2>
        <table>
          <thead>
            <tr><th>Algorithm</th><th>Policy</th><th>Primary Proof</th></tr>
          </thead>
          <tbody>
            $proof_rows
          </tbody>
        </table>
      </div>
      <div>
        <h2>Verifier Warning Samples</h2>
        <table>
          <thead>
            <tr><th>Algorithm</th><th>Policy</th><th>Warnings</th></tr>
          </thead>
          <tbody>
            $warning_rows
          </tbody>
        </table>
        <p class="small" style="margin-top: 8px;">Appendix page generated from <span class="mono">results/tables/verifier_positive.csv</span> and <span class="mono">results/tables/verifier_negative.csv</span>.</p>
      </div>
    </div>
  </div>
</body>
</html>
""").substitute(
        positive_total=len(positive_rows),
        negative_total=len(negative_rows),
        mean_coverage=_fmt_number(mean_coverage),
        blocked_summary="%d/%d" % (
            len([row for row in negative_rows if int(_to_float(row.get("blocked_flag")) or 0.0) == 1]),
            len(negative_rows),
        ),
        top_positive_rows="".join(_verifier_appendix_positive_row_html(row) for row in top_positive),
        negative_rows="".join(_verifier_appendix_negative_row_html(row) for row in negative_rows),
        proof_rows="".join(_verifier_appendix_proof_row_html(row) for row in top_positive[:8]),
        warning_rows="".join(_verifier_appendix_warning_row_html(row) for row in warning_rows),
    )
    dump_text(path, html)


def _coerce_row(row: Dict[str, str]) -> Dict[str, object]:
    coerced: Dict[str, object] = {}
    for key, value in row.items():
        if value is None:
            coerced[key] = ""
            continue
        stripped = value.strip()
        if stripped == "":
            coerced[key] = ""
            continue
        if stripped in {"True", "False"}:
            coerced[key] = stripped == "True"
            continue
        try:
            coerced[key] = float(stripped)
            continue
        except ValueError:
            coerced[key] = stripped
    return coerced


def _write_categorical_bar_figure(
    path: str,
    title: str,
    rows: Sequence[Dict[str, object]],
    category_key: str,
    value_key: str,
    color_key: str,
) -> None:
    values = []
    for row in rows:
        value = _to_float(row.get(value_key))
        label = _build_category_label(row, category_key)
        if value is None or not label:
            continue
        values.append({
            "label": label,
            "value": value,
            "series": _label(row.get(color_key)) or "default",
            "tooltip": _categorical_tooltip(row, label, value_key, value),
        })
    if not values:
        return
    values.sort(key=lambda item: item["value"], reverse=True)
    colors = _assign_colors([item["series"] for item in values])
    numeric_values = [float(item["value"]) for item in values]
    chart_top = CHART_TOP
    chart_height = SVG_HEIGHT - CHART_TOP - CHART_BOTTOM
    width = SVG_WIDTH - CHART_LEFT - CHART_RIGHT
    bar_gap = 14.0
    bar_width = max(18.0, min(84.0, (width - bar_gap * (len(values) - 1)) / max(len(values), 1)))
    total_bars_width = len(values) * bar_width + max(0, len(values) - 1) * bar_gap
    x_start = CHART_LEFT + max(0.0, (width - total_bars_width) / 2.0)
    y_min, y_max = _axis_bounds(numeric_values)
    zero_y = _map_y(0.0, y_min, y_max, chart_top, chart_height)

    parts = _svg_header(title, "bar")
    parts.extend(_draw_y_grid(y_min, y_max, chart_top, chart_height))
    parts.append(_svg_line(CHART_LEFT, zero_y, SVG_WIDTH - CHART_RIGHT, zero_y, "#111827", 1.2))
    for index, item in enumerate(values):
        x = x_start + index * (bar_width + bar_gap)
        y = _map_y(float(item["value"]), y_min, y_max, chart_top, chart_height)
        top = min(y, zero_y)
        height = max(1.0, abs(zero_y - y))
        color = colors[item["series"]]
        parts.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s"><title>%s</title></rect>'
            % (x, top, bar_width, height, color, _xml_escape(item["tooltip"]))
        )
        parts.append(_svg_text(x + bar_width / 2.0, SVG_HEIGHT - 62, item["label"], 11, "#111827", "middle", -28))
        parts.append(_svg_text(x + bar_width / 2.0, top - 8 if item["value"] >= 0 else top + height + 16, _fmt_number(float(item["value"])), 11, "#374151", "middle"))
    parts.extend(_draw_legend(colors))
    parts.extend(_chart_title(title, value_key, len(values)))
    parts.append(_svg_footer())
    dump_text(path, "\n".join(parts))


def _write_grouped_bar_figure(
    path: str,
    title: str,
    rows: Sequence[Dict[str, object]],
    group_key: str,
    series_key: str,
    value_key: str,
) -> None:
    grouped: Dict[str, Dict[str, float]] = {}
    series_labels: List[str] = []
    for row in rows:
        group = _label(row.get(group_key))
        series = _label(row.get(series_key))
        value = _to_float(row.get(value_key))
        if not group or not series or value is None:
            continue
        grouped.setdefault(group, {})[series] = value
        if series not in series_labels:
            series_labels.append(series)
    if not grouped or not series_labels:
        return
    groups = list(grouped.keys())
    colors = _assign_colors(series_labels)
    numeric_values = [value for group_values in grouped.values() for value in group_values.values()]
    chart_top = CHART_TOP
    chart_height = SVG_HEIGHT - CHART_TOP - CHART_BOTTOM
    width = SVG_WIDTH - CHART_LEFT - CHART_RIGHT
    y_min, y_max = _axis_bounds(numeric_values)
    zero_y = _map_y(0.0, y_min, y_max, chart_top, chart_height)
    cluster_width = width / max(len(groups), 1)
    inner_width = cluster_width * 0.72
    bar_width = max(12.0, min(42.0, inner_width / max(len(series_labels), 1)))

    parts = _svg_header(title, "grouped-bar")
    parts.extend(_draw_y_grid(y_min, y_max, chart_top, chart_height))
    parts.append(_svg_line(CHART_LEFT, zero_y, SVG_WIDTH - CHART_RIGHT, zero_y, "#111827", 1.2))
    for group_index, group in enumerate(groups):
        cluster_left = CHART_LEFT + group_index * cluster_width + (cluster_width - inner_width) / 2.0
        parts.append(_svg_text(cluster_left + inner_width / 2.0, SVG_HEIGHT - 48, group, 12, "#111827", "middle"))
        for series_index, series in enumerate(series_labels):
            value = grouped[group].get(series)
            if value is None:
                continue
            x = cluster_left + series_index * bar_width
            y = _map_y(value, y_min, y_max, chart_top, chart_height)
            top = min(y, zero_y)
            height = max(1.0, abs(zero_y - y))
            parts.append(
                '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" />'
                % (x, top, bar_width - 2.0, height, colors[series])
            )
    parts.extend(_draw_legend(colors))
    parts.extend(_chart_title(title, value_key, len(groups)))
    parts.append(_svg_footer())
    dump_text(path, "\n".join(parts))


def _write_search_archive_figure(path: str, title: str, rows: Sequence[Dict[str, object]]) -> None:
    series_map: Dict[str, List[Tuple[int, float]]] = {}
    best_points: List[Tuple[int, float]] = []
    best_so_far = None
    for index, row in enumerate(rows, start=1):
        origin = _label(row.get("origin")) or "unknown"
        value = _to_float(row.get("score"))
        if value is None:
            continue
        series_map.setdefault(origin, []).append((index, value))
        if best_so_far is None or value > best_so_far:
            best_so_far = value
        best_points.append((index, float(best_so_far)))
    if not series_map:
        return
    colors = _assign_colors(list(series_map.keys()) + ["best-so-far"])
    all_values = [point[1] for points in series_map.values() for point in points]
    all_values.extend(point[1] for point in best_points)
    y_min, y_max = _axis_bounds(all_values)
    chart_top = CHART_TOP
    chart_height = SVG_HEIGHT - CHART_TOP - CHART_BOTTOM
    width = SVG_WIDTH - CHART_LEFT - CHART_RIGHT
    x_max = max(point[0] for points in series_map.values() for point in points)
    parts = _svg_header(title, "line")
    parts.extend(_draw_y_grid(y_min, y_max, chart_top, chart_height))
    parts.extend(_draw_x_grid(x_max, chart_top, chart_height))
    for name, points in series_map.items():
        parts.append(_svg_polyline(points, y_min, y_max, x_max, chart_top, chart_height, width, colors[name], 2.6))
        for point in points:
            cx = _map_x(point[0], x_max, width)
            cy = _map_y(point[1], y_min, y_max, chart_top, chart_height)
            parts.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s" />' % (cx, cy, colors[name]))
    parts.append(_svg_polyline(best_points, y_min, y_max, x_max, chart_top, chart_height, width, colors["best-so-far"], 3.2, "6 5"))
    parts.extend(_draw_legend(colors))
    parts.extend(_chart_title("Search Archive Score Trend", "score", len(best_points)))
    parts.append(_svg_footer())
    dump_text(path, "\n".join(parts))


def _maybe_write_verifier_metric_figures(
    out_dir: str,
    basename: str,
    rows: Sequence[Dict[str, object]],
    category_key: str,
    color_key: str,
) -> List[str]:
    outputs: List[str] = []
    if any(_to_float(row.get("feature_coverage")) is not None for row in rows):
        coverage_path = "%s/%s_feature_coverage.svg" % (out_dir, basename)
        _write_categorical_bar_figure(coverage_path, "Feature Coverage", rows, category_key, "feature_coverage", color_key)
        outputs.append(coverage_path)
    if any(_to_float(row.get("proof_count")) is not None for row in rows) and any(_to_float(row.get("score")) is not None for row in rows):
        scatter_path = "%s/%s_proof_vs_score.svg" % (out_dir, basename)
        _write_scatter_figure(scatter_path, "Proof Count vs Score", rows, "proof_count", "score", color_key, category_key)
        outputs.append(scatter_path)
    return outputs


def _write_scatter_figure(
    path: str,
    title: str,
    rows: Sequence[Dict[str, object]],
    x_key: str,
    y_key: str,
    color_key: str,
    label_key: str,
) -> None:
    points = []
    for row in rows:
        x_value = _to_float(row.get(x_key))
        y_value = _to_float(row.get(y_key))
        if x_value is None or y_value is None:
            continue
        points.append({
            "x": x_value,
            "y": y_value,
            "series": _label(row.get(color_key)) or "default",
            "label": _build_category_label(row, label_key),
        })
    if not points:
        return
    colors = _assign_colors([point["series"] for point in points])
    x_min, x_max = _axis_bounds([point["x"] for point in points])
    y_min, y_max = _axis_bounds([point["y"] for point in points])
    chart_top = CHART_TOP
    chart_height = SVG_HEIGHT - CHART_TOP - CHART_BOTTOM
    width = SVG_WIDTH - CHART_LEFT - CHART_RIGHT

    parts = _svg_header(title, "scatter")
    parts.extend(_draw_y_grid(y_min, y_max, chart_top, chart_height))
    parts.extend(_draw_numeric_x_grid(x_min, x_max, width))
    for point in points:
        cx = _map_numeric_x(point["x"], x_min, x_max, width)
        cy = _map_y(point["y"], y_min, y_max, chart_top, chart_height)
        parts.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s" fill-opacity="0.85" />' % (cx, cy, colors[point["series"]]))
        parts.append(_svg_text(cx, cy - 12, point["label"], 10, "#374151", "middle"))
    parts.extend(_draw_legend(colors))
    parts.extend(_chart_title(title, "%s vs %s" % (x_key, y_key), len(points)))
    parts.append(_svg_text(SVG_WIDTH / 2.0, SVG_HEIGHT - 52, x_key, 12, "#374151", "middle"))
    parts.append(_svg_footer())
    dump_text(path, "\n".join(parts))


def _write_figure_index(path: str, figure_paths: Sequence[str]) -> None:
    lines = ["# Generated Figures", ""]
    for figure_path in figure_paths:
        lines.append("- %s" % figure_path)
    dump_text(path, "\n".join(lines) + "\n")


def _verifier_positive_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td>%s</td>"
        "<td class=\"mono\">%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("algorithm"))),
        _xml_escape(_label(row.get("policy_id"))),
        _xml_escape(_fmt_number(float(_to_float(row.get("feature_coverage")) or 0.0))),
        _xml_escape(str(int(_to_float(row.get("proof_count")) or 0))),
        _xml_escape(_label(row.get("primary_proof"))),
    )


def _verifier_negative_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td class=\"mono\">%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("case_id"))),
        _xml_escape(_label(row.get("status"))),
        _xml_escape(str(int(_to_float(row.get("error_count")) or 0))),
        _xml_escape(_label(row.get("primary_error"))),
    )


def _verifier_appendix_positive_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td>%s</td><td class=\"mono\">%s</td><td>%s</td><td>%s</td><td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("algorithm"))),
        _xml_escape(_label(row.get("policy_id"))),
        _xml_escape(_fmt_number(float(_to_float(row.get("feature_coverage")) or 0.0))),
        _xml_escape(str(int(_to_float(row.get("proof_count")) or 0))),
        _xml_escape(str(int(_to_float(row.get("path_count")) or 0))),
    )


def _verifier_appendix_negative_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td class=\"mono\">%s</td><td>%s</td><td>%s</td><td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("case_id"))),
        _xml_escape(_label(row.get("status"))),
        _xml_escape(str(int(_to_float(row.get("error_count")) or 0))),
        _xml_escape(_label(row.get("primary_error"))),
    )


def _verifier_appendix_proof_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td>%s</td><td class=\"mono\">%s</td><td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("algorithm"))),
        _xml_escape(_label(row.get("policy_id"))),
        _xml_escape(_label(row.get("primary_proof"))),
    )


def _verifier_appendix_warning_row_html(row: Dict[str, object]) -> str:
    return (
        "<tr>"
        "<td>%s</td><td class=\"mono\">%s</td><td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("algorithm"))),
        _xml_escape(_label(row.get("policy_id"))),
        _xml_escape(_label(row.get("warnings"))),
    )


def _native_backend_panel_html(item: Dict[str, object]) -> str:
    solver_rows = item["solver_rows"]
    rows_html = "".join(_native_backend_row_html(row) for row in solver_rows)
    native_count = len(item["native_rows"])
    return (
        '<div class="panel">'
        '<h2>%s</h2>'
        '<p>%d/%d solver baselines used native backends in this table.</p>'
        '<table>'
        '<thead><tr><th>Solver</th><th>Native</th><th>Backend</th><th>Mode</th><th>Detail</th><th>Score</th></tr></thead>'
        '<tbody>%s</tbody>'
        '</table>'
        '</div>'
    ) % (
        _xml_escape(str(item["name"])),
        native_count,
        len(solver_rows),
        rows_html,
    )


def _native_backend_row_html(row: Dict[str, object]) -> str:
    native_used = bool(row.get("native_used"))
    return (
        "<tr>"
        "<td class=\"mono\">%s</td>"
        "<td class=\"%s\">%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "<td>%s</td>"
        "</tr>"
    ) % (
        _xml_escape(_label(row.get("policy_id"))),
        "ok" if native_used else "no",
        "True" if native_used else "False",
        _xml_escape(_label(row.get("native_backend"))),
        _xml_escape(_label(row.get("backend_mode"))),
        _xml_escape(_label(row.get("backend_detail"))),
        _xml_escape(_fmt_number(float(_to_float(row.get("score")) or 0.0))),
    )


def _svg_header(title: str, chart_kind: str) -> List[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (SVG_WIDTH, SVG_HEIGHT, SVG_WIDTH, SVG_HEIGHT),
        '<rect width="100%" height="100%" fill="#ffffff" />',
        '<text x="36" y="40" font-size="24" font-family="Arial, Helvetica, sans-serif" fill="#111827">%s</text>' % _xml_escape(title),
        '<text x="36" y="62" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#6b7280">chart=%s generated_from_csv=true</text>' % _xml_escape(chart_kind),
    ]


def _svg_footer() -> str:
    return "</svg>"


def _chart_title(title: str, value_key: str, count: int) -> List[str]:
    return [
        '<text x="%d" y="%d" font-size="13" font-family="Arial, Helvetica, sans-serif" fill="#6b7280">%s</text>'
        % (CHART_LEFT, 62, _xml_escape("metric=%s items=%d" % (value_key, count))),
        _svg_text(22, CHART_TOP + 10, value_key, 12, "#374151", "start", -90),
    ]


def _draw_legend(colors: Dict[str, str]) -> List[str]:
    parts = []
    x = CHART_LEFT
    y = SVG_HEIGHT - 22
    step = 148
    for index, (label, color) in enumerate(colors.items()):
        x_pos = x + (index % 6) * step
        y_pos = y + (index // 6) * 18
        parts.append('<rect x="%d" y="%d" width="12" height="12" rx="2" fill="%s" />' % (x_pos, y_pos - 10, color))
        parts.append(_svg_text(x_pos + 18, y_pos, label, 12, "#374151", "start"))
    return parts


def _draw_y_grid(y_min: float, y_max: float, chart_top: float, chart_height: float) -> List[str]:
    parts = []
    for tick in _ticks(y_min, y_max, 5):
        y = _map_y(tick, y_min, y_max, chart_top, chart_height)
        parts.append(_svg_line(CHART_LEFT, y, SVG_WIDTH - CHART_RIGHT, y, "#e5e7eb", 1.0))
        parts.append(_svg_text(CHART_LEFT - 10, y + 4, _fmt_number(tick), 11, "#6b7280", "end"))
    return parts


def _draw_x_grid(x_max: int, chart_top: float, chart_height: float) -> List[str]:
    parts = []
    if x_max <= 0:
        return parts
    width = SVG_WIDTH - CHART_LEFT - CHART_RIGHT
    step = max(1, int(math.ceil(float(x_max) / 6.0)))
    for tick in range(1, x_max + 1, step):
        x = _map_x(tick, x_max, width)
        parts.append(_svg_line(x, chart_top, x, chart_top + chart_height, "#f3f4f6", 1.0))
        parts.append(_svg_text(x, SVG_HEIGHT - 54, str(tick), 11, "#6b7280", "middle"))
    return parts


def _draw_numeric_x_grid(x_min: float, x_max: float, width: float) -> List[str]:
    parts = []
    for tick in _ticks(x_min, x_max, 5):
        x = _map_numeric_x(tick, x_min, x_max, width)
        parts.append(_svg_line(x, CHART_TOP, x, CHART_TOP + (SVG_HEIGHT - CHART_TOP - CHART_BOTTOM), "#f3f4f6", 1.0))
        parts.append(_svg_text(x, SVG_HEIGHT - 54, _fmt_number(tick), 11, "#6b7280", "middle"))
    return parts


def _svg_polyline(
    points: Sequence[Tuple[int, float]],
    y_min: float,
    y_max: float,
    x_max: int,
    width: float,
    height: float,
    inner_width: float,
    color: str,
    stroke_width: float,
    dasharray: str = "",
) -> str:
    mapped = []
    for x_value, y_value in points:
        mapped.append("%.1f,%.1f" % (_map_x(x_value, x_max, inner_width), _map_y(y_value, y_min, y_max, width, height)))
    dash = ' stroke-dasharray="%s"' % dasharray if dasharray else ""
    return '<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s" />' % (
        color,
        stroke_width,
        dash,
        " ".join(mapped),
    )


def _svg_line(x1: float, y1: float, x2: float, y2: float, color: str, width: float) -> str:
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" />' % (x1, y1, x2, y2, color, width)


def _svg_text(x: float, y: float, text: str, size: int, color: str, anchor: str, rotate: int = 0) -> str:
    transform = ""
    if rotate:
        transform = ' transform="rotate(%d %.1f %.1f)"' % (rotate, x, y)
    return '<text x="%.1f" y="%.1f" font-size="%d" font-family="Arial, Helvetica, sans-serif" fill="%s" text-anchor="%s"%s>%s</text>' % (
        x,
        y,
        size,
        color,
        anchor,
        transform,
        _xml_escape(text),
    )


def _ticks(lower: float, upper: float, count: int) -> List[float]:
    if upper <= lower:
        return [lower]
    step = (upper - lower) / float(count)
    return [lower + step * index for index in range(count + 1)]


def _axis_bounds(values: Iterable[float]) -> Tuple[float, float]:
    numeric = [float(value) for value in values]
    lower = min(numeric)
    upper = max(numeric)
    if lower == upper:
        margin = abs(lower) * 0.15 + 1.0
        return lower - margin, upper + margin
    margin = (upper - lower) * 0.12
    lower = min(lower - margin, 0.0 if lower > 0.0 else lower - margin * 0.15)
    upper = max(upper + margin, 0.0 if upper < 0.0 else upper + margin * 0.15)
    return lower, upper


def _assign_colors(labels: Sequence[str]) -> Dict[str, str]:
    colors: Dict[str, str] = {}
    for index, label in enumerate(labels):
        if label not in colors:
            colors[label] = PALETTE[index % len(PALETTE)]
    return colors


def _map_y(value: float, lower: float, upper: float, top: float, height: float) -> float:
    if upper <= lower:
        return top + height / 2.0
    ratio = (value - lower) / (upper - lower)
    return top + height - ratio * height


def _map_x(index: int, max_index: int, width: float) -> float:
    if max_index <= 1:
        return CHART_LEFT + width / 2.0
    return CHART_LEFT + (float(index - 1) / float(max_index - 1)) * width


def _map_numeric_x(value: float, lower: float, upper: float, width: float) -> float:
    if upper <= lower:
        return CHART_LEFT + width / 2.0
    ratio = (value - lower) / (upper - lower)
    return CHART_LEFT + ratio * width


def _label(value: object) -> str:
    return str(value or "").strip()


def _build_category_label(row: Dict[str, object], category_key: str) -> str:
    label = _label(row.get(category_key))
    if category_key == "problem_family":
        policy = _label(row.get("policy_id"))
        if label and policy:
            return "%s/%s" % (label, policy)
    if category_key == "policy_id":
        variant = _label(row.get("variant"))
        if not variant:
            variant = _label(row.get("algorithm"))
        if variant and label and variant not in label:
            label = "%s/%s" % (variant, label)
    if _label(row.get("origin")) == "solver_baseline":
        backend = _label(row.get("native_backend"))
        if backend:
            label = "%s [%s]" % (label, backend)
        elif str(row.get("native_used")) == "False":
            label = "%s [surrogate]" % label
    return label


def _categorical_tooltip(row: Dict[str, object], label: str, value_key: str, value: float) -> str:
    parts = [label, "%s=%s" % (value_key, _fmt_number(value))]
    origin = _label(row.get("origin"))
    if origin:
        parts.append("origin=%s" % origin)
    if origin == "solver_baseline":
        parts.append("native_used=%s" % row.get("native_used"))
        backend = _label(row.get("native_backend"))
        if backend:
            parts.append("native_backend=%s" % backend)
        backend_mode = _label(row.get("backend_mode"))
        if backend_mode:
            parts.append("backend_mode=%s" % backend_mode)
        backend_detail = _label(row.get("backend_detail"))
        if backend_detail:
            parts.append("backend_detail=%s" % backend_detail)
    return " | ".join(parts)


def _collect_headers(rows: Sequence[Dict[str, object]]) -> List[str]:
    headers: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in headers:
                headers.append(key)
    return headers


def _has_solver_backend_rows(rows: Sequence[Dict[str, object]]) -> bool:
    return any(_label(row.get("origin")) == "solver_baseline" for row in rows)


def _to_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if value == value and value not in (float("inf"), float("-inf")):
            return float(value)
        return None
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return None
    return parsed


def _fmt_number(value: float) -> str:
    if abs(value) >= 1000.0:
        return "%.0f" % value
    if abs(value) >= 10.0:
        return "%.2f" % value
    if abs(value) >= 1.0:
        return "%.3f" % value
    return "%.4f" % value


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
