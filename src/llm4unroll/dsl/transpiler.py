from __future__ import annotations

from typing import Callable, Dict

from llm4unroll.dsl.parser import parse_policy_source


SAFE_GLOBALS: Dict[str, object] = {
    "__builtins__": {
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "range": range,
        "float": float,
        "int": int,
        "bool": bool,
    }
}


def transpile_identity(source: str) -> str:
    return source


def compile_policy(source: str) -> Callable:
    parsed = parse_policy_source(source)
    namespace: Dict[str, object] = {}
    exec(compile(parsed.tree, filename="<policy>", mode="exec"), SAFE_GLOBALS, namespace)
    policy = namespace.get(parsed.function_name)
    if not callable(policy):
        raise TypeError("Compiled policy is not callable.")
    return policy
