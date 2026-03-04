#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sec = evidence_root() / "security"
    path = sec / "slsa_provenance_v1.json"
    findings: list[str] = []
    if not path.exists():
        findings.append("missing slsa_provenance_v1.json")
        att: dict[str, Any] = {}
    else:
        att = json.loads(path.read_text(encoding="utf-8"))

    if att.get("_type") != "https://in-toto.io/Statement/v1":
        findings.append("invalid statement _type")
    if att.get("predicateType") != "https://slsa.dev/provenance/v1":
        findings.append("invalid predicateType")

    subjects = att.get("subject", [])
    if not isinstance(subjects, list):
        subjects = []
    subject_map: dict[str, str] = {}
    for item in subjects:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        digest = item.get("digest", {})
        if isinstance(name, str) and isinstance(digest, dict) and isinstance(digest.get("sha256"), str):
            subject_map[name] = digest["sha256"]

    expected = {
        "evidence/security/sbom.json": _sha256(sec / "sbom.json") if (sec / "sbom.json").exists() else "",
        "evidence/security/build_provenance.json": _sha256(sec / "build_provenance.json")
        if (sec / "build_provenance.json").exists()
        else "",
    }
    for name, digest in expected.items():
        if not digest:
            findings.append(f"missing subject artifact: {name}")
            continue
        got = subject_map.get(name, "")
        if got != digest:
            findings.append(f"subject digest mismatch: {name}")

    pred = att.get("predicate", {})
    if not isinstance(pred, dict):
        findings.append("missing predicate")
        pred = {}
    run_details = pred.get("runDetails", {})
    if not isinstance(run_details, dict):
        findings.append("missing runDetails")
        run_details = {}
    builder = run_details.get("builder", {})
    if not isinstance(builder, dict) or not isinstance(builder.get("id"), str) or not builder.get("id"):
        findings.append("missing builder id")

    status = "PASS" if not findings else "FAIL"
    payload: dict[str, Any] = {
        "status": status,
        "findings": findings,
        "summary": {"subject_count": len(subject_map), "expected_subjects": len(expected)},
        "metadata": {"gate": "slsa_attestation_gate"},
    }
    out = sec / "slsa_attestation.json"
    write_json_report(out, payload)
    print(f"SLSA_ATTESTATION_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
