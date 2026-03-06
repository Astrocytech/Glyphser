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

SECURITY_TOOLING = ROOT / "tooling" / "security"
POLICY = ROOT / "governance" / "security" / "security_gate_determinism_metadata_policy.json"


def _gate_relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _candidate_gate_paths() -> list[Path]:
    if not SECURITY_TOOLING.exists():
        return []
    return sorted(
        path
        for path in SECURITY_TOOLING.glob("*_gate.py")
        if path.name != "security_gate_deterministic_io_metadata_gate.py"
    )


def _load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("determinism metadata policy must be an object")
    return payload


def _normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        token = item.strip()
        if not token or token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_determinism_metadata_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_policy(POLICY)
        except Exception:
            findings.append("invalid_determinism_metadata_policy")
            policy = {}

    default_inputs = _normalize_string_list(policy.get("default_deterministic_inputs"))
    default_outputs = _normalize_string_list(policy.get("default_deterministic_outputs"))
    overrides_raw = policy.get("gate_metadata_overrides", {})
    overrides = overrides_raw if isinstance(overrides_raw, dict) else {}
    if not isinstance(overrides_raw, dict):
        findings.append("invalid_gate_metadata_overrides")

    checked = 0
    declared = 0
    missing = 0

    for gate_path in _candidate_gate_paths():
        checked += 1
        rel = _gate_relpath(gate_path)
        gate_meta = overrides.get(rel, {})
        if gate_meta and not isinstance(gate_meta, dict):
            findings.append(f"invalid_gate_override:{rel}")
            gate_meta = {}
        inputs = _normalize_string_list(gate_meta.get("deterministic_inputs")) or default_inputs
        outputs = _normalize_string_list(gate_meta.get("deterministic_outputs")) or default_outputs
        if not inputs or not outputs:
            missing += 1
            findings.append(f"missing_deterministic_io_metadata:{rel}")
            continue
        declared += 1

    for gate_rel in sorted(overrides):
        if not (ROOT / gate_rel).exists():
            findings.append(f"unknown_gate_override:{gate_rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "gates_checked": checked,
            "gates_with_declarations": declared,
            "gates_missing_declarations": missing,
        },
        "metadata": {"gate": "security_gate_deterministic_io_metadata_gate"},
    }
    out = evidence_root() / "security" / "security_gate_deterministic_io_metadata_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_GATE_DETERMINISTIC_IO_METADATA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
