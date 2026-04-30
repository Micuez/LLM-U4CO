# Verifier Negative Cases

| case_id | algorithm | status | blocked_flag | error_count | primary_error | all_errors |
| --- | --- | --- | --- | --- | --- | --- |
| missing_fallback | PDHG | BLOCKED | 1 | 2 | Every return path must include a fallback action before returning. | Every return path must include a fallback action before returning. | Policy must emit a fallback action on at least one path. |
| forbidden_import | ADMM | BLOCKED | 1 | 1 | Imports are not allowed in policy DSL. | Imports are not allowed in policy DSL. |
| illegal_feature | PCG | BLOCKED | 1 | 1 | State feature sigma is not allowed for PCG. | State feature sigma is not allowed for PCG. |
| illegal_action | LNS_REPAIR | BLOCKED | 1 | 1 | Action set_tau is not allowed for LNS_REPAIR. | Action set_tau is not allowed for LNS_REPAIR. |
| conflicting_actions | PDHG | BLOCKED | 1 | 1 | Conflicting actions emitted on one path: set_tau and scale_tau. | Conflicting actions emitted on one path: set_tau and scale_tau. |
| wrong_default_kind | PDHG | BLOCKED | 1 | 1 | Default for state feature instance_features must be dict. | Default for state feature instance_features must be dict. |
