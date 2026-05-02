# Manifest Status

- manifest: llm4unroll_real_experiments
- description: Paper-grade experiment scaffold for native solver runs, exact external-baseline probes, larger benchmark subsets, search, ablation, and reporting.

| Job | Stage | OK | Runtime(s) | Return | Artifacts |
| --- | --- | --- | --- | --- | --- |
| native_probe_pdhg_miplib_train | native_probe | True | 6.42 | 0 | results/tables/native_probe_pdhg_miplib_rootlp_train.csv |
| native_probe_admm_qp_train | native_probe | True | 7.40 | 0 | results/tables/native_probe_admm_admm_qp_train.csv |
| native_probe_alm_eq_qp_train | native_probe | True | 2.91 | 0 | results/tables/native_probe_alm_alm_eq_qp_train.csv |
| native_probe_pcg_linear_system_train | native_probe | True | 2.54 | 0 | results/tables/native_probe_pcg_pcg_linear_system_train.csv |
| solver_tracks_lns_repair_cover_train | native_probe | True | 2.22 | 0 | results/tables/solver_tracks_lns_repair_lns_repair_cover_train.csv |
| native_installation_blockers | native_probe | True | 0.68 | 0 | results/real_experiments/native_installation_blockers.json |
