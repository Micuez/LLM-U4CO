from __future__ import annotations

from llm4unroll.evaluator.report import build_report_figures, write_verifier_appendix_html, write_verifier_report_html
from llm4unroll.experiments.check_verifier import build_verifier_tables


def main():
    build_verifier_tables()
    outputs = build_report_figures()
    write_verifier_report_html("results/figures/verifier_report.html")
    write_verifier_appendix_html("results/figures/verifier_appendix.html")
    print("Generated %d figure files under results/figures" % len(outputs))


if __name__ == "__main__":
    main()
