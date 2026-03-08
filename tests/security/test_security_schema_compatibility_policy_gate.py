from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_schema_compatibility_policy_gate


def test_security_schema_compatibility_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "security_schema_compatibility_policy.json"
    pol.parent.mkdir(parents=True)
    pol.write_text(
        json.dumps(
            {
                "current_schema_version": 1,
                "minor_change_policy": "additive_only",
                "major_change_policy": "requires_migration_plan_and_approval",
                "allow_optional_field_additions": True,
                "allow_required_field_removals": False,
                "allow_field_type_changes_without_major": False,
                "required_major_change_evidence": ["adr_reference", "migration_plan", "approval_record"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "POLICY", pol)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_compatibility_policy_gate.main([]) == 0


def test_security_schema_compatibility_policy_gate_fails_on_invalid_policy(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "security_schema_compatibility_policy.json"
    pol.parent.mkdir(parents=True)
    pol.write_text(
        json.dumps({"current_schema_version": 0, "required_major_change_evidence": ["migration_plan"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "POLICY", pol)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_compatibility_policy_gate.main([]) == 1
