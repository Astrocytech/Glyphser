#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "compliance_export_profiles.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    profiles = policy.get("profiles", {}) if isinstance(policy, dict) and isinstance(policy.get("profiles"), dict) else {}

    for profile, entry in sorted(profiles.items()):
        if not isinstance(profile, str) or not isinstance(entry, dict):
            continue
        required_raw = entry.get("artifacts", []) if isinstance(entry.get("artifacts"), list) else []
        required = [str(item).strip() for item in required_raw if isinstance(item, str) and str(item).strip()]
        bundle = evidence_root() / "security" / "compliance_exports" / profile
        manifest = bundle / "export_manifest.json"
        sig = manifest.with_suffix(".json.sig")

        if not manifest.exists():
            findings.append(f"missing_profile_manifest:{profile}")
            continue
        if not sig.exists():
            findings.append(f"missing_profile_manifest_signature:{profile}")
            continue
        sig_text = sig.read_text(encoding="utf-8").strip()
        if not artifact_signing.verify_file(manifest, sig_text, key=artifact_signing.current_key(strict=False)):
            if not artifact_signing.verify_file(manifest, sig_text, key=artifact_signing.bootstrap_key()):
                findings.append(f"invalid_profile_manifest_signature:{profile}")
                continue

        payload = json.loads(manifest.read_text(encoding="utf-8"))
        copied_raw = payload.get("copied_artifacts", []) if isinstance(payload, dict) else []
        copied = {str(item).strip() for item in copied_raw if isinstance(item, str) and str(item).strip()}
        for artifact in required:
            if artifact not in copied:
                findings.append(f"missing_required_profile_artifact:{profile}:{artifact}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"profile_count": len(profiles)},
        "metadata": {"gate": "compliance_profile_artifact_gate"},
    }
    out = evidence_root() / "security" / "compliance_profile_artifact_gate.json"
    write_json_report(out, report)
    print(f"COMPLIANCE_PROFILE_ARTIFACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
