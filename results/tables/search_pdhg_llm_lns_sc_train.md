# Search Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PDHG | search_seed | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -3.354745 | 1.0 | 0.0 | search_seed |  |
| PDHG | search_variant_1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444121 | 0.833967 | 0.0 | mutation |  |
| PDHG | search_variant_2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444151 | 0.833967 | 0.0 | mutation |  |
| PDHG | search_seed_reflect | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -3.35469 | 1.0 | 0.0 | reflection | search_seed |
| PDHG | search_variant_1_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444154 | 0.833967 | 0.0 | funsearch_mutation | search_variant_1 |
| PDHG | search_variant_2_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444131 | 0.833967 | 0.0 | funsearch_mutation | search_variant_2 |
| PDHG | search_variant_1_top1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444143 | 0.833967 | 0.0 | funsearch_mutation | search_variant_1 |
| PDHG | search_variant_2_g2_top2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -2.444147 | 0.833967 | 0.0 | funsearch_mutation | search_variant_2_g2 |
