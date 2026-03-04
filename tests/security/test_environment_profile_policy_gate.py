from __future__ import annotations

import json
from pathlib import Path

from tooling.security import environment_profile_policy_gate


def test_environment_profile_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "environment_profile_policy.json"
    pol.parent.mkdir(parents=True)
    pol.write_text(
        json.dumps(
            {
                "profiles": {
                    "dev": {
                        "require_strict_key": False,
                        "require_signed_attestations": False,
                        "allow_policy_fallbacks": True,
                    },
                    "ci": {
                        "require_strict_key": True,
                        "require_signed_attestations": True,
                        "allow_policy_fallbacks": False,
                    },
                },
                "inheritance_order": ["dev", "ci"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(environment_profile_policy_gate, "ROOT", repo)
    monkeypatch.setattr(environment_profile_policy_gate, "POLICY", pol)
    monkeypatch.setattr(environment_profile_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert environment_profile_policy_gate.main([]) == 0


def test_environment_profile_policy_gate_fails_on_weakened_inheritance(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "environment_profile_policy.json"
    pol.parent.mkdir(parents=True)
    pol.write_text(
        json.dumps(
            {
                "profiles": {
                    "dev": {
                        "require_strict_key": True,
                        "require_signed_attestations": True,
                        "allow_policy_fallbacks": False,
                    },
                    "ci": {
                        "require_strict_key": False,
                        "require_signed_attestations": False,
                        "allow_policy_fallbacks": True,
                    },
                },
                "inheritance_order": ["dev", "ci"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(environment_profile_policy_gate, "ROOT", repo)
    monkeypatch.setattr(environment_profile_policy_gate, "POLICY", pol)
    monkeypatch.setattr(environment_profile_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert environment_profile_policy_gate.main([]) == 1
