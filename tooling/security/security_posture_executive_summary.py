#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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

REQUIRED_ARTIFACTS = {
    "security_super_gate": "security/security_super_gate.json",
    "security_verification_summary": "security/security_verification_summary.json",
    "security_pipeline_reliability_dashboard": "security/security_pipeline_reliability_dashboard.json",
    "security_dashboard": "security/security_dashboard.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    ev = evidence_root()
    findings: list[str] = []
    statuses: list[str] = []
    refs: list[dict[str, str | bool]] = []

    for name, rel in REQUIRED_ARTIFACTS.items():
        path = ev / rel
        relpath = str(path.relative_to(ROOT)).replace("\\", "/")
        if not path.exists():
            findings.append(f"missing_required_artifact:{name}:{relpath}")
            refs.append({"name": name, "path": relpath, "exists": False})
            statuses.append("MISSING")
            continue
        sha256 = _sha256(path)
        payload: dict[str, Any] = {}
        try:
            payload = _load_json(path)
        except Exception:
            findings.append(f"invalid_json_artifact:{name}:{relpath}")
        status = str(payload.get("status", "UNKNOWN")).upper()
        statuses.append(status)
        refs.append(
            {
                "name": name,
                "path": relpath,
                "sha256": f"sha256:{sha256}",
                "status": status,
                "exists": True,
            }
        )

    overall_status = "PASS"
    if any(status in {"FAIL", "MISSING"} for status in statuses):
        overall_status = "FAIL"
    elif any(status in {"WARN", "UNKNOWN"} for status in statuses):
        overall_status = "WARN"

    material = {"references": refs}
    references_digest = hashlib.sha256(_canonical(material).encode("utf-8")).hexdigest()
    report = {
        "status": overall_status,
        "findings": findings,
        "summary": {
            "overall_status": overall_status,
            "required_artifact_count": len(REQUIRED_ARTIFACTS),
            "resolved_artifact_count": sum(1 for item in refs if bool(item.get("exists"))),
            "machine_verifiable_reference_digest": f"sha256:{references_digest}",
        },
        "references": refs,
        "metadata": {
            "gate": "security_posture_executive_summary",
            "reference_mode": "sha256",
            "audience": "board",
        },
    }
    out = ev / "security" / "security_posture_executive_summary.json"
    write_json_report(out, report)
    board_out = ev / "security" / "security_board_posture_summary.json"
    write_json_report(board_out, report)
    print(f"SECURITY_POSTURE_EXECUTIVE_SUMMARY: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
