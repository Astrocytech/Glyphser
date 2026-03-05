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

POLICY = ROOT / "governance" / "security" / "package_metadata_anomaly_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _domain(email: str) -> str:
    addr = email.strip().lower()
    if "@" not in addr:
        return ""
    return addr.rsplit("@", 1)[-1]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_package_metadata_anomaly_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    snap_rel = str(policy.get("registry_snapshot_path", "governance/security/metadata/dependency_registry_snapshot.json")).strip()
    snapshot_path = ROOT / snap_rel
    snapshot = _load_json(snapshot_path) if snapshot_path.exists() else {}
    if not snapshot_path.exists():
        findings.append("missing_registry_snapshot")

    packages = snapshot.get("packages", {}) if isinstance(snapshot, dict) else {}
    if not isinstance(packages, dict):
        packages = {}

    disallowed_maintainers = {str(x).strip().lower() for x in policy.get("disallowed_maintainers", []) if isinstance(x, str)}
    disallowed_domains = {str(x).strip().lower() for x in policy.get("disallowed_email_domains", []) if isinstance(x, str)}
    expected = policy.get("expected_package_metadata", {}) if isinstance(policy, dict) else {}
    if not isinstance(expected, dict):
        expected = {}

    for package, meta in packages.items():
        if not isinstance(package, str) or not isinstance(meta, dict):
            continue
        maintainers = [str(x).strip().lower() for x in meta.get("maintainers", []) if isinstance(x, str) and str(x).strip()]
        emails = [str(x).strip().lower() for x in meta.get("emails", []) if isinstance(x, str) and str(x).strip()]
        domains = [str(x).strip().lower() for x in meta.get("domains", []) if isinstance(x, str) and str(x).strip()]

        for maintainer in maintainers:
            if maintainer in disallowed_maintainers:
                findings.append(f"disallowed_maintainer:{package}:{maintainer}")

        for email in emails:
            d = _domain(email)
            if d and d in disallowed_domains:
                findings.append(f"disallowed_email_domain:{package}:{d}")

        for d in domains:
            if d in disallowed_domains:
                findings.append(f"disallowed_domain:{package}:{d}")

        expected_meta = expected.get(package)
        if isinstance(expected_meta, dict):
            exp_maintainers = sorted(str(x).strip().lower() for x in expected_meta.get("maintainers", []) if isinstance(x, str))
            exp_emails = sorted(str(x).strip().lower() for x in expected_meta.get("emails", []) if isinstance(x, str))
            exp_domains = sorted(str(x).strip().lower() for x in expected_meta.get("domains", []) if isinstance(x, str))
            if exp_maintainers and sorted(set(maintainers)) != sorted(set(exp_maintainers)):
                findings.append(f"maintainer_drift:{package}")
            if exp_emails and sorted(set(emails)) != sorted(set(exp_emails)):
                findings.append(f"email_drift:{package}")
            if exp_domains and sorted(set(domains)) != sorted(set(exp_domains)):
                findings.append(f"domain_drift:{package}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "snapshot_path": snap_rel,
            "packages_evaluated": len(packages),
            "expected_metadata_packages": len(expected),
        },
        "metadata": {"gate": "package_metadata_anomaly_gate"},
    }

    out = evidence_root() / "security" / "package_metadata_anomaly_gate.json"
    write_json_report(out, report)
    print(f"PACKAGE_METADATA_ANOMALY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
