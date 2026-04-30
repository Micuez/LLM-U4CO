from __future__ import annotations

import csv
import glob

from llm4unroll.evaluator.report import write_phase1_table, write_table_chart


def main():
    rows = []
    for path in sorted(glob.glob("results/tables/*_train.csv")):
        if "search_" in path or "llm_lns" in path or "ood_" in path or "ablation_" in path:
            continue
        with open(path, "r", encoding="utf-8") as handle:
            rows.extend(list(csv.DictReader(handle)))
    write_phase1_table("results/tables/phase1.csv", rows)
    write_table_chart("results/tables/phase1.csv")
    print("Combined %d rows into results/tables/phase1.csv" % len(rows))


if __name__ == "__main__":
    main()
