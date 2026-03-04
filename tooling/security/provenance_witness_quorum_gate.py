#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.stage_s_policy import load_stage_s_policy

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_stage_s_policy()
    cfg = policy.get("provenance_witness", {})
    witness_path = ROOT / str(cfg.get("witness_file", "evidence/security/provenance_witnesses.json"))
    payload = json.loads(witness_path.read_text(encoding="utf-8")) if witness_path.exists() else {}
    witnesses = payload.get("witnesses", []) if isinstance(payload, dict) else []

    findings: list[str] = []
    unique_ids: set[str] = set()
    unique_roles: set[str] = set()
    if not isinstance(witnesses, list):
        findings.append("invalid_witnesses_list")
        witnesses = []

    for idx, item in enumerate(witnesses):
        if not isinstance(item, dict):
            findings.append(f"invalid_witness_entry:{idx}")
            continue
        wid = str(item.get("witness_id", "")).strip()
        role = str(item.get("role", "")).strip()
        if not wid:
            findings.append(f"missing_witness_id:{idx}")
        else:
            unique_ids.add(wid)
        if not role:
            findings.append(f"missing_witness_role:{idx}")
        else:
            unique_roles.add(role)

    if len(unique_ids) < int(cfg.get("minimum_unique_witnesses", 2)):
        findings.append("insufficient_witness_quorum")
    if len(unique_roles) < int(cfg.get("minimum_unique_roles", 2)):
        findings.append("insufficient_role_independence")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"unique_witnesses": len(unique_ids), "unique_roles": len(unique_roles)},
        "metadata": {"gate": "provenance_witness_quorum_gate"},
    }
    out = evidence_root() / "security" / "provenance_witness_quorum_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PROVENANCE_WITNESS_QUORUM_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
