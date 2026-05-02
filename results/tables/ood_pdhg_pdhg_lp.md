# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | pdhg_lp | pdhg_lp | vanilla | True |  | 0.0 | -0.291813 | 0.064554 | 0.0 |  |  |
| train | standard_split | train | pdhg_lp | pdhg_lp | adaptive | True |  | 0.4 | -2.682336 | 0.784892 | 0.0 |  |  |
| train | standard_split | train | pdhg_lp | pdhg_lp | conservative | True |  | 0.0 | -1.304392 | 0.423342 | 0.0 |  |  |
| train | standard_split | train | pdhg_lp | pdhg_lp | safe_fallback_only | True |  | 0.0 | -0.291808 | 0.064554 | 0.0 |  |  |
| train | standard_split | train | pdhg_lp | pdhg_lp | learned_controller | True |  | 0.4 | -2.466502 | 0.642906 | 0.0 |  |  |
| train | standard_split | train | pdhg_lp | pdhg_lp | llm_one_shot | True |  | 0.0 | -2.62029 | 0.790953 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | vanilla | True |  | 0.0 | -0.276424 | 0.061108 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | adaptive | True |  | 0.4 | -3.064089 | 0.750894 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | conservative | True |  | 0.0 | -1.174083 | 0.338916 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | safe_fallback_only | True |  | 0.0 | -0.276418 | 0.061108 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | learned_controller | True |  | 0.4 | -2.82275 | 0.682703 | 0.0 |  |  |
| validation | standard_split | validation | pdhg_lp | pdhg_lp | llm_one_shot | True |  | 0.0 | -2.727752 | 0.662318 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | vanilla | True |  | 0.0 | -0.283589 | 0.064655 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | adaptive | True |  | 0.4 | -3.859405 | 0.963522 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | conservative | True |  | 0.0 | -1.661462 | 0.412531 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | safe_fallback_only | True |  | 0.0 | -0.283595 | 0.064655 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | learned_controller | True |  | 0.4 | -3.468917 | 0.816326 | 0.0 |  |  |
| test | standard_split | test | pdhg_lp | pdhg_lp | llm_one_shot | True |  | 0.0 | -3.693495 | 0.935015 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | vanilla | True |  | 0.0 | -0.283592 | 0.064655 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | adaptive | True |  | 0.4 | -3.859391 | 0.963522 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | conservative | True |  | 0.0 | -1.661454 | 0.412531 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | safe_fallback_only | True |  | 0.0 | -0.283595 | 0.064655 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | learned_controller | True |  | 0.4 | -3.468906 | 0.816326 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pdhg_lp | pdhg_lp | llm_one_shot | True |  | 0.0 | -3.693498 | 0.935015 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | vanilla | True |  | 0.0 | -3.591482 | 0.82451 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | adaptive | True |  | 0.4 | -3.885811 | 1.0 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | conservative | True |  | 0.0 | -3.1553 | 0.933646 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | safe_fallback_only | True |  | 0.0 | -3.591494 | 0.82451 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | learned_controller | True |  | 0.4 | -3.785825 | 1.0 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_setcover_relaxation | pdhg_lp | setcover_relaxation | llm_one_shot | True |  | 0.0 | -3.735822 | 1.0 | 0.0 | synthetic_lp | setcover_relaxation |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | vanilla | True |  | 0.0 | -0.203696 | 0.001316 | 0.0 | synthetic | miplib |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | adaptive | True |  | 0.4 | -3.129155 | 1.0 | 0.0 | synthetic | miplib |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | conservative | True |  | 0.0 | -2.32572 | 0.779415 | 0.0 | synthetic | miplib |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | safe_fallback_only | True |  | 0.0 | -0.203696 | 0.001316 | 0.0 | synthetic | miplib |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | learned_controller | True |  | 0.4 | -3.029156 | 1.0 | 0.0 | synthetic | miplib |
| test | cross_problem_transfer | synthetic_to_miplib | pdhg_lp | miplib_rootlp | llm_one_shot | True |  | 0.0 | -2.979155 | 1.0 | 0.0 | synthetic | miplib |
