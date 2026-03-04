"""Deterministic artifact put (minimal)."""

from __future__ import annotations

from typing import Any, Dict


def artifact_put(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    return {"status": "OK"}
