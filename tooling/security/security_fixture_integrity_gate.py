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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

BASELINE = ROOT / "governance" / "security" / "security_fixture_integrity_baseline.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _collect_fixture_files(monitored_roots: list[str], allowed_extensions: set[str]) -> set[str]:
    collected: set[str] = set()
    for rel_root in monitored_roots:
        root_path = ROOT / rel_root
        if not root_path.exists() or not root_path.is_dir():
            continue
        for path in sorted(root_path.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if allowed_extensions and path.suffix not in allowed_extensions:
                continue
            collected.add(str(path.relative_to(ROOT)).replace("\\", "/"))
    return collected


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not BASELINE.exists():
        findings.append("missing_security_fixture_integrity_baseline")
        payload: dict[str, object] = {}
    else:
        payload = json.loads(BASELINE.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_security_fixture_integrity_baseline")
            payload = {}

    sig = BASELINE.with_suffix(".json.sig")
    if not sig.exists():
        findings.append("missing_security_fixture_integrity_baseline_signature")
    else:
        sig_text = sig.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(BASELINE, sig_text, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(BASELINE, sig_text, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_security_fixture_integrity_baseline_signature")

    raw_rows = payload.get("fixtures", [])
    monitored_roots = [str(x) for x in payload.get("monitored_roots", []) if isinstance(x, str) and str(x).strip()]
    allowed_extensions = {str(x) for x in payload.get("allowed_extensions", []) if isinstance(x, str) and str(x).strip()}

    fixture_rows: list[dict[str, str]] = []
    expected_paths: set[str] = set()
    if not isinstance(raw_rows, list):
        findings.append("invalid_security_fixture_integrity_rows")
        raw_rows = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        rel = str(row.get("path", "")).strip()
        digest = str(row.get("sha256", "")).strip().lower()
        if not rel or len(digest) != 64:
            findings.append("invalid_security_fixture_integrity_row")
            continue
        fixture_rows.append({"path": rel, "sha256": digest})
        expected_paths.add(rel)

    observed_paths = _collect_fixture_files(monitored_roots, allowed_extensions)
    for rel in sorted(observed_paths - expected_paths):
        findings.append(f"undeclared_fixture_file:{rel}")
    for rel in sorted(expected_paths - observed_paths):
        findings.append(f"missing_fixture_file:{rel}")

    for row in fixture_rows:
        rel = row["path"]
        expected = row["sha256"]
        path = ROOT / rel
        if not path.exists() or not path.is_file():
            continue
        actual = _sha256(path)
        if actual != expected:
            findings.append(f"tampered_fixture_hash_mismatch:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "baseline_entries": len(fixture_rows),
            "observed_fixture_files": len(observed_paths),
            "monitored_roots": monitored_roots,
        },
        "metadata": {"gate": "security_fixture_integrity_gate"},
    }
    out = evidence_root() / "security" / "security_fixture_integrity_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_FIXTURE_INTEGRITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
