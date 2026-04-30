# Search Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PDHG | search_seed | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -2.682403 | 0.784892 | 0.0 | search_seed |  |
| PDHG | search_variant_1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.222853 | 0.278459 | 0.0 | mutation |  |
| PDHG | search_variant_2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.267657 | 0.271429 | 0.0 | mutation |  |
| PDHG | search_seed_reflect | True | True |  |  | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Action scale_tau is emitted without reading state feature tau. | Action scale_sigma is emitted without reading state feature sigma. | Required features not referenced by policy: k, sigma, tau | 0.4 | 6 | -2.789314 | 0.819355 | 0.0 | reflection | search_seed |
| PDHG | search_variant_1_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.224409 | 0.280318 | 0.0 | funsearch_mutation | search_variant_1 |
| PDHG | search_variant_2_g2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.267656 | 0.271429 | 0.0 | funsearch_mutation | search_variant_2 |
| PDHG | search_variant_1_top1 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.223406 | 0.279666 | 0.0 | funsearch_mutation | search_variant_1 |
| PDHG | search_variant_1_g2_top2 | True | True |  |  | Required features not referenced by policy: k, r_d_norm, r_p_norm, sigma, tau | 0.0 | 2 | -1.224409 | 0.280318 | 0.0 | funsearch_mutation | search_variant_1_g2 |
