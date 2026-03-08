from __future__ import annotations

import json
from pathlib import Path

from tooling.security import algorithm_deprecation_rehearsal_lane


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_algorithm_deprecation_rehearsal_lane_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(sec / "policy_signature.json", {"metadata": {"key_provenance": {"adapter": "hmac"}}})
    _write(sec / "provenance_signature.json", {"metadata": {"key_provenance": {"adapter": "hmac"}}})
    _write(sec / "evidence_attestation_index.json", {"key_provenance": {"adapter": "kms"}})
    monkeypatch.setattr(algorithm_deprecation_rehearsal_lane, "ROOT", repo)
    monkeypatch.setattr(algorithm_deprecation_rehearsal_lane, "evidence_root", lambda: repo / "evidence")
    assert algorithm_deprecation_rehearsal_lane.main([]) == 0
    report = json.loads((sec / "algorithm_deprecation_rehearsal_lane.json").read_text(encoding="utf-8"))
    assert report["summary"]["simulated_failures"] == 3


def test_algorithm_deprecation_rehearsal_lane_fails_without_inputs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "evidence" / "security").mkdir(parents=True)
    monkeypatch.setattr(algorithm_deprecation_rehearsal_lane, "ROOT", repo)
    monkeypatch.setattr(algorithm_deprecation_rehearsal_lane, "evidence_root", lambda: repo / "evidence")
    assert algorithm_deprecation_rehearsal_lane.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "algorithm_deprecation_rehearsal_lane.json").read_text(encoding="utf-8")
    )
    assert "no_signing_adapters_available_for_rehearsal" in report["findings"]
