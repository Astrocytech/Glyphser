#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

BASELINE = ROOT / "governance" / "security" / "executable_review_annotations.json"


def _is_executable(path: Path) -> bool:
    mode = path.stat().st_mode
    return bool(mode & 0o111)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    sig = BASELINE.with_suffix(".json.sig")
    sig_text = sig.read_text(encoding="utf-8").strip()
    if not artifact_signing.verify_file(BASELINE, sig_text, key=artifact_signing.current_key(strict=False)):
        if not artifact_signing.verify_file(BASELINE, sig_text, key=artifact_signing.bootstrap_key()):
            findings.append("invalid_executable_review_annotations_signature")

    payload = json.loads(BASELINE.read_text(encoding="utf-8"))
    paths = payload.get("security_critical_paths", []) if isinstance(payload.get("security_critical_paths"), list) else []
    approved = payload.get("approved_executables", {}) if isinstance(payload.get("approved_executables"), dict) else {}

    observed_exec: list[str] = []
    for rel_dir in paths:
        if not isinstance(rel_dir, str) or not rel_dir.strip():
            continue
        base = ROOT / rel_dir
        if not base.exists() or not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if not _is_executable(path):
                continue
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            observed_exec.append(rel)
            row = approved.get(rel)
            if not isinstance(row, dict):
                findings.append(f"new_executable_without_review_annotation:{rel}")
                continue
            annotation = str(row.get("review_annotation", "")).strip()
            if not annotation:
                findings.append(f"missing_review_annotation_for_executable:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "observed_executables": len(observed_exec),
            "approved_executables": len(approved),
        },
        "metadata": {"gate": "executable_review_annotation_gate"},
    }
    out = evidence_root() / "security" / "executable_review_annotation_gate.json"
    write_json_report(out, report)
    print(f"EXECUTABLE_REVIEW_ANNOTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
