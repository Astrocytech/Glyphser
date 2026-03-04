"""Build deterministic gradient dependency order."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from runtime.glyphser.model.topo_sort_nodes import _node_id


def build_grad_dependency_order(
    ir_dag: Dict[str, Any],
    forward_execution_order: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    nodes = ir_dag.get("nodes", [])
    node_map = {_node_id(n): n for n in nodes}
    grad_edges = ir_dag.get("grad_edges") or []

    if not grad_edges:
        reverse_order = list(reversed(forward_execution_order))
        return reverse_order, 1

    edges: Dict[str, List[str]] = {nid: [] for nid in node_map}
    incoming: Dict[str, int] = {nid: 0 for nid in node_map}
    for edge in grad_edges:
        if not isinstance(edge, dict):
            raise ValueError("grad_edges must be list of dict")
        src = edge.get("src")
        dst = edge.get("dst")
        if src not in node_map or dst not in node_map:
            raise ValueError("grad_edges reference unknown node")
        edges[src].append(dst)
        incoming[dst] += 1

    order_index = {nid: idx for idx, nid in enumerate([_node_id(n) for n in forward_execution_order])}
    ready = [nid for nid, deg in incoming.items() if deg == 0]
    ready.sort(key=lambda nid: order_index.get(nid, 0))

    out: List[Dict[str, Any]] = []
    while ready:
        nid = ready.pop(0)
        out.append(node_map[nid])
        for dest in edges[nid]:
            incoming[dest] -= 1
            if incoming[dest] == 0:
                ready.append(dest)
                ready.sort(key=lambda nid2: order_index.get(nid2, 0))

    if len(out) != len(node_map):
        raise ValueError("cycle detected in grad dependency graph")

    reverse_order = list(reversed(forward_execution_order))
    reverse_ids = [_node_id(n) for n in reverse_order]
    out_ids = [_node_id(n) for n in out]
    reverse_equivalent_flag = 1 if reverse_ids == out_ids else 0

    return out, reverse_equivalent_flag
