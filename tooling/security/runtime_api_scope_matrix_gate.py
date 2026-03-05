#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


class _ScopeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.by_endpoint: dict[str, str] = {}
        self.scope_validator_calls = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        if node.name != "RuntimeApiService":
            return
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            endpoint = item.name
            expected_scope = ""
            for inner in ast.walk(item):
                if not isinstance(inner, ast.Call):
                    continue
                callee = inner.func
                if isinstance(callee, ast.Name) and callee.id == "_validate_scope":
                    self.scope_validator_calls += 1
                    for kw in inner.keywords:
                        if kw.arg == "expected" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            expected_scope = kw.value.value
            if expected_scope:
                self.by_endpoint[endpoint] = expected_scope


def _load_policy() -> dict[str, Any]:
    path = ROOT / "governance" / "security" / "runtime_api_scope_matrix_policy.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid runtime api scope matrix policy")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _load_policy()
    required = policy.get("required_scope_by_endpoint", {})
    if not isinstance(required, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in required.items()):
        raise ValueError("invalid required_scope_by_endpoint in policy")
    forbid_additional = bool(policy.get("forbid_additional_scope_validators", False))

    runtime_api = ROOT / "runtime" / "glyphser" / "api" / "runtime_api.py"
    tree = ast.parse(runtime_api.read_text(encoding="utf-8"), filename=str(runtime_api))
    visitor = _ScopeVisitor()
    visitor.visit(tree)

    for endpoint, expected_scope in sorted(required.items()):
        actual_scope = visitor.by_endpoint.get(endpoint, "")
        if not actual_scope:
            findings.append(f"missing_scope_validator:{endpoint}")
            continue
        if actual_scope != expected_scope:
            findings.append(f"scope_mismatch:{endpoint}:expected={expected_scope}:actual={actual_scope}")

    undocumented = sorted(endpoint for endpoint in visitor.by_endpoint if endpoint not in required)
    if undocumented:
        findings.append("undocumented_scope_validators:" + ",".join(undocumented))

    if forbid_additional:
        required_count = len(required)
        if visitor.scope_validator_calls != required_count:
            findings.append(
                f"unexpected_scope_validator_call_count:expected={required_count}:actual={visitor.scope_validator_calls}"
            )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_endpoints": sorted(required.keys()),
            "observed_endpoints": sorted(visitor.by_endpoint.keys()),
            "scope_validator_calls": visitor.scope_validator_calls,
            "forbid_additional_scope_validators": forbid_additional,
        },
        "metadata": {"gate": "runtime_api_scope_matrix_gate"},
    }
    out = evidence_root() / "security" / "runtime_api_scope_matrix_gate.json"
    write_json_report(out, report)
    print(f"RUNTIME_API_SCOPE_MATRIX_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
