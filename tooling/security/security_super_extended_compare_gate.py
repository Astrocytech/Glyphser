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
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")

SUPER_REPORT = ROOT / "evidence" / "security" / "security_super_gate.json"
MANIFEST = ROOT / "tooling" / "security" / "security_super_gate_manifest.json"
HISTORY = ROOT / "evidence" / "security" / "security_super_extended_failure_history.json"
EXCEPTION_REGISTRY = ROOT / "governance" / "security" / "temporary_exceptions.json"
EXTENDED_FAILURE_MAX_AGE_DAYS = 7


def _script_from_cmd(cmd: list[Any]) -> str:
    if len(cmd) < 2:
        return ""
    part = cmd[1]
    return str(part) if isinstance(part, str) else ""


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _load_active_signed_exception_scopes(findings: list[str]) -> set[str]:
    if not EXCEPTION_REGISTRY.exists():
        return set()
    sig = EXCEPTION_REGISTRY.with_suffix(".json.sig")
    if not sig.exists():
        findings.append("missing_exception_registry_signature")
        return set()
    key = artifact_signing.current_key(strict=False)
    if not artifact_signing.verify_file(EXCEPTION_REGISTRY, sig.read_text(encoding="utf-8").strip(), key=key):
        findings.append("invalid_exception_registry_signature")
        return set()
    payload = json.loads(EXCEPTION_REGISTRY.read_text(encoding="utf-8"))
    entries = payload.get("exceptions", []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        return set()
    now = datetime.now(UTC)
    scopes: set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            continue
        scope = str(item.get("scope", "")).strip()
        exp = _parse_ts(item.get("expires_at_utc", ""))
        if not scope or exp is None or exp <= now:
            continue
        scopes.add(scope)
    return scopes


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not SUPER_REPORT.exists():
        findings.append("missing_super_gate_report")
    if not MANIFEST.exists():
        findings.append("missing_manifest")
    if findings:
        report = {
            "status": "FAIL",
            "findings": findings,
            "summary": {"core_failures": 0, "extended_failures": 0},
            "metadata": {"gate": "security_super_extended_compare_gate"},
        }
        out = evidence_root() / "security" / "security_super_extended_compare_gate.json"
        write_json_report(out, report)
        print(f"SECURITY_SUPER_EXTENDED_COMPARE_GATE: {report['status']}")
        print(f"Report: {out}")
        return 1

    payload = json.loads(SUPER_REPORT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    core = set(manifest.get("core", []) if isinstance(manifest, dict) else [])
    extended = set(manifest.get("extended", []) if isinstance(manifest, dict) else [])
    results = payload.get("results", []) if isinstance(payload, dict) else []
    if not isinstance(results, list):
        results = []
    core_failures: list[str] = []
    extended_failures: list[str] = []
    unknown_failures: list[str] = []
    for rec in results:
        if not isinstance(rec, dict):
            continue
        if str(rec.get("status", "")) == "PASS":
            continue
        cmd = rec.get("cmd", [])
        if not isinstance(cmd, list):
            continue
        script = _script_from_cmd(cmd)
        if script in core:
            core_failures.append(script)
        elif script in extended:
            extended_failures.append(script)
        else:
            unknown_failures.append(script)
    for script in sorted(set(unknown_failures)):
        findings.append(f"unknown_failed_gate:{script}")

    now = datetime.now(UTC)
    history_payload = {}
    if HISTORY.exists():
        try:
            history_payload = json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception:
            history_payload = {}
    entries = history_payload.get("entries", {}) if isinstance(history_payload, dict) else {}
    if not isinstance(entries, dict):
        entries = {}

    for script in sorted(set(extended_failures)):
        item = entries.get(script, {})
        if not isinstance(item, dict):
            item = {}
        first_seen = str(item.get("first_seen_utc", "")).strip() or now.isoformat()
        entries[script] = {
            "first_seen_utc": first_seen,
            "last_seen_utc": now.isoformat(),
        }
    for script in list(entries.keys()):
        if script not in set(extended_failures):
            entries.pop(script, None)

    aged_extended_failures: list[dict[str, Any]] = []
    for script in sorted(set(extended_failures)):
        first = _parse_ts(entries.get(script, {}).get("first_seen_utc", "")) or now
        age_days = max(0, int((now - first).total_seconds() // 86400))
        if age_days > EXTENDED_FAILURE_MAX_AGE_DAYS:
            aged_extended_failures.append({"script": script, "age_days": age_days})

    if aged_extended_failures:
        scopes = _load_active_signed_exception_scopes(findings)
        for item in aged_extended_failures:
            scope = f"extended_failure:{item['script']}"
            if scope in scopes:
                continue
            findings.append(f"extended_failure_core_blocker:{item['script']}:age_days:{item['age_days']}")

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(
        json.dumps({"schema_version": 1, "updated_at_utc": now.isoformat(), "entries": entries}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "core_failures": len(set(core_failures)),
            "extended_failures": len(set(extended_failures)),
            "unknown_failures": len(set(unknown_failures)),
            "extended_failure_max_age_days": EXTENDED_FAILURE_MAX_AGE_DAYS,
            "aged_extended_failures": aged_extended_failures,
        },
        "metadata": {"gate": "security_super_extended_compare_gate"},
        "classification": {
            "core_failures": sorted(set(core_failures)),
            "extended_failures": sorted(set(extended_failures)),
            "unknown_failures": sorted(set(unknown_failures)),
        },
    }
    out = evidence_root() / "security" / "security_super_extended_compare_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_SUPER_EXTENDED_COMPARE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
