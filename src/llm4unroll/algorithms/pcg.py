from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import add, dot, norm2, scale, sub


class PCGRunner(UnrolledAlgorithmRunner):
    algorithm_name = "PCG"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        h = payload["H"]
        rhs = payload["rhs"]
        x_star = payload["x_star"]

        n = len(rhs)
        x = [0.0] * n
        r = sub(rhs, _sym_matvec(h, x))
        p = list(r)
        damping = 1.0
        step_clip = 1.0
        stagnation_count = 0
        best_residual = norm2(r)
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()

        for k in range(budget.max_iters):
            residual_norm = norm2(r)
            residual_ratio = residual_norm / max(best_residual, 1e-9)
            direction_curvature = dot(p, _sym_matvec(h, p))
            state = {
                "k": k,
                "obj": _quadratic_objective(h, rhs, x),
                "obj_prev": trace.objectives[-1] if trace.objectives else _quadratic_objective(h, rhs, x),
                "gap": norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9),
                "residual_norm": residual_norm,
                "residual_ratio": residual_ratio,
                "direction_curvature": direction_curvature,
                "precond_quality": 1.0,
                "step_clip": step_clip,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state({
                "violation": residual_norm,
                "gap": norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9),
            }, None if not trace.primal_residuals else {"violation": trace.primal_residuals[-1]})
            if not guard_status.ok:
                failed = True
                failure_reason = guard_status.reason
                break

            policy_output = policy(state)
            do_restart = False
            for action in policy_output.get("actions", []):
                name = action.get("name")
                value = action.get("value")
                if name == "damp" and value is not None:
                    damping = max(0.05, min(1.0, float(value)))
                elif name == "clip_update" and value is not None:
                    step_clip = max(1e-3, min(5.0, float(value)))
                elif name == "restart":
                    do_restart = True
                elif name == "fallback":
                    damping = min(damping, 1.0)

            if do_restart:
                p = list(r)

            hp = _sym_matvec(h, p)
            denom = max(dot(p, hp), 1e-9)
            alpha = min(step_clip, damping * dot(r, r) / denom)
            x = add(x, scale(p, alpha))
            r_next = sub(r, scale(hp, alpha))
            beta = dot(r_next, r_next) / max(dot(r, r), 1e-9)
            p = add(r_next, scale(p, beta))
            r = r_next

            trace.objectives.append(_quadratic_objective(h, rhs, x))
            trace.gaps.append(norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9))
            trace.primal_residuals.append(residual_norm)
            trace.dual_residuals.append(abs(direction_curvature))
            if residual_norm < best_residual - 1e-9:
                best_residual = residual_norm
                stagnation_count = 0
            else:
                stagnation_count += 1

        final_gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
        final_residual = norm2(sub(rhs, _sym_matvec(h, x)))
        return EvalMetrics(
            objective=_quadratic_objective(h, rhs, x),
            best_bound=None,
            gap=final_gap,
            primal_residual=final_residual,
            dual_residual=abs(dot(x, _sym_matvec(h, x))),
            violation=final_residual,
            integrality_gap=None,
            runtime=time.time() - started,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__},
        )


def _sym_matvec(matrix, vector):
    out = [0.0] * len(vector)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            out[i] += value * vector[j]
    return out


def _quadratic_objective(h, rhs, x):
    hx = _sym_matvec(h, x)
    return 0.5 * dot(x, hx) - dot(rhs, x)
