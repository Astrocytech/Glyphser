"""Collect gradients from tensor map."""
from __future__ import annotations

from typing import Any, Dict


def collect_gradients(tensor_map: Dict[str, Dict[str, Any]], ir_dag: Dict[str, Any]) -> Dict[str, Any]:
    grads: Dict[str, Any] = {}
    grad_outputs = ir_dag.get("grad_outputs") or []
    if not grad_outputs:
        return grads
    for entry in grad_outputs:
        if isinstance(entry, str):
            tensor_id = entry
        elif isinstance(entry, dict) and "tensor_id" in entry:
            tensor_id = entry["tensor_id"]
        elif isinstance(entry, dict) and "node_id" in entry:
            tensor_id = f"{entry['node_id']}:{entry.get('output_idx', 0)}"
        else:
            continue
        if tensor_id in tensor_map:
            grads[tensor_id] = tensor_map[tensor_id].get("value")
    return grads
