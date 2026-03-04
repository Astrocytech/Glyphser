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
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _as_required(policy: dict[str, object]) -> list[str]:
    raw = policy.get("security_workflow_evidence_required", [])
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        name = item.strip()
        if not name:
            continue
        if name.startswith("evidence/security/"):
            name = name.removeprefix("evidence/security/")
        out.append(name)
    return sorted(set(out))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    policy = load_policy()
    required = _as_required(policy)
    manifest_path = sec / "upload_manifest.json"
    sig_path = sec / "upload_manifest.json.sig"
    findings: list[str] = []
    manifest: dict[str, object] = {}

    if not manifest_path.exists():
        findings.append("missing_upload_manifest")
    else:
        try:
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                manifest = parsed
            else:
                findings.append("invalid_upload_manifest")
        except Exception:
            findings.append("invalid_upload_manifest")
    if not sig_path.exists():
        findings.append("missing_upload_manifest_signature")
    elif manifest_path.exists():
        sig = sig_path.read_text(encoding="utf-8").strip()
        if not sig or not verify_file(manifest_path, sig, key=current_key(strict=False)):
            findings.append("upload_manifest_signature_mismatch")

    listed = manifest.get("summary", {}).get("artifacts", []) if isinstance(manifest.get("summary", {}), dict) else []
    if not isinstance(listed, list):
        listed = []
    listed_names = {str(x) for x in listed if isinstance(x, str)}
    for rel in required:
        if rel not in listed_names:
            findings.append(f"manifest_missing_required_artifact:{rel}")
        if not (sec / rel).exists():
            findings.append(f"required_artifact_missing_on_disk:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_artifacts": required,
            "listed_artifacts": sorted(listed_names),
            "required_count": len(required),
            "listed_count": len(listed_names),
        },
        "metadata": {"gate": "upload_manifest_completeness_gate"},
    }
    out = sec / "upload_manifest_completeness_gate.json"
    write_json_report(out, report)
    print(f"UPLOAD_MANIFEST_COMPLETENESS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
