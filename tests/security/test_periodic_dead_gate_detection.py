from __future__ import annotations

import json
from pathlib import Path

from tooling.security import periodic_dead_gate_detection


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_periodic_dead_gate_detection_passes_when_all_gates_wired_and_recent(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec_dir = repo / "tooling" / "security"
    wf = repo / ".github" / "workflows"
    _write(sec_dir / "alpha_gate.py", "def main(argv=None):\n    return 0\n")
    _write(wf / "ci.yml", "jobs:\n  x:\n    steps:\n      - run: python tooling/security/alpha_gate.py\n")
    state = repo / "evidence" / "security" / "periodic_dead_gate_detection_state.json"
    _write(state, json.dumps({"last_scan_utc": "2026-03-01T00:00:00+00:00"}))
    monkeypatch.setattr(periodic_dead_gate_detection, "ROOT", repo)
    monkeypatch.setattr(periodic_dead_gate_detection, "SECURITY_DIR", sec_dir)
    monkeypatch.setattr(periodic_dead_gate_detection, "WORKFLOW_DIR", wf)
    monkeypatch.setattr(periodic_dead_gate_detection, "STATE", state)
    monkeypatch.setattr(periodic_dead_gate_detection, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert periodic_dead_gate_detection.main([]) == 0


def test_periodic_dead_gate_detection_fails_when_scan_is_stale(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec_dir = repo / "tooling" / "security"
    wf = repo / ".github" / "workflows"
    _write(sec_dir / "alpha_gate.py", "def main(argv=None):\n    return 0\n")
    _write(wf / "ci.yml", "jobs:\n  x:\n    steps:\n      - run: python tooling/security/alpha_gate.py\n")
    state = repo / "evidence" / "security" / "periodic_dead_gate_detection_state.json"
    _write(state, json.dumps({"last_scan_utc": "2025-01-01T00:00:00+00:00"}))
    monkeypatch.setattr(periodic_dead_gate_detection, "ROOT", repo)
    monkeypatch.setattr(periodic_dead_gate_detection, "SECURITY_DIR", sec_dir)
    monkeypatch.setattr(periodic_dead_gate_detection, "WORKFLOW_DIR", wf)
    monkeypatch.setattr(periodic_dead_gate_detection, "STATE", state)
    monkeypatch.setattr(periodic_dead_gate_detection, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert periodic_dead_gate_detection.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "periodic_dead_gate_detection.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("dead_gate_periodic_scan_stale:") for item in report["findings"])
