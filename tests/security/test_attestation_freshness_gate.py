from __future__ import annotations

import json
from pathlib import Path

from tooling.security import attestation_freshness_gate


def test_attestation_freshness_gate_passes_for_fresh_required_artifacts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    for name in ["a.sig", "b.sig", "c.sig"]:
        (sec / name).write_text("sig\n", encoding="utf-8")

    monkeypatch.setattr(attestation_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(attestation_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        attestation_freshness_gate,
        "load_policy",
        lambda: {
            "max_attestation_age_hours": 168,
            "required_attestation_files": [
                "evidence/security/a.sig",
                "evidence/security/b.sig",
                "evidence/security/c.sig",
            ],
        },
    )
    assert attestation_freshness_gate.main([]) == 0


def test_attestation_freshness_gate_fails_on_missing_artifact(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.sig").write_text("sig\n", encoding="utf-8")
    monkeypatch.setattr(attestation_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(attestation_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        attestation_freshness_gate,
        "load_policy",
        lambda: {
            "max_attestation_age_hours": 168,
            "required_attestation_files": ["evidence/security/a.sig", "evidence/security/missing.sig"],
        },
    )
    assert attestation_freshness_gate.main([]) == 1
    payload = json.loads((sec / "attestation_freshness_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_attestation:") for item in payload["findings"])


def test_attestation_freshness_gate_fails_on_clock_consistency_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.sig").write_text("sig\n", encoding="utf-8")

    monkeypatch.setattr(attestation_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(attestation_freshness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        attestation_freshness_gate,
        "load_policy",
        lambda: {
            "max_attestation_age_hours": 168,
            "required_attestation_files": ["evidence/security/a.sig"],
        },
    )
    monkeypatch.setattr(
        attestation_freshness_gate,
        "clock_consistency_violation",
        lambda _now: "clock_consistency_violation:wall_vs_monotonic_drift_seconds:9.000:tolerance_seconds:5.000",
    )
    assert attestation_freshness_gate.main([]) == 1
    payload = json.loads((sec / "attestation_freshness_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("clock_consistency_violation:") for item in payload["findings"])
