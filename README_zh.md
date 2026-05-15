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

## 代码结构导读

这个仓库的组织方式比较清晰：`src/` 放核心代码，`configs/` 放实验配方，`scripts/` 放一键脚本，`results/` 放跑出来的结果。

```text
LLM-U4CO/
├── README.md
├── README_zh.md
├── pyproject.toml
├── configs/                  # YAML 配置、backend 示例、manifest
├── data/                     # 内置 synthetic 数据和小规模 benchmark 示例
├── results/                  # 表格、review 文档、真实实验探针输出
├── scripts/                  # setup / 数据准备 / 复现实验脚本
└── src/llm4unroll/           # 核心 Python 包
    ├── algorithms/           # PDHG、ADMM、FISTA、ALM、DRS、PCG、LNS_REPAIR runner
    ├── benchmarks/           # synthetic 实例生成器与真实数据 loader
    ├── dsl/                  # policy DSL、schema、parser、transpiler、verifier、guard
    ├── evaluator/            # 指标计算、smoke test、评分、结果导出
    ├── experiments/          # baseline/search/ablation/OOD/manifest 等 CLI 入口
    ├── registry/             # algorithm/problem/baseline 注册表
    ├── search/               # prompt、LLM client、population archive、搜索适配器
    ├── solvers/              # native 或 surrogate solver 接口层
    ├── learned_controller.py # learned-controller baseline 导出
    ├── policies.py           # 手写 baseline 与 search seed policy
    ├── math_utils.py
    └── utils.py
```

### 各层职责

- `src/llm4unroll/experiments/`：最上层运行入口。平时最常用的是 `run_baselines.py`、`run_search.py`、`run_ablation.py`、`run_ood.py`、`run_manifest.py`。
- `src/llm4unroll/experiments/common.py`：公共装配层。负责读 config、选 runner、构造 budget，并按 `problem_family` 生成实例。
- `src/llm4unroll/registry/algorithm_registry.py`：核心协议表。每条算法线在这里定义允许读取哪些状态特征、允许发出哪些动作、以及安全约束是什么。
- `src/llm4unroll/dsl/`：策略 DSL 与安全层。`schema.py` 定义结构，`verifier.py` 做静态检查，`transpiler.py` 把策略源码编译成可执行函数，`guards.py` 负责运行时安全兜底。
- `src/llm4unroll/algorithms/`：具体算法 runner 层。每个 runner 都继承 `algorithms/base.py`，把“策略如何介入某个优化迭代过程”实现出来。
- `src/llm4unroll/benchmarks/`：数据与实例构造层。`synthetic_lp_qp.py` 负责 synthetic，`miplib.py` 和 `llm_lns_data.py` 负责真实风格数据载入。
- `src/llm4unroll/evaluator/`：评估与产物输出层。`optimisation_evaluator.py` 会逐实例执行 policy 或 solver baseline，再把指标聚合成统一分数。
- `src/llm4unroll/search/`：LLM 搜索层。这里有 prompt 模板、OpenAI-compatible client、候选池管理，以及 FunSearch / ReEvo 风格的变异逻辑。
- `src/llm4unroll/solvers/`：solver baseline 层。对 HiGHS、OSQP、OR-Tools、PySCIPOpt、Ecole 做统一封装；native backend 不可用时，会回退到 surrogate。
- `configs/`：实验配方层。决定算法、问题族、budget、数据路径、实例数量、LLM provider 等。
- `scripts/`：粗粒度自动化脚本。适合 setup、数据检查、整套实验复现。
- `results/`：输出目录。包含表格、日志、review 报告、环境探针和真实实验汇总。

### 主执行链路

大多数实验的代码链路可以概括成：

`configs/*.yaml`
-> `experiments/common.py`
-> `registry/algorithm_registry.py`
-> `benchmarks/*` + `algorithms/*`
-> `dsl/verifier.py` 和 `dsl/guards.py`
-> `evaluator/optimisation_evaluator.py`
-> `evaluator/report.py`
-> `results/tables/*` 与 `results/logs/*`

如果是 search，还会再多一层：

`experiments/run_search.py`
-> `search/prompts.py`
-> `search/llm_client.py`
-> `search/population.py`
-> `search/funsearch_adapter.py` / `search/reevo_adapter.py`

### 推荐阅读顺序

如果你想较快读懂这个仓库，我建议按下面顺序看：

1. `src/llm4unroll/experiments/common.py`：先看 config、runner、budget、instance 是怎么装起来的。
2. `src/llm4unroll/registry/algorithm_registry.py`：再看每条算法线的状态/动作/安全约束。
3. `src/llm4unroll/dsl/schema.py` 和 `src/llm4unroll/dsl/verifier.py`：理解 policy 为什么不会“随便生成随便跑”。
4. `src/llm4unroll/algorithms/base.py` + 任意一个具体 runner（建议 `algorithms/pdhg.py`）：理解迭代过程如何接入策略。
5. `src/llm4unroll/experiments/run_baselines.py`：看 baseline 是怎么做 verifier、smoke test、evaluation、落表的。
6. `src/llm4unroll/experiments/run_search.py` 和 `src/llm4unroll/search/`：再看 LLM 搜索是怎么叠上去的。
7. `src/llm4unroll/solvers/` 和 `src/llm4unroll/benchmarks/`：最后按需补 solver backend 与数据侧细节。

## 当前能力矩阵

下面这张表刻意区分“接口存在”“surrogate 可跑”“native 已验证”和“论文级仍待补齐”，避免把它们混成一团：

| 模块 | implemented | runnable_with_surrogate | native_verified | paper_scale_pending |
| --- | --- | --- | --- | --- |
| DSL / verifier / runtime guard | Yes | Yes | N/A | No |
| PDHG / ADMM / FISTA 主线 | Yes | Yes | Partial | Yes |
| ALM / DRS / PCG / LNS_REPAIR | Yes（已补更完整 state/action） | Yes | Partial | Yes |
| solver baseline 接口 | Yes | Yes | Depends on local environment | Yes |
| native backend probe 入口 | Yes | Yes | Depends on local environment | Yes |
| random / evolution without LLM | Yes | Yes | N/A | Partial |
| grid_search baseline | Yes | Yes | N/A | Partial |
| bayesian_optimisation baseline | Yes（已补独立实验入口） | Yes | N/A | Partial |
| learned_controller baseline | Yes（PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR 均已覆盖最小 / 高预算 / paper-scale 导出版） | Yes | N/A | Partial |
| llm_one_shot baseline | Yes | Yes | Depends on LLM backend | Yes |
| ablation 主矩阵 | Yes（最小版） | Yes | N/A | Yes |
| OOD / transfer | Yes（当前为基础版） | Yes | N/A | Yes |
| LLM-LNS 四族数据覆盖 | Partial | Partial | N/A | Yes |

建议先看这几个自动报告：

- `results/real_experiments/environment_report.md`
- `results/tables/native_probe_pdhg_miplib_rootlp_train.csv`
- `results/review/verified_tracks_status.json`
- `results/review/plan_implementation_status.json`
- `results/review/strict_alignment_audit_2026-05-02.md`
- `results/review/remediation_checklist_2026-05-02.md`

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
PYTHONPATH=src python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_sc.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_strong_baselines --config configs/pdhg_llm_lns_is.yaml --split train
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

如果 manifest 产物检查只缺 LLM-LNS 的 paper-budget ablation，可以单独补跑：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_llm_lns_sc_paper.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.run_ablation --config configs/pdhg_llm_lns_is_paper.yaml --split train
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

当前 `run_ablation` 已覆盖的主要维度包括：

- `safe_fallback_only`
- `llm_only_one_shot`
- `without_reflection`
- `without_evolution`
- `random_search_same_budget`
- `bo_same_budget`
- `evolution_without_llm`
- `without_verifier`
- `prompt_variant`
- `llm_model_variant`

如果要走完整的论文级实验脚手架，也可以直接用 manifest：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_environment
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json
PYTHONPATH=src python3 -m llm4unroll.experiments.aggregate_real_experiments
```

如果你想单独检查“native 主线到底有没有真的接上”，现在有一个更明确的入口：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.check_native_backends --config configs/pdhg_miplib_rootlp.yaml --split train
```

这个入口会直接输出 `native_probe_*.csv`，比单看环境报告更接近真实实验行为。

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
- `support_level=native_verified`

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
- `budget.profile` 现已支持 `heurigym_small`、`heurigym_medium`、`paper_native` 等预设，便于按 HeuriGym 风格统一预算
- 如果 backend 缺失，框架仍可运行，并在结果里记录 `backend_mode=surrogate`
- `check_native_backends` 会把当前状态显式汇总为 `native_verified` 或 `surrogate_only`

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

## 已验证算法线映射表

下面这张表只列“当前仓库里已经有 runner、配置和结果产物可对应起来”的算法线，方便快速定位实现和验证证据。

| 算法线 | Runner | 代表配置 | 关键状态/动作 | 已验证结果 | train-small-test-large | cross-problem transfer |
| --- | --- | --- | --- | --- | --- | --- |
| PDHG synthetic LP | `PDHGRunner` | `configs/pdhg_synthetic_lp.yaml` | `r_p_norm / r_d_norm / tau / sigma / restart / scale_tau / scale_sigma` | `results/tables/pdhg_pdhg_lp_train.csv` | `pdhg_lp` | `pdhg_lp -> setcover_relaxation`、`pdhg_lp -> miplib_rootlp` |
| PDHG MIPLIB root-LP | `PDHGRunner` | `configs/pdhg_miplib_rootlp.yaml` | `gap / violation / tau / sigma / native probe` | `results/tables/pdhg_miplib_rootlp_train.csv`、`results/tables/native_probe_pdhg_miplib_rootlp_train.csv` | `miplib_rootlp` | `miplib_rootlp -> llm_lns_sc` |
| PDHG LLM-LNS SC | `PDHGRunner` | `configs/pdhg_llm_lns_sc.yaml` | `mip-style LP relaxation / residual balancing / solver baseline` | `results/tables/pdhg_llm_lns_sc_train.csv` | `llm_lns_sc` | `llm_lns_sc -> llm_lns_is` |
| PDHG LLM-LNS IS | `PDHGRunner` | `configs/pdhg_llm_lns_is.yaml` | `instance_features / residual balancing / solver baseline` | `results/tables/pdhg_llm_lns_is_train.csv` | `llm_lns_is` | `llm_lns_is -> llm_lns_sc` |
| ADMM synthetic QP | `ADMMRunner` | `configs/admm_synthetic_qp.yaml` | `r_p_norm / r_d_norm / rho / scale_rho / restart / native probe` | `results/tables/admm_admm_qp_train.csv`、`results/tables/native_probe_admm_admm_qp_train.csv` | `admm_qp` | `admm_qp -> admm_qp_relaxation` |
| FISTA LASSO | `FISTARunner` | `configs/fista_lasso.yaml` | `obj / obj_prev / gap / momentum / restart / scale_tau` | `results/tables/fista_fista_lasso_train.csv` | `fista_lasso` | `fista_lasso -> fista_sparse_coding` |
| ALM equality-QP | `ALMRunner` | `configs/alm_eq_qp.yaml` | `violation / rho / dual_residual / grad_norm / clip_update / native probe` | `results/tables/alm_alm_eq_qp_train.csv`、`results/tables/native_probe_alm_alm_eq_qp_train.csv` | `alm_eq_qp` | `alm_eq_qp -> alm_cover_relaxation` |
| DRS feasibility | `DouglasRachfordRunner` | `configs/drs_feasibility.yaml` | `residual_norm / lambda_relax / dual_residual / set_lambda_relax / clip_update` | `results/tables/drs_drs_feasibility_train.csv` | `drs_feasibility` | `drs_feasibility -> drs_affine_box_shifted` |
| PCG linear system | `PCGRunner` | `configs/pcg_linear_system.yaml` | `residual_ratio / direction_curvature / gap / clip_update / restart / native probe` | `results/tables/pcg_pcg_linear_system_train.csv`、`results/tables/native_probe_pcg_pcg_linear_system_train.csv` | `pcg_linear_system` | `pcg_linear_system -> pcg_graph_laplacian` |
| LNS repair cover | `LNSRepairRunner` | `configs/lns_repair_cover.yaml` | `mip_gap / fractionality / neighbourhood_size / repair_progress / set_neighbourhood_size` | `results/tables/lns_repair_lns_repair_cover_train.csv` | `lns_repair_cover` | `lns_repair_cover -> lns_repair_cover_dense` |

如果只想确认某条线“是不是已经不只是占位”，最直接的办法是同时看三样：

- 对应 `configs/*.yaml`
- 对应 `results/tables/*.csv`
- `PYTHONPATH=src python3 -m llm4unroll.experiments.check_verifier`

如果你想要 machine-readable 版本的状态页，可以直接生成：

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.build_status_page
```

主要产物：

- `results/review/verified_tracks_status.json`
- `results/review/verified_tracks_status.md`
- `results/review/plan_implementation_status.json`
- `results/review/plan_implementation_status.md`

## 当前状态

已经实现并静态闭环：

- DSL、verifier、runtime guard
- 主要 operator-splitting runner
- synthetic + 小规模 Phase 2 benchmark
- evaluator、candidate archive、failure log、report layer
- baseline、search、ablation、OOD、random search、evolution without LLM
- LLM-LNS heuristic vs LLM4Unroll vs combined pipeline 的强对照入口，以及外部风格高保真对照轨
- grid_search、独立 bayesian_optimisation baseline、最小训练版 + 高预算版 + paper-scale learned_controller、llm_one_shot
- native backend probe 入口
- mock / 本地 OpenAI-compatible / 远程 API 的 LLM 接入
- native-or-fallback solver interface

带 surrogate fallback 的部分：

- solver backend 缺失时仍可运行
- Phase 2 数据路径仍保留 bundled mock LP fallback，但当前本地已接入真实 MILPBench LLM-LNS 数据，并优先加载真实 LP
- 没有真实 LLM 时可用 `mock` 跑通搜索闭环
- Bayesian optimisation 已具备独立实验入口；learned-controller 已升级到最小训练版 + 高预算版 + paper-scale 版，但还不是论文级完整版
- native probe 会按当前环境自动显示 `native_verified` 或 `surrogate_only`；本仓库这轮已打通本地 `highspy / osqp / ortools / pyscipopt` 多主线探测

目前环境报告已显式标出：

- 哪些 native backend 缺失
- LLM-LNS 四族数据是否完整
- 真实 LLM-LNS 数据当前覆盖到哪些 level（easy / medium / hard）
- 当前 Phase 2 是否 `complete_phase2`

## 尚未完成

真实实验部分：

- 安装完整 native solver 环境后重跑大规模实验
- 继续把真实 LLM-LNS 数据从当前 easy / medium 扩到完整 hard，并补更完整的真实 MIPLIB 子集
- 跑论文级大预算 search、ablation、OOD
- 与真实外部 baseline 做同硬件、同 timeout、同预算对照

框架扩展但尚未做满的部分：

- 更大规模、真实硬件长预算版 Bayesian optimisation baseline（当前已具备独立实验入口）
- native solver 覆盖继续向论文级全覆盖推进（当前已完成本地 `highspy / osqp / ortools / pyscipopt` 多轨 probe，`ecole / scip` 仍缺）
- 更强版 learned-controller baseline（当前已覆盖 `PDHG / ADMM / FISTA / DRS / ALM / PCG / LNS_REPAIR` 的最小训练版、高预算版与 paper-scale 版，但仍不是论文级完整版）
- 更完整的论文级 ablation 矩阵
- PySCIPOpt callback 级接入、Ecole 主 benchmark 化、OR-Tools 专项 PDLP / CP-SAT track
- 外部系统级全文复现（当前已补高保真 `LLM-LNS heuristic` / `combined pipeline` 对照轨与 repo-local fullstack replay）
- 更完整的 HeuriGym 风格 benchmark 集成（当前已补 `budget.profile` 预算预设）

简而言之：当前仓库已经是一个可运行、可复现实验流程的框架；剩余工作主要集中在真实大规模实验和论文级扩展项。
