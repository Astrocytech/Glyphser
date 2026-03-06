from __future__ import annotations

import json
from pathlib import Path

from tooling.security import canonical_json_cross_os_artifact_hash_gate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _seed_targets(base: Path, *, drift_file: str | None = None) -> None:
    for filename in canonical_json_cross_os_artifact_hash_gate.TARGET_FILENAMES:
        payload = {"status": "PASS", "filename": filename, "k": 1}
        if filename == drift_file:
            payload["k"] = 2
        _write_json(base / "nested" / filename, payload)


def test_canonical_json_cross_os_artifact_hash_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    left = repo / "parity" / "linux"
    right = repo / "parity" / "macos"
    _seed_targets(left)
    _seed_targets(right)
    monkeypatch.setattr(canonical_json_cross_os_artifact_hash_gate, "ROOT", repo)
    monkeypatch.setattr(canonical_json_cross_os_artifact_hash_gate, "evidence_root", lambda: repo / "evidence")
    assert canonical_json_cross_os_artifact_hash_gate.main(["--left-dir", str(left), "--right-dir", str(right)]) == 0


def test_canonical_json_cross_os_artifact_hash_gate_fails_on_hash_drift(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    left = repo / "parity" / "linux"
    right = repo / "parity" / "macos"
    _seed_targets(left)
    _seed_targets(right, drift_file="security_event_schema_gate.json")
    monkeypatch.setattr(canonical_json_cross_os_artifact_hash_gate, "ROOT", repo)
    monkeypatch.setattr(canonical_json_cross_os_artifact_hash_gate, "evidence_root", lambda: repo / "evidence")
    assert canonical_json_cross_os_artifact_hash_gate.main(["--left-dir", str(left), "--right-dir", str(right)]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "canonical_json_cross_os_artifact_hash_gate.json").read_text(encoding="utf-8")
    )
    assert "canonical_json_hash_mismatch:security_event_schema_gate.json" in report["findings"]
