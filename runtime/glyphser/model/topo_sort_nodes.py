"""Deterministic topological sort for ModelIR nodes."""

from __future__ import annotations

from typing import Any, Dict, List


def _node_id(node: Dict[str, Any]) -> str:
    node_id = node.get("node_id") or node.get("id")
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("node_id must be non-empty string")
    return node_id


def _input_refs(node: Dict[str, Any]) -> List[str]:
    inputs = node.get("inputs") or []
    refs: List[str] = []
    if not isinstance(inputs, list):
        raise ValueError("inputs must be list")
    for entry in inputs:
        if isinstance(entry, str):
            refs.append(entry)
        elif isinstance(entry, dict) and "node_id" in entry:
            refs.append(entry["node_id"])
    return refs


def topo_sort_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Stable Kahn's algorithm using input order as tie-breaker.
    id_to_node = {_node_id(n): n for n in nodes}
    incoming = {_node_id(n): 0 for n in nodes}
    edges: Dict[str, List[str]] = {_node_id(n): [] for n in nodes}
    order_index = {_node_id(n): i for i, n in enumerate(nodes)}

    for n in nodes:
        nid = _node_id(n)
        for src in _input_refs(n):
            if src not in incoming:
                raise ValueError(f"unknown input node: {src}")
            edges[src].append(nid)
            incoming[nid] += 1

    ready = [nid for nid, deg in incoming.items() if deg == 0]
    ready.sort(key=lambda nid: order_index[nid])

    out: List[Dict[str, Any]] = []
    while ready:
        nid = ready.pop(0)
        out.append(id_to_node[nid])
        for dest in edges[nid]:
            incoming[dest] -= 1
            if incoming[dest] == 0:
                ready.append(dest)
                ready.sort(key=lambda nid2: order_index[nid2])

    if len(out) != len(nodes):
        raise ValueError("cycle detected in ModelIR graph")
    return out
