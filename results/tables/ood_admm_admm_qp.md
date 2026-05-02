# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | admm_qp | admm_qp | vanilla | True |  | 0.0 | -0.200176 | 0.0 | 0.0 |  |  |
| train | standard_split | train | admm_qp | admm_qp | adaptive | True |  | 0.5 | -0.850181 | 0.0 | 0.0 |  |  |
| train | standard_split | train | admm_qp | admm_qp | conservative | True |  | 0.5 | -0.600185 | 0.0 | 0.0 |  |  |
| train | standard_split | train | admm_qp | admm_qp | safe_fallback_only | True |  | 0.0 | -0.200175 | 0.0 | 0.0 |  |  |
| train | standard_split | train | admm_qp | admm_qp | learned_controller | True |  | 0.5 | -0.750183 | 0.0 | 0.0 |  |  |
| train | standard_split | train | admm_qp | admm_qp | llm_one_shot | True |  | 0.5 | -0.750178 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | vanilla | True |  | 0.0 | -0.200226 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | adaptive | True |  | 0.5 | -0.850232 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | conservative | True |  | 0.5 | -0.600234 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | safe_fallback_only | True |  | 0.0 | -0.200225 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | learned_controller | True |  | 0.5 | -0.750239 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | admm_qp | admm_qp | llm_one_shot | True |  | 0.5 | -0.750233 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | vanilla | True |  | 0.0 | -0.200279 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | adaptive | True |  | 0.5 | -0.850288 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | conservative | True |  | 0.5 | -0.600295 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | safe_fallback_only | True |  | 0.0 | -0.200276 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | learned_controller | True |  | 0.5 | -0.750292 | 0.0 | 0.0 |  |  |
| test | standard_split | test | admm_qp | admm_qp | llm_one_shot | True |  | 0.5 | -0.750288 | 0.0 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | vanilla | True |  | 0.0 | -0.200282 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | adaptive | True |  | 0.5 | -0.85029 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | conservative | True |  | 0.5 | -0.600292 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | safe_fallback_only | True |  | 0.0 | -0.200281 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | learned_controller | True |  | 0.5 | -0.750294 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | admm_qp | admm_qp | llm_one_shot | True |  | 0.5 | -0.750294 | 0.0 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | vanilla | True |  | 0.0 | -0.284069 | 0.087353 | 0.0 | box_qp | relaxation_shift |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | adaptive | True |  | 0.5 | -0.934078 | 0.087353 | 0.0 | box_qp | relaxation_shift |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | conservative | True |  | 0.5 | -0.684079 | 0.087353 | 0.0 | box_qp | relaxation_shift |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | safe_fallback_only | True |  | 0.0 | -0.284078 | 0.087353 | 0.0 | box_qp | relaxation_shift |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | learned_controller | True |  | 0.5 | -0.834086 | 0.087353 | 0.0 | box_qp | relaxation_shift |
| test | cross_problem_transfer | box_qp_to_relaxation | admm_qp | admm_qp_relaxation | llm_one_shot | True |  | 0.5 | -0.834082 | 0.087353 | 0.0 | box_qp | relaxation_shift |
