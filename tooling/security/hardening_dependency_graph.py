#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not REGISTRY.exists():
        findings.append("missing_hardening_pending_item_registry")
        entries: list[dict[str, Any]] = []
    else:
        registry = _load_json(REGISTRY)
        raw = registry.get("entries", [])
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    ids = {str(row.get("id", "")).strip() for row in entries if str(row.get("id", "")).strip()}
    graph: dict[str, set[str]] = {}
    indegree: dict[str, int] = defaultdict(int)
    for row in entries:
        item_id = str(row.get("id", "")).strip()
        if not item_id:
            continue
        deps_raw = row.get("dependencies", [])
        deps = [str(dep).strip() for dep in deps_raw if str(dep).strip()] if isinstance(deps_raw, list) else []
        graph[item_id] = set()
        for dep in deps:
            if dep not in ids:
                findings.append(f"unknown_dependency:{item_id}:{dep}")
                continue
            graph[item_id].add(dep)
            indegree[item_id] += 1
        indegree.setdefault(item_id, indegree.get(item_id, 0))

    reverse: dict[str, set[str]] = defaultdict(set)
    for node, deps in graph.items():
        for dep in deps:
            reverse[dep].add(node)

    queue = deque(sorted([node for node, deg in indegree.items() if deg == 0]))
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in sorted(reverse.get(node, set())):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(graph):
        cycle_nodes = sorted(set(graph) - set(order))
        findings.append(f"dependency_cycle_detected:{'|'.join(cycle_nodes[:20])}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "nodes": len(graph),
            "edges": sum(len(deps) for deps in graph.values()),
            "ordered_nodes": len(order),
        },
        "metadata": {"report": "hardening_dependency_graph"},
        "order": order,
        "graph": {node: sorted(deps) for node, deps in sorted(graph.items())},
    }
    out = evidence_root() / "security" / "hardening_dependency_graph.json"
    write_json_report(out, report)
    print(f"HARDENING_DEPENDENCY_GRAPH: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
