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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
bootstrap_key = artifact_signing.bootstrap_key
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MANIFEST = ROOT / "governance" / "security" / "policy_signature_manifest.json"
REGISTRY = ROOT / "governance" / "security" / "policy_deprecation_registry.json"
TOMBSTONES = ROOT / "governance" / "security" / "policy_tombstone_changelog.json"


def _parse_iso(text: str) -> datetime | None:
    raw = str(text).strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _verify_tombstone_signature(path: Path, sig_path: Path) -> tuple[bool, str]:
    if not sig_path.exists():
        return False, "missing_tombstone_changelog_signature"
    signature = sig_path.read_text(encoding="utf-8").strip()
    if not signature:
        return False, "empty_tombstone_changelog_signature"
    try:
        key = current_key(strict=False)
    except Exception as exc:
        key = None
        err = str(exc)
    else:
        err = ""
    if key is not None and verify_file(path, signature, key=key):
        return True, "ok"
    if verify_file(path, signature, key=bootstrap_key()):
        return True, "ok_bootstrap_key"
    if err:
        return False, f"tombstone_changelog_signature_verification_error:{err}"
    return False, "invalid_tombstone_changelog_signature"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    manifest_payload = _load_json(MANIFEST)
    manifest_entries = manifest_payload.get("policies", []) if isinstance(manifest_payload, dict) else []
    manifest_set: set[str] = {
        str(item).strip() for item in manifest_entries if isinstance(item, str) and str(item).strip()
    }

    if not TOMBSTONES.exists():
        findings.append("missing_policy_tombstone_changelog")
        tombstones: list[dict[str, Any]] = []
    else:
        sig_ok, sig_reason = _verify_tombstone_signature(TOMBSTONES, TOMBSTONES.with_suffix(".json.sig"))
        if not sig_ok:
            findings.append(sig_reason)
        changelog = _load_json(TOMBSTONES)
        raw_tombstones = changelog.get("tombstones", []) if isinstance(changelog, dict) else []
        tombstones = [item for item in raw_tombstones if isinstance(item, dict)] if isinstance(raw_tombstones, list) else []
        if str(changelog.get("schema_version", "")).strip() != "glyphser-policy-tombstones.v1":
            findings.append("invalid_policy_tombstone_schema_version")

    tombstoned_policies: set[str] = set()
    for idx, entry in enumerate(tombstones):
        policy = str(entry.get("policy", "")).strip()
        removed_utc = _parse_iso(entry.get("removed_utc", ""))
        reason = str(entry.get("reason", "")).strip()
        if not policy:
            findings.append(f"invalid_tombstone_policy:{idx}")
            continue
        if removed_utc is None:
            findings.append(f"invalid_tombstone_removed_utc:{policy}")
        if not reason:
            findings.append(f"missing_tombstone_reason:{policy}")
        if policy in tombstoned_policies:
            findings.append(f"duplicate_tombstone_entry:{policy}")
        tombstoned_policies.add(policy)
        if policy in manifest_set:
            findings.append(f"tombstoned_policy_still_in_manifest:{policy}")

    registry_payload = _load_json(REGISTRY)
    raw_deprecations = registry_payload.get("deprecations", []) if isinstance(registry_payload, dict) else []
    deprecations = [item for item in raw_deprecations if isinstance(item, dict)] if isinstance(raw_deprecations, list) else []

    removed_candidates = 0
    for entry in deprecations:
        policy = str(entry.get("policy", "")).strip()
        if not policy:
            continue
        policy_path = ROOT / policy
        if policy_path.exists():
            continue
        removed_candidates += 1
        if policy not in tombstoned_policies:
            findings.append(f"missing_tombstone_for_removed_policy:{policy}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_policies": len(manifest_set),
            "tombstone_entries": len(tombstoned_policies),
            "removed_policies_from_registry": removed_candidates,
        },
        "metadata": {"gate": "policy_tombstone_changelog_gate"},
    }
    out = evidence_root() / "security" / "policy_tombstone_changelog_gate.json"
    write_json_report(out, report)
    print(f"POLICY_TOMBSTONE_CHANGELOG_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
