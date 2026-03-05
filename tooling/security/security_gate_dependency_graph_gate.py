#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
POLICY = ROOT / "governance" / "security" / "security_gate_dependency_policy.json"


def _normalize_gate_entry(value: str) -> str:
    text = str(value).strip().strip('"')
    if ".py" in text:
        return text[: text.find(".py") + 3]
    return text.split()[0] if text else ""


def _load_manifest(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("super gate manifest must be a JSON object")
    items: list[str] = []
    for key in ("core", "extended"):
        raw = payload.get(key, [])
        if not isinstance(raw, list):
            raise ValueError(f"manifest field '{key}' must be a list")
        for entry in raw:
            normalized = _normalize_gate_entry(str(entry))
            if normalized:
                items.append(normalized)
    return sorted(set(items))


def _load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("dependency policy must be a JSON object")
    return payload


def _cycle_findings(nodes: list[str], deps: dict[str, list[str]]) -> list[str]:
    findings: list[str] = []
    color: dict[str, int] = {node: 0 for node in nodes}
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = 1
        stack.append(node)
        for dep in deps.get(node, []):
            if dep not in color:
                continue
            if color[dep] == 0:
                visit(dep)
            elif color[dep] == 1:
                if dep in stack:
                    idx = stack.index(dep)
                    cycle = stack[idx:] + [dep]
                    findings.append(f"cyclic_dependency:{'->'.join(cycle)}")
        stack.pop()
        color[node] = 2

    for node in nodes:
        if color[node] == 0:
            visit(node)
    return sorted(set(findings))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    gates = _load_manifest(MANIFEST)
    policy = _load_policy(POLICY)

    raw_deps = policy.get("dependencies", {})
    if not isinstance(raw_deps, dict):
        raise ValueError("policy 'dependencies' must be an object")
    dependency_map: dict[str, list[str]] = {gate: [] for gate in gates}
    for gate, raw_list in raw_deps.items():
        normalized_gate = _normalize_gate_entry(str(gate))
        if normalized_gate not in dependency_map:
            findings.append(f"unknown_gate_in_dependency_policy:{normalized_gate}")
            continue
        if not isinstance(raw_list, list):
            findings.append(f"invalid_dependency_list:{normalized_gate}")
            continue
        normalized_deps = [_normalize_gate_entry(str(item)) for item in raw_list]
        deduped = sorted({dep for dep in normalized_deps if dep})
        dependency_map[normalized_gate] = deduped

    for gate, deps in dependency_map.items():
        for dep in deps:
            if dep not in dependency_map:
                findings.append(f"unknown_dependency:{gate}:{dep}")
        if gate in deps:
            findings.append(f"self_dependency:{gate}")

    critical_controls = policy.get("critical_controls", [])
    if not isinstance(critical_controls, list):
        raise ValueError("policy 'critical_controls' must be a list")

    single_points: list[dict[str, Any]] = []
    for item in critical_controls:
        if not isinstance(item, dict):
            findings.append("invalid_critical_control_entry")
            continue
        control_id = str(item.get("control_id", "")).strip()
        raw_verifiers = item.get("verifiers", [])
        required = int(item.get("required_redundant_verifiers", 2))
        if not control_id:
            findings.append("critical_control_missing_id")
            continue
        if not isinstance(raw_verifiers, list):
            findings.append(f"critical_control_invalid_verifiers:{control_id}")
            continue
        verifiers = sorted({_normalize_gate_entry(str(v)) for v in raw_verifiers if _normalize_gate_entry(str(v))})
        unknown = sorted(verifier for verifier in verifiers if verifier not in dependency_map)
        if unknown:
            findings.append(f"critical_control_unknown_verifier:{control_id}:{','.join(unknown)}")
        valid_verifiers = [verifier for verifier in verifiers if verifier in dependency_map]
        if len(valid_verifiers) < max(required, 1):
            single_points.append(
                {
                    "control_id": control_id,
                    "required_redundant_verifiers": max(required, 1),
                    "available_verifiers": valid_verifiers,
                }
            )
            findings.append(f"single_point_of_failure:{control_id}")

    findings.extend(_cycle_findings(gates, dependency_map))

    reverse_edges: dict[str, list[str]] = {gate: [] for gate in gates}
    edge_count = 0
    for gate, deps in dependency_map.items():
        for dep in deps:
            if dep in reverse_edges:
                reverse_edges[dep].append(gate)
                edge_count += 1
    for gate in reverse_edges:
        reverse_edges[gate] = sorted(set(reverse_edges[gate]))

    graph = {
        "nodes": gates,
        "dependencies": dependency_map,
        "dependents": reverse_edges,
        "single_points_of_failure": single_points,
    }
    graph_path = evidence_root() / "security" / "security_gate_dependency_graph.json"
    write_json_report(graph_path, graph)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": sorted(set(findings)),
        "summary": {
            "gate_count": len(gates),
            "edge_count": edge_count,
            "single_points_of_failure": len(single_points),
        },
        "metadata": {"gate": "security_gate_dependency_graph_gate"},
    }
    out = evidence_root() / "security" / "security_gate_dependency_graph_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_GATE_DEPENDENCY_GRAPH_GATE: {report['status']}")
    print(f"Graph: {graph_path}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
