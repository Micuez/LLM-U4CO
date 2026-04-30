from __future__ import annotations

from llm4unroll.solvers.ecole_interface import EcoleInterface
from llm4unroll.solvers.highs_interface import HighsInterface
from llm4unroll.solvers.ortools_interface import ORToolsInterface
from llm4unroll.solvers.osqp_interface import OSQPInterface
from llm4unroll.solvers.pyscipopt_interface import PyScipOptInterface


def build_solver_interfaces():
    return [
        HighsInterface(),
        OSQPInterface(),
        PyScipOptInterface(),
        ORToolsInterface(),
        EcoleInterface(),
    ]
