# Environment Report

## Solver backends

| Name | Mode | Available | Support | Paper Pending | Detail |
| --- | --- | --- | --- | --- | --- |
| highspy | python_package | True | native_verified | True | importable |
| osqp | python_package | True | native_verified | True | importable |
| ortools | python_package | True | native_verified | True | importable |
| pyscipopt | python_package | True | native_verified | True | importable |
| ecole | python_package | False | surrogate_only | True | ModuleNotFoundError: No module named 'ecole' |
| highs | command | False | surrogate_only | True | not found |
| scip | command | False | surrogate_only | True | not found |

## LLM backends

| Mode | Available | Detail |
| --- | --- | --- |
| mock | True | always available |
| openai_compatible | True | requires configured base_url/model/api_key |

## MIPLIB

- list_path: data/miplib/miplib_small.txt
- configured: True
- existing_files: 1
- missing_files: 0

## LLM-LNS

- root: data/llm_lns
- lp_files: 372
- data_source: milpbench_real
- real_lp_files: 360
- real_levels: {'easy': 120, 'medium': 120, 'hard': 120}
- mock_lp_files: 12
- families: {'SC_easy_instance': 93, 'IS_easy_instance': 93, 'MVC_easy_instance': 93, 'MIKS_easy_instance': 93}
- complete_phase2: True

## External repos

- LLM-LNS: True
- MILPBench: True
- HeuriGym: True
