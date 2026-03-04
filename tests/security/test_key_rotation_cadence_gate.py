from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import key_rotation_cadence_gate


def test_key_rotation_cadence_gate_passes_with_signed_recent_record(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "key_management_policy.json"
    policy.write_text(
        json.dumps(
            {
                "maximum_rotation_age_days": 90,
                "rotation_record_path": "governance/security/key_rotation_record.json",
                "require_signed_rotation_record": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    record = gov / "key_rotation_record.json"
    record.write_text(
        json.dumps({"key_id": "kid", "rotated_at_utc": "2026-03-01T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )
    record.with_suffix(".json.sig").write_text(sign_file(record, key=current_key(strict=False)) + "\n", encoding="utf-8")

    monkeypatch.setattr(key_rotation_cadence_gate, "ROOT", repo)
    monkeypatch.setattr(key_rotation_cadence_gate, "evidence_root", lambda: repo / "evidence")
    assert key_rotation_cadence_gate.main([]) == 0


def test_key_rotation_cadence_gate_fails_on_old_or_unsigned_record(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (gov / "key_management_policy.json").write_text(
        json.dumps(
            {
                "maximum_rotation_age_days": 1,
                "rotation_record_path": "governance/security/key_rotation_record.json",
                "require_signed_rotation_record": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (gov / "key_rotation_record.json").write_text(
        json.dumps({"key_id": "kid", "rotated_at_utc": "2020-01-01T00:00:00+00:00"}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(key_rotation_cadence_gate, "ROOT", repo)
    monkeypatch.setattr(key_rotation_cadence_gate, "evidence_root", lambda: repo / "evidence")
    assert key_rotation_cadence_gate.main([]) == 1
