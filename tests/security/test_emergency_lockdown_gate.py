from __future__ import annotations

import json
from pathlib import Path

from tooling.security import emergency_lockdown_gate


def test_emergency_lockdown_gate_passes_for_disabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "emergency_lockdown_policy.json"
    policy.write_text(
        json.dumps(
            {
                "lockdown_enabled": False,
                "disable_publish": False,
                "disable_replay": False,
                "reason": "",
                "approved_by": "",
                "expires_at_utc": "",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    from runtime.glyphser.security.artifact_signing import current_key, sign_file

    policy.with_suffix(".json.sig").write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(emergency_lockdown_gate, "ROOT", repo)
    monkeypatch.setattr(emergency_lockdown_gate, "evidence_root", lambda: repo / "evidence")
    assert emergency_lockdown_gate.main([]) == 0
