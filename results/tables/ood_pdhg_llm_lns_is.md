# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | llm_lns_is | llm_lns_is | vanilla | True |  | 0.0 | -0.200179 | 0.0 | 0.0 |  |  |
| train | standard_split | train | llm_lns_is | llm_lns_is | adaptive | True |  | 0.4 | -8.556178 | 15.709057 | 0.0 |  |  |
| train | standard_split | train | llm_lns_is | llm_lns_is | conservative | True |  | 0.0 | -3.50494 | 1.53662 | 0.0 |  |  |
| train | standard_split | train | llm_lns_is | llm_lns_is | safe_fallback_only | True |  | 0.0 | -0.200177 | 0.0 | 0.0 |  |  |
| train | standard_split | train | llm_lns_is | llm_lns_is | learned_controller | True |  | 0.4 | -8.107996 | 14.377601 | 0.0 |  |  |
| train | standard_split | train | llm_lns_is | llm_lns_is | llm_one_shot | True |  | 0.0 | -8.589995 | 17.153104 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | vanilla | True |  | 0.0 | -0.200226 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | adaptive | True |  | 0.4 | -8.558232 | 15.709057 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | conservative | True |  | 0.0 | -3.539591 | 1.534044 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | safe_fallback_only | True |  | 0.0 | -0.200215 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | learned_controller | True |  | 0.4 | -8.357302 | 14.377601 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_is | llm_lns_is | llm_one_shot | True |  | 0.0 | -8.624489 | 17.153104 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | vanilla | True |  | 0.0 | -0.200179 | 0.0 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | adaptive | True |  | 0.4 | -8.75295 | 19.342581 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | conservative | True |  | 0.0 | -3.621864 | 1.85832 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | safe_fallback_only | True |  | 0.0 | -0.200188 | 0.0 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | learned_controller | True |  | 0.4 | -8.249012 | 14.95386 | 0.0 |  |  |
| test | standard_split | test | llm_lns_is | llm_lns_is | llm_one_shot | True |  | 0.0 | -8.776394 | 20.872622 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | vanilla | True |  | 0.0 | -0.200186 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | adaptive | True |  | 0.4 | -8.752983 | 19.342581 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | conservative | True |  | 0.0 | -3.621858 | 1.85832 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | safe_fallback_only | True |  | 0.0 | -0.200179 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | learned_controller | True |  | 0.4 | -8.249009 | 14.95386 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_is | llm_lns_is | llm_one_shot | True |  | 0.0 | -8.776393 | 20.872622 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | vanilla | True |  | 0.0 | -0.472127 | 0.311988 | 0.0 | independent_set | set_cover |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | adaptive | True |  | 0.4 | -3.354627 | 1.0 | 0.0 | independent_set | set_cover |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | conservative | True |  | 0.0 | -2.661051 | 0.872664 | 0.0 | independent_set | set_cover |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.472127 | 0.311988 | 0.0 | independent_set | set_cover |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | learned_controller | True |  | 0.4 | -3.254636 | 1.0 | 0.0 | independent_set | set_cover |
| test | cross_problem_transfer | independent_set_to_setcover | llm_lns_is | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.204624 | 1.0 | 0.0 | independent_set | set_cover |
