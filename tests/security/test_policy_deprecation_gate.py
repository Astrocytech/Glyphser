from __future__ import annotations

import json
from pathlib import Path

from tooling.security import policy_deprecation_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_policy_deprecation_gate_passes_with_future_sunset(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "policy_deprecation_registry.json",
        {
            "deprecations": [
                {
                    "policy": "p.json",
                    "sunset_date_utc": "2099-01-01T00:00:00+00:00",
                    "replacement_controls": ["new-control"],
                    "migration_evidence": [],
                }
            ]
        },
    )

    monkeypatch.setattr(policy_deprecation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_deprecation_gate, "REGISTRY", repo / "governance" / "security" / "policy_deprecation_registry.json")
    monkeypatch.setattr(policy_deprecation_gate, "evidence_root", lambda: ev)

    assert policy_deprecation_gate.main([]) == 0


def test_policy_deprecation_gate_fails_when_past_sunset_without_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "policy_deprecation_registry.json",
        {
            "deprecations": [
                {
                    "policy": "p.json",
                    "sunset_date_utc": "2000-01-01T00:00:00+00:00",
                    "replacement_controls": ["new-control"],
                    "migration_evidence": [],
                }
            ]
        },
    )

    monkeypatch.setattr(policy_deprecation_gate, "ROOT", repo)
    monkeypatch.setattr(policy_deprecation_gate, "REGISTRY", repo / "governance" / "security" / "policy_deprecation_registry.json")
    monkeypatch.setattr(policy_deprecation_gate, "evidence_root", lambda: ev)

    assert policy_deprecation_gate.main([]) == 1
    report = json.loads((ev / "security" / "policy_deprecation_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("missing_migration_evidence_post_sunset:") for item in report["findings"])
