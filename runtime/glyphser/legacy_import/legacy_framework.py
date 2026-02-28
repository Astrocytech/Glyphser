"""Deterministic legacy framework import (minimal)."""
from __future__ import annotations

from typing import Any, Dict


def legacy_framework_import(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    return {"status": "OK"}
