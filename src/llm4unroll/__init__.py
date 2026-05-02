"""Minimal Phase 1 implementation of LLM4Unroll."""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["__version__"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_VENDOR_DIR = _REPO_ROOT / ".vendor"
if _VENDOR_DIR.is_dir():
    vendor_path = str(_VENDOR_DIR)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)

__version__ = "0.1.0"
