#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid policy object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    adv = _load(ROOT / "governance" / "security" / "advanced_hardening_policy.json")
    key = _load(ROOT / "governance" / "security" / "key_management_policy.json")
    cont = _load(ROOT / "governance" / "security" / "container_provenance_policy.json")

    max_age = int(adv.get("max_attestation_age_hours", 168))
    if max_age <= 0:
        findings.append("invalid_max_attestation_age_hours")
    migration_pct = float(adv.get("schema_strict_min_migration_pct", 95.0))
    if migration_pct < 50.0 or migration_pct > 100.0:
        findings.append("invalid_schema_strict_min_migration_pct")

    min_len = int(key.get("minimum_key_length", 32))
    min_entropy = float(key.get("minimum_entropy_bits", 80))
    max_rot_days = int(key.get("maximum_rotation_age_days", 90))
    if min_len < 16:
        findings.append("invalid_minimum_key_length")
    if min_entropy <= 0.0:
        findings.append("invalid_minimum_entropy_bits")
    if max_rot_days <= 0:
        findings.append("invalid_maximum_rotation_age_days")
    if min_entropy < min_len:
        findings.append("entropy_threshold_too_low_for_min_length")

    required_lanes = {str(x).strip().lower() for x in cont.get("cosign_required_lanes", []) if isinstance(x, str)}
    skippable_lanes = {str(x).strip().lower() for x in cont.get("cosign_skippable_lanes", []) if isinstance(x, str)}
    if not required_lanes:
        findings.append("missing_cosign_required_lanes")
    overlap = sorted(required_lanes & skippable_lanes)
    for lane in overlap:
        findings.append(f"cosign_lane_overlap:{lane}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policies_checked": 3,
            "cosign_required_lanes": sorted(required_lanes),
            "cosign_skippable_lanes": sorted(skippable_lanes),
        },
        "metadata": {"gate": "policy_semantic_validation_gate"},
    }
    out = evidence_root() / "security" / "policy_semantic_validation_gate.json"
    write_json_report(out, report)
    print(f"POLICY_SEMANTIC_VALIDATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
