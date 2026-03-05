#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _status(path: Path) -> str:
    return str(_load_json(path).get("status", "MISSING")).upper()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    signal_reports = {
        "security_super_gate": _status(sec / "security_super_gate.json"),
        "provenance_signature": _status(sec / "provenance_signature.json"),
        "evidence_attestation_gate": _status(sec / "evidence_attestation_gate.json"),
        "rolling_merkle_checkpoints": _status(sec / "rolling_merkle_checkpoints.json"),
    }
    missing_signals = sorted(name for name, status in signal_reports.items() if status == "MISSING")
    if missing_signals:
        findings.append(f"missing_signals:{','.join(missing_signals)}")

    failed_signals = sorted(name for name, status in signal_reports.items() if status == "FAIL")
    if failed_signals:
        findings.append(f"failed_signals:{','.join(failed_signals)}")

    detection_window = "< 1 release workflow run"
    if missing_signals:
        detection_window = "unknown (missing prerequisite signals)"

    blast_radius = "run-scoped evidence bundle"
    if failed_signals:
        blast_radius = "potential multi-stage release evidence impact"

    trust_assumptions = [
        "GitHub-hosted runner integrity and isolation assumptions hold for each job",
        "Repository and workflow definitions are branch-protected and reviewed",
        "Signing key material (GLYPHSER_PROVENANCE_HMAC_KEY) remains confidential",
        "Uploaded artifacts preserve byte integrity between build and verify consumption",
    ]

    report = {
        "status": "PASS" if not failed_signals else "FAIL",
        "findings": findings,
        "summary": {
            "time_to_detect": {
                "window": detection_window,
                "basis": [
                    "release verify-signatures lane reruns provenance + attestation gates",
                    "security_super_gate consolidates prerequisite gate outcomes",
                ],
            },
            "blast_radius": {
                "scope": blast_radius,
                "max_affected_scope": "release run evidence and promotion decision chain",
            },
            "required_trust_assumptions": trust_assumptions,
            "signal_statuses": signal_reports,
        },
        "metadata": {"gate": "tamper_cost_model_report"},
    }
    out = sec / "tamper_cost_model_report.json"
    write_json_report(out, report)
    print(f"TAMPER_COST_MODEL_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
