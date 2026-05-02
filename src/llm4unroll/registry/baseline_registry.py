BASELINE_REGISTRY = {
    "vanilla": "Default fallback-only policy.",
    "adaptive": "Hand-crafted residual balancing or restart policy.",
    "conservative": "More conservative hand-crafted policy with stronger damping and restart fallback.",
    "safe_fallback_only": "Strict fallback-only control used as the lower-bound safety baseline.",
    "grid_search": "Deterministic safe-template sweep over a small threshold and scaling grid.",
    "bayesian_optimisation": "Standalone Bayesian-optimisation-style safe baseline with acquisition-guided proposal over verified policy templates.",
    "random_search": "Randomized threshold and scaling search over safe templates.",
    "evolution_without_llm": "Mutation-only policy search without any LLM generation or reflection.",
    "llm_one_shot": "Single generated policy evaluated without reflection or evolution.",
    "learned_controller": "Minimal trained controller baseline: a distilled tiny MLP exported back into the safe DSL for PDHG/ADMM/FISTA/DRS/ALM/PCG/LNS_REPAIR.",
    "learned_controller_high_budget": "Higher-budget learned controller baseline: a larger distilled MLP with more samples and epochs, exported back into the safe DSL for the same algorithm families.",
    "learned_controller_paper_scale": "Paper-scale learned controller baseline: a substantially larger distilled MLP with expanded samples and epochs, exported back into the safe DSL for the same algorithm families.",
}
