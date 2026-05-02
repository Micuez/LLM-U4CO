# Evolution Without LLM Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PDHG | search_seed | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -3.129217 | 1.0 | 0.0 | search_seed |  |
| PDHG | search_variant_1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.995709 | 0.63983 | 0.0 | mutation |  |
| PDHG | search_variant_2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764571 | 0.47618 | 0.0 | mutation |  |
| PDHG | evo_g01_p00_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764587 | 0.47618 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g01_p00_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764575 | 0.47618 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g01_p01_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.995712 | 0.63983 | 0.0 | evolution_no_llm | search_variant_1 |
| PDHG | evo_g01_p01_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.995718 | 0.63983 | 0.0 | evolution_no_llm | search_variant_1 |
| PDHG | evo_g02_p00_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764575 | 0.47618 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g02_p00_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764571 | 0.47618 | 0.0 | evolution_no_llm | search_variant_2 |
| PDHG | evo_g02_p01_c00 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764571 | 0.47618 | 0.0 | evolution_no_llm | evo_g01_p00_c01 |
| PDHG | evo_g02_p01_c01 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764573 | 0.47618 | 0.0 | evolution_no_llm | evo_g01_p00_c01 |
