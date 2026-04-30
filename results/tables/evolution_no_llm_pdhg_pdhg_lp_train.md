# Evolution Without LLM Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PDHG | search_seed | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -2.682364 | 0.784892 | 0.0 | search_seed |  |
| PDHG | search_variant_1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.222828 | 0.278459 | 0.0 | mutation |  |
| PDHG | search_variant_2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.267633 | 0.271429 | 0.0 | mutation |  |
| PDHG | evo_g01_p00_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.209272 | 0.251052 | 0.0 | evolution_no_llm | search_variant_1 |
| PDHG | evo_g01_p00_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.223384 | 0.279666 | 0.0 | evolution_no_llm | search_variant_1 |
| PDHG | evo_g01_p01_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.267621 | 0.271429 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g01_p01_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.267623 | 0.271429 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g02_p00_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.274577 | 0.298036 | 0.0 | evolution_no_llm | evo_g01_p00_c00 |
| PDHG | evo_g02_p00_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.22475 | 0.283264 | 0.0 | evolution_no_llm | evo_g01_p00_c00 |
| PDHG | evo_g02_p01_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.282408 | 0.297804 | 0.0 | evolution_no_llm | search_variant_1 |
| PDHG | evo_g02_p01_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.283304 | 0.297571 | 0.0 | evolution_no_llm | search_variant_1 |
