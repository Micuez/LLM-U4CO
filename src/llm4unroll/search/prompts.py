SYSTEM_PROMPT = """
You are designing a verifiable update policy for an unrolled operator-splitting optimiser.
Return Python code for `policy(state: dict) -> dict`.
The policy must only read allowed state fields and must always include a fallback action.
"""

GENERATION_PROMPT = """
Design a compact policy for the target algorithm. Prefer residual balancing, conservative damping,
and restarts triggered by stagnation or metric imbalance.
"""

REFLECTION_PROMPT = """
Given the diagnostics, revise thresholds, multiplicative factors, and fallback behavior to reduce failure rate.
"""


def build_generation_prompt(algorithm_name: str, problem_family: str, spec, parent_source: str = "", diagnostics: str = "") -> str:
    lines = [
        "Target algorithm: %s" % algorithm_name,
        "Problem family: %s" % problem_family,
        "Allowed state features: %s" % ", ".join(spec.state.allowed_features),
        "Required state features: %s" % ", ".join(spec.state.required_features),
        "Allowed actions: %s" % ", ".join(action.name for action in spec.actions),
        GENERATION_PROMPT.strip(),
    ]
    if parent_source:
        lines.append("Parent policy source:\n%s" % parent_source)
    if diagnostics:
        lines.append("Diagnostics:\n%s" % diagnostics)
        lines.append(REFLECTION_PROMPT.strip())
    lines.append("Output only Python code for one function named `policy`.")
    return "\n\n".join(lines)
