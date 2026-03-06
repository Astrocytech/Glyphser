#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
bootstrap_key = artifact_signing.bootstrap_key
verify_file = artifact_signing.verify_file
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

MATRIX = ROOT / "governance" / "security" / "threat_control_matrix.json"
ATTESTATION = ROOT / "governance" / "security" / "metadata" / "THREAT_MODEL_CHANGE_ATTESTATION.json"
CONTROL_ID_RE = re.compile(r"CTRL-[A-Z0-9_-]+")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _critical_control_ids(matrix_payload: dict[str, Any]) -> set[str]:
    critical_gates = {str(x).strip() for x in matrix_payload.get("critical_gates", []) if isinstance(x, str)}
    out: set[str] = set()
    for item in matrix_payload.get("controls", []):
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id", "")).strip()
        gates = {str(x).strip() for x in item.get("gates", []) if isinstance(x, str)}
        if cid and gates.intersection(critical_gates):
            out.add(cid)
    return out


def _changed_control_ids() -> set[str]:
    matrix_rel = MATRIX.relative_to(ROOT).as_posix()
    proc = run_checked(["git", "diff", "--unified=0", "HEAD~1", "HEAD", "--", matrix_rel], cwd=ROOT)
    if proc.returncode != 0:
        return set()
    changed: set[str] = set()
    for line in (proc.stdout or "").splitlines():
        if not line or line[0] not in {"+", "-"}:
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        for match in CONTROL_ID_RE.findall(line):
            changed.add(match)
    return changed


def _verify_attestation_signature(path: Path, sig: Path) -> bool:
    sig_text = sig.read_text(encoding="utf-8").strip()
    if not sig_text:
        return False
    if verify_file(path, sig_text, key=current_key(strict=False)):
        return True
    return verify_file(path, sig_text, key=bootstrap_key())


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    summary: dict[str, Any] = {"required": False, "skipped": False}

    if not MATRIX.exists():
        findings.append("missing_threat_control_matrix")
    else:
        matrix = _read_json(MATRIX)
        if not isinstance(matrix, dict):
            findings.append("invalid_threat_control_matrix")
            matrix = {}
        critical_ids = _critical_control_ids(matrix)
        changed_ids = _changed_control_ids()
        impacted = sorted(changed_ids.intersection(critical_ids))
        summary.update(
            {
                "changed_controls": sorted(changed_ids),
                "critical_controls": sorted(critical_ids),
                "impacted_critical_controls": impacted,
            }
        )
        if not impacted:
            summary["skipped"] = True
        else:
            summary["required"] = True
            sig = ATTESTATION.with_suffix(".json.sig")
            if not ATTESTATION.exists():
                findings.append("missing_threat_model_change_attestation")
            elif not sig.exists():
                findings.append("missing_threat_model_change_attestation_signature")
            elif not _verify_attestation_signature(ATTESTATION, sig):
                findings.append("invalid_threat_model_change_attestation_signature")
            else:
                payload = _read_json(ATTESTATION)
                if not isinstance(payload, dict):
                    findings.append("invalid_threat_model_change_attestation_payload")
                else:
                    status = str(payload.get("status", "")).upper()
                    if status != "APPROVED":
                        findings.append("attestation_not_approved")
                    controls = {str(x).strip() for x in payload.get("changed_controls", []) if isinstance(x, str)}
                    for cid in impacted:
                        if cid not in controls:
                            findings.append(f"attestation_missing_control:{cid}")
                    approvers = payload.get("approvers", [])
                    if not isinstance(approvers, list) or not approvers:
                        findings.append("missing_attestation_approvers")
                    if not str(payload.get("rationale", "")).strip():
                        findings.append("missing_attestation_rationale")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": summary,
        "metadata": {"gate": "threat_model_change_attestation_gate"},
    }
    out = evidence_root() / "security" / "threat_model_change_attestation_gate.json"
    write_json_report(out, report)
    print(f"THREAT_MODEL_CHANGE_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
