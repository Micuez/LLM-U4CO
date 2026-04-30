from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import clip, norm2, sub


class ADMMRunner(UnrolledAlgorithmRunner):
    algorithm_name = "ADMM"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        diag_q = payload["diag_q"]
        q = payload["q"]
        lower = payload["lower"]
        upper = payload["upper"]
        x_star = payload["x_star"]

        n = len(diag_q)
        x = [0.0] * n
        z = [0.0] * n
        u = [0.0] * n
        z_prev = list(z)
        rho = 1.0
        alpha = 1.5
        clip_scale = 1.0
        stagnation_count = 0
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()
        best_obj = float("inf")

        for k in range(budget.max_iters):
            primal_residual = norm2(sub(x, z))
            dual_residual = rho * norm2(sub(z, z_prev))
            obj = 0.5 * sum(diag_q[i] * x[i] * x[i] for i in range(n)) + sum(q[i] * x[i] for i in range(n))
            gap = norm2(sub(z, x_star)) / max(norm2(x_star), 1e-9)
            state = {
                "k": k,
                "obj": obj,
                "obj_prev": trace.objectives[-1] if trace.objectives else obj,
                "gap": gap,
                "r_p_norm": primal_residual,
                "r_d_norm": dual_residual,
                "violation": max(0.0, max(abs(min(0.0, v - lower)) + abs(max(0.0, v - upper)) for v in z)),
                "rho": rho,
                "alpha": alpha,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state(state, None if not trace.primal_residuals else {
                "r_p_norm": trace.primal_residuals[-1],
                "r_d_norm": trace.dual_residuals[-1],
                "violation": 0.0,
            })
            if not guard_status.ok:
                failed = True
                failure_reason = guard_status.reason
                break

            policy_output = policy(state)
            for action in policy_output.get("actions", []):
                name = action.get("name")
                value = action.get("value")
                if name == "set_rho" and value is not None:
                    rho = self.guard.clip_named("rho", float(value))
                elif name == "scale_rho" and value is not None:
                    rho = self.guard.clip_named("rho", rho * float(value))
                elif name == "damp" and value is not None:
                    clip_scale = max(0.05, min(1.0, float(value)))
                elif name == "restart":
                    u = [0.0] * n
                elif name == "fallback":
                    rho = min(rho, 1.0)
                    clip_scale = min(clip_scale, 1.0)

            x = [(rho * (z[i] - u[i]) - q[i]) / (diag_q[i] + rho) for i in range(n)]
            x_hat = [alpha * x[i] + (1.0 - alpha) * z[i] for i in range(n)]
            z_prev = list(z)
            z_target = clip([x_hat[i] + u[i] for i in range(n)], lower, upper)
            z = [z[i] + clip_scale * (z_target[i] - z[i]) for i in range(n)]
            u = [u[i] + x_hat[i] - z[i] for i in range(n)]

            trace.objectives.append(obj)
            trace.gaps.append(gap)
            trace.primal_residuals.append(primal_residual)
            trace.dual_residuals.append(dual_residual)
            if obj < best_obj - 1e-9:
                best_obj = obj
                stagnation_count = 0
            else:
                stagnation_count += 1

        final_obj = 0.5 * sum(diag_q[i] * z[i] * z[i] for i in range(n)) + sum(q[i] * z[i] for i in range(n))
        final_gap = norm2(sub(z, x_star)) / max(norm2(x_star), 1e-9)
        final_primal = norm2(sub(x, z))
        final_dual = rho * norm2(sub(z, z_prev))
        runtime = time.time() - started
        return EvalMetrics(
            objective=final_obj,
            best_bound=None,
            gap=final_gap,
            primal_residual=final_primal,
            dual_residual=final_dual,
            violation=max(0.0, max(abs(min(0.0, v - lower)) + abs(max(0.0, v - upper)) for v in z)),
            integrality_gap=None,
            runtime=runtime,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__, "rho": rho},
        )
