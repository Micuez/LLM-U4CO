from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import dot, matvec, norm2, scale, soft_threshold, sub, t_matvec


def _estimate_lipschitz(a):
    cols = len(a[0]) if a else 0
    estimate = 0.0
    for j in range(cols):
        column_sq = sum(row[j] * row[j] for row in a)
        estimate = max(estimate, column_sq)
    return max(estimate * len(a), 1.0)


class FISTARunner(UnrolledAlgorithmRunner):
    algorithm_name = "FISTA"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        a = payload["A"]
        b = payload["b"]
        lam = payload["lambda"]
        cols = len(a[0])

        x = [0.0] * cols
        y = list(x)
        x_prev = list(x)
        tau = 1.0 / _estimate_lipschitz(a)
        t = 1.0
        momentum = 0.9
        clip_scale = 1.0
        stagnation_count = 0
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()
        reference = _solve_reference(a, b, lam)
        best_obj = float("inf")

        for k in range(budget.max_iters):
            residual = sub(matvec(a, y), b)
            gradient = t_matvec(a, residual)
            obj = 0.5 * dot(residual, residual) + lam * sum(abs(v) for v in x)
            ref_residual = sub(matvec(a, x), b)
            ref_obj = 0.5 * dot(ref_residual, ref_residual) + lam * sum(abs(v) for v in reference)
            gap = abs(obj - ref_obj) / max(abs(ref_obj), 1e-9)
            step_norm = norm2(sub(x, x_prev))
            state = {
                "k": k,
                "obj": obj,
                "obj_prev": trace.objectives[-1] if trace.objectives else obj,
                "gap": gap,
                "grad_norm": norm2(gradient),
                "step_norm": step_norm,
                "tau": tau,
                "momentum": momentum,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state({
                "obj": obj,
                "gap": gap,
                "tau": tau,
                "momentum": momentum,
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
                if name == "set_tau" and value is not None:
                    tau = self.guard.clip_named("tau", float(value))
                elif name == "scale_tau" and value is not None:
                    tau = self.guard.clip_named("tau", tau * float(value))
                elif name == "set_momentum" and value is not None:
                    momentum = max(0.0, min(0.999, float(value)))
                elif name == "damp" and value is not None:
                    clip_scale = max(0.05, min(1.0, float(value)))
                elif name == "restart":
                    do_restart = True
                elif name == "fallback":
                    tau = min(tau, 1.0 / _estimate_lipschitz(a))
                    momentum = min(momentum, 0.9)

            x_prev = list(x)
            proposed = soft_threshold([y_i - tau * g_i for y_i, g_i in zip(y, gradient)], tau * lam)
            x = [x_prev[i] + clip_scale * (proposed[i] - x_prev[i]) for i in range(cols)]
            t_next = 0.5 * (1.0 + (1.0 + 4.0 * t * t) ** 0.5)
            beta = 0.0 if do_restart else min(momentum, (t - 1.0) / max(t_next, 1e-9))
            y = [x[i] + beta * (x[i] - x_prev[i]) for i in range(cols)]
            t = 1.0 if do_restart else t_next

            trace.objectives.append(obj)
            trace.gaps.append(gap)
            trace.primal_residuals.append(norm2(residual))
            trace.dual_residuals.append(step_norm)
            if obj < best_obj - 1e-9:
                best_obj = obj
                stagnation_count = 0
            else:
                stagnation_count += 1

        residual = sub(matvec(a, x), b)
        final_obj = 0.5 * dot(residual, residual) + lam * sum(abs(v) for v in x)
        reference_residual = sub(matvec(a, reference), b)
        reference_obj = 0.5 * dot(reference_residual, reference_residual) + lam * sum(abs(v) for v in reference)
        final_gap = abs(final_obj - reference_obj) / max(abs(reference_obj), 1e-9)
        runtime = time.time() - started
        return EvalMetrics(
            objective=final_obj,
            best_bound=None,
            gap=final_gap,
            primal_residual=norm2(residual),
            dual_residual=norm2(sub(x, x_prev)),
            violation=0.0,
            integrality_gap=None,
            runtime=runtime,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__, "reference_obj": reference_obj},
        )


def _solve_reference(a, b, lam):
    cols = len(a[0])
    x = [0.0] * cols
    y = list(x)
    t = 1.0
    tau = 1.0 / _estimate_lipschitz(a)
    for _ in range(200):
        gradient = t_matvec(a, sub(matvec(a, y), b))
        x_next = soft_threshold([y_i - tau * g_i for y_i, g_i in zip(y, gradient)], tau * lam)
        t_next = 0.5 * (1.0 + (1.0 + 4.0 * t * t) ** 0.5)
        beta = (t - 1.0) / t_next
        y = [x_next[i] + beta * (x_next[i] - x[i]) for i in range(cols)]
        x = x_next
        t = t_next
    return x
