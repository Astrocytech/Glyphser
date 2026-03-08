from __future__ import annotations

import json
from pathlib import Path

from tooling.security import temporary_waiver_gate


def test_temporary_waiver_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "temporary_waiver_policy.json").write_text(
        json.dumps(
            {
                "max_active_waivers": 2,
                "max_active_waivers_per_control_family": 1,
                "required_fields": ["id", "reason", "expires_at_utc", "owner", "control_family"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "repro").mkdir(parents=True)
    (repo / "evidence" / "repro" / "waivers.json").write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "id": "w1",
                        "reason": "x",
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                        "owner": "sec",
                        "control_family": "identity",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(temporary_waiver_gate, "ROOT", repo)
    monkeypatch.setattr(temporary_waiver_gate, "evidence_root", lambda: repo / "evidence")
    assert temporary_waiver_gate.main([]) == 0


def test_temporary_waiver_gate_fails_when_control_family_limit_exceeded(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "temporary_waiver_policy.json").write_text(
        json.dumps(
            {
                "max_active_waivers": 5,
                "max_active_waivers_per_control_family": 1,
                "required_fields": ["id", "reason", "expires_at_utc", "owner", "control_family"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "repro").mkdir(parents=True)
    (repo / "evidence" / "repro" / "waivers.json").write_text(
        json.dumps(
            {
                "waivers": [
                    {
                        "id": "w1",
                        "reason": "x",
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                        "owner": "sec",
                        "control_family": "identity",
                    },
                    {
                        "id": "w2",
                        "reason": "y",
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                        "owner": "sec",
                        "control_family": "identity",
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(temporary_waiver_gate, "ROOT", repo)
    monkeypatch.setattr(temporary_waiver_gate, "evidence_root", lambda: repo / "evidence")
    assert temporary_waiver_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "temporary_waiver_gate.json").read_text(encoding="utf-8"))
    assert "active_waivers_exceed_control_family_limit:identity:2:1" in report["findings"]
