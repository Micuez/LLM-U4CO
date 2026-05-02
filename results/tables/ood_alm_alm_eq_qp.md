# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | vanilla | True |  | 0.0 | -0.204024 | 0.002001 | 0.0 |  |  |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | adaptive | True |  | 0.3333 | -0.700453 | 0.000108 | 0.0 |  |  |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | conservative | True |  | 0.3333 | -0.501947 | 0.001057 | 0.0 |  |  |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | safe_fallback_only | True |  | 0.0 | -0.204022 | 0.002001 | 0.0 |  |  |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | learned_controller | True |  | 0.3333 | -0.700454 | 0.000108 | 0.0 |  |  |
| train | standard_split | train | alm_eq_qp | alm_eq_qp | llm_one_shot | True |  | 0.6667 | -1.105366 | 0.002173 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | vanilla | True |  | 0.0 | -0.216176 | 0.006146 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | adaptive | True |  | 0.3333 | -0.705581 | 0.002117 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | conservative | True |  | 0.3333 | -0.508122 | 0.004482 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | safe_fallback_only | True |  | 0.0 | -0.216182 | 0.006146 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | learned_controller | True |  | 0.3333 | -0.705585 | 0.002117 | 0.0 |  |  |
| validation | standard_split | validation | alm_eq_qp | alm_eq_qp | llm_one_shot | True |  | 0.6667 | -1.117487 | 0.008453 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | vanilla | True |  | 0.0 | -0.27237 | 0.018545 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | adaptive | True |  | 0.3333 | -0.804908 | 0.028731 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | conservative | True |  | 0.3333 | -0.587311 | 0.023239 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | safe_fallback_only | True |  | 0.0 | -0.272357 | 0.018545 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | learned_controller | True |  | 0.3333 | -0.804901 | 0.028731 | 0.0 |  |  |
| test | standard_split | test | alm_eq_qp | alm_eq_qp | llm_one_shot | True |  | 0.6667 | -1.232643 | 0.03358 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | vanilla | True |  | 0.0 | -0.272372 | 0.018545 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | adaptive | True |  | 0.3333 | -0.804925 | 0.028731 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | conservative | True |  | 0.3333 | -0.587312 | 0.023239 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | safe_fallback_only | True |  | 0.0 | -0.272359 | 0.018545 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | learned_controller | True |  | 0.3333 | -0.804898 | 0.028731 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | alm_eq_qp | alm_eq_qp | llm_one_shot | True |  | 0.6667 | -1.232627 | 0.03358 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | vanilla | True |  | 0.0 | -1.838086 | 1.631309 | 0.0 | equality_qp | cover_relaxation |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | adaptive | True |  | 0.3333 | -2.069821 | 1.332323 | 0.0 | equality_qp | cover_relaxation |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | conservative | True |  | 0.3333 | -2.091638 | 1.503589 | 0.0 | equality_qp | cover_relaxation |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | safe_fallback_only | True |  | 0.0 | -1.838085 | 1.631309 | 0.0 | equality_qp | cover_relaxation |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | learned_controller | True |  | 0.3333 | -2.069824 | 1.332323 | 0.0 | equality_qp | cover_relaxation |
| test | cross_problem_transfer | equality_qp_to_cover_relaxation | alm_eq_qp | alm_cover_relaxation | llm_one_shot | True |  | 0.6667 | -2.897079 | 1.375362 | 0.0 | equality_qp | cover_relaxation |
