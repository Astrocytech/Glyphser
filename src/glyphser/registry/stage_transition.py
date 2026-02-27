"""Deterministic registry stage transition (minimal)."""
from __future__ import annotations

from typing import Any, Dict


def stage_transition(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    return {
        "status": "OK",
        "from": request.get("from"),
        "to": request.get("to"),
    }
