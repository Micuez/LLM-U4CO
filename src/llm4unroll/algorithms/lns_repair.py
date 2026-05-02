from __future__ import annotations

import time

from llm4unroll.algorithms.base import RunBudget, RunTrace, UnrolledAlgorithmRunner
from llm4unroll.evaluator.metrics import EvalMetrics
from llm4unroll.math_utils import norm2


class LNSRepairRunner(UnrolledAlgorithmRunner):
    algorithm_name = "LNS_REPAIR"

    def run(self, instance, policy, budget: RunBudget) -> EvalMetrics:
        payload = instance.payload
        cover = payload["cover_matrix"]
        costs = payload["costs"]
        x_star = payload["x_star"]
        fractional_target = payload["fractional_target"]

        n = len(costs)
        x = [0.5 for _ in range(n)]
        neighbourhood_ratio = 0.3
        damping = 1.0
        step_clip = 1.0
        stagnation_count = 0
        best_obj = float("inf")
        trace = RunTrace()
        failed = False
        failure_reason = ""
        started = time.time()

        for k in range(budget.max_iters):
            violation = _cover_violation(cover, x)
            rounded = [1.0 if value >= 0.5 else 0.0 for value in x]
            incumbent_obj = _penalized_objective(costs, rounded, cover)
            best_bound = sum(cost * val for cost, val in zip(costs, x_star))
            mip_gap = abs(incumbent_obj - best_bound) / max(abs(best_bound), 1e-9)
            lp_gap = norm2([x[i] - fractional_target[i] for i in range(n)]) / max(norm2(fractional_target), 1e-9)
            fractionality = sum(min(value, 1.0 - value) for value in x) / max(n, 1)
            state = {
                "k": k,
                "incumbent_obj": incumbent_obj,
                "best_bound": best_bound,
                "mip_gap": mip_gap,
                "lp_gap": lp_gap,
                "fractionality": fractionality,
                "violation": violation,
                "neighbourhood_size": neighbourhood_ratio,
                "repair_progress": 1.0 - lp_gap,
                "step_clip": step_clip,
                "stagnation_count": stagnation_count,
                "instance_features": instance.instance_features,
            }
            guard_status = self.guard.check_state({
                "gap": mip_gap,
                "violation": violation,
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
                elif name == "set_neighbourhood_size" and value is not None:
                    neighbourhood_ratio = max(0.05, min(0.95, float(value)))
                elif name == "scale_neighbourhood_size" and value is not None:
                    neighbourhood_ratio = max(0.05, min(0.95, neighbourhood_ratio * float(value)))
                elif name == "clip_update" and value is not None:
                    step_clip = max(0.1, min(2.0, float(value)))
                elif name == "restart":
                    do_restart = True
                elif name == "fallback":
                    damping = min(damping, 1.0)

            if do_restart:
                x = [0.5 for _ in range(n)]
                neighbourhood_ratio = 0.3

            move_count = max(1, int(neighbourhood_ratio * n))
            ranked = sorted(range(n), key=lambda idx: abs(x[idx] - fractional_target[idx]), reverse=True)
            for idx in ranked[:move_count]:
                x[idx] = x[idx] + min(step_clip, damping) * (fractional_target[idx] - x[idx])
                x[idx] = min(max(x[idx], 0.0), 1.0)
            neighbourhood_ratio = min(0.9, max(0.1, neighbourhood_ratio + 0.02 * (1 if violation > 0 else -1)))

            trace.objectives.append(incumbent_obj)
            trace.gaps.append(mip_gap)
            trace.primal_residuals.append(violation)
            trace.dual_residuals.append(lp_gap)
            if incumbent_obj < best_obj - 1e-9:
                best_obj = incumbent_obj
                stagnation_count = 0
            else:
                stagnation_count += 1

        rounded = [1.0 if value >= 0.5 else 0.0 for value in x]
        final_obj = _penalized_objective(costs, rounded, cover)
        best_bound = sum(cost * val for cost, val in zip(costs, x_star))
        final_gap = abs(final_obj - best_bound) / max(abs(best_bound), 1e-9)
        final_violation = _cover_violation(cover, rounded)
        return EvalMetrics(
            objective=final_obj,
            best_bound=best_bound,
            gap=final_gap,
            primal_residual=final_violation,
            dual_residual=norm2([rounded[i] - fractional_target[i] for i in range(n)]),
            violation=final_violation,
            integrality_gap=0.0,
            runtime=time.time() - started,
            iterations=len(trace.objectives),
            memory_mb=None,
            failed=failed,
            failure_reason=failure_reason,
            diagnostics={"trace": trace.__dict__},
        )


def _cover_violation(cover, x):
    violation = 0.0
    for row in cover:
        coverage = sum(row[j] * x[j] for j in range(len(x)))
        violation += max(0.0, 1.0 - coverage)
    return violation


def _penalized_objective(costs, x, cover):
    return sum(cost * val for cost, val in zip(costs, x)) + 5.0 * _cover_violation(cover, x)
