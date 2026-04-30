from __future__ import annotations

import csv
import glob

from llm4unroll.evaluator.report import write_phase1_table, write_table_chart


def main():
    rows = []
    for path in sorted(glob.glob("results/tables/*llm_lns*_train.csv")):
        if "search_" in path:
            continue
        with open(path, "r", encoding="utf-8") as handle:
            rows.extend(list(csv.DictReader(handle)))
    write_phase1_table("results/tables/phase2_llm_lns.csv", rows)
    write_table_chart("results/tables/phase2_llm_lns.csv")
    print("Combined %d rows into results/tables/phase2_llm_lns.csv" % len(rows))


if __name__ == "__main__":
    main()
