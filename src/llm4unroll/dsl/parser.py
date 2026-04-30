from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List


@dataclass
class ParsedPolicy:
    source: str
    function_name: str
    actions_literals: List[str]
    tree: ast.AST


def parse_policy_source(source: str) -> ParsedPolicy:
    stripped = source.strip()
    tree = ast.parse(stripped)
    function_name = ""
    actions_literals: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not function_name:
            function_name = node.name
        if isinstance(node, ast.Dict):
            for key_node, value_node in zip(node.keys, node.values):
                if isinstance(key_node, ast.Constant) and key_node.value == "name" and isinstance(value_node, ast.Constant):
                    actions_literals.append(str(value_node.value))
    if not function_name:
        raise ValueError("Policy source must define a function.")
    return ParsedPolicy(
        source=stripped,
        function_name=function_name,
        actions_literals=actions_literals,
        tree=tree,
    )
