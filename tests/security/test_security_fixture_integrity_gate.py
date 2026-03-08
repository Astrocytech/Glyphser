from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import security_fixture_integrity_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_security_fixture_integrity_gate_passes_with_matching_hashes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fixture = repo / "tests" / "security" / "corpus" / "sample.json"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text('{"ok": true}\n', encoding="utf-8")

    baseline = repo / "governance" / "security" / "security_fixture_integrity_baseline.json"
    payload = {
        "monitored_roots": ["tests/security/corpus"],
        "allowed_extensions": [".json"],
        "fixtures": [{"path": "tests/security/corpus/sample.json", "sha256": security_fixture_integrity_gate._sha256(fixture)}],
    }
    _write_json(baseline, payload)
    _sign(baseline)

    monkeypatch.setattr(security_fixture_integrity_gate, "ROOT", repo)
    monkeypatch.setattr(security_fixture_integrity_gate, "BASELINE", baseline)
    monkeypatch.setattr(security_fixture_integrity_gate, "evidence_root", lambda: repo / "evidence")
    assert security_fixture_integrity_gate.main([]) == 0


def test_security_fixture_integrity_gate_fails_on_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    fixture = repo / "tests" / "security" / "corpus" / "sample.json"
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text('{"ok": true}\n', encoding="utf-8")

    baseline = repo / "governance" / "security" / "security_fixture_integrity_baseline.json"
    payload = {
        "monitored_roots": ["tests/security/corpus"],
        "allowed_extensions": [".json"],
        "fixtures": [{"path": "tests/security/corpus/sample.json", "sha256": "0" * 64}],
    }
    _write_json(baseline, payload)
    _sign(baseline)

    monkeypatch.setattr(security_fixture_integrity_gate, "ROOT", repo)
    monkeypatch.setattr(security_fixture_integrity_gate, "BASELINE", baseline)
    monkeypatch.setattr(security_fixture_integrity_gate, "evidence_root", lambda: repo / "evidence")
    assert security_fixture_integrity_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_fixture_integrity_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("tampered_fixture_hash_mismatch:") for item in report["findings"])
