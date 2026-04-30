from __future__ import annotations

from llm4unroll.benchmarks.llm_lns_data import summarize_llm_lns_assets


def main():
    summary = summarize_llm_lns_assets()
    for key, value in summary.items():
        print("%s: %s" % (key, value))


if __name__ == "__main__":
    main()
