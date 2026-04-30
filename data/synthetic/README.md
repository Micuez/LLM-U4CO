# Synthetic benchmark staging

This directory is reserved for saved synthetic benchmark snapshots if you want
to persist generated LP/QP/LASSO instances outside the in-memory generators.

The current framework can run without any files here because the synthetic
benchmarks are generated on demand in `src/llm4unroll/benchmarks/synthetic_lp_qp.py`.
