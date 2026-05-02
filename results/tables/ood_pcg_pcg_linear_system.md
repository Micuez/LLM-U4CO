# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | vanilla | True |  | 0.0 | -0.468176 | 3e-06 | 0.0 |  |  |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | adaptive | True |  | 0.0 | -0.918176 | 5e-06 | 0.0 |  |  |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | conservative | True |  | 0.0 | -0.668171 | 6e-06 | 0.0 |  |  |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | safe_fallback_only | True |  | 0.0 | -0.468155 | 3e-06 | 0.0 |  |  |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | learned_controller | True |  | 0.0 | -0.91816 | 5e-06 | 0.0 |  |  |
| train | standard_split | train | pcg_linear_system | pcg_linear_system | llm_one_shot | True |  | 0.0 | -1.218168 | 5e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | vanilla | True |  | 0.0 | -0.55514 | 2e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | adaptive | True |  | 0.0 | -1.005148 | 4e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | conservative | True |  | 0.0 | -0.755153 | 5e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | safe_fallback_only | True |  | 0.0 | -0.555157 | 2e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | learned_controller | True |  | 0.0 | -1.005162 | 4e-06 | 0.0 |  |  |
| validation | standard_split | validation | pcg_linear_system | pcg_linear_system | llm_one_shot | True |  | 0.0 | -1.305163 | 5e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | vanilla | True |  | 0.0 | -0.712338 | 2e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | adaptive | True |  | 0.0 | -1.162328 | 3e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | conservative | True |  | 0.0 | -0.912327 | 4e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | safe_fallback_only | True |  | 0.0 | -0.712305 | 2e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | learned_controller | True |  | 0.0 | -1.162328 | 3e-06 | 0.0 |  |  |
| test | standard_split | test | pcg_linear_system | pcg_linear_system | llm_one_shot | True |  | 0.0 | -1.462331 | 4e-06 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | vanilla | True |  | 0.0 | -0.712337 | 2e-06 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | adaptive | True |  | 0.0 | -1.16232 | 3e-06 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | conservative | True |  | 0.0 | -0.912341 | 4e-06 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | safe_fallback_only | True |  | 0.0 | -0.712331 | 2e-06 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | learned_controller | True |  | 0.0 | -1.16233 | 3e-06 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | pcg_linear_system | pcg_linear_system | llm_one_shot | True |  | 0.0 | -1.462333 | 4e-06 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | vanilla | True |  | 0.0 | -1.010072 | 1e-06 | 0.0 | dense_spd | graph_laplacian |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | adaptive | True |  | 0.0 | -1.460048 | 6e-06 | 0.0 | dense_spd | graph_laplacian |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | conservative | True |  | 0.0 | -1.21105 | 0.000452 | 0.0 | dense_spd | graph_laplacian |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | safe_fallback_only | True |  | 0.0 | -1.010029 | 1e-06 | 0.0 | dense_spd | graph_laplacian |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | learned_controller | True |  | 0.0 | -1.460068 | 6e-06 | 0.0 | dense_spd | graph_laplacian |
| test | cross_problem_transfer | linear_system_to_graph_laplacian | pcg_linear_system | pcg_graph_laplacian | llm_one_shot | True |  | 0.0 | -1.760075 | 6e-06 | 0.0 | dense_spd | graph_laplacian |
