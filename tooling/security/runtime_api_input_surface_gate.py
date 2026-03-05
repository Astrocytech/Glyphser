#!/usr/bin/env python3
from __future__ import annotations

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


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid json object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _load_json(ROOT / "governance" / "security" / "runtime_api_input_surface_policy.json")
    schemas = _load_json(ROOT / "runtime" / "glyphser" / "api" / "schemas" / "runtime_api_schemas.json")

    requested = policy.get("request_schemas", [])
    if not isinstance(requested, list) or not all(isinstance(x, str) for x in requested):
        raise ValueError("invalid request_schemas in runtime api input surface policy")
    fragments = [str(x).lower() for x in policy.get("forbidden_property_fragments", []) if isinstance(x, str) and x]
    if not fragments:
        raise ValueError("forbidden_property_fragments must not be empty")
    allowlisted = {str(x) for x in policy.get("allowlisted_properties", []) if isinstance(x, str)}

    checked: dict[str, list[str]] = {}
    for schema_name in requested:
        schema = schemas.get(schema_name)
        if not isinstance(schema, dict):
            findings.append(f"missing_schema:{schema_name}")
            continue
        props = schema.get("properties", {})
        if not isinstance(props, dict):
            findings.append(f"invalid_properties:{schema_name}")
            continue
        prop_names = sorted(str(k) for k in props.keys())
        checked[schema_name] = prop_names
        for prop in prop_names:
            if prop in allowlisted:
                continue
            lower = prop.lower()
            hit = next((frag for frag in fragments if frag in lower), "")
            if hit:
                findings.append(f"forbidden_property_fragment:{schema_name}:{prop}:{hit}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_schemas": sorted(checked.keys()),
            "forbidden_fragments": fragments,
            "allowlisted_properties": sorted(allowlisted),
        },
        "metadata": {"gate": "runtime_api_input_surface_gate"},
    }
    out = evidence_root() / "security" / "runtime_api_input_surface_gate.json"
    write_json_report(out, report)
    print(f"RUNTIME_API_INPUT_SURFACE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
