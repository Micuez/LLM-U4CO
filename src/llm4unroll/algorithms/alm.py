from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import dot, matvec, norm2, scale, sub, t_matvec


class ALMRunner(UnrolledAlgorithmRunner):
    algorithm_name = "ALM"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        a = payload["A"]
        b = payload["b"]
        x_star = payload["x_star"]
        reg = payload["reg"]
        c = payload["c"]

        n = len(x_star)
        m = len(b)
        x = [0.0] * n
        lam = [0.0] * m
        rho = 1.0
        clip_scale = 1.0
        stagnation_count = 0
        best_obj = float("inf")
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()
        grad_scale = 1.0 / max(1.0, reg + 2.0 * rho * len(a))

        for k in range(budget.max_iters):
            ax_minus_b = sub(matvec(a, x), b)
            violation = norm2(ax_minus_b)
            dual_term = t_matvec(a, [lam_i + rho * res_i for lam_i, res_i in zip(lam, ax_minus_b)])
            gradient = [reg * x[i] + c[i] + dual_term[i] for i in range(n)]
            obj = 0.5 * reg * dot(x, x) + dot(c, x)
            gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)

            state = {
                "k": k,
                "obj": obj,
                "obj_prev": trace.objectives[-1] if trace.objectives else obj,
                "gap": gap,
                "violation": violation,
                "rho": rho,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state(state, None if not trace.primal_residuals else {
                "violation": trace.primal_residuals[-1],
            })
            if not guard_status.ok:
                failed = True
                failure_reason = guard_status.reason
                break

            policy_output = policy(state)
            do_restart = False
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
                    do_restart = True
                elif name == "fallback":
                    rho = min(rho, 1.0)
                    clip_scale = min(clip_scale, 1.0)

            if do_restart:
                lam = [0.0] * m

            grad_scale = 1.0 / max(1.0, reg + 2.0 * rho * len(a))
            x_next = [x[i] - clip_scale * grad_scale * gradient[i] for i in range(n)]
            x = x_next
            lam = [lam_i + rho * res_i for lam_i, res_i in zip(lam, sub(matvec(a, x), b))]

            trace.objectives.append(obj)
            trace.gaps.append(gap)
            trace.primal_residuals.append(violation)
            trace.dual_residuals.append(norm2(lam))
            if obj < best_obj - 1e-9:
                best_obj = obj
                stagnation_count = 0
            else:
                stagnation_count += 1

        final_violation = norm2(sub(matvec(a, x), b))
        final_obj = 0.5 * reg * dot(x, x) + dot(c, x)
        final_gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
        return EvalMetrics(
            objective=final_obj,
            best_bound=None,
            gap=final_gap,
            primal_residual=final_violation,
            dual_residual=norm2(lam),
            violation=final_violation,
            integrality_gap=None,
            runtime=time.time() - started,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__, "rho": rho},
        )
