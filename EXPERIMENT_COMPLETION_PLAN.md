# Experiment Completion Plan

This document converts the current review assessment into a concrete follow-up experiment plan for turning LLM-U4CO from a verified pilot-scale artifact into a submission-grade NeurIPS/ICLR/ICML-style result.

## 1. Reframe the Main Claim

The current evidence does not yet support a raw performance-SOTA claim. The strongest defensible claim is:

> LLM-U4CO is a verifier-audited framework for generating, filtering, executing, and evaluating LLM-produced unrolled optimization policies. It shows that unconstrained LLM policy search is brittle, while typed DSL verification, runtime guards, fallback policies, OOD evaluation, and manifest-driven reporting make LLM-for-optimization experiments safe and reproducible.

Follow-up experiments should therefore separate two goals:

- **Safety/framework claim:** prove that the verifier and evaluation protocol reliably catch invalid or risky policies across algorithm families.
- **Performance claim:** identify at least one setting where LLM-guided policy search or LLM4Unroll refinement gives a statistically meaningful improvement over strong non-LLM baselines.

## 2. Missing Experiments for a Submission-Grade Package

### 2.1 Scale Up Verified Runs

Current paper configs are pilot scale, usually around 4-8 train instances and 2-5 validation/test instances. For a top-conference submission, expand each major track to larger and repeated runs.

Required additions:

- Run at least 30-100 instances per major family when data is available.
- Use at least 3 random seeds for each main experiment.
- Report mean, median, standard error, and confidence intervals.
- Separate easy / medium / hard splits for LLM-LNS-derived data.
- Keep train, validation, and test splits fixed and documented.
- Add a manifest profile such as `configs/submission_experiment_manifest.json`.

Priority tracks:

- PDHG synthetic LP
- PDHG MIPLIB root-LP
- PDHG LLM-LNS set cover
- PDHG LLM-LNS independent set
- ADMM synthetic QP
- FISTA LASSO
- LNS repair cover

### 2.2 Establish a Positive Performance Case

The current results show that `vanilla` or `safe_fallback_only` often outperforms learned or LLM-generated controllers. This is an important negative result, but the paper will be stronger if at least one controlled setting shows a real gain.

Required additions:

- Search for one family where LLM-generated policies improve median gap, runtime, or iteration count under the same budget.
- Compare against `vanilla`, `adaptive`, `conservative`, `safe_fallback_only`, random search, evolution without LLM, and Bayesian-optimisation-style baselines.
- Report improvement on validation and held-out test, not only train.
- Add paired statistical tests or bootstrap confidence intervals.
- Include a failure-mode table for settings where LLM search hurts performance.

Candidate directions:

- Instance-conditioned step-size control for PDHG.
- Conservative learned restart/fallback policies for FISTA or ADMM.
- LNS repair policy selection where the policy chooses repair scale or neighborhood schedule.
- Hybrid selection: use verifier-safe LLM candidates only when a validation selector predicts improvement; otherwise fall back to vanilla.

### 2.3 Complete Strong Baselines

Current strong baselines exist, but exact external replay is still blocked by environment and upstream credential placeholders.

Required additions:

- Finish exact LLM-LNS upstream replay after API endpoint/key handling is cleaned.
- Run SC, IS, MVC, and MIKS external scripts where possible.
- Compare external heuristic, LLM4Unroll-only, and combined pipeline under the same instance set and budget.
- Add same-hardware, same-time-limit comparisons.
- Record API model, base URL, token budget, sampling parameters, and total cost.

Expected evidence:

- A table showing which external baselines are exact, repo-local replays, or surrogate-style approximations.
- A clear distinction between real native solver evidence and surrogate fallback evidence.

### 2.4 Finish Native Solver Validation

Native package probes are partially available, but command-line SCIP/HiGHS and Ecole coverage remain incomplete.

Required additions:

- Install and verify command-line HiGHS and SCIP if possible.
- Resolve Ecole importability or document it as an environment blocker.
- Re-run native probes after installation.
- For each solver row, report `native_used=True/False`, backend detail, and fallback reason.
- Avoid mixing surrogate solver rows with native solver conclusions.

Priority native checks:

- HiGHS for LP relaxations.
- OSQP for QP and linear-system tracks.
- PySCIPOpt / SCIP for MILP and repair tracks.
- OR-Tools for combinatorial repair baselines.
- Ecole only if a compatible SCIP toolchain can be installed cleanly.

### 2.5 Expand OOD and Transfer Evidence

Current OOD tables show broad coverage and stable failure rates, but not yet LLM-policy superiority.

Required additions:

- Run train-small/test-large scaling experiments.
- Run cross-family transfer with fixed source policy and held-out target family.
- Report degradation from train to validation/test.
- Add OOD plots grouped by policy type.
- Include a selector/fallback analysis: when should the framework reject a learned or LLM-generated policy?

Key metrics:

- median gap
- median residual
- fail rate
- runtime
- verifier pass rate
- fallback trigger rate
- score delta against vanilla and safe fallback

### 2.6 Quantify LLM Search Cost and Failure Modes

A top-conference submission needs cost and reliability accounting.

Required additions:

- Number of prompts and candidates per run.
- Token usage and estimated API cost.
- Verifier rejection rate.
- Smoke-test rejection rate.
- Runtime-guard fallback rate.
- Top invalid-policy categories.
- Sensitivity to model, temperature, and search budget.

Recommended ablations:

- without verifier
- without fallback
- without reflection
- without evolution
- one-shot only
- random candidates with verifier
- non-LLM evolutionary candidates with verifier
- different LLM providers or model families

## 3. Paper Tables and Figures to Add

Required main-paper tables:

- Main result table: vanilla / safe fallback / best LLM policy / random / evolution / BO / native solver.
- OOD table: train / validation / test and train-small/test-large split.
- Strong baseline table for LLM-LNS-style external baselines.
- Verifier table: positive pass cases and negative blocked cases.
- Cost table: prompts, candidates, verifier rejects, smoke rejects, API cost.

Required figures:

- Score and gap distributions by policy type.
- Search trajectory over candidate generations.
- Verifier rejection breakdown.
- Runtime-vs-gap tradeoff.
- OOD degradation plot.
- Native/surrogate backend coverage chart.

## 4. Acceptance Criteria Before Submission

The project is ready for a serious submission draft when the following are true:

- Manifest-listed submission experiments have zero missing artifacts.
- Result tables distinguish native, surrogate, mock, and external-replay evidence.
- At least one performance-positive setting is statistically convincing, or the paper is explicitly framed as a negative/safety benchmark.
- All main claims are backed by tables generated from scripts, not hand-written summaries.
- API keys and local configs are excluded from git.
- Large results, logs, figures, datasets, candidates, and local run artifacts are excluded from the main code commit.
- The paper text clearly states which evidence is pilot-scale and which is submission-scale.

## 5. Immediate Next Commands

Suggested next experiment stage:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/real_experiment_manifest.json --dry-run
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```

After defining larger configs:

```bash
PYTHONPATH=src python3 -m llm4unroll.experiments.run_manifest --manifest configs/submission_experiment_manifest.json
PYTHONPATH=src python3 -m llm4unroll.experiments.build_report_figures
```
