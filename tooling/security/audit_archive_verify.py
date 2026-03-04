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
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _is_safe_member(base: Path, member_name: str) -> bool:
    target = (base / member_name).resolve()
    return str(target).startswith(str(base.resolve()) + str(Path("/")))


def _extract_archive_safely(archive: Path, extract: Path, *, expected_member: str) -> list[str]:
    findings: list[str] = []
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        names = [m.name for m in members]
        if expected_member not in names:
            findings.append(f"missing_expected_member:{expected_member}")
        for member in members:
            if member.islnk() or member.issym():
                findings.append(f"disallowed_link_member:{member.name}")
                continue
            if member.ischr() or member.isblk() or member.isfifo() or member.isdev():
                findings.append(f"disallowed_special_member:{member.name}")
                continue
            if not _is_safe_member(extract, member.name):
                findings.append(f"unsafe_tar_member:{member.name}")
                continue
            try:
                tf.extract(member, extract, filter="data")
            except TypeError:
                tf.extract(member, extract)
    return findings


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    log = ROOT / "artifacts" / "generated" / "tmp" / "security" / "audit.log.jsonl"
    archive = sec / "audit-log-archive.tar.gz"
    extract = sec / "audit-restore-check"
    findings: list[str] = []
    sec.mkdir(parents=True, exist_ok=True)

    if not log.exists():
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("", encoding="utf-8")

    with tarfile.open(archive, "w:gz") as tf:
        tf.add(log, arcname="audit.log.jsonl")

    if extract.exists():
        shutil.rmtree(extract)
    extract.mkdir(parents=True, exist_ok=True)
    findings.extend(_extract_archive_safely(archive, extract, expected_member="audit.log.jsonl"))
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
    write_json_report(out, report)
    print(f"AUDIT_ARCHIVE_VERIFY: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
