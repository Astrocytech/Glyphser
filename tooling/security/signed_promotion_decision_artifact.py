#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

GO_NO_GO = ROOT / "evidence" / "security" / "promotion_go_no_go_report.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_list(raw: str) -> list[str]:
    text = raw.strip()
    if not text:
        return []
    try:
        payload = json.loads(text)
    except Exception:
        return [item.strip() for item in text.split(",") if item.strip()]
    if isinstance(payload, list):
        return [str(item).strip() for item in payload if str(item).strip()]
    return []


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not GO_NO_GO.exists():
        findings.append("missing_promotion_go_no_go_report")
        decision_payload: dict[str, Any] = {}
    else:
        decision_payload = _load_json(GO_NO_GO)

    go_no_go_findings = decision_payload.get("findings", []) if isinstance(decision_payload, dict) else []
    if not isinstance(go_no_go_findings, list):
        go_no_go_findings = []

    bypassed = _parse_list(os.environ.get("GLYPHSER_BYPASSED_BLOCKERS", ""))
    approval_chain = _parse_list(os.environ.get("GLYPHSER_APPROVAL_CHAIN", ""))

    unmatched = [item for item in bypassed if item not in {str(x) for x in go_no_go_findings}]
    if unmatched:
        findings.append(f"bypassed_blockers_not_in_go_no_go_report:{'|'.join(unmatched)}")
    if bypassed and len(approval_chain) < 2:
        findings.append("insufficient_approval_chain_for_bypass")

    artifact = {
        "status": "PASS" if not findings else "FAIL",
        "decision": str(((decision_payload.get("summary") or {}) if isinstance(decision_payload.get("summary"), dict) else {}).get("decision", "UNKNOWN")),
        "bypassed_blockers": bypassed,
        "approval_chain": approval_chain,
        "go_no_go_report_path": str(GO_NO_GO.relative_to(ROOT)).replace("\\", "/"),
    }
    artifact_path = evidence_root() / "security" / "promotion_decision_artifact.json"
    write_json_report(artifact_path, artifact)

    sig_path = artifact_path.with_suffix(".json.sig")
    sig = sign_file(artifact_path, key=current_key(strict=False))
    sig_path.write_text(sig + "\n", encoding="utf-8")
    if not verify_file(artifact_path, sig, key=current_key(strict=False)):
        findings.append("promotion_decision_artifact_signature_invalid")

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "decision": artifact["decision"],
            "bypassed_blockers": len(bypassed),
            "approval_chain_length": len(approval_chain),
        },
        "metadata": {"gate": "signed_promotion_decision_artifact"},
    }
    out = evidence_root() / "security" / "signed_promotion_decision_artifact_gate.json"
    write_json_report(out, gate)
    print(f"SIGNED_PROMOTION_DECISION_ARTIFACT: {gate['status']}")
    print(f"Artifact: {artifact_path}")
    print(f"Gate: {out}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
