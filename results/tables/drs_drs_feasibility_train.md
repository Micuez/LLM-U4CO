# Baseline Summary

| algorithm | problem_family | policy_id | origin | native_used | native_backend | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | median_violation | median_runtime | median_primal_residual | median_dual_residual | median_iterations | fail_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DRS | drs_feasibility | vanilla | baseline |  |  | True | True |  |  | Required features not referenced by policy: k, residual_norm | 0.0 | 1 | -0.747792 | 0.724358 | 0.001525 | 0.001433 | 0.001525 | 0.00179 | 70 | 0.0 |
| DRS | drs_feasibility | adaptive | baseline |  |  | True | True |  |  | Required features not referenced by policy: k | 0.5 | 6 | -1.302613 | 0.729108 | 0.002708 | 0.001239 | 0.002708 | 0.003156 | 70 | 0.0 |
| DRS | drs_feasibility | conservative | baseline |  |  | True | True |  |  | Required features not referenced by policy: k, residual_norm | 0.0 | 2 | -0.96149 | 0.737791 | 0.004848 | 0.001586 | 0.004848 | 0.005684 | 70 | 0.0 |
| DRS | drs_feasibility | safe_fallback_only | baseline |  |  | True | True |  |  | Required features not referenced by policy: k, residual_norm | 0.0 | 1 | -0.74785 | 0.724358 | 0.001525 | 0.001822 | 0.001525 | 0.00179 | 70 | 0.0 |
| DRS | drs_feasibility | learned_controller | baseline |  |  | True | True |  |  | Required features not referenced by policy: k | 0.5 | 6 | -1.302683 | 0.729108 | 0.002708 | 0.001711 | 0.002708 | 0.003156 | 70 | 0.0 |
| DRS | drs_feasibility | llm_one_shot | baseline |  |  | True | True |  |  | Required features not referenced by policy: k | 0.5 | 6 | -1.401494 | 0.728046 | 0.002438 | 0.001065 | 0.002438 | 0.002847 | 70 | 0.0 |
