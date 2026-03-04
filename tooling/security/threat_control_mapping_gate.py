#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root

MATRIX = ROOT / "governance" / "security" / "threat_control_matrix.json"
THREAT_META = ROOT / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json"
SUPER_MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
CONTROL_ID_RE = re.compile(r"^CTRL-[A-Z0-9_-]+$")
MANIFEST_EXEMPT_GATES = {"tooling/security/security_super_gate.py"}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _manifest_gates() -> set[str]:
    payload = _read_json(SUPER_MANIFEST)
    if not isinstance(payload, dict):
        return set()
    gates = set()
    for bucket in ("core", "extended"):
        gates.update(_string_list(payload.get(bucket, [])))
    return gates


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not MATRIX.exists():
        findings.append("missing_matrix:governance/security/threat_control_matrix.json")
    if not THREAT_META.exists():
        findings.append("missing_threat_metadata:governance/security/metadata/THREAT_MODEL.meta.json")
    if not SUPER_MANIFEST.exists():
        findings.append("missing_super_manifest:tooling/security/security_super_gate_manifest.json")
    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"controls": 0, "critical_gates": 0},
            "metadata": {"gate": "threat_control_mapping_gate"},
        }
        out = evidence_root() / "security" / "threat_control_mapping_gate.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"THREAT_CONTROL_MAPPING_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    matrix = _read_json(MATRIX)
    meta = _read_json(THREAT_META)
    manifest_gates = _manifest_gates()

    controls = matrix.get("controls", []) if isinstance(matrix, dict) else []
    critical_gates = _string_list(matrix.get("critical_gates", []) if isinstance(matrix, dict) else [])
    threat_control_ids = _string_list(meta.get("control_ids", []) if isinstance(meta, dict) else [])
    if not isinstance(controls, list):
        controls = []
        findings.append("invalid_controls:must_be_list")
    if not threat_control_ids:
        findings.append("missing_or_empty_threat_metadata_control_ids")

    control_ids: list[str] = []
    gate_to_owners: dict[str, set[str]] = {}

    for ix, raw in enumerate(controls):
        if not isinstance(raw, dict):
            findings.append(f"invalid_control:{ix}:not_object")
            continue
        cid = str(raw.get("id", "")).strip()
        if not cid or not CONTROL_ID_RE.fullmatch(cid):
            findings.append(f"invalid_control_id:{ix}:{cid or 'empty'}")
            continue
        if cid in control_ids:
            findings.append(f"duplicate_control_id:{cid}")
        control_ids.append(cid)

        owner = str(raw.get("owner", "")).strip()
        if not owner:
            findings.append(f"missing_owner:{cid}")

        gates = _string_list(raw.get("gates", []))
        workflows = _string_list(raw.get("workflows", []))
        evidence = _string_list(raw.get("evidence", []))

        if not gates:
            findings.append(f"missing_gates:{cid}")
        if not workflows:
            findings.append(f"missing_workflows:{cid}")
        if not evidence:
            findings.append(f"missing_evidence:{cid}")

        workflow_texts: dict[str, str] = {}
        for wf in workflows:
            wf_path = ROOT / wf
            if not wf_path.exists():
                findings.append(f"missing_workflow:{cid}:{wf}")
                continue
            workflow_texts[wf] = wf_path.read_text(encoding="utf-8")

        for gate in gates:
            gate_path = ROOT / gate
            if not gate_path.exists():
                findings.append(f"missing_gate_script:{cid}:{gate}")
            if gate not in manifest_gates and gate not in MANIFEST_EXEMPT_GATES:
                findings.append(f"gate_not_in_super_manifest:{cid}:{gate}")
            mentioned = False
            gate_name = Path(gate).name
            for text in workflow_texts.values():
                if gate in text or gate_name in text:
                    mentioned = True
                    break
            if not mentioned:
                findings.append(f"gate_not_wired_in_mapped_workflows:{cid}:{gate}")
            if owner:
                gate_to_owners.setdefault(gate, set()).add(owner)

        for ev in evidence:
            if not ev.endswith(".json") and not ev.endswith(".jsonl"):
                findings.append(f"non_json_evidence_path:{cid}:{ev}")

    expected = set(threat_control_ids)
    actual = set(control_ids)
    for missing in sorted(expected - actual):
        findings.append(f"threat_metadata_control_unmapped:{missing}")
    for unexpected in sorted(actual - expected):
        findings.append(f"matrix_control_missing_from_threat_metadata:{unexpected}")

    for gate in critical_gates:
        owners = gate_to_owners.get(gate, set())
        if not owners:
            findings.append(f"critical_gate_without_control_owner:{gate}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "controls": len(control_ids),
            "critical_gates": len(critical_gates),
            "mapped_gates": len(gate_to_owners),
        },
        "metadata": {"gate": "threat_control_mapping_gate"},
    }
    out = evidence_root() / "security" / "threat_control_mapping_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"THREAT_CONTROL_MAPPING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
