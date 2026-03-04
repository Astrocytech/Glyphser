from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_super_gate_membership_guard_gate


def test_membership_guard_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps(
            {
                "core": ["tooling/security/a.py"],
                "extended": ["tooling/security/b.py"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (gov / "security_super_gate_membership_baseline.json").write_text(
        json.dumps(
            {
                "required_core": ["tooling/security/a.py"],
                "required_extended": ["tooling/security/b.py"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_gate_membership_guard_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_super_gate_membership_guard_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(
        security_super_gate_membership_guard_gate,
        "BASELINE",
        gov / "security_super_gate_membership_baseline.json",
    )
    monkeypatch.setattr(security_super_gate_membership_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_gate_membership_guard_gate.main([]) == 0


def test_membership_guard_gate_fails_on_missing_required_entries(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": [], "extended": []}) + "\n",
        encoding="utf-8",
    )
    (gov / "security_super_gate_membership_baseline.json").write_text(
        json.dumps(
            {
                "required_core": ["tooling/security/a.py"],
                "required_extended": ["tooling/security/b.py"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_gate_membership_guard_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_super_gate_membership_guard_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(
        security_super_gate_membership_guard_gate,
        "BASELINE",
        gov / "security_super_gate_membership_baseline.json",
    )
    monkeypatch.setattr(security_super_gate_membership_guard_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_gate_membership_guard_gate.main([]) == 1
