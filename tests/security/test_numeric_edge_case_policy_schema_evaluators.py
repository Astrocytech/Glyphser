from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_report_schema_contract_gate, security_schema_compatibility_policy_gate


def _write(path: Path, raw: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw, encoding="utf-8")


def test_schema_compatibility_policy_gate_rejects_nan_inf_and_very_large_int(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_schema_compatibility_policy.json"

    _write(
        policy,
        '{"current_schema_version": NaN, "minor_change_policy":"additive_only","major_change_policy":"requires_migration_plan_and_approval","allow_optional_field_additions":true,"allow_required_field_removals":false,"allow_field_type_changes_without_major":false,"required_major_change_evidence":["adr_reference","migration_plan","approval_record"]}\n',
    )
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_compatibility_policy_gate.main([]) == 1

    _write(
        policy,
        '{"current_schema_version": Infinity, "minor_change_policy":"additive_only","major_change_policy":"requires_migration_plan_and_approval","allow_optional_field_additions":true,"allow_required_field_removals":false,"allow_field_type_changes_without_major":false,"required_major_change_evidence":["adr_reference","migration_plan","approval_record"]}\n',
    )
    assert security_schema_compatibility_policy_gate.main([]) == 1

    _write(
        policy,
        '{"current_schema_version": 999999999999, "minor_change_policy":"additive_only","major_change_policy":"requires_migration_plan_and_approval","allow_optional_field_additions":true,"allow_required_field_removals":false,"allow_field_type_changes_without_major":false,"required_major_change_evidence":["adr_reference","migration_plan","approval_record"]}\n',
    )
    assert security_schema_compatibility_policy_gate.main([]) == 1


def test_report_schema_contract_gate_rejects_numeric_edge_cases(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    contract = repo / "governance" / "security" / "security_report_schema_contract.json"
    monkeypatch.setattr(security_report_schema_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_schema_contract_gate, "CONTRACT", contract)
    monkeypatch.setattr(security_report_schema_contract_gate, "evidence_root", lambda: repo / "evidence")

    _write(
        contract,
        '{"required_fields":["status","findings","summary","metadata","schema_version"],"status_values":["PASS","FAIL","WARN"],"schema_version": NaN}\n',
    )
    assert security_report_schema_contract_gate.main([]) == 1

    _write(
        contract,
        '{"required_fields":["status","findings","summary","metadata","schema_version"],"status_values":["PASS","FAIL","WARN"],"schema_version": Infinity}\n',
    )
    assert security_report_schema_contract_gate.main([]) == 1

    _write(
        contract,
        '{"required_fields":["status","findings","summary","metadata","schema_version"],"status_values":["PASS","FAIL","WARN"],"schema_version": 999999999999}\n',
    )
    assert security_report_schema_contract_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_report_schema_contract_gate.json").read_text(encoding="utf-8"))
    assert "invalid_schema_version" in report["findings"]

