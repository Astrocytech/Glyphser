"""UML Model IR validation and hashing."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from runtime.glyphser.serialization.canonical_cbor import encode_canonical

_ALLOWED_DTYPES = {
    "float16": 2,
    "float32": 4,
    "float64": 8,
    "int32": 4,
    "int64": 8,
}
_MAX_NODE_COUNT = 4096
_MAX_INPUTS_PER_NODE = 256
_MAX_SHAPE_RANK = 16
_MAX_DIM_VALUE = 1_000_000
_MAX_TENSOR_BYTES = 2 * 1024 * 1024 * 1024


class IRValidationError(ValueError):
    pass


def _require_dict(obj: Any, label: str) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        raise IRValidationError(f"{label} must be dict")
    return obj


def _require_list(obj: Any, label: str) -> List[Any]:
    if not isinstance(obj, list):
        raise IRValidationError(f"{label} must be list")
    return obj


def _node_id(node: Dict[str, Any]) -> str:
    node_id = node.get("node_id") or node.get("id")
    if not isinstance(node_id, str) or not node_id:
        raise IRValidationError("node_id must be non-empty string")
    return node_id


def _normalize_inputs(inputs: Any) -> List[Dict[str, Any]]:
    if inputs is None:
        return []
    if isinstance(inputs, list):
        normalized: List[Dict[str, Any]] = []
        for entry in inputs:
            if isinstance(entry, str):
                normalized.append({"node_id": entry, "output_idx": 0})
            elif isinstance(entry, dict):
                if "node_id" in entry:
                    normalized.append(
                        {
                            "node_id": entry["node_id"],
                            "output_idx": entry.get("output_idx", 0),
                        }
                    )
                elif "input_key" in entry:
                    normalized.append({"input_key": entry["input_key"]})
                else:
                    raise IRValidationError("input reference missing node_id/input_key")
            else:
                raise IRValidationError("input reference must be string or dict")
        if len(normalized) > _MAX_INPUTS_PER_NODE:
            raise IRValidationError("too many input references")
        return normalized
    raise IRValidationError("inputs must be list")


def _normalize_shape(shape: Any) -> List[int]:
    if shape is None:
        raise IRValidationError("shape_out missing")
    if isinstance(shape, list):
        if len(shape) > _MAX_SHAPE_RANK:
            raise IRValidationError("shape rank too large")
        out: List[int] = []
        for dim in shape:
            if not isinstance(dim, int) or dim < 0 or dim > _MAX_DIM_VALUE:
                raise IRValidationError("shape_out must contain non-negative ints")
            out.append(dim)
        return out
    raise IRValidationError("shape_out must be list")


def _normalize_dtype(dtype: Any) -> str:
    if dtype is None:
        return "float32"
    if not isinstance(dtype, str):
        raise IRValidationError("dtype must be string")
    if dtype not in _ALLOWED_DTYPES:
        raise IRValidationError(f"unsupported dtype: {dtype}")
    return dtype


def dtype_size_bytes(dtype: str) -> int:
    return _ALLOWED_DTYPES[dtype]


def tensor_size_bytes(shape: List[int], dtype: str) -> int:
    size = 1
    for dim in shape:
        size *= dim
    return size * dtype_size_bytes(dtype)


def validate_ir_dag(ir_dag: Any) -> Dict[str, Any]:
    ir = _require_dict(ir_dag, "ir_dag")
    nodes_raw = ir.get("nodes") or ir.get("operators")
    nodes_list = _require_list(nodes_raw, "nodes")
    if len(nodes_list) > _MAX_NODE_COUNT:
        raise IRValidationError("too many nodes")

    ir_schema_hash = ir.get("ir_schema_hash")
    if not isinstance(ir_schema_hash, str) or not ir_schema_hash:
        raise IRValidationError("ir_schema_hash missing")

    normalized_nodes: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for node in nodes_list:
        node = _require_dict(node, "node")
        nid = _node_id(node)
        if nid in seen_ids:
            raise IRValidationError(f"duplicate node_id: {nid}")
        seen_ids.add(nid)
        instr = node.get("instr") or node.get("op")
        if not isinstance(instr, str) or not instr:
            raise IRValidationError(f"node {nid} instr missing")
        inputs = _normalize_inputs(node.get("inputs"))
        shape_out = _normalize_shape(node.get("shape_out") or node.get("shape"))
        dtype = _normalize_dtype(node.get("dtype"))
        if tensor_size_bytes(shape_out, dtype) > _MAX_TENSOR_BYTES:
            raise IRValidationError(f"tensor size exceeds limit for node: {nid}")
        normalized_nodes.append(
            {
                "node_id": nid,
                "instr": instr,
                "inputs": inputs,
                "params": node.get("params", {}),
                "shape_out": shape_out,
                "dtype": dtype,
                "saved_for_backward": bool(node.get("saved_for_backward", False)),
                "role": node.get("role", "activation"),
                "arena": node.get("arena"),
            }
        )

    outputs_raw = ir.get("outputs") or []
    outputs: List[Dict[str, Any]] = []
    for out in outputs_raw:
        if isinstance(out, str):
            outputs.append({"node_id": out, "output_idx": 0})
        elif isinstance(out, dict):
            if "node_id" not in out:
                raise IRValidationError("output missing node_id")
            outputs.append({"node_id": out["node_id"], "output_idx": out.get("output_idx", 0)})
        else:
            raise IRValidationError("output entry must be string or dict")

    node_ids = {n["node_id"] for n in normalized_nodes}
    for node in normalized_nodes:
        for ref in node["inputs"]:
            if "node_id" in ref and ref["node_id"] not in node_ids:
                raise IRValidationError(f"unknown input node: {ref['node_id']}")

    for out in outputs:
        if out["node_id"] not in node_ids:
            raise IRValidationError(f"unknown output node: {out['node_id']}")

    normalized = {
        "ir_schema_hash": ir_schema_hash,
        "nodes": normalized_nodes,
        "outputs": outputs,
        "grad_edges": ir.get("grad_edges", []),
        "meta": ir.get("meta", {}),
    }

    ir_hash = _compute_ir_hash(normalized)
    provided = ir.get("ir_hash")
    if provided is not None:
        if not isinstance(provided, str):
            raise IRValidationError("ir_hash must be string")
        if provided != ir_hash:
            raise IRValidationError("ir_hash mismatch")

    normalized["ir_hash"] = ir_hash
    return normalized


def _compute_ir_hash(ir_normalized: Dict[str, Any]) -> str:
    payload = {k: v for k, v in ir_normalized.items() if k != "ir_hash"}
    cbor = encode_canonical(payload)
    return hashlib.sha256(cbor).hexdigest()
