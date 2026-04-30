# LLM4Unroll 中文说明

这是 `LLM4Unroll_完整项目方案.tex` 的可运行代码框架版本。

当前项目已经打通以下主线：

- 安全策略 DSL、静态 verifier、运行时 safety guard
- PDHG、ADMM、FISTA、ALM、DRS、PCG、LNS_REPAIR runner
- Phase 1 synthetic benchmark
- Phase 2 小规模 LLM-LNS / MIPLIB 风格 benchmark
- baseline、search、ablation、OOD 实验入口
- mock / 本地 OpenAI-compatible / 远程 API 的 LLM 接口
- HiGHS、OSQP、OR-Tools、PySCIPOpt、Ecole 的 native-or-surrogate solver baseline
- 表格、SVG 图、verifier appendix、native backend usage 报告

## 快速开始

先安装项目：

```bash
python3 -m pip install -e .
```

运行基础 sanity check：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/admm_synthetic_qp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/fista_lasso.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/pdhg_synthetic_lp.yaml
```

也可以直接跑整套框架自检：

```bash
bash scripts/reproduce_phase1.sh
bash scripts/reproduce_phase2.sh
bash scripts/reproduce_framework.sh
bash scripts/reproduce_real_experiments.sh --dry-run
```

## 数据与外部仓库

准备外部仓库软链接：

```bash
bash scripts/setup_external.sh
```

检查 LLM-LNS / MILPBench 本地数据情况：

```bash
bash scripts/prepare_llm_lns_data.sh
```

## 真实实验流程

如果你要跑论文级真实实验，建议按下面流程：

1. 准备外部仓库和数据链接

```bash
bash scripts/setup_external.sh
bash scripts/prepare_llm_lns_data.sh
```

2. 安装原生 solver backend

```bash
python3 -m pip install highspy osqp ortools
python3 -m pip install pyscipopt
python3 -m pip install ecole
```

3. 准备 benchmark 数据

- `data/miplib/miplib_small.txt`：维护 root LP 文件列表
- `data/llm_lns/...`：放置 LLM-LNS 的 LP 数据
- 如需更大实验，可调整 `configs/*.yaml` 里的实例数量

4. 选择 LLM 模式

- `configs/search_mock_llm.yaml`：框架 smoke test
- `configs/search_openai_compatible.example.yaml`：本地部署模型或远程 API

5. 跑 baseline / search

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_baselines --config configs/pdhg_llm_lns_sc.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_evolution_baseline --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_random_search --config configs/pdhg_miplib_rootlp.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_search --config configs/search_openai_compatible.example.yaml --split train
```

6. 跑消融、OOD 和报告生成

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_synthetic_lp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ood --config configs/pdhg_miplib_rootlp.yaml
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

如果要走完整的论文级实验脚手架，也可以直接用 manifest：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_environment
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json
PYTHONPATH=src python3 -m llm4unroll.experiments.aggregate_real_experiments
```

或者直接运行辅助脚本：

```bash
bash scripts/reproduce_real_experiments.sh --dry-run
bash scripts/reproduce_real_experiments.sh
```

7. 查看输出

- 表格：`results/tables/`
- 候选策略归档：`results/candidates/`
- 日志：`results/logs/`
- 图和附录页：`results/figures/`
- 环境检查和 manifest 状态：`results/real_experiments/`

如果 native backend 生效，solver 行里会看到：

- `native_used=True`
- `native_backend=highspy|osqp|ortools|pyscipopt|ecole|...`

如果环境不完整，也可以继续跑，只是会自动退回 `surrogate`。

## LLM 接口

检查当前 LLM client：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_llm_client --config configs/search_mock_llm.yaml
```

如果要接本地部署模型或远程 API，可参考：

- `configs/search_openai_compatible.example.yaml`

需要设置：

- `llm.base_url`
- `llm.model`
- `llm.api_key`（如果需要）

该接口兼容 OpenAI-compatible `/v1/chat/completions` 服务。

## 原生 solver backend

solver baseline 会自动在 `native` 和 `surrogate` 之间切换，不需要额外开关。

当前支持：

- `HiGHS`：优先 `highspy`，其次 `highs` 命令
- `OSQP`：`osqp` Python 包
- `OR-Tools`：`ortools` Python 包
- `PySCIPOpt`：`pyscipopt` Python 包，必要时回退到 `scip` 命令
- `Ecole`：`ecole` Python 包和 SCIP bridge subprocess

完整实验脚手架示例：

- `configs/real_experiment_manifest.json`

建议安装：

```bash
python3 -m pip install highspy osqp ortools
python3 -m pip install pyscipopt
python3 -m pip install ecole
```

注意：

- `PySCIPOpt` 和 `Ecole` 通常需要本地有可用的 SCIP 环境
- `HiGHS` 也可以通过系统 PATH 里的 `highs` 命令启用
- 如果 backend 缺失，框架仍可运行，并在结果里记录 `backend_mode=surrogate`

## 图表与报告

图表层可以直接从 CSV 生成 SVG，不依赖 `matplotlib` 或 `pandas`：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

主要输出包括：

- baseline / search / ablation / OOD 图：`results/figures/`
- verifier 页面：`results/figures/verifier_report.html`
- verifier 附录页：`results/figures/verifier_appendix.html`
- native backend usage 汇总页：`results/figures/native_backend_report.html`

## 当前状态

已经实现并静态闭环：

- DSL、verifier、runtime guard
- 主要 operator-splitting runner
- synthetic + 小规模 Phase 2 benchmark
- evaluator、candidate archive、failure log、report layer
- baseline、search、ablation、OOD、random search、evolution without LLM
- mock / 本地 OpenAI-compatible / 远程 API 的 LLM 接入
- native-or-fallback solver interface

带 surrogate fallback 的部分：

- solver backend 缺失时仍可运行
- Phase 2 数据不足时可使用 bundled mock LP
- 没有真实 LLM 时可用 `mock` 跑通搜索闭环

## 尚未完成

真实实验部分：

- 安装完整 native solver 环境后重跑大规模实验
- 使用更完整的 MIPLIB / LLM-LNS 数据
- 跑论文级大预算 search、ablation、OOD
- 与真实外部 baseline 做同预算对照

框架扩展但尚未做满的部分：

- Bayesian optimisation / grid search baseline
- learned-controller baseline
- 独立的 `LLM one-shot without verifier` 实验入口
- 更完整的论文级 ablation 矩阵
- PySCIPOpt callback 级接入、Ecole 主 benchmark 化、OR-Tools 专项 PDLP / CP-SAT track
- LLM-LNS heuristic 与 LLM4Unroll 的完整组合式强对照
- HeuriGym 风格 benchmark 集成

简而言之：当前仓库已经是一个可运行、可复现实验流程的框架；剩余工作主要集中在真实大规模实验和论文级扩展项。
