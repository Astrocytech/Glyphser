#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import hashlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")

INCIDENT_POLICY = ROOT / "governance" / "security" / "incident_response_policy.json"
API_CONTRACT_VERSION = "v1"


def _severity_for_status(status: str) -> str:
    up = status.upper()
    if up == "FAIL":
        return "high"
    if up == "WARN":
        return "medium"
    return "low"


def _urgency_for_severity(severity: str) -> str:
    if severity == "high":
        return "page"
    if severity == "medium":
        return "ticket"
    return "none"


def _operator_pseudonym(operator_id: str, *, key: str) -> str:
    digest = hashlib.sha256(f"{key}:{operator_id}".encode("utf-8")).hexdigest()
    return f"op_{digest[:16]}"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    out = sec / "security_events.jsonl"
    summary_out = sec / "security_event_export.json"
    run_id = (
        os.environ.get("GITHUB_RUN_ID", "").strip()
        or os.environ.get("GLYPHSER_RUN_ID", "").strip()
        or "local"
    )

    routing = {}
    if INCIDENT_POLICY.exists():
        policy = json.loads(INCIDENT_POLICY.read_text(encoding="utf-8"))
        if isinstance(policy, dict):
            ar = policy.get("alert_routing_test", {})
            if isinstance(ar, dict):
                routing = ar
    pager_channel = str(routing.get("primary_contact", "security@glyphser.local")).strip() or "security@glyphser.local"
    playbook = "governance/security/OPERATIONS.md"
    operator_id = (
        os.environ.get("GLYPHSER_OPERATOR_ID", "").strip()
        or os.environ.get("GITHUB_ACTOR", "").strip()
        or "unknown-operator"
    )
    pseudonym_key = os.environ.get("GLYPHSER_OPERATOR_PSEUDONYM_KEY", "").strip() or artifact_signing.current_key(
        strict=False
    ).decode("utf-8", errors="ignore")
    operator_pseudonym = _operator_pseudonym(operator_id, key=pseudonym_key)

    events: list[dict[str, Any]] = []
    for path in sorted(sec.glob("*.json")):
        if path.name == "security_event_export.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        status = str(payload.get("status", "")).upper()
        if status not in {"FAIL", "WARN"}:
            continue
        control_id = path.stem
        severity = _severity_for_status(status)
        event = {
            "api_contract_version": API_CONTRACT_VERSION,
            "event_type": "security_gate_status",
            "severity": severity,
            "control_id": control_id,
            "run_id": run_id,
            "artifact_ref": str(path.relative_to(ROOT)).replace("\\", "/"),
            "status": status,
            "pager_channel": pager_channel,
            "urgency": _urgency_for_severity(severity),
            "playbook": playbook,
            "operator_id_pseudonym": operator_pseudonym,
        }
        events.append(event)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(ev, sort_keys=True) + "\n" for ev in events), encoding="utf-8")
    summary = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "events_emitted": len(events),
            "output": str(out.relative_to(ROOT)).replace("\\", "/"),
            "operator_pseudonymization": "deterministic_sha256",
        },
        "metadata": {"gate": "security_event_export", "api_contract_version": API_CONTRACT_VERSION},
    }
    write_json_report(summary_out, summary)
    print("SECURITY_EVENT_EXPORT: PASS")
    print(f"Report: {summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
