"""Deterministic forward (minimal)."""
from __future__ import annotations

from typing import Any, Dict, List


def forward(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    inputs = request.get("inputs", [])
    if not isinstance(inputs, list):
        raise ValueError("inputs must be list")
    return {"outputs": inputs}
