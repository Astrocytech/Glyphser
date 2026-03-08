from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import oncall_triage_sla_drill_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_oncall_triage_sla_drill_gate_passes_with_10_cases_within_sla(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "oncall_triage_sla_policy.json"
    drill = repo / "governance" / "security" / "oncall_triage_sla_drill.json"
    _write_json(policy, {"required_sample_size": 10, "max_triage_minutes": 30})
    _sign(policy)
    _write_json(
        drill,
        {
            "cases": [
                {
                    "failure_code": f"f{i}",
                    "triage_started_at_utc": "2026-03-05T00:00:00+00:00",
                    "triaged_at_utc": "2026-03-05T00:10:00+00:00",
                }
                for i in range(10)
            ]
        },
    )
    _sign(drill)

    monkeypatch.setattr(oncall_triage_sla_drill_gate, "ROOT", repo)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "POLICY", policy)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "DRILL", drill)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "evidence_root", lambda: repo / "evidence")
    assert oncall_triage_sla_drill_gate.main([]) == 0


def test_oncall_triage_sla_drill_gate_fails_on_sla_breach(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "oncall_triage_sla_policy.json"
    drill = repo / "governance" / "security" / "oncall_triage_sla_drill.json"
    _write_json(policy, {"required_sample_size": 1, "max_triage_minutes": 10})
    _sign(policy)
    _write_json(
        drill,
        {
            "cases": [
                {
                    "failure_code": "f1",
                    "triage_started_at_utc": "2026-03-05T00:00:00+00:00",
                    "triaged_at_utc": "2026-03-05T00:20:00+00:00",
                }
            ]
        },
    )
    _sign(drill)

    monkeypatch.setattr(oncall_triage_sla_drill_gate, "ROOT", repo)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "POLICY", policy)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "DRILL", drill)
    monkeypatch.setattr(oncall_triage_sla_drill_gate, "evidence_root", lambda: repo / "evidence")
    assert oncall_triage_sla_drill_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "oncall_triage_sla_drill_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("oncall_triage_sla_breach:") for item in report["findings"])
