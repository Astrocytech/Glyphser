from __future__ import annotations

import json
from pathlib import Path

from tooling.security import telemetry_completeness_sli_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_telemetry_completeness_sli_gate_passes_at_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_completeness": {
                "required_fields": ["event_type", "severity"],
                "required_fields_present_rate_threshold": 1.0,
            }
        },
    )
    _write(repo / "evidence" / "security" / "security_events.jsonl", '{"event_type":"security_gate_status","severity":"low"}\n')

    monkeypatch.setattr(telemetry_completeness_sli_gate, "ROOT", repo)
    monkeypatch.setattr(telemetry_completeness_sli_gate, "POLICY", repo / "governance/security/security_observability_policy.json")
    monkeypatch.setattr(telemetry_completeness_sli_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_completeness_sli_gate.main([]) == 0


def test_telemetry_completeness_sli_gate_fails_below_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "security_observability_policy.json",
        {
            "telemetry_completeness": {
                "required_fields": ["event_type", "severity"],
                "required_fields_present_rate_threshold": 1.0,
            }
        },
    )
    _write(repo / "evidence" / "security" / "security_events.jsonl", '{"event_type":"security_gate_status"}\n')

    monkeypatch.setattr(telemetry_completeness_sli_gate, "ROOT", repo)
    monkeypatch.setattr(telemetry_completeness_sli_gate, "POLICY", repo / "governance/security/security_observability_policy.json")
    monkeypatch.setattr(telemetry_completeness_sli_gate, "evidence_root", lambda: repo / "evidence")
    assert telemetry_completeness_sli_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "telemetry_completeness_sli_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("telemetry_completeness_below_threshold:") for item in report["findings"])
