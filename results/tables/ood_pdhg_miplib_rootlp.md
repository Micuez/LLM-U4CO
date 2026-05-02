# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | vanilla | True |  | 0.0 | -0.200391 | 6.4e-05 | 0.0 |  |  |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | adaptive | True |  | 0.4 | -3.129209 | 1.0 | 0.0 |  |  |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | conservative | True |  | 0.0 | -2.325785 | 0.779422 | 0.0 |  |  |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | safe_fallback_only | True |  | 0.0 | -0.200397 | 6.4e-05 | 0.0 |  |  |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | learned_controller | True |  | 0.4 | -3.02921 | 1.0 | 0.0 |  |  |
| train | standard_split | train | miplib_rootlp | miplib_rootlp | llm_one_shot | True |  | 0.0 | -2.979206 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | vanilla | True |  | 0.0 | -0.200384 | 6.4e-05 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | adaptive | True |  | 0.4 | -3.129203 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | conservative | True |  | 0.0 | -2.325781 | 0.779422 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | safe_fallback_only | True |  | 0.0 | -0.200383 | 6.4e-05 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | learned_controller | True |  | 0.4 | -3.029206 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | miplib_rootlp | miplib_rootlp | llm_one_shot | True |  | 0.0 | -2.979202 | 1.0 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | vanilla | True |  | 0.0 | -0.200383 | 6.4e-05 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | adaptive | True |  | 0.4 | -3.1292 | 1.0 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | conservative | True |  | 0.0 | -2.325775 | 0.779422 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | safe_fallback_only | True |  | 0.0 | -0.20038 | 6.4e-05 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | learned_controller | True |  | 0.4 | -3.029199 | 1.0 | 0.0 |  |  |
| test | standard_split | test | miplib_rootlp | miplib_rootlp | llm_one_shot | True |  | 0.0 | -2.979199 | 1.0 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | vanilla | True |  | 0.0 | -0.200378 | 6.4e-05 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | adaptive | True |  | 0.4 | -3.129201 | 1.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | conservative | True |  | 0.0 | -2.325777 | 0.779422 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | safe_fallback_only | True |  | 0.0 | -0.200379 | 6.4e-05 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | learned_controller | True |  | 0.4 | -3.029199 | 1.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | miplib_rootlp | miplib_rootlp | llm_one_shot | True |  | 0.0 | -2.979198 | 1.0 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | vanilla | True |  | 0.0 | -0.472128 | 0.311988 | 0.0 | miplib | llm_lns_sc |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | adaptive | True |  | 0.4 | -3.354629 | 1.0 | 0.0 | miplib | llm_lns_sc |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | conservative | True |  | 0.0 | -2.661036 | 0.872664 | 0.0 | miplib | llm_lns_sc |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.472126 | 0.311988 | 0.0 | miplib | llm_lns_sc |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | learned_controller | True |  | 0.4 | -3.254631 | 1.0 | 0.0 | miplib | llm_lns_sc |
| test | cross_problem_transfer | miplib_to_llm_lns_sc | miplib_rootlp | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.204628 | 1.0 | 0.0 | miplib | llm_lns_sc |
