from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from tooling.security import independent_verifier_profile_gate


@dataclass
class _Proc:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    exit_reason: str = "exit"


def test_independent_verifier_profile_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profile = repo / "governance" / "security" / "independent_verifier_profile.json"
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_text(
        json.dumps(
            {
                "profile_id": "read_only_verifier_v1",
                "role": "read_only_verifier",
                "allowed_commands": [
                    "python tooling/security/offline_verification_gate.py",
                    "python tooling/security/offline_verify.py --help",
                ],
                "verification_evidence_commands": [
                    "python tooling/security/offline_verify.py --help",
                ],
                "forbidden_command_patterns": [" rm ", " git push "],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(independent_verifier_profile_gate, "ROOT", repo)
    monkeypatch.setattr(independent_verifier_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(independent_verifier_profile_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(independent_verifier_profile_gate, "run_checked", lambda *args, **kwargs: _Proc(returncode=0))

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
                "verification_evidence_commands": ["python tooling/security/offline_verification_gate.py && git push"],
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


def test_independent_verifier_profile_gate_fails_when_evidence_command_execution_fails(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    profile = repo / "governance" / "security" / "independent_verifier_profile.json"
    profile.parent.mkdir(parents=True, exist_ok=True)
    cmd = "python tooling/security/offline_verify.py --help"
    profile.write_text(
        json.dumps(
            {
                "profile_id": "read_only_verifier_v1",
                "role": "read_only_verifier",
                "allowed_commands": [cmd],
                "verification_evidence_commands": [cmd],
                "forbidden_command_patterns": [" git push "],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(independent_verifier_profile_gate, "ROOT", repo)
    monkeypatch.setattr(independent_verifier_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(independent_verifier_profile_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        independent_verifier_profile_gate,
        "run_checked",
        lambda *args, **kwargs: _Proc(returncode=2, stderr="failed"),
    )

    assert independent_verifier_profile_gate.main([]) == 1
