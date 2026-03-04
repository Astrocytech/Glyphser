"""Deterministic registry version create (minimal)."""

from __future__ import annotations

from typing import Any, Dict


def version_create(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    version = request.get("version")
    return {"status": "OK", "version": version}
