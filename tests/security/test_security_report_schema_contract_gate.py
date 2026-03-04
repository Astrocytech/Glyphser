from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_report_schema_contract_gate


def test_security_report_schema_contract_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract = repo / "governance" / "security" / "security_report_schema_contract.json"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_fields": ["status", "findings", "summary", "metadata", "schema_version"],
                "status_values": ["PASS", "FAIL", "WARN"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_report_schema_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_schema_contract_gate, "CONTRACT", contract)
    monkeypatch.setattr(security_report_schema_contract_gate, "evidence_root", lambda: repo / "evidence")

    assert security_report_schema_contract_gate.main([]) == 0


def test_security_report_schema_contract_gate_fails_with_missing_values(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract = repo / "governance" / "security" / "security_report_schema_contract.json"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(json.dumps({"schema_version": 0}) + "\n", encoding="utf-8")

    monkeypatch.setattr(security_report_schema_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_schema_contract_gate, "CONTRACT", contract)
    monkeypatch.setattr(security_report_schema_contract_gate, "evidence_root", lambda: repo / "evidence")

    assert security_report_schema_contract_gate.main([]) == 1
