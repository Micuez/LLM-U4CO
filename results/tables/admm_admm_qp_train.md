# Baseline Summary

| algorithm | problem_family | policy_id | origin | native_used | native_backend | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | median_violation | median_runtime | median_primal_residual | median_dual_residual | median_iterations | fail_rate | backend_mode | backend_detail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADMM | admm_qp | vanilla | baseline |  |  | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, rho | 0.0 | 1 | -0.200189 | 0.0 | 0.0 | 0.001259 | 0.0 | 0.0 | 60 | 0.0 |  |  |
| ADMM | admm_qp | adaptive | baseline |  |  | True | True |  |  | Action scale_rho is emitted without reading state feature rho. | Action scale_rho is emitted without reading state feature rho. | Required features not referenced by policy: k, rho | 0.5 | 6 | -0.850188 | 0.0 | 0.0 | 0.001251 | 0.0 | 0.0 | 60 | 0.0 |  |  |
| ADMM | admm_qp | conservative | baseline |  |  | True | True |  |  | Action scale_rho is emitted without reading state feature rho. | Action scale_rho is emitted without reading state feature rho. | Required features not referenced by policy: k, rho | 0.5 | 3 | -0.600189 | 0.0 | 0.0 | 0.001263 | 0.0 | 0.0 | 60 | 0.0 |  |  |
| ADMM | admm_qp | HiGHS | solver_baseline | False |  |  |  |  |  |  |  |  | -0.00018 | 0.0 | 0.0 | 0.001204 | 0.0 | 0.0 | 1 | 0.0 | surrogate | ModuleNotFoundError: No module named 'highspy' |
| ADMM | admm_qp | OSQP | solver_baseline | False |  |  |  |  |  |  |  |  | -0.00015 | 0.0 | 0.0 | 0.001003 | 0.0 | 0.0 | 1 | 0.0 | surrogate | ModuleNotFoundError: No module named 'osqp' |
