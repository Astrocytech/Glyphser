from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_deterministic_io_metadata_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_gate_deterministic_io_metadata_gate_passes_with_defaults(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", "def main():\n    return 0\n")
    _write(sec / "beta_gate.py", "def main():\n    return 0\n")
    policy = repo / "governance" / "security" / "security_gate_determinism_metadata_policy.json"
    _write(
        policy,
        json.dumps(
            {
                "default_deterministic_inputs": ["repo_sources"],
                "default_deterministic_outputs": ["evidence/security/<gate>.json"],
                "gate_metadata_overrides": {},
            }
        )
        + "\n",
    )

    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "POLICY", policy)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_deterministic_io_metadata_gate.main([]) == 0


def test_security_gate_deterministic_io_metadata_gate_fails_for_missing_declarations(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", "def main():\n    return 0\n")
    policy = repo / "governance" / "security" / "security_gate_determinism_metadata_policy.json"
    _write(policy, json.dumps({"gate_metadata_overrides": {}}) + "\n")

    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "POLICY", policy)
    monkeypatch.setattr(security_gate_deterministic_io_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_deterministic_io_metadata_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "security_gate_deterministic_io_metadata_gate.json").read_text(
            encoding="utf-8"
        )
    )
    assert "missing_deterministic_io_metadata:tooling/security/alpha_gate.py" in report["findings"]
