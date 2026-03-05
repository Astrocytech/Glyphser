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

CONTRACT = ROOT / "governance" / "security" / "external_artifact_trust_contract.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _list_of_nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not CONTRACT.exists():
        findings.append("missing_external_artifact_trust_contract")
        payload: dict[str, Any] = {}
    else:
        try:
            payload = _load_json(CONTRACT)
        except Exception:
            payload = {}
            findings.append("invalid_external_artifact_trust_contract")

    for field in ("contract_id", "owner", "reviewed_at_utc"):
        if not str(payload.get(field, "")).strip():
            findings.append(f"missing_field:{field}")

    if not _list_of_nonempty_strings(payload.get("accepted_repositories")):
        findings.append("invalid_accepted_repositories")
    if not _list_of_nonempty_strings(payload.get("required_attestations")):
        findings.append("invalid_required_attestations")
    if not isinstance(payload.get("required_signer_identity_match"), bool):
        findings.append("invalid_required_signer_identity_match")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "accepted_repositories": len(payload.get("accepted_repositories", []))
            if isinstance(payload.get("accepted_repositories"), list)
            else 0,
            "required_attestations": len(payload.get("required_attestations", []))
            if isinstance(payload.get("required_attestations"), list)
            else 0,
        },
        "metadata": {"gate": "external_artifact_trust_contract_gate"},
    }
    out = evidence_root() / "security" / "external_artifact_trust_contract_gate.json"
    write_json_report(out, report)
    print(f"EXTERNAL_ARTIFACT_TRUST_CONTRACT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
