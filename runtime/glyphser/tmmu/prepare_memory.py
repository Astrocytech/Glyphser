"""Deterministic TMMU prepare memory implementation."""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

from runtime.glyphser.serialization.canonical_cbor import encode_canonical
from runtime.glyphser.model.ir_schema import IRValidationError, validate_ir_dag, tensor_size_bytes, dtype_size_bytes
from runtime.glyphser.model.topo_sort_nodes import topo_sort_nodes
from runtime.glyphser.error.emit import emit_error


class TMMUError(RuntimeError):
    pass


def _align_up(value: int, alignment: int) -> int:
    if alignment <= 0:
        raise TMMUError("alignment must be positive")
    if value % alignment == 0:
        return value
    return value + (alignment - (value % alignment))


def _default_arena_config() -> Dict[str, Dict[str, int]]:
    return {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}


def _execution_order_nodes(ir_dag: Dict[str, Any], execution_order: Any) -> List[Dict[str, Any]]:
    if execution_order is None:
        return topo_sort_nodes(ir_dag["nodes"])
    if isinstance(execution_order, list):
        if execution_order and isinstance(execution_order[0], dict):
            return execution_order
        node_map = {n["node_id"]: n for n in ir_dag["nodes"]}
        nodes = []
        for nid in execution_order:
            if nid not in node_map:
                raise TMMUError("execution_order references unknown node")
            nodes.append(node_map[nid])
        return nodes
    raise TMMUError("execution_order must be list")


def _analyze_liveness(
    ir_dag: Dict[str, Any],
    execution_order: List[Dict[str, Any]],
    mode: str,
) -> List[Dict[str, Any]]:
    order_index = {node["node_id"]: idx for idx, node in enumerate(execution_order)}
    consumers: Dict[str, int] = {}
    for node in execution_order:
        for ref in node.get("inputs", []):
            if "node_id" in ref:
                src = ref["node_id"]
                consumers[src] = max(consumers.get(src, -1), order_index[node["node_id"]])

    live_ranges: List[Dict[str, Any]] = []
    for node in execution_order:
        nid = node["node_id"]
        birth = order_index[nid]
        death = consumers.get(nid, birth)
        if mode == "backward" and node.get("saved_for_backward"):
            death = max(death, len(execution_order) - 1)
        if death < birth:
            raise TMMUError("invalid liveness interval")
        tensor_id = f"{nid}:0"
        live_ranges.append(
            {
                "tensor_id": tensor_id,
                "node_id": nid,
                "birth": birth,
                "death": death,
                "shape": node["shape_out"],
                "dtype": node["dtype"],
                "role": node.get("role", "activation"),
                "arena": node.get("arena"),
            }
        )
    return live_ranges


def _choose_arena(live: Dict[str, Any], arena_config: Dict[str, Dict[str, int]]) -> str:
    if live.get("arena"):
        return live["arena"]
    role = live.get("role", "activation")
    if role in {"param", "parameter", "weights"} and "parameters" in arena_config:
        return "parameters"
    if role in {"grad", "gradient"} and "grads" in arena_config:
        return "grads"
    if "default" in arena_config:
        return "default"
    return sorted(arena_config.keys())[0]


def _assign_logical_slots(
    live_ranges: List[Dict[str, Any]],
    arena_config: Dict[str, Dict[str, int]],
) -> Tuple[Dict[str, Tuple[str, int]], Dict[Tuple[str, int], int], Dict[Tuple[str, int], int]]:
    per_arena: Dict[str, List[Dict[str, Any]]] = {name: [] for name in arena_config}
    for live in live_ranges:
        arena = _choose_arena(live, arena_config)
        live = {**live, "arena": arena}
        per_arena[arena].append(live)

    assignment: Dict[str, Tuple[str, int]] = {}
    slot_sizes: Dict[Tuple[str, int], int] = {}
    slot_alignments: Dict[Tuple[str, int], int] = {}

    for arena, lives in per_arena.items():
        lives.sort(key=lambda x: (x["birth"], -tensor_size_bytes(x["shape"], x["dtype"]), x["tensor_id"]))
        active: List[Tuple[int, int]] = []  # (death, slot_id)
        free_slots: List[int] = []
        next_slot_id = 0
        for live in lives:
            birth = live["birth"]
            still_active: List[Tuple[int, int]] = []
            for death, slot_id in active:
                if death < birth:
                    free_slots.append(slot_id)
                else:
                    still_active.append((death, slot_id))
            active = still_active
            free_slots.sort()
            if free_slots:
                slot_id = free_slots.pop(0)
            else:
                slot_id = next_slot_id
                next_slot_id += 1
            active.append((live["death"], slot_id))
            tensor_id = live["tensor_id"]
            assignment[tensor_id] = (arena, slot_id)
            size_bytes = tensor_size_bytes(live["shape"], live["dtype"])
            alignment_bytes = dtype_size_bytes(live["dtype"])
            slot_sizes[(arena, slot_id)] = max(slot_sizes.get((arena, slot_id), 0), size_bytes)
            slot_alignments[(arena, slot_id)] = max(slot_alignments.get((arena, slot_id), 0), alignment_bytes)

    return assignment, slot_sizes, slot_alignments


def _map_to_virtual_addresses(
    assignment: Dict[str, Tuple[str, int]],
    arena_config: Dict[str, Dict[str, int]],
    slot_sizes: Dict[Tuple[str, int], int],
    slot_alignments: Dict[Tuple[str, int], int],
) -> Dict[Tuple[str, int], int]:
    offsets: Dict[Tuple[str, int], int] = {}
    for arena, config in arena_config.items():
        slots = sorted({slot for (a, slot) in slot_sizes if a == arena})
        offset = 0
        for slot_id in slots:
            align = max(slot_alignments.get((arena, slot_id), 1), config.get("alignment_bytes", 1))
            offset = _align_up(offset, align)
            if offset < 0 or offset > (2**64 - 1):
                raise TMMUError("allocation overflow")
            offsets[(arena, slot_id)] = offset
            offset += slot_sizes[(arena, slot_id)]
        capacity = config.get("capacity_bytes", 0)
        if capacity and offset > capacity:
            raise TMMUError("arena too small")
    return offsets


def _plan_hash(
    ir_hash: str,
    mode: str,
    arena_config: Dict[str, Any],
    execution_order: List[Dict[str, Any]],
    assignment: Dict[str, Tuple[str, int]],
    offsets: Dict[Tuple[str, int], int],
) -> str:
    execution_order_ids = [node["node_id"] for node in execution_order]
    execution_order_hash = hashlib.sha256(encode_canonical(execution_order_ids)).hexdigest()
    arena_config_hash = hashlib.sha256(encode_canonical(arena_config)).hexdigest()
    shard_spec_hash = hashlib.sha256(encode_canonical({})).hexdigest()
    slot_assignment_table = [
        [tensor_id, arena, slot] for tensor_id, (arena, slot) in sorted(assignment.items())
    ]
    logical_address_table = [
        [arena, slot, offsets[(arena, slot)]]
        for (arena, slot) in sorted(offsets.keys())
    ]
    payload = [
        "tmmu_plan",
        [
            ir_hash,
            mode,
            arena_config_hash,
            execution_order_hash,
            0,
            1,
            shard_spec_hash,
            slot_assignment_table,
            logical_address_table,
        ],
    ]
    return hashlib.sha256(encode_canonical(payload)).hexdigest()


def prepare_memory(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return {"error": emit_error("CONTRACT_VIOLATION", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory")}
    ir_dag = request.get("ir_dag") or request.get("uml_model_ir_dag")
    if ir_dag is None:
        return {"error": emit_error("INVALID_IR_SHAPES", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", ir_hash="", node_id="")}
    try:
        ir = validate_ir_dag(ir_dag)
    except IRValidationError:
        return {"error": emit_error("INVALID_IR_SHAPES", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", ir_hash="", node_id="")}
    try:
        execution_order = _execution_order_nodes(ir, request.get("execution_order"))
    except Exception:
        return {"error": emit_error("LIVENESS_CYCLE", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", ir_hash=ir.get("ir_hash", ""), node_id="")}
    mode = request.get("mode", "forward")
    arena_config = request.get("arena_config") or request.get("tmmu_context", {}).get("arena_config")
    if arena_config is None:
        arena_config = _default_arena_config()
    try:
        live_ranges = _analyze_liveness(ir, execution_order, mode)
        assignment, slot_sizes, slot_alignments = _assign_logical_slots(live_ranges, arena_config)
        offsets = _map_to_virtual_addresses(assignment, arena_config, slot_sizes, slot_alignments)
        tmmu_plan_hash = _plan_hash(ir["ir_hash"], mode, arena_config, execution_order, assignment, offsets)
    except TMMUError as exc:
        msg = str(exc)
        if "arena too small" in msg:
            return {"error": emit_error("ARENA_TOO_SMALL", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", arena="", capacity="", required="")}
        if "allocation overflow" in msg:
            return {"error": emit_error("ALLOCATION_OVERFLOW", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", arena="", offset="", size="")}
        if "alignment" in msg:
            return {"error": emit_error("ALIGNMENT_VIOLATION", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", arena="", logical_slot="")}
        return {"error": emit_error("ADDRESS_COLLISION", "invalid request", operator_id="Glyphser.TMMU.PrepareMemory", t="", arena="", logical_slot="")}

    tensor_map: Dict[str, Dict[str, Any]] = {}
    for live in live_ranges:
        tensor_id = live["tensor_id"]
        arena, slot_id = assignment[tensor_id]
        offset = offsets[(arena, slot_id)]
        size_bytes = tensor_size_bytes(live["shape"], live["dtype"])
        tensor_map[tensor_id] = {
            "arena": arena,
            "logical_slot": slot_id,
            "offset_bytes": offset,
            "size_bytes": size_bytes,
            "shape": live["shape"],
            "dtype": live["dtype"],
            "role": live.get("role", "activation"),
            "value": [0 for _ in range(size_bytes // dtype_size_bytes(live["dtype"]))],
        }

    slot_count = len({slot for (_, slot) in assignment.values()})
    tensor_count = len(live_ranges)
    memory_reuse_ratio = 0.0
    if tensor_count:
        memory_reuse_ratio = max(0.0, 1.0 - (slot_count / tensor_count))
    total_slot_bytes = sum(slot_sizes.values()) if slot_sizes else 0
    total_tensor_bytes = sum(tensor_size_bytes(l["shape"], l["dtype"]) for l in live_ranges)
    internal_fragmentation_ratio = 0.0
    if total_slot_bytes:
        internal_fragmentation_ratio = max(0.0, 1.0 - (total_tensor_bytes / total_slot_bytes))

    metrics = {
        "peak_tmmu_usage": total_slot_bytes,
        "memory_reuse_ratio": memory_reuse_ratio,
        "internal_fragmentation_ratio": internal_fragmentation_ratio,
        "tmmu_plan_hash": tmmu_plan_hash,
    }

    tmmu_state_next = {
        "tmmu_plan_hash": tmmu_plan_hash,
        "arena_config": arena_config,
    }

    return {
        "tensor_map": tensor_map,
        "metrics": metrics,
        "tmmu_plan_hash": tmmu_plan_hash,
        "tmmu_state_next": tmmu_state_next,
    }
