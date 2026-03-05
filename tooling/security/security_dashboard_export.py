#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _control_coverage_ratio() -> dict[str, float | int]:
    matrix = _load(ROOT / "governance" / "security" / "threat_control_matrix.json")
    meta = _load(ROOT / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json")
    controls = matrix.get("controls", []) if isinstance(matrix.get("controls"), list) else []
    required = meta.get("control_ids", []) if isinstance(meta.get("control_ids"), list) else []
    implemented_controls = len([row for row in controls if isinstance(row, dict) and str(row.get("id", "")).strip()])
    required_controls = len([row for row in required if isinstance(row, str) and str(row).strip()])
    ratio = round((implemented_controls / required_controls), 4) if required_controls else 0.0
    return {
        "implemented_controls": implemented_controls,
        "required_controls": required_controls,
        "control_coverage_ratio": ratio,
    }


def _parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        parsed = _parse_utc(fixed)
        if parsed is not None:
            return parsed
    return datetime.now(UTC)


def _mean_hardening_lead_time() -> dict[str, float | int]:
    payload = _load(ROOT / "governance" / "security" / "hardening_issue_enforcement_timeline.json")
    events = payload.get("events", []) if isinstance(payload.get("events"), list) else []
    samples_hours: list[float] = []
    invalid = 0
    complete = 0
    for row in events:
        if not isinstance(row, dict):
            invalid += 1
            continue
        identified = _parse_utc(row.get("issue_identified_at_utc"))
        enforced = _parse_utc(row.get("enforced_in_ci_at_utc"))
        if identified is None or enforced is None:
            invalid += 1
            continue
        delta_hours = (enforced - identified).total_seconds() / 3600.0
        if delta_hours < 0:
            invalid += 1
            continue
        complete += 1
        samples_hours.append(delta_hours)
    mean_hours = round(sum(samples_hours) / len(samples_hours), 2) if samples_hours else 0.0
    return {
        "hardening_lead_time_samples": len(events),
        "hardening_lead_time_complete_records": complete,
        "hardening_lead_time_invalid_records": invalid,
        "mean_hardening_lead_time_hours": mean_hours,
    }


def _false_positive_rate_per_gate() -> dict[str, object]:
    payload = _load(ROOT / "governance" / "security" / "security_gate_false_positive_log.json")
    events = payload.get("events", []) if isinstance(payload.get("events"), list) else []
    totals: dict[str, int] = {}
    false_positives: dict[str, int] = {}
    invalid_records = 0
    for row in events:
        if not isinstance(row, dict):
            invalid_records += 1
            continue
        gate = str(row.get("gate", "")).strip()
        classification = str(row.get("classification", "")).strip().lower()
        if not gate or classification not in {"true_positive", "false_positive"}:
            invalid_records += 1
            continue
        totals[gate] = totals.get(gate, 0) + 1
        if classification == "false_positive":
            false_positives[gate] = false_positives.get(gate, 0) + 1
    per_gate = {gate: round(false_positives.get(gate, 0) / total, 4) for gate, total in sorted(totals.items()) if total > 0}
    overall_total = sum(totals.values())
    overall_fp = sum(false_positives.values())
    return {
        "false_positive_rate_per_gate": per_gate,
        "false_positive_reviewed_findings": overall_total,
        "false_positive_records_invalid": invalid_records,
        "false_positive_rate_overall": round((overall_fp / overall_total), 4) if overall_total else 0.0,
    }


def _bypass_exception_volume_and_aging() -> dict[str, float | int]:
    now = _now_utc()
    ages_days: list[float] = []
    invalid_aging_records = 0
    active_exceptions = 0
    active_waivers = 0
    nearing_expiry = 0

    exceptions_payload = _load(ROOT / "governance" / "security" / "temporary_exceptions.json")
    exceptions = exceptions_payload.get("exceptions", []) if isinstance(exceptions_payload.get("exceptions"), list) else []
    for row in exceptions:
        if not isinstance(row, dict):
            invalid_aging_records += 1
            continue
        exp = _parse_utc(row.get("expires_at_utc"))
        if exp is None or exp <= now:
            continue
        active_exceptions += 1
        if (exp - now).total_seconds() <= 7 * 24 * 3600:
            nearing_expiry += 1
        created = _parse_utc(row.get("created_at_utc"))
        if created is None or created > now:
            invalid_aging_records += 1
            continue
        ages_days.append((now - created).total_seconds() / 86400.0)

    waiver_policy = _load(ROOT / "governance" / "security" / "temporary_waiver_policy.json")
    glob_pattern = str(waiver_policy.get("waiver_file_glob", "evidence/**/waivers.json")).strip() or "evidence/**/waivers.json"
    if glob_pattern.startswith("evidence/"):
        glob_pattern = glob_pattern[len("evidence/") :]
    for path in sorted(evidence_root().glob(glob_pattern)):
        payload = _load(path)
        waivers = payload.get("waivers", []) if isinstance(payload.get("waivers"), list) else []
        for row in waivers:
            if not isinstance(row, dict):
                invalid_aging_records += 1
                continue
            exp = _parse_utc(row.get("expires_at_utc"))
            if exp is None or exp <= now:
                continue
            active_waivers += 1
            if (exp - now).total_seconds() <= 7 * 24 * 3600:
                nearing_expiry += 1
            created = _parse_utc(row.get("created_at_utc"))
            if created is None or created > now:
                invalid_aging_records += 1
                continue
            ages_days.append((now - created).total_seconds() / 86400.0)

    return {
        "active_exception_volume": active_exceptions,
        "active_waiver_volume": active_waivers,
        "active_bypass_exception_volume_total": active_exceptions + active_waivers,
        "bypass_exception_aging_records": len(ages_days),
        "bypass_exception_aging_invalid_records": invalid_aging_records,
        "bypass_exception_aging_mean_days": round((sum(ages_days) / len(ages_days)), 2) if ages_days else 0.0,
        "bypass_exception_aging_max_days": round(max(ages_days), 2) if ages_days else 0.0,
        "bypass_exception_nearing_expiry_7d": nearing_expiry,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    contract_version = "v1"
    report = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "policy_signature": _load(sec / "policy_signature.json").get("status", "MISSING"),
            "provenance_signature": _load(sec / "provenance_signature.json").get("status", "MISSING"),
            "attestation": _load(sec / "evidence_attestation_gate.json").get("status", "MISSING"),
            "slo": _load(sec / "security_slo_report.json").get("summary", {}),
            "kpis": {
                **_control_coverage_ratio(),
                **_mean_hardening_lead_time(),
                **_false_positive_rate_per_gate(),
                **_bypass_exception_volume_and_aging(),
            },
        },
        "metadata": {"gate": "security_dashboard_export", "api_contract_version": contract_version},
    }
    out = sec / "security_dashboard.json"
    write_json_report(out, report)
    print(f"SECURITY_DASHBOARD_EXPORT: {report['status']}")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
