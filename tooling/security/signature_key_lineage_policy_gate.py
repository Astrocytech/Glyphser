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

POLICY = ROOT / "governance" / "security" / "signature_key_lineage_policy.json"
ARTIFACTS = {
    "policy_signature": "policy_signature.json",
    "provenance_signature": "provenance_signature.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _key_provenance(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata", {})
    if isinstance(metadata, dict):
        kp = metadata.get("key_provenance", {})
        if isinstance(kp, dict) and kp:
            return kp
    kp = payload.get("key_provenance", {})
    return kp if isinstance(kp, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_signature_key_lineage_policy")
        policy_payload: dict[str, Any] = {}
    else:
        try:
            policy_payload = _load_json(POLICY)
        except Exception:
            policy_payload = {}
            findings.append("invalid_signature_key_lineage_policy")

    key_views: dict[str, dict[str, Any]] = {}
    for alias, filename in ARTIFACTS.items():
        path = sec / filename
        if not path.exists():
            findings.append(f"missing_signature_artifact:{alias}:{filename}")
            key_views[alias] = {}
            continue
        try:
            payload = _load_json(path)
        except Exception:
            findings.append(f"invalid_signature_artifact:{alias}:{filename}")
            key_views[alias] = {}
            continue
        key_views[alias] = _key_provenance(payload)
        if not key_views[alias]:
            findings.append(f"missing_key_provenance:{alias}")

    required_pairs = policy_payload.get("required_pairs", []) if isinstance(policy_payload, dict) else []
    if not isinstance(required_pairs, list):
        required_pairs = []
    if not required_pairs:
        findings.append("missing_required_pairs")

    checked_pairs = 0
    for pair in required_pairs:
        if not isinstance(pair, dict):
            findings.append("invalid_required_pair:not_object")
            continue
        left = str(pair.get("left", "")).strip()
        right = str(pair.get("right", "")).strip()
        fields = pair.get("must_match_fields", [])
        if not left or not right or not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
            findings.append("invalid_required_pair:missing_left_right_or_fields")
            continue
        checked_pairs += 1
        left_kp = key_views.get(left, {})
        right_kp = key_views.get(right, {})
        if not left_kp or not right_kp:
            continue
        for field in fields:
            left_value = str(left_kp.get(field, "")).strip()
            right_value = str(right_kp.get(field, "")).strip()
            if left_value != right_value:
                findings.append(f"key_lineage_mismatch:{left}:{right}:{field}:{left_value}!={right_value}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_pairs": len(required_pairs),
            "checked_pairs": checked_pairs,
            "artifacts_checked": len(ARTIFACTS),
        },
        "metadata": {"gate": "signature_key_lineage_policy_gate", "policy_path": str(POLICY.relative_to(ROOT))},
    }
    out = sec / "signature_key_lineage_policy_gate.json"
    write_json_report(out, report)
    print(f"SIGNATURE_KEY_LINEAGE_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
