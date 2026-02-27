"""Deterministic backend driver load (minimal)."""
from __future__ import annotations

from typing import Any, Dict


def load_driver(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    driver_id = request.get("driver_id") or "default"
    return {"status": "OK", "driver_id": driver_id}
