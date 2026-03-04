from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_super_extended_compare_gate


def test_super_extended_compare_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps(
            {
                "results": [
                    {"cmd": ["python", "tooling/security/a.py"], "status": "FAIL"},
                    {"cmd": ["python", "tooling/security/b.py"], "status": "PASS"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 0


def test_super_extended_compare_gate_fails_on_unknown_failure(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    sec = repo / "tooling" / "security"
    ev.mkdir(parents=True)
    sec.mkdir(parents=True)
    (ev / "security_super_gate.json").write_text(
        json.dumps({"results": [{"cmd": ["python", "tooling/security/unknown.py"], "status": "FAIL"}]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a.py"], "extended": ["tooling/security/b.py"]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_extended_compare_gate, "SUPER_REPORT", ev / "security_super_gate.json")
    monkeypatch.setattr(
        security_super_extended_compare_gate,
        "MANIFEST",
        sec / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(security_super_extended_compare_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_extended_compare_gate.main([]) == 1
