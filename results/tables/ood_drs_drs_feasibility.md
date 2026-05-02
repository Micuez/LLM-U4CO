# OOD Summary

| split | evaluation_mode | scenario | source_problem_family | target_problem_family | policy_id | verified | errors | feature_coverage | score | median_gap | fail_rate | source_scale | target_scale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | standard_split | train | drs_feasibility | drs_feasibility | vanilla | True |  | 0.0 | -0.747721 | 0.724358 | 0.0 |  |  |
| train | standard_split | train | drs_feasibility | drs_feasibility | adaptive | True |  | 0.5 | -1.302572 | 0.729108 | 0.0 |  |  |
| train | standard_split | train | drs_feasibility | drs_feasibility | conservative | True |  | 0.0 | -0.961396 | 0.737791 | 0.0 |  |  |
| train | standard_split | train | drs_feasibility | drs_feasibility | safe_fallback_only | True |  | 0.0 | -0.747717 | 0.724358 | 0.0 |  |  |
| train | standard_split | train | drs_feasibility | drs_feasibility | learned_controller | True |  | 0.5 | -1.302569 | 0.729108 | 0.0 |  |  |
| train | standard_split | train | drs_feasibility | drs_feasibility | llm_one_shot | True |  | 0.5 | -1.401476 | 0.728046 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | vanilla | True |  | 0.0 | -0.775564 | 0.770915 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | adaptive | True |  | 0.5 | -1.332184 | 0.779214 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | conservative | True |  | 0.0 | -0.991642 | 0.791012 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | safe_fallback_only | True |  | 0.0 | -0.775568 | 0.770915 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | learned_controller | True |  | 0.5 | -1.332186 | 0.779214 | 0.0 |  |  |
| validation | standard_split | validation | drs_feasibility | drs_feasibility | llm_one_shot | True |  | 0.5 | -1.430753 | 0.777387 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | vanilla | True |  | 0.0 | -0.737321 | 0.702676 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | adaptive | True |  | 0.5 | -1.292418 | 0.706643 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | conservative | True |  | 0.0 | -0.952779 | 0.71528 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | safe_fallback_only | True |  | 0.0 | -0.737322 | 0.702676 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | learned_controller | True |  | 0.5 | -1.292417 | 0.706643 | 0.0 |  |  |
| test | standard_split | test | drs_feasibility | drs_feasibility | llm_one_shot | True |  | 0.5 | -1.390814 | 0.705358 | 0.0 |  |  |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | vanilla | True |  | 0.0 | -0.737321 | 0.702676 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | adaptive | True |  | 0.5 | -1.292418 | 0.706643 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | conservative | True |  | 0.0 | -0.952779 | 0.71528 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | safe_fallback_only | True |  | 0.0 | -0.73732 | 0.702676 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | learned_controller | True |  | 0.5 | -1.29242 | 0.706643 | 0.0 | small_train | large_test |
| test | train_small_test_large | train_small_test_large | drs_feasibility | drs_feasibility | llm_one_shot | True |  | 0.5 | -1.39082 | 0.705358 | 0.0 | small_train | large_test |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | vanilla | True |  | 0.0 | -0.818009 | 0.853956 | 0.0 | affine_box | shifted_box |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | adaptive | True |  | 0.5 | -1.368556 | 0.853961 | 0.0 | affine_box | shifted_box |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | conservative | True |  | 0.0 | -1.019802 | 0.853989 | 0.0 | affine_box | shifted_box |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | safe_fallback_only | True |  | 0.0 | -0.818009 | 0.853956 | 0.0 | affine_box | shifted_box |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | learned_controller | True |  | 0.5 | -1.368556 | 0.853961 | 0.0 | affine_box | shifted_box |
| test | cross_problem_transfer | affine_box_to_shifted_box | drs_feasibility | drs_affine_box_shifted | llm_one_shot | True |  | 0.5 | -1.46853 | 0.85396 | 0.0 | affine_box | shifted_box |
