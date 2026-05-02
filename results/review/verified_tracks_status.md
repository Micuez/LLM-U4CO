# Verified Track Status

| Section | Track | Runner | Code Modules | Config | Artifacts | Train-small-test-large | Cross-problem transfer | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 实验计划 / Phase 1 | PDHG synthetic LP | PDHGRunner | 3/3 | OK | 3/3 | pdhg_lp | pdhg_lp->setcover_relaxation<br>pdhg_lp->miplib_rootlp | verified_artifacts_present |
| 与专业求解器结合 / 路线 A | PDHG MIPLIB root-LP | PDHGRunner | 4/4 | OK | 3/3 | miplib_rootlp | miplib_rootlp->llm_lns_sc | verified_artifacts_present |
| 实验计划 / Phase 2 | PDHG LLM-LNS SC | PDHGRunner | 3/3 | OK | 4/4 | llm_lns_sc | llm_lns_sc->llm_lns_is | verified_artifacts_present |
| 实验计划 / Phase 2 | PDHG LLM-LNS IS | PDHGRunner | 3/3 | OK | 3/3 | llm_lns_is | llm_lns_is->llm_lns_sc | verified_artifacts_present |
| 实验计划 / Phase 1 | ADMM synthetic QP | ADMMRunner | 4/4 | OK | 4/4 | admm_qp | admm_qp->admm_qp_relaxation | verified_artifacts_present |
| 实验计划 / Phase 1 | FISTA LASSO | FISTARunner | 2/2 | OK | 3/3 | fista_lasso | fista_lasso->fista_sparse_coding | verified_artifacts_present |
| 算法 Runner 设计 / 扩展线 | ALM equality-QP | ALMRunner | 2/2 | OK | 4/4 | alm_eq_qp | alm_eq_qp->alm_cover_relaxation | verified_artifacts_present |
| 算法 Runner 设计 / 扩展线 | DRS feasibility | DouglasRachfordRunner | 2/2 | OK | 3/3 | drs_feasibility | drs_feasibility->drs_affine_box_shifted | verified_artifacts_present |
| 算法 Runner 设计 / 扩展线 | PCG linear system | PCGRunner | 2/2 | OK | 4/4 | pcg_linear_system | pcg_linear_system->pcg_graph_laplacian | verified_artifacts_present |
| 与专业求解器结合 / 路线 B | LNS repair cover | LNSRepairRunner | 2/2 | OK | 4/4 | lns_repair_cover | lns_repair_cover->lns_repair_cover_dense | verified_artifacts_present |
