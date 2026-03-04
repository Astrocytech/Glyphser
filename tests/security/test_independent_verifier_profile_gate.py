from __future__ import annotations

import json
from pathlib import Path

from tooling.security import independent_verifier_profile_gate


def test_independent_verifier_profile_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profile = repo / "governance" / "security" / "independent_verifier_profile.json"
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_text(
        json.dumps(
            {
                "profile_id": "read_only_verifier_v1",
                "role": "read_only_verifier",
                "allowed_commands": ["python tooling/security/offline_verification_gate.py"],
                "forbidden_command_patterns": [" rm ", " git push "],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(independent_verifier_profile_gate, "ROOT", repo)
    monkeypatch.setattr(independent_verifier_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(independent_verifier_profile_gate, "evidence_root", lambda: repo / "evidence")

    assert independent_verifier_profile_gate.main([]) == 0
    report = json.loads(
        (repo / "evidence" / "security" / "independent_verifier_profile_gate.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "PASS"


def test_independent_verifier_profile_gate_fails_for_forbidden_command(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profile = repo / "governance" / "security" / "independent_verifier_profile.json"
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_text(
        json.dumps(
            {
                "profile_id": "read_only_verifier_v1",
                "role": "read_only_verifier",
                "allowed_commands": ["python tooling/security/offline_verification_gate.py && git push"],
                "forbidden_command_patterns": [" git push "],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(independent_verifier_profile_gate, "ROOT", repo)
    monkeypatch.setattr(independent_verifier_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(independent_verifier_profile_gate, "evidence_root", lambda: repo / "evidence")

    assert independent_verifier_profile_gate.main([]) == 1
