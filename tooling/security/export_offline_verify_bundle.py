#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    contract_version = "v1"
    policy = load_policy()
    out_dir = ROOT / str(policy.get("offline_bundle_dir", "evidence/security/offline_verify_bundle"))
    out_dir.mkdir(parents=True, exist_ok=True)
    payloads = [
        ROOT / "governance" / "security" / "policy_signature_manifest.json",
        ROOT / "governance" / "security" / "provenance_revocation_list.json",
        ROOT / "evidence" / "security" / "build_provenance.json",
        ROOT / "evidence" / "security" / "sbom.json",
        ROOT / "evidence" / "security" / "evidence_chain_of_custody.json",
    ]
    files: list[Path] = []
    for payload in payloads:
        files.append(payload)
        files.append(payload.with_suffix(payload.suffix + ".sig"))
    findings: list[str] = []
    exported: list[str] = []
    for src in files:
        if not src.exists():
            findings.append(f"missing_source:{src}")
            continue
        dst = out_dir / src.name
        dst.write_bytes(src.read_bytes())
        exported.append(src.name)

    verify = out_dir / "VERIFY.txt"
    verify.write_text(
        "Run: python tooling/security/offline_verify.py --bundle-dir <this-dir>\n",
        encoding="utf-8",
    )
    exported.append(verify.name)

    manifest_path = out_dir / "export_manifest.json"
    manifest_payload = {
        "schema_version": 1,
        "api_contract_version": contract_version,
        "package": "offline_verify_bundle",
        "files": [{"name": name, "sha256": _sha256(out_dir / name)} for name in sorted(exported)],
        "generator": "tooling/security/export_offline_verify_bundle.py",
    }
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    strict_signing = str(os.environ.get("GLYPHSER_STRICT_SIGNING", "")).strip().lower() in {"1", "true", "yes"}
    key = current_key(strict=strict_signing)
    manifest_sig = sign_file(manifest_path, key=key)
    manifest_sig_path = manifest_path.with_suffix(".json.sig")
    manifest_sig_path.write_text(manifest_sig + "\n", encoding="utf-8")
    if not verify_file(manifest_path, manifest_sig, key=key):
        findings.append("export_manifest_signature_verification_failed")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "bundle_dir": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
            "exported_files": sorted(exported),
            "manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
            "manifest_signature": str(manifest_sig_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "export_offline_verify_bundle", "api_contract_version": contract_version},
    }
    out = evidence_root() / "security" / "offline_verify_bundle_export.json"
    write_json_report(out, report)
    print(f"OFFLINE_VERIFY_BUNDLE_EXPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
