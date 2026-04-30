from __future__ import annotations

import time
from typing import Dict, List

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import add, dot, matvec, norm2, scale, sub, t_matvec


def _project_nonnegative(values: List[float]) -> List[float]:
    return [max(0.0, value) for value in values]


class PDHGRunner(UnrolledAlgorithmRunner):
    algorithm_name = "PDHG"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        a = payload["A"]
        b = payload["b"]
        c = payload["c"]
        reg = payload["reg"]
        x_star = payload["x_star"]

        n = len(c)
        m = len(b)
        x = [0.0] * n
        x_prev = list(x)
        x_bar = list(x)
        y = [0.0] * m
        tau = 0.4
        sigma = 0.4
        theta = 1.0
        clip_scale = 1.0
        stagnation_count = 0
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()
        best_obj = float("inf")

        for k in range(budget.max_iters):
            primal_residual = norm2(sub(matvec(a, x), b))
            dual_step = norm2(sub(x, x_prev))
            obj = dot(c, x) + 0.5 * reg * dot(x, x)
            x_gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
            state = {
                "k": k,
                "obj": obj,
                "obj_prev": trace.objectives[-1] if trace.objectives else obj,
                "gap": x_gap,
                "r_p_norm": primal_residual,
                "r_d_norm": dual_step,
                "violation": primal_residual,
                "tau": tau,
                "sigma": sigma,
                "theta": theta,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }

            guard_status = self.guard.check_state(state, None if not trace.primal_residuals else {
                "r_p_norm": trace.primal_residuals[-1],
                "r_d_norm": trace.dual_residuals[-1],
                "violation": trace.primal_residuals[-1],
            })
            if not guard_status.ok:
                failed = True
                failure_reason = guard_status.reason
                break

            policy_output = policy(state)
            for action in policy_output.get("actions", []):
                name = action.get("name")
                value = action.get("value")
                if name == "set_tau" and value is not None:
                    tau = self.guard.clip_named("tau", float(value))
                elif name == "set_sigma" and value is not None:
                    sigma = self.guard.clip_named("sigma", float(value))
                elif name == "scale_tau" and value is not None:
                    tau = self.guard.clip_named("tau", tau * float(value))
                elif name == "scale_sigma" and value is not None:
                    sigma = self.guard.clip_named("sigma", sigma * float(value))
                elif name == "damp" and value is not None:
                    clip_scale = max(0.05, min(1.0, float(value)))
                elif name == "restart":
                    x_bar = list(x)
                    y = [0.0] * m
                elif name == "fallback":
                    tau = min(tau, 0.4)
                    sigma = min(sigma, 0.4)
                    clip_scale = min(clip_scale, 1.0)

            y = add(y, scale(sub(matvec(a, x_bar), b), sigma))
            gradient = add(t_matvec(a, y), c)
            x_candidate = []
            for idx, value in enumerate(x):
                numerator = value - tau * gradient[idx]
                new_value = numerator / (1.0 + tau * reg)
                delta = new_value - value
                x_candidate.append(value + clip_scale * delta)
            x_prev = list(x)
            x = _project_nonnegative(x_candidate)
            x_bar = add(x, scale(sub(x, x_prev), theta))

            trace.objectives.append(obj)
            trace.gaps.append(x_gap)
            trace.primal_residuals.append(primal_residual)
            trace.dual_residuals.append(dual_step)
            if obj < best_obj - 1e-9:
                best_obj = obj
                stagnation_count = 0
            else:
                stagnation_count += 1

        final_obj = dot(c, x) + 0.5 * reg * dot(x, x)
        final_gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
        final_primal = norm2(sub(matvec(a, x), b))
        final_dual = norm2(sub(x, x_prev))
        runtime = time.time() - started
        return EvalMetrics(
            objective=final_obj,
            best_bound=None,
            gap=final_gap,
            primal_residual=final_primal,
            dual_residual=final_dual,
            violation=final_primal,
            integrality_gap=None,
            runtime=runtime,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__, "x_norm": norm2(x)},
        )
