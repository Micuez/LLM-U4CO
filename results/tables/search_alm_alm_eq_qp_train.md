# Search Summary

| algorithm | policy_id | verified | smoke_ok | smoke_reason | errors | warnings | feature_coverage | proof_count | score | median_gap | fail_rate | origin | parent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ALM | search_seed | True | True |  |  | Action scale_rho is emitted without reading state feature rho. | Action scale_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Required features not referenced by policy: k, rho | 0.3333 | 6 | -0.707153 | 0.003682 | 0.0 | search_seed |  |
| ALM | search_variant_1 | True | True |  |  | Required features not referenced by policy: k | 0.6667 | 12 | -1.114438 | 0.006121 | 0.0 | mutation |  |
| ALM | search_variant_2 | True | True |  |  | Required features not referenced by policy: k | 0.6667 | 6 | -0.968667 | 0.008027 | 0.0 | mutation |  |
| ALM | llm_seed | True | True |  |  | Required features not referenced by policy: k, rho, violation | 0.0 | 1 | -0.207137 | 0.003083 | 0.0 | llm_generated | llm |
| ALM | search_seed_reflect | True | True |  |  | Action scale_rho is emitted without reading state feature rho. | Action scale_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Action set_rho is emitted without reading state feature rho. | Required features not referenced by policy: k, rho | 0.3333 | 6 | -0.707474 | 0.003064 | 0.0 | reflection | search_seed |
| ALM | search_variant_1_g2 | True | True |  |  | Required features not referenced by policy: k | 0.6667 | 12 | -1.110616 | 0.004657 | 0.0 | funsearch_mutation | search_variant_1 |
| ALM | search_variant_2_g2 | True | True |  |  | Required features not referenced by policy: k | 0.6667 | 6 | -0.962943 | 0.006382 | 0.0 | funsearch_mutation | search_variant_2 |
| ALM | llm_seed_reflect | True | True |  |  | Required features not referenced by policy: k, rho, violation | 0.0 | 1 | -0.207132 | 0.003083 | 0.0 | llm_generated | llm_seed |
| ALM | llm_seed_reflect_top1 | True | True |  |  | Required features not referenced by policy: k, rho, violation | 0.0 | 1 | -0.207129 | 0.003083 | 0.0 | funsearch_mutation | llm_seed_reflect |
| ALM | llm_seed_top2 | True | True |  |  | Required features not referenced by policy: k, rho, violation | 0.0 | 1 | -0.207129 | 0.003083 | 0.0 | funsearch_mutation | llm_seed |
