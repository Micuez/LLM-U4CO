# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | vanilla | True |  | 0.0 | -0.335377 | 0.0 | 0.0 |  |  |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | adaptive | True |  | 0.5 | -0.885371 | 0.0 | 0.0 |  |  |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | conservative | True |  | 0.25 | -0.53538 | 0.0 | 0.0 |  |  |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | safe_fallback_only | True |  | 0.0 | -0.335372 | 0.0 | 0.0 |  |  |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | learned_controller | True |  | 0.5 | -0.885368 | 0.0 | 0.0 |  |  |
| train | standard_split | train | lns_repair_cover | lns_repair_cover | llm_one_shot | True |  | 0.5 | -1.035373 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | vanilla | True |  | 0.0 | -0.367436 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | adaptive | True |  | 0.5 | -0.917447 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | conservative | True |  | 0.25 | -0.567439 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | safe_fallback_only | True |  | 0.0 | -0.367431 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | learned_controller | True |  | 0.5 | -0.917444 | 0.0 | 0.0 |  |  |
| validation | standard_split | validation | lns_repair_cover | lns_repair_cover | llm_one_shot | True |  | 0.5 | -1.067442 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | vanilla | True |  | 0.0 | -0.380133 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | adaptive | True |  | 0.5 | -0.93014 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | conservative | True |  | 0.25 | -0.580128 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | safe_fallback_only | True |  | 0.0 | -0.380131 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | learned_controller | True |  | 0.5 | -0.93013 | 0.0 | 0.0 |  |  |
| test | standard_split | test | lns_repair_cover | lns_repair_cover | llm_one_shot | True |  | 0.5 | -1.080132 | 0.0 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | vanilla | True |  | 0.0 | -0.380122 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | adaptive | True |  | 0.5 | -0.930129 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | conservative | True |  | 0.25 | -0.580128 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | safe_fallback_only | True |  | 0.0 | -0.380121 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | learned_controller | True |  | 0.5 | -0.930129 | 0.0 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | lns_repair_cover | lns_repair_cover | llm_one_shot | True |  | 0.5 | -1.08013 | 0.0 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | vanilla | True |  | 0.0 | -0.49878 | 0.0 | 0.0 | sparse_cover | dense_cover |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | adaptive | True |  | 0.5 | -1.04879 | 0.0 | 0.0 | sparse_cover | dense_cover |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | conservative | True |  | 0.25 | -1.57909 | 0.85382 | 0.0 | sparse_cover | dense_cover |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | safe_fallback_only | True |  | 0.0 | -0.498783 | 0.0 | 0.0 | sparse_cover | dense_cover |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | learned_controller | True |  | 0.5 | -1.048804 | 0.0 | 0.0 | sparse_cover | dense_cover |
| test | cross_problem_transfer | cover_repair_to_dense_cover | lns_repair_cover | lns_repair_cover_dense | llm_one_shot | True |  | 0.5 | -1.198802 | 0.0 | 0.0 | sparse_cover | dense_cover |
