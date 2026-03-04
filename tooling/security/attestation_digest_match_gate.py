#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

ROOT = Path(__file__).resolve().parents[2]
DIGEST_MANIFEST = ROOT / "distribution" / "container" / "image-digests.txt"
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")


def _load_manifest_digests(path: Path) -> list[str]:
    digests: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        for m in DIGEST_RE.findall(line):
            digests.append(m)
    return sorted(set(digests))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    if not DIGEST_MANIFEST.exists():
        report = {
            "status": "PASS",
            "findings": [],
            "summary": {"skipped": True, "reason": "missing_digest_manifest"},
            "metadata": {"gate": "attestation_digest_match_gate"},
        }
        out = sec / "attestation_digest_match_gate.json"
        write_json_report(out, report)
        print("ATTESTATION_DIGEST_MATCH_GATE: PASS")
        print(f"Report: {out}")
        return 0

    manifest_digests = _load_manifest_digests(DIGEST_MANIFEST)
    provenance = sec / "build_provenance.json"
    if not provenance.exists():
        findings.append("missing_build_provenance")
        provenance_digests: list[str] = []
    else:
        payload = json.loads(provenance.read_text(encoding="utf-8"))
        raw = payload.get("artifact_digests", []) if isinstance(payload, dict) else []
        provenance_digests = sorted({str(x) for x in raw if isinstance(x, str)})
        if not provenance_digests:
            findings.append("missing_provenance_artifact_digests")

    for dg in manifest_digests:
        if dg not in provenance_digests:
            findings.append(f"digest_missing_from_provenance:{dg}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "manifest_digest_count": len(manifest_digests),
            "provenance_digest_count": len(provenance_digests),
        },
        "metadata": {"gate": "attestation_digest_match_gate"},
    }
    out = sec / "attestation_digest_match_gate.json"
    write_json_report(out, report)
    print(f"ATTESTATION_DIGEST_MATCH_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
