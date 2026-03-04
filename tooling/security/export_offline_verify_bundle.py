#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    out_dir = ROOT / str(policy.get("offline_bundle_dir", "evidence/security/offline_verify_bundle"))
    out_dir.mkdir(parents=True, exist_ok=True)
    files = [
        ROOT / "governance" / "security" / "policy_signature_manifest.json",
        ROOT / "governance" / "security" / "provenance_revocation_list.json",
        ROOT / "evidence" / "security" / "build_provenance.json",
        ROOT / "evidence" / "security" / "build_provenance.json.sig",
        ROOT / "evidence" / "security" / "sbom.json",
        ROOT / "evidence" / "security" / "sbom.json.sig",
    ]
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
        "Run policy_signature_gate.py and provenance_signature_gate.py against this bundle.\n",
        encoding="utf-8",
    )

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"bundle_dir": str(out_dir.relative_to(ROOT)).replace('\\', '/'), "exported_files": exported},
        "metadata": {"gate": "export_offline_verify_bundle"},
    }
    out = evidence_root() / "security" / "offline_verify_bundle_export.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"OFFLINE_VERIFY_BUNDLE_EXPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
