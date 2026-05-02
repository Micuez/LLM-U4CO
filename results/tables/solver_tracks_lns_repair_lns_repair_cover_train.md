# Solver Specialist Track Summary

| algorithm | problem_family | split | solver_name | origin | specialist_track | available | native_used | support_level | supports_native | supports_surrogate | paper_scale_pending | backend_mode | backend_detail | score | median_gap | median_violation | median_runtime | median_iterations | fail_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LNS_REPAIR | lns_repair_cover | train | PySCIPOpt | solver_specialist | callback_ready_primal_heuristic_track | True | True |  | False | False | True | python_package | python package pyscipopt importable | -0.560259 | 0.0 | 0.0 | 0.007521 | 1 | 0.0 |
| LNS_REPAIR | lns_repair_cover | train | OR-Tools | solver_specialist | ortools_mip_relaxation_track | True | True |  | False | False | True | python_package | python package ortools importable | -0.847108 | 0.332439 | 0.0 | 0.006432 | 0 | 0.0 |
| LNS_REPAIR | lns_repair_cover | train | Ecole | solver_specialist | ecole_benchmark_bridge_track | False | False | surrogate_only | False | True | True | surrogate | ModuleNotFoundError: No module named 'ecole' | -0.135387 | 0.0 | 0.0 | 0.001447 | 1 | 0.0 |
