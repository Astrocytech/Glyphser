from __future__ import annotations

import json
from pathlib import Path

from tooling.security import temporary_waiver_gate


def test_temporary_waiver_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "temporary_waiver_policy.json").write_text(
        json.dumps({"max_active_waivers": 2, "required_fields": ["id", "reason", "expires_at_utc", "owner"]}) + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "repro").mkdir(parents=True)
    (repo / "evidence" / "repro" / "waivers.json").write_text(
        json.dumps({"waivers": [{"id": "w1", "reason": "x", "expires_at_utc": "2099-01-01T00:00:00+00:00", "owner": "sec"}]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(temporary_waiver_gate, "ROOT", repo)
    monkeypatch.setattr(temporary_waiver_gate, "evidence_root", lambda: repo / "evidence")
    assert temporary_waiver_gate.main([]) == 0
