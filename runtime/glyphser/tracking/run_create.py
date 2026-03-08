"""Deterministic run create (minimal)."""

from __future__ import annotations

from typing import Any, Dict


def run_create(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    run_id = request.get("run_id") or "run-1"
    return {"status": "OK", "run_id": run_id}
