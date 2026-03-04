#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import importlib
from pathlib import Path
from typing import Any

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "governance" / "security" / "container_provenance_policy.json"
_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")


def _manifest_digests(path: Path) -> list[str]:
    digests: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        for match in _DIGEST_RE.findall(line):
            digests.add(match)
    return sorted(digests)


def _emit(status: str, findings: list[str], summary: dict[str, Any]) -> int:
    payload = {
        "status": status,
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "container_registry_provenance_gate"},
    }
    out = evidence_root() / "security" / "container_registry_provenance_gate.json"
    write_json_report(out, payload)
    print(f"CONTAINER_REGISTRY_PROVENANCE_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy_payload = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy_payload, dict):
        raise ValueError("invalid container provenance policy")

    env_enabled = os.environ.get("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "").strip().lower()
    publishing_enabled = bool(policy_payload.get("container_publishing_enabled", False))
    if env_enabled in {"1", "true", "yes"}:
        publishing_enabled = True
    elif env_enabled in {"0", "false", "no"}:
        publishing_enabled = False

    digest_manifest_rel = str(policy_payload.get("container_digest_manifest", "")).strip()
    digest_manifest = ROOT / digest_manifest_rel
    verification_rel = os.environ.get(
        "GLYPHSER_CONTAINER_REGISTRY_VERIFY_REPORT",
        "distribution/container/registry-provenance-verify.json",
    ).strip()
    verification_report = ROOT / verification_rel

    if not publishing_enabled:
        return _emit(
            "PASS",
            [],
            {
                "skipped": True,
                "reason": "container_publishing_disabled",
                "verification_report": verification_rel,
            },
        )

    findings: list[str] = []
    manifest_digests: list[str] = []
    if not digest_manifest.exists():
        findings.append(f"missing_digest_manifest:{digest_manifest_rel}")
    else:
        manifest_digests = _manifest_digests(digest_manifest)
        if not manifest_digests:
            findings.append("digest_manifest_has_no_valid_digests")

    if not verification_report.exists():
        findings.append(f"missing_registry_verification_report:{verification_rel}")
        report_payload: dict[str, Any] = {}
    else:
        report_payload = json.loads(verification_report.read_text(encoding="utf-8"))
        if not isinstance(report_payload, dict):
            findings.append("invalid_registry_verification_report")
            report_payload = {}

    reported_digests_raw = report_payload.get("verified_digests", [])
    reported_digests = sorted({str(x) for x in reported_digests_raw if isinstance(x, str)})
    if verification_report.exists():
        status = str(report_payload.get("status", "")).upper()
        if status != "PASS":
            findings.append("registry_verification_status_not_pass")
        if not reported_digests:
            findings.append("registry_verification_missing_verified_digests")

    for digest in manifest_digests:
        if digest not in reported_digests:
            findings.append(f"digest_not_verified_by_registry:{digest}")

    return _emit(
        "PASS" if not findings else "FAIL",
        findings,
        {
            "skipped": False,
            "publish_mode": True,
            "digest_manifest": digest_manifest_rel,
            "verification_report": verification_rel,
            "manifest_digest_count": len(manifest_digests),
            "verified_digest_count": len(reported_digests),
        },
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
