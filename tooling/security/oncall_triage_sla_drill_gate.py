#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "oncall_triage_sla_policy.json"
DRILL = ROOT / "governance" / "security" / "oncall_triage_sla_drill.json"


def _parse_ts(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _verify_signed_json(path: Path, findings: list[str], missing_code: str, invalid_code: str) -> dict[str, object]:
    if not path.exists():
        findings.append(missing_code)
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    sig_path = path.with_suffix(".json.sig")
    if not sig_path.exists():
        findings.append(f"missing_signature:{path.name}")
        return payload if isinstance(payload, dict) else {}
    sig_text = sig_path.read_text(encoding="utf-8").strip()
    verified = artifact_signing.verify_file(path, sig_text, key=artifact_signing.current_key(strict=False))
    if not verified:
        verified = artifact_signing.verify_file(path, sig_text, key=artifact_signing.bootstrap_key())
    if not verified:
        findings.append(invalid_code)
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = _verify_signed_json(
        POLICY,
        findings,
        "missing_oncall_triage_sla_policy",
        "invalid_oncall_triage_sla_policy_signature",
    )
    drill = _verify_signed_json(
        DRILL,
        findings,
        "missing_oncall_triage_sla_drill",
        "invalid_oncall_triage_sla_drill_signature",
    )

    required_sample = int(policy.get("required_sample_size", 10)) if isinstance(policy.get("required_sample_size"), int) else 10
    max_triage_minutes = int(policy.get("max_triage_minutes", 30)) if isinstance(policy.get("max_triage_minutes"), int) else 30
    cases = drill.get("cases", [])
    if not isinstance(cases, list):
        cases = []
        findings.append("invalid_oncall_triage_sla_drill_cases")

    if len(cases) < required_sample:
        findings.append(f"insufficient_oncall_triage_sla_drill_cases:{len(cases)}<{required_sample}")

    durations: list[float] = []
    for idx, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            findings.append(f"invalid_oncall_triage_case:{idx}")
            continue
        started = _parse_ts(str(case.get("triage_started_at_utc", "")))
        triaged = _parse_ts(str(case.get("triaged_at_utc", "")))
        failure_code = str(case.get("failure_code", "")).strip()
        if not failure_code:
            findings.append(f"missing_failure_code:{idx}")
        if started is None or triaged is None:
            findings.append(f"invalid_oncall_triage_timestamps:{idx}")
            continue
        delta_min = (triaged - started).total_seconds() / 60.0
        durations.append(delta_min)
        if delta_min < 0:
            findings.append(f"negative_oncall_triage_duration:{idx}")
            continue
        if delta_min > max_triage_minutes:
            findings.append(f"oncall_triage_sla_breach:{idx}:{delta_min:.2f}>{max_triage_minutes}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_sample_size": required_sample,
            "observed_cases": len(cases),
            "max_triage_minutes": max_triage_minutes,
            "max_observed_triage_minutes": max(durations) if durations else 0.0,
        },
        "metadata": {"gate": "oncall_triage_sla_drill_gate"},
    }
    out = evidence_root() / "security" / "oncall_triage_sla_drill_gate.json"
    write_json_report(out, report)
    print(f"ONCALL_TRIAGE_SLA_DRILL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
