"""Minimal deterministic model IR executor (stub)."""
from __future__ import annotations

from typing import Any, Dict, List


def execute(ir: Dict[str, Any], inputs: List[float]) -> List[float]:
    # Deterministic placeholder: apply optional scalar and bias, then sum.
    scale = float(ir.get("scale", 1.0))
    bias = float(ir.get("bias", 0.0))
    output = [x * scale + bias for x in inputs]
    return output
