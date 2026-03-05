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

POLICY = ROOT / "governance" / "security" / "hardening_status_transition_policy.json"
REGISTRY = ROOT / "governance" / "security" / "hardening_pending_item_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _as_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip().lower() for item in value if str(item).strip()}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY.exists():
        findings.append("missing_hardening_status_transition_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    if not REGISTRY.exists():
        findings.append("missing_hardening_pending_item_registry")
        entries: list[dict[str, Any]] = []
    else:
        registry = _load_json(REGISTRY)
        raw = registry.get("entries", [])
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    allowed_statuses = _as_set(policy.get("allowed_statuses", ["pending", "in_progress", "done"]))
    transitions = policy.get("allowed_transitions", {})
    if not isinstance(transitions, dict):
        transitions = {}
    requires_proof = bool(policy.get("done_requires_verification_proof", True))
    requires_pre_failure_evidence = bool(policy.get("implementation_requires_pre_failure_evidence", True))
    requires_post_implementation_proof = bool(policy.get("done_requires_post_implementation_proof", True))
    requires_evidence_link = bool(policy.get("done_requires_evidence_link", True))
    required_post_implementation_fields = (
        [str(item).strip() for item in policy.get("done_required_post_implementation_fields", []) if str(item).strip()]
        if isinstance(policy.get("done_required_post_implementation_fields", []), list)
        else []
    )
    if requires_post_implementation_proof and not required_post_implementation_fields:
        required_post_implementation_fields = ["tests_passed_ref", "gate_passed_ref", "ci_lane_ref"]

    for idx, row in enumerate(entries):
        status = str(row.get("status", "")).strip().lower()
        previous = str(row.get("previous_status", status)).strip().lower()
        proof = str(row.get("verification_proof", "")).strip()
        negative_test_evidence_ref = str(row.get("negative_test_evidence_ref", "")).strip()
        verification = row.get("verification", {}) if isinstance(row.get("verification"), dict) else {}
        pre_failure_evidence = str(verification.get("pre_implementation_failure", "")).strip()
        item_id = str(row.get("id", f"idx-{idx}")).strip()
        if status not in allowed_statuses:
            findings.append(f"invalid_status:{item_id}:{status or 'empty'}")
            continue
        allowed_next = _as_set(transitions.get(previous, [previous]))
        if status not in allowed_next:
            findings.append(f"invalid_status_transition:{item_id}:{previous}->{status}")
        if requires_pre_failure_evidence and status in {"in_progress", "done"}:
            if not negative_test_evidence_ref and not pre_failure_evidence:
                findings.append(f"missing_pre_failure_evidence_for_implementation:{item_id}")
        if status == "done" and requires_proof and not proof:
            findings.append(f"missing_verification_proof_for_done:{item_id}")
        if status == "done" and requires_post_implementation_proof:
            missing_fields = [
                field
                for field in required_post_implementation_fields
                if not str(verification.get(field, "")).strip()
            ]
            if missing_fields:
                findings.append(
                    f"missing_post_implementation_proof_for_done:{item_id}:{','.join(sorted(missing_fields))}"
                )
            if not str(row.get("ci_run_ref", "")).strip():
                findings.append(f"missing_ci_run_ref_for_done:{item_id}")
        if status == "done" and requires_evidence_link and not str(row.get("evidence_link", "")).strip():
            findings.append(f"missing_evidence_link_for_done:{item_id}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "entries_checked": len(entries),
            "allowed_statuses": sorted(allowed_statuses),
            "requires_done_verification_proof": requires_proof,
            "requires_pre_failure_evidence": requires_pre_failure_evidence,
            "requires_post_implementation_proof": requires_post_implementation_proof,
            "required_post_implementation_fields": required_post_implementation_fields,
            "requires_evidence_link": requires_evidence_link,
        },
        "metadata": {"gate": "hardening_status_transition_gate"},
    }
    out = evidence_root() / "security" / "hardening_status_transition_gate.json"
    write_json_report(out, report)
    print(f"HARDENING_STATUS_TRANSITION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
