from __future__ import annotations

import json
from pathlib import Path

from tooling.security import unicode_confusable_detection_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_unicode_confusable_detection_gate_passes_ascii_paths_and_identifiers(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
        {"core": ["tooling/security/a_gate.py"], "extended": ["tooling/security/b_gate.py"]},
    )
    _write(
        repo / "governance" / "security" / "threat_model_control_map.json",
        {"controls": [{"control_id": "CTRL-001", "gate": "tooling/security/a_gate.py"}]},
    )
    (repo / "governance" / "security" / "policy.json").write_text("{}\n", encoding="utf-8")
    (repo / "tooling" / "security" / "normal_gate.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "security-normal.yml").write_text("name: normal\n", encoding="utf-8")

    monkeypatch.setattr(unicode_confusable_detection_gate, "ROOT", repo)
    monkeypatch.setattr(unicode_confusable_detection_gate, "MANIFEST", repo / "tooling/security/security_super_gate_manifest.json")
    monkeypatch.setattr(unicode_confusable_detection_gate, "CONTROL_MAP", repo / "governance/security/threat_model_control_map.json")
    monkeypatch.setattr(unicode_confusable_detection_gate, "evidence_root", lambda: repo / "evidence")
    assert unicode_confusable_detection_gate.main([]) == 0


def test_unicode_confusable_detection_gate_fails_non_ascii_filename(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
        {"core": ["tooling/security/a_gate.py"], "extended": []},
    )
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "threat_model_control_map.json").write_text('{"controls":[]}\n', encoding="utf-8")
    # Uses Cyrillic "і" instead of ASCII "i" to simulate confusable filename risk.
    (repo / "governance" / "security" / "polіcy.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(unicode_confusable_detection_gate, "ROOT", repo)
    monkeypatch.setattr(unicode_confusable_detection_gate, "MANIFEST", repo / "tooling/security/security_super_gate_manifest.json")
    monkeypatch.setattr(unicode_confusable_detection_gate, "CONTROL_MAP", repo / "governance/security/threat_model_control_map.json")
    monkeypatch.setattr(unicode_confusable_detection_gate, "evidence_root", lambda: repo / "evidence")
    assert unicode_confusable_detection_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "unicode_confusable_detection_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("filename_non_ascii:governance/security/pol") for item in report["findings"])
