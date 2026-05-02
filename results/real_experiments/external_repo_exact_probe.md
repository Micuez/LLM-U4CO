# External Repo Exact Probe

| Target | Problem | Can Attempt Exact Run | Repo Head | Main Blockers |
| --- | --- | --- | --- | --- |
| LLM-LNS SC exact repo script | llm_lns_sc | False | 5faa077964b0296e2f5cf2915eef0a0bb61904c6 | upstream script still contains placeholder API credentials, missing LLM_API_KEY / LLM_API_ENDPOINT |
| LLM-LNS IS exact repo script | llm_lns_is | False | 5faa077964b0296e2f5cf2915eef0a0bb61904c6 | upstream script still contains placeholder API credentials, missing LLM_API_KEY / LLM_API_ENDPOINT |
| LLM-LNS MVC exact repo script | llm_lns_mvc | False | 5faa077964b0296e2f5cf2915eef0a0bb61904c6 | upstream script still contains placeholder API credentials, missing LLM_API_KEY / LLM_API_ENDPOINT |
| LLM-LNS MIKS exact repo script | llm_lns_miks | False | 5faa077964b0296e2f5cf2915eef0a0bb61904c6 | upstream script still contains placeholder API credentials, missing LLM_API_KEY / LLM_API_ENDPOINT |

## Probe notes

- `gurobipy` probe checks both importability and `gp.Model()` creation.
- `can_attempt_exact_run=True` requires real `LLM_API_KEY` / `LLM_API_ENDPOINT` and no placeholder API credentials left in the upstream script body.

## Exact commands

- `python3 baselines/LLM-LNS/src/MILP Problems/SC_eoh_change_prompt_ACP.py`
- `python3 baselines/LLM-LNS/src/MILP Problems/IS_eoh_change_prompt_ACP.py`
- `python3 baselines/LLM-LNS/src/MILP Problems/MVC_eoh_change_prompt_ACP.py`
- `python3 baselines/LLM-LNS/src/MILP Problems/MIKS_eoh_change_prompt_ACP.py`
