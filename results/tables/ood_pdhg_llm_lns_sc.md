# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | vanilla | True |  | 0.0 | -0.207982 | 0.007177 | 0.0 |  |  |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | adaptive | True |  | 0.4 | -3.354629 | 1.0 | 0.0 |  |  |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | conservative | True |  | 0.0 | -2.680789 | 0.910018 | 0.0 |  |  |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.207978 | 0.007177 | 0.0 |  |  |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | learned_controller | True |  | 0.4 | -3.254641 | 1.0 | 0.0 |  |  |
| train | standard_split | train | llm_lns_sc | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.20462 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | vanilla | True |  | 0.0 | -0.219902 | 0.007177 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | adaptive | True |  | 0.4 | -3.574697 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | conservative | True |  | 0.0 | -2.941816 | 0.910018 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.219901 | 0.007177 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | learned_controller | True |  | 0.4 | -3.474698 | 1.0 | 0.0 |  |  |
| validation | standard_split | validation | llm_lns_sc | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.424697 | 1.0 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | vanilla | True |  | 0.0 | -0.472122 | 0.311988 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | adaptive | True |  | 0.4 | -3.354624 | 1.0 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | conservative | True |  | 0.0 | -2.661032 | 0.872664 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.472137 | 0.311988 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | learned_controller | True |  | 0.4 | -3.254641 | 1.0 | 0.0 |  |  |
| test | standard_split | test | llm_lns_sc | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.204622 | 1.0 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | vanilla | True |  | 0.0 | -0.472124 | 0.311988 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | adaptive | True |  | 0.4 | -3.354623 | 1.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | conservative | True |  | 0.0 | -2.661032 | 0.872664 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | safe_fallback_only | True |  | 0.0 | -0.472121 | 0.311988 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | learned_controller | True |  | 0.4 | -3.254624 | 1.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | llm_lns_sc | llm_lns_sc | llm_one_shot | True |  | 0.0 | -3.204624 | 1.0 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | vanilla | True |  | 0.0 | -0.20018 | 0.0 | 0.0 | set_cover | independent_set |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | adaptive | True |  | 0.4 | -8.752941 | 19.342581 | 0.0 | set_cover | independent_set |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | conservative | True |  | 0.0 | -3.621855 | 1.85832 | 0.0 | set_cover | independent_set |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | safe_fallback_only | True |  | 0.0 | -0.200189 | 0.0 | 0.0 | set_cover | independent_set |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | learned_controller | True |  | 0.4 | -8.249006 | 14.95386 | 0.0 | set_cover | independent_set |
| test | cross_problem_transfer | setcover_to_independent_set | llm_lns_sc | llm_lns_is | llm_one_shot | True |  | 0.0 | -8.776408 | 20.872622 | 0.0 | set_cover | independent_set |
