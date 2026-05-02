from __future__ import annotations

import csv
import glob
from typing import Dict, List

from llm4unroll.evaluator.report import write_markdown_summary, write_phase1_table, write_table_chart


def _load_rows(patterns: List[str]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            with open(path, "r", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    row["source_table"] = path.rsplit("/", 1)[-1]
                    rows.append(row)
    return rows


def main() -> None:
    patterns = [
        "results/tables/*miplib*_train.csv",
        "results/tables/*llm_lns*_train.csv",
        "results/tables/native_probe_*_train.csv",
        "results/tables/ablation_*miplib*_train.csv",
        "results/tables/evolution_no_llm_*miplib*_train.csv",
        "results/tables/random_search_*miplib*_train.csv",
        "results/tables/search_*miplib*_train.csv",
        "results/tables/ood_*miplib*.csv",
    ]
    rows = _load_rows(patterns)
    write_phase1_table("results/tables/real_experiment_summary.csv", rows)
    write_table_chart("results/tables/real_experiment_summary.csv")
    write_markdown_summary("results/tables/real_experiment_summary.md", "Real Experiment Summary", rows)
    print("Saved real experiment summary to results/tables/real_experiment_summary.csv")


if __name__ == "__main__":
    main()
