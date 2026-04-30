# Environment Report

## Solver backends

| Name | Mode | Available | Detail |
| --- | --- | --- | --- |
| highspy | python_package | False | ModuleNotFoundError: No module named 'highspy' |
| osqp | python_package | False | ModuleNotFoundError: No module named 'osqp' |
| ortools | python_package | False | ModuleNotFoundError: No module named 'ortools' |
| pyscipopt | python_package | False | ModuleNotFoundError: No module named 'pyscipopt' |
| ecole | python_package | False | ModuleNotFoundError: No module named 'ecole' |
| highs | command | False | not found |
| scip | command | False | not found |

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
- lp_files: 6
- families: {'SC_easy_instance': 3, 'IS_easy_instance': 3, 'MVC_easy_instance': 0, 'MIKS_easy_instance': 0}
