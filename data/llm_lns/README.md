# LLM-LNS data staging

Expected optional inputs:

- `external/MILPBench`
- or `data/llm_lns/MILPBench`

The Phase 2 loader currently looks for the small MILP families used by LLM-LNS:

- `IS`
- `SC`
- `MVC`
- `MIKS`

Run:

```bash
bash scripts/setup_external.sh
bash scripts/prepare_llm_lns_data.sh
```
