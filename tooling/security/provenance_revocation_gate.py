#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    rev = json.loads((ROOT / "governance" / "security" / "provenance_revocation_list.json").read_text(encoding="utf-8"))
    revoked_digests = set(str(x).strip().lower() for x in rev.get("revoked_digests", []) if isinstance(x, str))
    revoked_sigs = set(str(x).strip().lower() for x in rev.get("revoked_signatures", []) if isinstance(x, str))
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked = 0
    for path in sorted(sec.glob("*.json")):
        checked += 1
        digest = _sha(path)
        if digest in revoked_digests:
            findings.append(f"revoked_digest:{path.name}")
    for path in sorted(sec.glob("*.sig")):
        checked += 1
        sig = path.read_text(encoding="utf-8").strip().lower()
        if sig in revoked_sigs:
            findings.append(f"revoked_signature:{path.name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_files": checked,
            "revoked_digests": len(revoked_digests),
            "revoked_signatures": len(revoked_sigs),
        },
        "metadata": {"gate": "provenance_revocation_gate"},
    }
    out = sec / "provenance_revocation_gate.json"
    write_json_report(out, report)
    print(f"PROVENANCE_REVOCATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
