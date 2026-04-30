from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from llm4unroll.dsl.schema import ActionSpec, PolicySpec


DISALLOWED_NAMES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "pathlib",
    "requests",
    "urllib",
    "shutil",
}

SAFE_NUMERIC_CALLS = {"abs", "min", "max", "float", "int", "bool", "len"}
SCALAR_KINDS = {"number", "bool", "unknown"}


@dataclass
class VerificationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    used_features: List[str] = field(default_factory=list)
    emitted_actions: List[str] = field(default_factory=list)
    max_actions_per_path: int = 0
    feature_coverage: float = 0.0
    proof_obligations: List[str] = field(default_factory=list)
    diagnostics: Dict[str, object] = field(default_factory=dict)


@dataclass
class ValueInfo:
    kind: str
    const_value: object = None


@dataclass
class FlowState:
    env: Dict[str, ValueInfo]
    fallback_guaranteed: bool = False
    actions_defined: bool = False
    actions_upper_bound: int = 0
    path_actions: List[str] = field(default_factory=list)
    path_action_payloads: List[Tuple[str, object]] = field(default_factory=list)
    path_conditions: List[str] = field(default_factory=list)
    proof_notes: List[str] = field(default_factory=list)

    def clone(self) -> "FlowState":
        return FlowState(
            env=dict(self.env),
            fallback_guaranteed=self.fallback_guaranteed,
            actions_defined=self.actions_defined,
            actions_upper_bound=self.actions_upper_bound,
            path_actions=list(self.path_actions),
            path_action_payloads=list(self.path_action_payloads),
            path_conditions=list(self.path_conditions),
            proof_notes=list(self.proof_notes),
        )


class PolicyVerifier:
    def __init__(self, spec: PolicySpec):
        self.spec = spec
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.used_features: List[str] = []
        self.emitted_actions: List[str] = []
        self.proof_obligations: List[str] = []
        self.path_diagnostics: List[Dict[str, object]] = []
        self._saw_return = False

    def verify(self, source: str) -> VerificationResult:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return VerificationResult(ok=False, errors=[repr(exc)])

        function = self._extract_policy_function(tree)
        if function is None:
            return VerificationResult(ok=False, errors=self.errors or ["Policy source must define def policy(state):"])

        initial_state = FlowState(env={"state": ValueInfo("state")})
        fallthrough_states = self._analyze_block(function.body, [initial_state])

        if self.spec.safety.require_explicit_return and fallthrough_states:
            self.errors.append("Policy must return {'actions': actions} on every control-flow path.")
        if self.spec.safety.require_fallback and "fallback" not in self.emitted_actions:
            self.errors.append("Policy must emit a fallback action on at least one path.")

        missing_required = [name for name in self.spec.state.required_features if name not in self.used_features]
        if missing_required:
            self.warnings.append("Required features not referenced by policy: %s" % ", ".join(sorted(missing_required)))

        max_actions = 0
        for state in fallthrough_states:
            max_actions = max(max_actions, state.actions_upper_bound)
        required_count = len(self.spec.state.required_features)
        covered_required = len([name for name in self.spec.state.required_features if name in self.used_features])
        coverage = 1.0 if required_count == 0 else float(covered_required) / float(required_count)
        return VerificationResult(
            ok=not self.errors,
            errors=self.errors,
            warnings=self.warnings,
            used_features=sorted(set(self.used_features)),
            emitted_actions=self.emitted_actions[:],
            max_actions_per_path=max(max_actions, self._static_max_actions()),
            feature_coverage=coverage,
            proof_obligations=self.proof_obligations[:],
            diagnostics={
                "paths": self.path_diagnostics,
                "required_features": list(self.spec.state.required_features),
                "covered_required_features": covered_required,
            },
        )

    def _extract_policy_function(self, tree: ast.Module) -> Optional[ast.FunctionDef]:
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        extra_nodes = [node for node in tree.body if not isinstance(node, ast.FunctionDef) and not self._is_docstring_expr(node)]
        if extra_nodes:
            for node in extra_nodes:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    self.errors.append("Imports are not allowed in policy DSL.")
                else:
                    self.errors.append("Only a single top-level policy function is allowed.")
        if len(functions) != 1:
            self.errors.append("Policy source must contain exactly one top-level function.")
            return None
        function = functions[0]
        if function.name != "policy":
            self.errors.append("Policy function must be named policy.")
        if function.decorator_list:
            self.errors.append("Decorators are not allowed in policy DSL.")
        if len(function.args.args) != 1 or function.args.args[0].arg != "state":
            self.errors.append("Policy signature must be policy(state).")
        if function.args.defaults or function.args.kwonlyargs or function.args.kw_defaults or function.args.vararg or function.args.kwarg:
            self.errors.append("Policy signature must not use defaults, *args, or **kwargs.")
        if not function.body:
            self.errors.append("Policy function body is empty.")
        return function

    def _analyze_block(self, statements: Sequence[ast.stmt], states: List[FlowState]) -> List[FlowState]:
        current_states = states
        for statement in statements:
            if not current_states:
                break
            next_states: List[FlowState] = []
            for state in current_states:
                next_states.extend(self._analyze_statement(statement, state))
            current_states = next_states
        return current_states

    def _analyze_statement(self, statement: ast.stmt, state: FlowState) -> List[FlowState]:
        if isinstance(statement, ast.Assign):
            self._validate_assign(statement, state)
            return [state]
        if isinstance(statement, ast.Expr):
            self._validate_expr_statement(statement.value, state)
            return [state]
        if isinstance(statement, ast.If):
            self._validate_expression(statement.test, state, expect_bool=True)
            then_state = state.clone()
            else_state = state.clone()
            then_state.path_conditions.append("if %s" % self._render_expr(statement.test))
            else_state.path_conditions.append("else not (%s)" % self._render_expr(statement.test))
            then_fallthrough = self._analyze_block(statement.body, [then_state])
            else_fallthrough = self._analyze_block(statement.orelse, [else_state]) if statement.orelse else [else_state]
            return then_fallthrough + else_fallthrough
        if isinstance(statement, ast.Return):
            self._validate_return(statement, state)
            self._saw_return = True
            return []
        if isinstance(statement, ast.Pass):
            return [state]
        self.errors.append("Unsupported statement %s in policy DSL." % statement.__class__.__name__)
        return [state]

    def _validate_assign(self, statement: ast.Assign, state: FlowState) -> None:
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
            self.errors.append("Only simple variable assignment is allowed.")
            return
        target = statement.targets[0].id
        if target in DISALLOWED_NAMES:
            self.errors.append("Forbidden variable name %s." % target)
            return
        if target == "state":
            self.errors.append("Rebinding state is not allowed.")
            return
        if target == "actions":
            if not isinstance(statement.value, ast.List) or statement.value.elts:
                self.errors.append("actions must be initialised as an empty list.")
                return
            state.actions_defined = True
            state.actions_upper_bound = 0
            state.fallback_guaranteed = False
            state.env[target] = ValueInfo("actions")
            state.proof_notes.append("actions initialised")
            return
        value_info = self._validate_expression(statement.value, state)
        state.env[target] = value_info

    def _validate_expr_statement(self, node: ast.expr, state: FlowState) -> None:
        if not isinstance(node, ast.Call):
            self.errors.append("Expression statements must be action emissions.")
            return
        self._validate_action_call(node, state)

    def _validate_action_call(self, node: ast.Call, state: FlowState) -> None:
        if not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, ast.Name):
            self.errors.append("Only actions.append(...) and actions.extend(...) are allowed as statements.")
            return
        owner = node.func.value.id
        method = node.func.attr
        if owner != "actions":
            self.errors.append("Only the actions list may be mutated inside a policy.")
            return
        if not state.actions_defined:
            self.errors.append("actions must be defined before append/extend.")
            return
        if method == "append":
            if len(node.args) != 1 or node.keywords:
                self.errors.append("actions.append must take exactly one positional action dict.")
                return
            action_name = self._validate_action_dict(node.args[0], state)
            if action_name:
                state.actions_upper_bound += 1
                state.path_actions.append(action_name)
                state.path_action_payloads.append((action_name, self._extract_action_value(node.args[0])))
                if action_name == "fallback":
                    state.fallback_guaranteed = True
                    state.proof_notes.append("fallback guaranteed")
        elif method == "extend":
            if len(node.args) != 1 or node.keywords:
                self.errors.append("actions.extend must take exactly one positional list of action dicts.")
                return
            arg = node.args[0]
            if not isinstance(arg, ast.List):
                self.errors.append("actions.extend requires a literal list of action dicts.")
                return
            appended = 0
            fallback_all = True
            for item in arg.elts:
                action_name = self._validate_action_dict(item, state)
                if action_name:
                    appended += 1
                    state.path_actions.append(action_name)
                    state.path_action_payloads.append((action_name, self._extract_action_value(item)))
                    if action_name != "fallback":
                        fallback_all = False
            state.actions_upper_bound += appended
            if appended and fallback_all:
                state.fallback_guaranteed = True
                state.proof_notes.append("fallback guaranteed via extend")
        else:
            self.errors.append("Only append/extend are allowed on actions.")
            return
        if state.actions_upper_bound > self.spec.safety.max_actions_per_call:
            self.errors.append(
                "Policy may emit more than %d actions on one path." % self.spec.safety.max_actions_per_call
            )

    def _validate_action_dict(self, node: ast.AST, state: FlowState) -> Optional[str]:
        if not isinstance(node, ast.Dict):
            self.errors.append("Each action must be a literal dict.")
            return None
        payload = self._extract_dict(node)
        unknown_keys = [key for key in payload if key not in {"name", "value"}]
        if unknown_keys:
            self.errors.append("Unsupported action keys: %s." % ", ".join(sorted(unknown_keys)))
        name_node = payload.get("name")
        if not isinstance(name_node, ast.Constant) or not isinstance(name_node.value, str):
            self.errors.append("Action name must be a string literal.")
            return None
        action_name = str(name_node.value)
        action_spec = self._action_spec(action_name)
        if action_spec is None:
            self.errors.append("Action %s is not allowed for %s." % (action_name, self.spec.algorithm))
            return action_name
        if action_spec.arity == 0 and "value" in payload:
            self.errors.append("Action %s must not carry a value." % action_name)
        if action_spec.arity > 0 and "value" not in payload:
            self.errors.append("Action %s requires a numeric value." % action_name)
        if "value" in payload:
            value_info = self._validate_expression(payload["value"], state)
            if value_info.kind not in {action_spec.value_kind, "unknown"}:
                self.errors.append("Action %s value must be %s." % (action_name, action_spec.value_kind))
            if value_info.const_value is not None:
                self._check_action_bounds(action_name, float(value_info.const_value), action_spec)
        self._check_conflicting_actions(action_name, state, action_spec)
        self._check_parameter_guardrail(action_name, state, action_spec)
        self.emitted_actions.append(action_name)
        return action_name

    def _validate_return(self, statement: ast.Return, state: FlowState) -> None:
        if statement.value is None:
            self.errors.append("Policy must return a dict payload, not bare return.")
            return
        if not isinstance(statement.value, ast.Dict):
            self.errors.append("Policy must return a dict with an actions field.")
            return
        payload = self._extract_dict(statement.value)
        if "actions" not in payload:
            self.errors.append("Return payload must include an actions field.")
            return
        actions_value = payload["actions"]
        if isinstance(actions_value, ast.Name):
            if actions_value.id != "actions":
                self.errors.append("Return payload must expose the actions list.")
            elif not state.actions_defined:
                self.errors.append("actions must be defined before return.")
        elif isinstance(actions_value, ast.List):
            for item in actions_value.elts:
                self._validate_action_dict(item, state)
        else:
            self.errors.append("Return actions must be the actions variable or a literal list.")
        if "metadata" in payload:
            metadata_info = self._validate_expression(payload["metadata"], state)
            if metadata_info.kind not in {"dict", "unknown"}:
                self.errors.append("metadata must be a literal dict or derived dict-like value.")
        if self.spec.safety.require_fallback and not state.fallback_guaranteed:
            self.errors.append("Every return path must include a fallback action before returning.")
        self._check_mathematical_safety(state)
        self.path_diagnostics.append({
            "conditions": list(state.path_conditions),
            "actions": list(state.path_actions),
            "proof_notes": list(state.proof_notes),
            "fallback_guaranteed": state.fallback_guaranteed,
            "actions_upper_bound": state.actions_upper_bound,
        })
        if state.fallback_guaranteed:
            self.proof_obligations.append(
                "path[%d]: fallback satisfied under %s" % (
                    len(self.path_diagnostics),
                    ", ".join(state.path_conditions) if state.path_conditions else "root",
                )
            )

    def _validate_expression(self, node: ast.AST, state: FlowState, expect_bool: bool = False) -> ValueInfo:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return ValueInfo("bool", node.value)
            if isinstance(node.value, (int, float)):
                return ValueInfo("number", float(node.value))
            if isinstance(node.value, str):
                return ValueInfo("string", node.value)
            if node.value is None:
                return ValueInfo("none", None)
            self.errors.append("Unsupported constant %r." % (node.value,))
            return ValueInfo("unknown")
        if isinstance(node, ast.Name):
            if node.id in DISALLOWED_NAMES:
                self.errors.append("Forbidden name %s." % node.id)
                return ValueInfo("unknown")
            if node.id not in state.env:
                self.errors.append("Unknown variable %s." % node.id)
                return ValueInfo("unknown")
            return state.env[node.id]
        if isinstance(node, ast.BinOp):
            left = self._validate_expression(node.left, state)
            right = self._validate_expression(node.right, state)
            if left.kind not in SCALAR_KINDS or right.kind not in SCALAR_KINDS:
                self.errors.append("Binary arithmetic only supports scalar expressions.")
                return ValueInfo("unknown")
            const_value = self._const_eval_binop(node.op, left.const_value, right.const_value)
            return ValueInfo("number", const_value)
        if isinstance(node, ast.UnaryOp):
            operand = self._validate_expression(node.operand, state)
            if operand.kind not in SCALAR_KINDS:
                self.errors.append("Unary operators only support scalar expressions.")
                return ValueInfo("unknown")
            if isinstance(node.op, ast.Not):
                return ValueInfo("bool", None if operand.const_value is None else not bool(operand.const_value))
            if isinstance(node.op, (ast.UAdd, ast.USub)):
                value = operand.const_value
                if value is not None and isinstance(value, (int, float)):
                    value = +value if isinstance(node.op, ast.UAdd) else -value
                else:
                    value = None
                return ValueInfo("number", value)
            self.errors.append("Unsupported unary operator %s." % node.op.__class__.__name__)
            return ValueInfo("unknown")
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                self._validate_expression(value, state, expect_bool=True)
            return ValueInfo("bool")
        if isinstance(node, ast.Compare):
            left = self._validate_expression(node.left, state)
            if left.kind not in SCALAR_KINDS and left.kind != "string":
                self.errors.append("Comparisons only support scalar/string expressions.")
            for comparator in node.comparators:
                info = self._validate_expression(comparator, state)
                if info.kind not in SCALAR_KINDS and info.kind != "string":
                    self.errors.append("Comparisons only support scalar/string expressions.")
            return ValueInfo("bool")
        if isinstance(node, ast.IfExp):
            self._validate_expression(node.test, state, expect_bool=True)
            body = self._validate_expression(node.body, state)
            orelse = self._validate_expression(node.orelse, state)
            if body.kind == orelse.kind:
                return ValueInfo(body.kind)
            return ValueInfo("unknown")
        if isinstance(node, ast.Call):
            return self._validate_call_expression(node, state)
        if isinstance(node, ast.Dict):
            for key_node, value_node in zip(node.keys, node.values):
                key_info = self._validate_expression(key_node, state)
                if key_info.kind != "string":
                    self.errors.append("Dict keys must be string literals.")
                self._validate_expression(value_node, state)
            return ValueInfo("dict")
        if isinstance(node, ast.List):
            for item in node.elts:
                self._validate_expression(item, state)
            return ValueInfo("list")
        if isinstance(node, ast.Tuple):
            for item in node.elts:
                self._validate_expression(item, state)
            return ValueInfo("tuple")
        if isinstance(node, ast.Attribute):
            self.errors.append("Attribute access is restricted to state.get and actions.append/extend.")
            return ValueInfo("unknown")
        if isinstance(node, ast.Subscript):
            self.errors.append("Direct subscripting is not allowed; use state.get(..., default).")
            return ValueInfo("unknown")
        self.errors.append("Unsupported expression %s in policy DSL." % node.__class__.__name__)
        return ValueInfo("unknown")

    def _validate_call_expression(self, node: ast.Call, state: FlowState) -> ValueInfo:
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "state" and node.func.attr == "get":
                return self._validate_state_get(node, state)
            self.errors.append("Method calls other than state.get and actions.append/extend are forbidden.")
            return ValueInfo("unknown")
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in SAFE_NUMERIC_CALLS:
                self.errors.append("Call to %s is forbidden." % name)
                return ValueInfo("unknown")
            for arg in node.args:
                self._validate_expression(arg, state)
            for keyword in node.keywords:
                self._validate_expression(keyword.value, state)
            return ValueInfo("number")
        self.errors.append("Unsupported callable form in policy DSL.")
        return ValueInfo("unknown")

    def _validate_state_get(self, node: ast.Call, state: FlowState) -> ValueInfo:
        if len(node.args) == 0 or len(node.args) > 2 or node.keywords:
            self.errors.append("state.get must be called as state.get('feature', default).")
            return ValueInfo("unknown")
        key_node = node.args[0]
        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
            self.errors.append("state.get feature name must be a string literal.")
            return ValueInfo("unknown")
        key = str(key_node.value)
        if key not in self.spec.state.allowed_features:
            self.errors.append("State feature %s is not allowed for %s." % (key, self.spec.algorithm))
        self.used_features.append(key)
        if self.spec.safety.require_state_get_default and len(node.args) != 2:
            self.errors.append("state.get('%s', default) must provide an explicit default." % key)
        default_info = ValueInfo("unknown")
        if len(node.args) == 2:
            default_info = self._validate_expression(node.args[1], state)
        feature_spec = self.spec.state.feature_types.get(key)
        expected_kind = feature_spec.kind if feature_spec else "number"
        if len(node.args) == 2 and feature_spec and default_info.kind not in {feature_spec.default_kind, "unknown"}:
            self.errors.append(
                "Default for state feature %s must be %s." % (key, feature_spec.default_kind)
            )
        if key == "instance_features":
            return ValueInfo(expected_kind if default_info.kind in {"dict", "list", "tuple", "unknown"} else "unknown")
        const_value = default_info.const_value if default_info.kind == expected_kind else None
        return ValueInfo(expected_kind, const_value)

    def _action_spec(self, name: str) -> Optional[ActionSpec]:
        for action_spec in self.spec.actions:
            if action_spec.name == name:
                return action_spec
        return None

    def _check_action_bounds(self, action_name: str, value: float, spec: ActionSpec) -> None:
        if spec.minimum is not None and value < spec.minimum:
            self.errors.append("Action %s value %.6g is below minimum %.6g." % (action_name, value, spec.minimum))
        if spec.maximum is not None and value > spec.maximum:
            self.errors.append("Action %s value %.6g exceeds maximum %.6g." % (action_name, value, spec.maximum))

    def _check_conflicting_actions(self, action_name: str, state: FlowState, spec: ActionSpec) -> None:
        if not self.spec.safety.forbid_conflicting_actions:
            return
        for previous in state.path_actions:
            if previous in spec.conflicts_with:
                self.errors.append("Conflicting actions emitted on one path: %s and %s." % (previous, action_name))

    def _check_parameter_guardrail(self, action_name: str, state: FlowState, spec: ActionSpec) -> None:
        if not self.spec.safety.require_parameter_guardrails:
            return
        guards = {
            "set_tau": "tau",
            "scale_tau": "tau",
            "set_sigma": "sigma",
            "scale_sigma": "sigma",
            "set_rho": "rho",
            "scale_rho": "rho",
            "set_momentum": "momentum",
        }
        feature = guards.get(action_name)
        if feature and feature not in self.used_features:
            self.warnings.append("Action %s is emitted without reading state feature %s." % (action_name, feature))

    def _extract_dict(self, node: ast.Dict) -> Dict[str, ast.AST]:
        payload: Dict[str, ast.AST] = {}
        for key_node, value_node in zip(node.keys, node.values):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                self.errors.append("Dict keys in policy DSL must be string literals.")
                continue
            payload[str(key_node.value)] = value_node
        return payload

    def _extract_action_value(self, node: ast.AST) -> object:
        if not isinstance(node, ast.Dict):
            return None
        payload = self._extract_dict(node)
        value_node = payload.get("value")
        if isinstance(value_node, ast.Constant):
            return value_node.value
        return None

    def _const_eval_binop(self, op: ast.operator, left: object, right: object) -> Optional[float]:
        if left is None or right is None:
            return None
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return None
        if isinstance(op, ast.Add):
            return float(left + right)
        if isinstance(op, ast.Sub):
            return float(left - right)
        if isinstance(op, ast.Mult):
            return float(left * right)
        if isinstance(op, ast.Div):
            if right == 0:
                self.errors.append("Division by zero detected in policy expression.")
                return None
            return float(left / right)
        if isinstance(op, ast.Pow):
            return float(left ** right)
        return None

    def _static_max_actions(self) -> int:
        return len(self.emitted_actions)

    def _is_docstring_expr(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )

    def _render_expr(self, node: ast.AST) -> str:
        try:
            return ast.unparse(node)
        except Exception:
            return node.__class__.__name__

    def _check_mathematical_safety(self, state: FlowState) -> None:
        if self.spec.algorithm == "PDHG":
            self._check_pdhg_guardrails(state)
        elif self.spec.algorithm == "FISTA":
            self._check_fista_guardrails(state)

    def _check_pdhg_guardrails(self, state: FlowState) -> None:
        tau_values = [value for name, value in state.path_action_payloads if name == "set_tau" and isinstance(value, (int, float))]
        sigma_values = [value for name, value in state.path_action_payloads if name == "set_sigma" and isinstance(value, (int, float))]
        if tau_values and sigma_values:
            tau = float(tau_values[-1])
            sigma = float(sigma_values[-1])
            if tau * sigma > 1.0:
                self.errors.append("PDHG mathematical guard failed: set_tau * set_sigma must stay <= 1.0 in verifier proxy.")

        scale_tau = [float(value) for name, value in state.path_action_payloads if name == "scale_tau" and isinstance(value, (int, float))]
        scale_sigma = [float(value) for name, value in state.path_action_payloads if name == "scale_sigma" and isinstance(value, (int, float))]
        if scale_tau and scale_sigma:
            proxy = scale_tau[-1] * scale_sigma[-1]
            if proxy > 1.35:
                self.warnings.append("PDHG proxy guard: scale_tau * scale_sigma is aggressive (%.3f)." % proxy)

    def _check_fista_guardrails(self, state: FlowState) -> None:
        momentum_values = [float(value) for name, value in state.path_action_payloads if name == "set_momentum" and isinstance(value, (int, float))]
        if momentum_values and momentum_values[-1] > 0.97 and "restart" not in state.path_actions:
            self.warnings.append("FISTA proxy guard: high momentum without restart may be unstable.")


def verify_policy_source(source: str, spec: PolicySpec) -> VerificationResult:
    return PolicyVerifier(spec).verify(source)
