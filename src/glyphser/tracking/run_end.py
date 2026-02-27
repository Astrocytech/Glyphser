"""Deterministic run end (minimal)."""
from __future__ import annotations

from typing import Any, Dict


def run_end(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    return {"status": "OK", "run_id": request.get("run_id")}
