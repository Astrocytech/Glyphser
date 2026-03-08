from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_super_gate_manifest_gate


def test_security_super_gate_manifest_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["alpha.py"], "extended": ["beta.py"]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate.py").write_text("alpha.py\nbeta.py\n", encoding="utf-8")
    monkeypatch.setattr(security_super_gate_manifest_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate_manifest_gate, "MANIFEST", sec / "security_super_gate_manifest.json")
    monkeypatch.setattr(security_super_gate_manifest_gate, "SUPER_GATE", sec / "security_super_gate.py")
    monkeypatch.setattr(security_super_gate_manifest_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_gate_manifest_gate.main([]) == 0


def test_security_super_gate_manifest_gate_fails_on_missing_entry(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["alpha.py"], "extended": ["beta.py"]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate.py").write_text("alpha.py\n", encoding="utf-8")
    monkeypatch.setattr(security_super_gate_manifest_gate, "ROOT", repo)
    monkeypatch.setattr(security_super_gate_manifest_gate, "MANIFEST", sec / "security_super_gate_manifest.json")
    monkeypatch.setattr(security_super_gate_manifest_gate, "SUPER_GATE", sec / "security_super_gate.py")
    monkeypatch.setattr(security_super_gate_manifest_gate, "evidence_root", lambda: repo / "evidence")
    assert security_super_gate_manifest_gate.main([]) == 1
    report = json.loads((ev / "security_super_gate_manifest_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_extended_snippet:") for item in report["findings"])
