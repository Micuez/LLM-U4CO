# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | fista_lasso | fista_lasso | vanilla | True |  | 0.0 | -0.290512 | 2e-06 | 0.0 |  |  |
| train | standard_split | train | fista_lasso | fista_lasso | adaptive | True |  | 0.4 | -0.940838 | 1.9e-05 | 0.0 |  |  |
| train | standard_split | train | fista_lasso | fista_lasso | conservative | True |  | 0.4 | -0.594374 | 0.000597 | 0.0 |  |  |
| train | standard_split | train | fista_lasso | fista_lasso | safe_fallback_only | True |  | 0.0 | -0.290445 | 2e-06 | 0.0 |  |  |
| train | standard_split | train | fista_lasso | fista_lasso | learned_controller | True |  | 0.4 | -1.300107 | 0.384758 | 0.0 |  |  |
| train | standard_split | train | fista_lasso | fista_lasso | llm_one_shot | True |  | 0.4 | -0.79289 | 0.000203 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | vanilla | True |  | 0.0 | -0.291407 | 3.8e-05 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | adaptive | True |  | 0.4 | -0.942738 | 0.000143 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | conservative | True |  | 0.4 | -0.605857 | 0.004045 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | safe_fallback_only | True |  | 0.0 | -0.291341 | 3.8e-05 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | learned_controller | True |  | 0.4 | -1.827888 | 1.115197 | 0.0 |  |  |
| validation | standard_split | validation | fista_lasso | fista_lasso | llm_one_shot | True |  | 0.4 | -0.798865 | 0.001754 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | vanilla | True |  | 0.0 | -0.301974 | 0.00013 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | adaptive | True |  | 0.4 | -0.955743 | 0.000333 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | conservative | True |  | 0.4 | -0.693971 | 0.064869 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | safe_fallback_only | True |  | 0.0 | -0.301956 | 0.00013 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | learned_controller | True |  | 0.4 | -2.262781 | 1.932113 | 0.0 |  |  |
| test | standard_split | test | fista_lasso | fista_lasso | llm_one_shot | True |  | 0.4 | -0.821105 | 0.005398 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | vanilla | True |  | 0.0 | -0.302044 | 0.00013 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | adaptive | True |  | 0.4 | -0.955751 | 0.000333 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | conservative | True |  | 0.4 | -0.694109 | 0.064869 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | safe_fallback_only | True |  | 0.0 | -0.302072 | 0.00013 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | learned_controller | True |  | 0.4 | -2.262673 | 1.932113 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | fista_lasso | fista_lasso | llm_one_shot | True |  | 0.4 | -0.821042 | 0.005398 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | vanilla | True |  | 0.0 | -0.34169 | 0.001672 | 0.0 | lasso | sparse_coding |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | adaptive | True |  | 0.4 | -1.308488 | 0.193653 | 0.0 | lasso | sparse_coding |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | conservative | True |  | 0.4 | -1.455434 | 0.727333 | 0.0 | lasso | sparse_coding |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | safe_fallback_only | True |  | 0.0 | -0.34172 | 0.001672 | 0.0 | lasso | sparse_coding |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | learned_controller | True |  | 0.4 | -1.865046 | 0.865193 | 0.0 | lasso | sparse_coding |
| test | cross_problem_transfer | lasso_to_sparse_coding | fista_lasso | fista_sparse_coding | llm_one_shot | True |  | 0.4 | -1.424878 | 0.449739 | 0.0 | lasso | sparse_coding |
