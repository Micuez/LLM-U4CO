from __future__ import annotations

from llm4unroll.experiments.common import load_config, parse_args
from llm4unroll.search.llm_client import build_llm_client
from llm4unroll.search.prompts import GENERATION_PROMPT, SYSTEM_PROMPT


def main():
    args = parse_args("Check llm4unroll LLM client connectivity.")
    config = load_config(args.config)
    llm_cfg = config.get("llm", {})
    client = build_llm_client(llm_cfg)
    text = client.generate(SYSTEM_PROMPT, GENERATION_PROMPT)
    print(text[:400])


if __name__ == "__main__":
    main()
