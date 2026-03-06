#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
POLICY = ROOT / "governance" / "security" / "security_cross_report_consistency_policy.json"


def _report_name_from_cmd(cmd: list[str]) -> str | None:
    if len(cmd) < 2:
        return None
    script = Path(cmd[1]).name
    if not script.endswith(".py"):
        return None
    stem = script[:-3]
    if stem == "security_super_gate":
        return None
    return stem + ".json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    super_path = sec / "security_super_gate.json"
    findings: list[str] = []
    checked = 0

    if not super_path.exists():
        findings.append("missing_security_super_gate_report")
        results: list[dict[str, object]] = []
        super_status = ""
    else:
        payload = json.loads(super_path.read_text(encoding="utf-8"))
        raw = payload.get("results", []) if isinstance(payload, dict) else []
        results = [r for r in raw if isinstance(r, dict)]
        super_status = str(payload.get("status", "")).upper() if isinstance(payload, dict) else ""

    for row in results:
        cmd = row.get("cmd", [])
        status = str(row.get("status", "")).upper()
        if not isinstance(cmd, list):
            continue
        report_name = _report_name_from_cmd([str(x) for x in cmd])
        if not report_name:
            continue
        report_path = sec / report_name
        checked += 1
        if not report_path.exists():
            findings.append(f"missing_component_report:{report_name}")
            continue
        try:
            component = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_component_report_json:{report_name}")
            continue
        component_status = str(component.get("status", "")).upper()
        if component_status != status:
            findings.append(f"status_mismatch:{report_name}:{status}:{component_status or 'UNKNOWN'}")

    if super_status:
        expected_super_status = "FAIL" if any(str(row.get("status", "")).upper() != "PASS" for row in results) else "PASS"
        if expected_super_status != super_status:
            findings.append(f"super_gate_status_component_mismatch:expected:{expected_super_status}:actual:{super_status}")

    policy_report_path = sec / "policy_signature.json"
    if policy_report_path.exists():
        try:
            policy_report = json.loads(policy_report_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append("invalid_policy_signature_report_json")
            policy_report = {}
        if isinstance(policy_report, dict) and str(policy_report.get("status", "")).upper() == "PASS":
            checks = policy_report.get("checks", {})
            if not isinstance(checks, dict):
                findings.append("policy_pass_missing_checks")
                checks = {}
            manifest_path = ROOT / "governance" / "security" / "policy_signature_manifest.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                findings.append("invalid_policy_signature_manifest")
                manifest = {}
            required = manifest.get("policies", []) if isinstance(manifest, dict) else []
            if not isinstance(required, list):
                required = []
            for rel in required:
                if not isinstance(rel, str):
                    continue
                item = checks.get(rel, {})
                ok = bool(item.get("ok")) if isinstance(item, dict) else False
                if not ok:
                    findings.append(f"policy_pass_missing_verified_file:{rel}")

    provenance_report_path = sec / "provenance_signature.json"
    if provenance_report_path.exists():
        try:
            provenance_report = json.loads(provenance_report_path.read_text(encoding="utf-8"))
        except Exception:
            findings.append("invalid_provenance_signature_report_json")
            provenance_report = {}
        if isinstance(provenance_report, dict) and str(provenance_report.get("status", "")).upper() == "PASS":
            checks = provenance_report.get("checks", {})
            if not isinstance(checks, dict) or not checks:
                findings.append("provenance_pass_missing_checks")
                checks = {}
            key = current_key(strict=False)
            for name, item in checks.items():
                if not isinstance(item, dict):
                    findings.append(f"provenance_pass_invalid_check_entry:{name}")
                    continue
                artifact_rel = str(item.get("artifact", "")).strip()
                signature_rel = str(item.get("signature", "")).strip()
                if not artifact_rel or not signature_rel:
                    findings.append(f"provenance_pass_missing_paths:{name}")
                    continue
                artifact_path = ROOT / artifact_rel
                signature_path = ROOT / signature_rel
                if not artifact_path.exists() or not signature_path.exists():
                    findings.append(f"provenance_pass_missing_artifact_or_signature:{name}")
                    continue
                sig = signature_path.read_text(encoding="utf-8").strip()
                if not sig:
                    findings.append(f"provenance_pass_empty_signature:{name}")
                    continue
                if not verify_file(artifact_path, sig, key=key):
                    findings.append(f"provenance_pass_hash_or_signature_mismatch:{name}")

    policy: dict[str, object] = {}
    if POLICY.exists():
        try:
            payload = json.loads(POLICY.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                policy = payload
        except Exception:
            findings.append("invalid_cross_report_consistency_policy")
    skew_limit = float(policy.get("max_timestamp_skew_seconds", 21600)) if isinstance(policy, dict) else 21600.0
    related_raw = policy.get("related_reports", []) if isinstance(policy, dict) else []
    related_reports = related_raw if isinstance(related_raw, list) else []
    if not related_reports:
        related_reports = ["security_super_gate.json", "policy_signature.json", "provenance_signature.json"]

    timestamps: dict[str, datetime] = {}
    for report_name in related_reports:
        if not isinstance(report_name, str):
            continue
        report_path = sec / report_name
        if not report_path.exists():
            continue
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        generated = str(metadata.get("generated_at_utc", "")).strip() if isinstance(metadata, dict) else ""
        if not generated:
            findings.append(f"missing_generated_at_utc:{report_name}")
            continue
        try:
            timestamps[report_name] = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        except ValueError:
            findings.append(f"invalid_generated_at_utc:{report_name}")

    if len(timestamps) >= 2:
        ordered = sorted(timestamps.values())
        skew_seconds = (ordered[-1] - ordered[0]).total_seconds()
        if skew_seconds > skew_limit:
            findings.append(f"stale_timestamp_skew:{int(skew_seconds)}>{int(skew_limit)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_components": checked},
        "metadata": {"gate": "security_cross_gate_consistency_gate"},
    }
    out = sec / "security_cross_gate_consistency_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_CROSS_GATE_CONSISTENCY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
