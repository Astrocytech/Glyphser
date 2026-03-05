from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_retention_policy_gate


def test_security_retention_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "storage_location": "immutable://glyphser-security-evidence",
                "retention_class": "long_term",
                "legal_hold_supported": True,
                "manifest_required": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_retention_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_retention_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_retention_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_retention_policy_gate.main([]) == 0


def test_security_retention_policy_gate_fails_for_missing_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(json.dumps({"storage_location": ""}) + "\n", encoding="utf-8")

    monkeypatch.setattr(security_retention_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_retention_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_retention_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_retention_policy_gate.main([]) == 1


def test_security_retention_policy_gate_fails_when_legal_hold_not_supported(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "storage_location": "immutable://glyphser-security-evidence",
                "retention_class": "long_term",
                "legal_hold_supported": False,
                "manifest_required": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_retention_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_retention_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_retention_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_retention_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_retention_policy_gate.json").read_text("utf-8"))
    assert "legal_hold_must_be_supported" in report["findings"]


def test_security_retention_policy_gate_fails_when_retention_not_archive_grade(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "storage_location": "immutable://glyphser-security-evidence",
                "retention_class": "short",
                "legal_hold_supported": True,
                "manifest_required": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_retention_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_retention_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_retention_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_retention_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_retention_policy_gate.json").read_text("utf-8"))
    assert "unsupported_retention_class:short" in report["findings"]
