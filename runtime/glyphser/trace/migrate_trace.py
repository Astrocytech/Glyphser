"""Deterministic trace migration (minimal)."""

from __future__ import annotations

from typing import Any, Dict


def migrate_trace(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    trace = request.get("trace", {})
    return {"status": "OK", "trace": trace}
