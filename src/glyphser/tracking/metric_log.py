"""Deterministic metric log (minimal)."""
from __future__ import annotations

from typing import Any, Dict


def metric_log(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    return {"status": "OK"}
