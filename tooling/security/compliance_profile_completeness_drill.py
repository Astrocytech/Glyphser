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

POLICY = ROOT / "governance" / "security" / "compliance_export_profiles.json"


def _quarter_tag(now: datetime) -> str:
    quarter = ((now.month - 1) // 3) + 1
    return f"{now.year}-Q{quarter}"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    now = datetime.now(UTC)
    findings: list[str] = []
    drill_rows: list[dict[str, object]] = []

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
        copied: set[str] = set()

        if not manifest.exists():
            findings.append(f"drill_missing_profile_manifest:{profile}")
        elif not sig.exists():
            findings.append(f"drill_missing_profile_manifest_signature:{profile}")
        else:
            sig_text = sig.read_text(encoding="utf-8").strip()
            if not artifact_signing.verify_file(manifest, sig_text, key=artifact_signing.current_key(strict=False)):
                if not artifact_signing.verify_file(manifest, sig_text, key=artifact_signing.bootstrap_key()):
                    findings.append(f"drill_invalid_profile_manifest_signature:{profile}")
                else:
                    payload = json.loads(manifest.read_text(encoding="utf-8"))
                    copied_raw = payload.get("copied_artifacts", []) if isinstance(payload, dict) else []
                    copied = {str(item).strip() for item in copied_raw if isinstance(item, str) and str(item).strip()}
            else:
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                copied_raw = payload.get("copied_artifacts", []) if isinstance(payload, dict) else []
                copied = {str(item).strip() for item in copied_raw if isinstance(item, str) and str(item).strip()}

        missing = sorted(item for item in required if item not in copied)
        for item in missing:
            findings.append(f"drill_missing_required_profile_artifact:{profile}:{item}")

        drill_rows.append(
            {
                "profile": profile,
                "required_artifact_count": len(required),
                "copied_artifact_count": len(copied),
                "missing_artifacts": missing,
            }
        )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "quarter": _quarter_tag(now),
            "drill_timestamp_utc": now.isoformat(),
            "profile_count": len(drill_rows),
        },
        "metadata": {"gate": "compliance_profile_completeness_drill"},
        "profiles": drill_rows,
    }
    out = evidence_root() / "security" / "compliance_profile_completeness_drill.json"
    write_json_report(out, report)
    print(f"COMPLIANCE_PROFILE_COMPLETENESS_DRILL: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
