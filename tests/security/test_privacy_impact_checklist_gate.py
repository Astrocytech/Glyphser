from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import privacy_impact_checklist_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_privacy_impact_checklist_gate_passes_when_required_fields_are_reviewed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "privacy_impact_checklist_policy.json"
    schema = repo / "governance" / "security" / "security_event_schema.json"
    checklist = repo / "governance" / "security" / "privacy_impact_checklist_telemetry.json"

    _write(policy, {"telemetry_schema_path": str(schema.relative_to(repo)), "privacy_checklist_path": str(checklist.relative_to(repo))})
    _sign(policy)
    _write(schema, {"required_fields": ["event_type", "severity"]})
    _write(
        checklist,
        {
            "approved_by": "security-team",
            "reviewed_at_utc": "2026-03-05T00:00:00+00:00",
            "reviewed_fields": ["event_type", "severity"],
        },
    )
    _sign(checklist)

    monkeypatch.setattr(privacy_impact_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(privacy_impact_checklist_gate, "POLICY", policy)
    monkeypatch.setattr(privacy_impact_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert privacy_impact_checklist_gate.main([]) == 0


def test_privacy_impact_checklist_gate_fails_when_new_field_not_reviewed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "privacy_impact_checklist_policy.json"
    schema = repo / "governance" / "security" / "security_event_schema.json"
    checklist = repo / "governance" / "security" / "privacy_impact_checklist_telemetry.json"

    _write(policy, {"telemetry_schema_path": str(schema.relative_to(repo)), "privacy_checklist_path": str(checklist.relative_to(repo))})
    _sign(policy)
    _write(schema, {"required_fields": ["event_type", "new_sensitive_field"]})
    _write(
        checklist,
        {
            "approved_by": "security-team",
            "reviewed_at_utc": "2026-03-05T00:00:00+00:00",
            "reviewed_fields": ["event_type"],
        },
    )
    _sign(checklist)

    monkeypatch.setattr(privacy_impact_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(privacy_impact_checklist_gate, "POLICY", policy)
    monkeypatch.setattr(privacy_impact_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert privacy_impact_checklist_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "privacy_impact_checklist_gate.json").read_text(encoding="utf-8"))
    assert "telemetry_field_missing_privacy_impact_review:new_sensitive_field" in report["findings"]
