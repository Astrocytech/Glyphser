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

STANDARDS_PROFILE = ROOT / "governance" / "security" / "security_standards_profile.json"
LOCAL_PINNING_REPORT = ROOT / "evidence" / "security" / "workflow_pinning_gate.json"
LOCAL_PERMISSIONS_REPORT = ROOT / "evidence" / "security" / "security_workflow_permissions_policy_gate.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _status(path: Path) -> str:
    if not path.exists():
        return "UNKNOWN"
    try:
        payload = _load_json(path)
    except Exception:
        return "UNKNOWN"
    value = str(payload.get("status", "UNKNOWN")).upper()
    if value not in {"PASS", "FAIL"}:
        return "UNKNOWN"
    return value


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not STANDARDS_PROFILE.exists():
        consumer_repos: list[str] = []
        findings.append("missing_security_standards_profile")
    else:
        try:
            standards = _load_json(STANDARDS_PROFILE)
            raw = standards.get("consumer_repos", [])
            consumer_repos = [str(item) for item in raw if isinstance(item, str) and str(item).strip()] if isinstance(raw, list) else []
        except Exception:
            consumer_repos = []
            findings.append("invalid_security_standards_profile")

    local_pinning = _status(LOCAL_PINNING_REPORT)
    local_permissions = _status(LOCAL_PERMISSIONS_REPORT)

    rows: list[dict[str, str]] = [
        {
            "repo": "glyphser",
            "pinning_conformance": local_pinning,
            "permissions_conformance": local_permissions,
            "evidence_source": "local_security_gate_reports",
        }
    ]
    for repo in sorted(consumer_repos):
        rows.append(
            {
                "repo": repo,
                "pinning_conformance": "PENDING_EXTERNAL_ATTESTATION",
                "permissions_conformance": "PENDING_EXTERNAL_ATTESTATION",
                "evidence_source": "federated_repo_attestation_required",
            }
        )

    if local_pinning == "FAIL":
        findings.append("local_pinning_nonconformant")
    if local_permissions == "FAIL":
        findings.append("local_permissions_nonconformant")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "repos_reported": len(rows),
            "consumer_repos": len(consumer_repos),
            "local_pinning": local_pinning,
            "local_permissions": local_permissions,
        },
        "metadata": {"gate": "ecosystem_conformance_report"},
        "rows": rows,
    }
    out = evidence_root() / "security" / "ecosystem_conformance_report.json"
    write_json_report(out, report)
    print(f"ECOSYSTEM_CONFORMANCE_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
