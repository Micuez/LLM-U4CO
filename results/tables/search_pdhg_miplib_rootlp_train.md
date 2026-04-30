# Search Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PDHG | search_seed | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -3.129236 | 1.0 | 0.0 | search_seed |  |
| PDHG | search_variant_1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.99579 | 0.63983 | 0.0 | mutation |  |
| PDHG | search_variant_2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764574 | 0.47618 | 0.0 | mutation |  |
| PDHG | search_seed_reflect | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -3.129243 | 1.0 | 0.0 | reflection | search_seed |
| PDHG | search_variant_1_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.995818 | 0.63983 | 0.0 | funsearch_mutation | search_variant_1 |
| PDHG | search_variant_2_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764576 | 0.47618 | 0.0 | funsearch_mutation | search_variant_2 |
| PDHG | search_variant_2_top1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764569 | 0.47618 | 0.0 | funsearch_mutation | search_variant_2 |
| PDHG | search_variant_2_g2_top2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.764584 | 0.47618 | 0.0 | funsearch_mutation | search_variant_2_g2 |
