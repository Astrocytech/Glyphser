from __future__ import annotations

import json
from pathlib import Path

from tooling.security import incident_timeline_reconstruction


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_incident_timeline_reconstruction_passes_with_signed_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    _write(sec / "a_gate.json", {"status": "PASS", "metadata": {"generated_at_utc": "2026-03-05T00:00:01+00:00"}})
    (sec / "a_gate.json.sig").write_text("sig\n", encoding="utf-8")
    _write(sec / "b_gate.json", {"status": "FAIL", "metadata": {"generated_at_utc": "2026-03-05T00:00:02+00:00"}})
    (sec / "b_gate.json.sig").write_text("sig\n", encoding="utf-8")
    monkeypatch.setattr(incident_timeline_reconstruction, "ROOT", repo)
    monkeypatch.setattr(incident_timeline_reconstruction, "evidence_root", lambda: repo / "evidence")
    assert incident_timeline_reconstruction.main([]) == 0
    report = json.loads((sec / "incident_timeline_reconstruction.json").read_text(encoding="utf-8"))
    assert report["summary"]["timeline_events"] == 2
    assert report["timeline"][0]["artifact"] == "security/a_gate.json"


def test_incident_timeline_reconstruction_fails_without_signed_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    _write(sec / "a_gate.json", {"status": "PASS"})
    monkeypatch.setattr(incident_timeline_reconstruction, "ROOT", repo)
    monkeypatch.setattr(incident_timeline_reconstruction, "evidence_root", lambda: repo / "evidence")
    assert incident_timeline_reconstruction.main([]) == 1
    report = json.loads((sec / "incident_timeline_reconstruction.json").read_text(encoding="utf-8"))
    assert "no_signed_security_evidence_for_timeline" in report["findings"]
