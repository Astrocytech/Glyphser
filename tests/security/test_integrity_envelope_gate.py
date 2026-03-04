from __future__ import annotations

import json
from pathlib import Path

from tooling.security import integrity_envelope_gate


def _mk(path: Path) -> None:
    path.write_text('{"status":"PASS"}\n', encoding="utf-8")


def test_integrity_envelope_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in integrity_envelope_gate.LINKED_REPORTS:
        _mk(sec / name)
    monkeypatch.setattr(integrity_envelope_gate, "ROOT", repo)
    monkeypatch.setattr(integrity_envelope_gate, "evidence_root", lambda: repo / "evidence")
    assert integrity_envelope_gate.main([]) == 0
    assert (sec / integrity_envelope_gate.ENVELOPE).exists()
    assert (sec / integrity_envelope_gate.ENVELOPE_SIG).exists()


def test_integrity_envelope_gate_fails_when_link_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _mk(sec / "policy_signature.json")
    _mk(sec / "provenance_signature.json")
    monkeypatch.setattr(integrity_envelope_gate, "ROOT", repo)
    monkeypatch.setattr(integrity_envelope_gate, "evidence_root", lambda: repo / "evidence")
    assert integrity_envelope_gate.main([]) == 1
    payload = json.loads((sec / "integrity_envelope_gate.json").read_text("utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_linked_report:") for item in payload["findings"])
