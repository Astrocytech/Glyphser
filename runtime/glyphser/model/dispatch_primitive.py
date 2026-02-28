"""Deterministic primitive dispatch."""
from __future__ import annotations

from typing import Any, Dict, Tuple

class PrimitiveUnsupportedError(RuntimeError):
    pass


class ShapeMismatchError(RuntimeError):
    pass


def _infer_shape(value: Any) -> list[int]:
    if isinstance(value, list):
        if not value:
            return [0]
        if isinstance(value[0], list):
            return [len(value), len(value[0])]
        return [len(value)]
    return []


def dispatch_primitive(
    node: Dict[str, Any],
    inputs: list[Any],
    theta: Dict[str, Any],
    mode: str,
    driver: Any,
    rng_state: int,
) -> Tuple[Any, int]:
    instr = node["instr"]
    params = node.get("params", {})
    output, rng_state_next = driver.dispatch(instr, inputs, params, theta, mode, rng_state)
    expected_shape = node.get("shape_out") or []
    actual_shape = _infer_shape(output)
    if expected_shape != actual_shape:
        raise ShapeMismatchError(f"shape mismatch for {node['node_id']}")
    return output, rng_state_next
