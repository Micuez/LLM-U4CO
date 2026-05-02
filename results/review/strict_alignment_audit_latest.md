# LLM4Unroll 与 `LLM4Unroll_完整项目方案.pdf` 最新严格对应性审查

审查时间：2026-05-02

## 结论

当前项目已非常接近严格对应完整方案，剩余差距主要集中在论文级大规模实验与更强外部基线。

## 已核验的自动化证据

本轮自动流程已经覆盖：

1. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.check_environment`
2. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.check_verifier`
3. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run`
4. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.build_status_page`
5. `PYTHONPATH=src:.vendor python3 -m llm4unroll.experiments.generate_review_docs`

## 当前对得比较好的部分

- DSL / verifier / runtime guard 已闭环，见 `results/tables/verifier_positive.csv` 与 `results/tables/verifier_negative.csv`。
- Operator-splitting runner 主线已覆盖 `PDHG / ADMM / FISTA / ALM / DRS / PCG / LNS_REPAIR`。
- OOD / transfer 已扩到多算法族，并在 `results/review/verified_tracks_status.json` 里区分 `train_small_test_large` 与 `cross_problem_transfer`。
- Manifest 编排和审查自动化已落地，计划状态页中 `实验计划 / Manifest 编排` 与 `审查与整改流程产品化` 都是 `implemented_with_artifacts`。

## 与完整方案仍有差距的地方

- Phase 2 LLM-LNS 四族真实 MILPBench 数据已接入，并覆盖 easy / medium / hard 多档规模。
- native solver 已扩到多条本地真 backend 主线；当前可用 native backend 数量 = `4`，但完整论文级 native 覆盖仍未完成。
- learned-controller 已具备最小真模型版、更高预算版和 paper-scale 版，并覆盖 `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR`；剩余差距主要是更大真实训练数据和论文级长程实验预算。
- 强对照 baseline 已包含 repo 内最小主线、外部风格高保真复现主线，以及 repo-local fullstack replay；剩余差距主要是外部仓库 bit-for-bit / 同硬件全文级复刻。

## 关键状态摘录

- `实验计划 / Manifest 编排`: implemented_with_artifacts
- `实验计划 / 强对照 Baseline`: implemented_with_artifacts
- `PDHG LLM-LNS SC`: verified_artifacts_present
- `PDHG LLM-LNS IS`: verified_artifacts_present

## 建议下一步

1. 补齐 exact external baseline 复刻所缺环境：missing LLM_API_KEY / LLM_API_ENDPOINT, upstream script still contains placeholder API credentials。
2. 继续推进 native solver 论文级主线，从当前本地 `highspy / osqp / ortools / pyscipopt` 多 backend 探测扩到更完整环境。

