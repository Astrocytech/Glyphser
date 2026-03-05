#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY_PATH = ROOT / "governance" / "security" / "dependency_freshness_policy.json"
LOCK_PATH = ROOT / "requirements.lock"


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _parse_iso_utc(raw: str) -> datetime | None:
    text = str(raw).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _direct_dependencies(lock_path: Path) -> set[str]:
    if not lock_path.exists():
        return set()
    out: set[str] = set()
    for raw in lock_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, _ = line.split("==", 1)
        out.add(name.strip().lower())
    return out


def _vulnerability_entries(pip_audit_report: dict[str, Any]) -> list[tuple[str, str]]:
    report = pip_audit_report.get("report")
    deps: list[dict[str, Any]] = []
    if isinstance(report, list):
        deps = [item for item in report if isinstance(item, dict)]
    elif isinstance(report, dict):
        raw = report.get("dependencies", [])
        if isinstance(raw, list):
            deps = [item for item in raw if isinstance(item, dict)]

    out: list[tuple[str, str]] = []
    for dep in deps:
        package = str(dep.get("name", "")).strip().lower()
        if not package:
            continue
        vulns = dep.get("vulns", [])
        if not isinstance(vulns, list):
            continue
        for vuln in vulns:
            if not isinstance(vuln, dict):
                continue
            vuln_id = str(vuln.get("id", "")).strip() or "unknown"
            out.append((package, vuln_id))
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(POLICY_PATH) if POLICY_PATH.exists() else {}
    max_age_days = int(policy.get("max_known_vulnerable_age_days", 14))
    enforce_transitive_only = bool(policy.get("enforce_transitive_only", True))
    fail_on_missing = bool(policy.get("fail_on_missing_pip_audit_report", False))
    history_rel = str(
        policy.get("history_path", "evidence/security/dependency_vulnerability_freshness_history.json")
    ).strip()
    history_path = ROOT / history_rel

    sec = evidence_root() / "security"
    pip_audit_path = sec / "pip_audit.json"
    findings: list[str] = []
    if max_age_days < 0:
        findings.append("invalid_policy:max_known_vulnerable_age_days")
        max_age_days = 0

    pip_audit = _load_json(pip_audit_path) if pip_audit_path.exists() else {}
    if not pip_audit and fail_on_missing:
        findings.append("missing_pip_audit_report")

    now = _now_utc()
    report_generated_at = None
    if pip_audit:
        report_generated_at = _parse_iso_utc(pip_audit.get("metadata", {}).get("generated_at_utc", ""))
    observed_at = report_generated_at or now

    direct = _direct_dependencies(LOCK_PATH)
    observed_raw = _vulnerability_entries(pip_audit) if pip_audit else []
    observed: set[tuple[str, str]] = set()
    for package, vuln_id in observed_raw:
        if enforce_transitive_only and package in direct:
            continue
        observed.add((package, vuln_id))

    history = _load_json(history_path) if history_path.exists() else {}
    entries = history.get("entries", {})
    if not isinstance(entries, dict):
        entries = {}

    for package, vuln_id in sorted(observed):
        key = f"{package}|{vuln_id}"
        prev = entries.get(key, {})
        if not isinstance(prev, dict):
            prev = {}
        first_seen = str(prev.get("first_seen_utc", "")).strip() or observed_at.isoformat()
        entries[key] = {
            "package": package,
            "vulnerability_id": vuln_id,
            "first_seen_utc": first_seen,
            "last_seen_utc": observed_at.isoformat(),
            "resolved_at_utc": "",
        }

    for key, payload in list(entries.items()):
        if not isinstance(payload, dict):
            continue
        package = str(payload.get("package", "")).strip().lower()
        vuln_id = str(payload.get("vulnerability_id", "")).strip()
        if not package or not vuln_id:
            continue
        if (package, vuln_id) in observed:
            continue
        if not str(payload.get("resolved_at_utc", "")).strip():
            payload["resolved_at_utc"] = observed_at.isoformat()
            entries[key] = payload

    active_ages: list[dict[str, Any]] = []
    for package, vuln_id in sorted(observed):
        key = f"{package}|{vuln_id}"
        payload = entries.get(key, {})
        first_seen = _parse_iso_utc(payload.get("first_seen_utc", "")) if isinstance(payload, dict) else None
        if first_seen is None:
            first_seen = observed_at
        age_days = max(0, int((observed_at - first_seen).total_seconds() // 86400))
        active_ages.append({"package": package, "vulnerability_id": vuln_id, "age_days": age_days})
        if age_days > max_age_days:
            findings.append(f"vulnerability_age_exceeded:{package}:{vuln_id}:age_days:{age_days}:max_days:{max_age_days}")

    history_payload = {
        "schema_version": 1,
        "updated_at_utc": observed_at.isoformat(),
        "entries": entries,
    }
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "PASS" if not findings else "FAIL"
    report = {
        "status": status,
        "findings": findings,
        "summary": {
            "max_known_vulnerable_age_days": max_age_days,
            "enforce_transitive_only": enforce_transitive_only,
            "active_transitive_vulnerabilities": len(observed),
            "aged_vulnerabilities": [item for item in active_ages if int(item.get("age_days", 0)) > max_age_days],
            "history_path": str(history_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "dependency_freshness_gate"},
    }
    out = sec / "dependency_freshness_gate.json"
    write_json_report(out, report)
    print(f"DEPENDENCY_FRESHNESS_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
