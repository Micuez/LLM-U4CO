# Native Installation Blockers

| Component | Status | Blocking | Detail |
| --- | --- | --- | --- |
| PySCIPOpt package | available | False | importable |
| Ecole package | missing | True | ModuleNotFoundError: No module named 'ecole'; pip only left a same-name `ecole==0.0.1` dist-info stub, not the SCIP/Ecole module |
| SCIP command | missing | True | not found on PATH |
| HiGHS command | missing | False | not found on PATH |

## Remaining blockers

- Ecole is still not importable locally; the latest native install attempt fails in PEP517 metadata with missing `skbuild`, prior attempts also hit deeper CMake/xtl toolchain issues, and pip only left a non-importable same-name `ecole==0.0.1` stub.
- SCIP command-line binary is still absent, so command-backed native SCIP validation cannot run even though PySCIPOpt is importable.
