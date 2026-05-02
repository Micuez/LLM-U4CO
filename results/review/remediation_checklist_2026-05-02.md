# LLM4Unroll 最新整改清单

自动生成时间：2026-05-02

## P0

- [x] baseline registry 与实验入口补齐
- [x] ablation 主矩阵最小闭环
- [x] LLM-LNS 四族数据完整

## P1

- [x] 扩展 runner 与验证产物
- [x] README / 状态页区分 implemented / verified
- [x] native solver 论文级主线

## P2

- [x] transfer / generalization 扩展
- [x] 强对照 baseline（最小主线版）
- [x] learned-controller 最小真模型版
- [x] learned-controller 跨全部算法族推广或适用范围收口
- [x] HeuriGym 风格 budget 设置
- [x] 外部 LLM-LNS heuristic / 组合式 pipeline 高保真复现
- [x] 更高预算 learned-controller 强对照版
- [x] repo-local fullstack 外部 baseline replay
- [x] paper-scale learned-controller 训练导出版
- [x] 独立 Bayesian optimisation baseline 入口
- [x] exact external baseline 的 `gurobipy` / license 运行时探针
- [ ] exact external baseline 的 API 环境就绪

## P3

- [x] 审查自动化脚本
- [x] machine-readable 状态页与 manifest coverage
- [x] 自动重写并归档日期化 strict audit / remediation 历史版本

## 当前主要剩余项

1. 补齐 `ecole, scip` 的本地 native 环境与原生验证。
2. 补齐 exact external baseline 复刻所缺环境：missing LLM_API_KEY / LLM_API_ENDPOINT, upstream script still contains placeholder API credentials。
3. 在同硬件、同 timeout 下系统重跑大预算 search / ablation / OOD / transfer 全表。
4. 把外部 baseline 继续推进到 bit-for-bit、同预算、同硬件的全文级复刻。
5. 补完论文级 ablation 矩阵的剩余实跑。

## 未形成完整 AI 会议实验闭环的内容

1. native solver 全覆盖仍未完成：缺少 `ecole, scip` 的本地可用环境或原生验证结果。
2. 大预算真实实验尚未在同硬件、同 timeout 条件下系统重跑 search / ablation / OOD / transfer 全表。
3. 外部 baseline 尚未做到外部仓库 bit-for-bit、同预算、同硬件的全文级复刻。
4. 论文级 ablation 仍未做满：不同 LLM 模型、temperature、prompt variant 与安全开关矩阵尚未全部实跑。

