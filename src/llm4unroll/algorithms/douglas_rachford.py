from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import add, matvec, norm2, scale, sub, t_matvec


class DouglasRachfordRunner(UnrolledAlgorithmRunner):
    algorithm_name = "DRS"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        a = payload["A"]
        b = payload["b"]
        x_star = payload["x_star"]
        lower = payload["lower"]
        upper = payload["upper"]

        n = len(x_star)
        z = [0.0] * n
        damping = 1.0
        step_clip = 1.0
        stagnation_count = 0
        best_residual = float("inf")
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()

        for k in range(budget.max_iters):
            x = _project_affine(a, b, z)
            reflected = add(scale(x, 2.0), scale(z, -1.0))
            y = [min(max(value, lower), upper) for value in reflected]
            residual = norm2(sub(y, x))
            gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
            obj = 0.5 * residual * residual
            state = {
                "k": k,
                "obj": obj,
                "obj_prev": trace.objectives[-1] if trace.objectives else obj,
                "gap": gap,
                "residual_norm": residual,
                "lambda_relax": damping,
                "dual_residual": norm2(sub(z, x)),
                "step_clip": step_clip,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state({
                "obj": obj,
                "gap": gap,
                "violation": residual,
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
                elif name == "set_lambda_relax" and value is not None:
                    damping = max(0.05, min(1.95, float(value)))
                elif name == "scale_lambda_relax" and value is not None:
                    damping = max(0.05, min(1.95, damping * float(value)))
                elif name == "clip_update" and value is not None:
                    step_clip = max(1e-3, min(5.0, float(value)))
                elif name == "restart":
                    do_restart = True
                elif name == "fallback":
                    damping = min(damping, 1.0)

            if do_restart:
                z = [0.0] * n
            else:
                z = add(z, scale(sub(y, x), min(damping, step_clip)))

            trace.objectives.append(obj)
            trace.gaps.append(gap)
            trace.primal_residuals.append(residual)
            trace.dual_residuals.append(norm2(sub(z, x)))
            if residual < best_residual - 1e-9:
                best_residual = residual
                stagnation_count = 0
            else:
                stagnation_count += 1

        x = _project_affine(a, b, z)
        final_residual = norm2(sub([min(max(2.0 * x_i - z_i, lower), upper) for x_i, z_i in zip(x, z)], x))
        final_gap = norm2(sub(x, x_star)) / max(norm2(x_star), 1e-9)
        return EvalMetrics(
            objective=0.5 * final_residual * final_residual,
            best_bound=None,
            gap=final_gap,
            primal_residual=final_residual,
            dual_residual=norm2(sub(z, x)),
            violation=final_residual,
            integrality_gap=None,
            runtime=time.time() - started,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__},
        )


def _project_affine(a, b, point):
    residual = sub(matvec(a, point), b)
    correction = t_matvec(a, residual)
    scale_factor = 1.0 / max(1.0, len(a))
    return [point[i] - scale_factor * correction[i] for i in range(len(point))]
