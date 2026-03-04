#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

audit = importlib.import_module("runtime.glyphser.security.audit")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    log = ROOT / "artifacts" / "generated" / "tmp" / "security" / "audit.log.jsonl"
    archive = sec / "audit-log-archive.tar.gz"
    extract = sec / "audit-restore-check"
    findings: list[str] = []

    if not log.exists():
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("", encoding="utf-8")

    with tarfile.open(archive, "w:gz") as tf:
        tf.add(log, arcname="audit.log.jsonl")

    if extract.exists():
        shutil.rmtree(extract)
    extract.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(extract)
    restored = extract / "audit.log.jsonl"
    result = audit.verify_chain(restored)
    if str(result.get("status", "FAIL")).upper() != "PASS":
        findings.append("restored_audit_chain_invalid")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"archive": str(archive.relative_to(ROOT)).replace("\\", "/")},
        "metadata": {"gate": "audit_archive_verify"},
    }
    out = sec / "audit_archive_verify.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"AUDIT_ARCHIVE_VERIFY: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
