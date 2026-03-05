from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_event_export


def test_security_event_export_emits_events_for_fail_and_warn(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "a.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    (sec / "b.json").write_text(json.dumps({"status": "WARN"}) + "\n", encoding="utf-8")
    (sec / "c.json").write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "incident_response_policy.json").write_text(
        json.dumps({"alert_routing_test": {"primary_contact": "oncall@example.test"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_RUN_ID", "run-1")
    monkeypatch.setenv("GLYPHSER_OPERATOR_ID", "alice.operator")
    monkeypatch.setenv("GLYPHSER_OPERATOR_PSEUDONYM_KEY", "test-pseudonym-key")
    monkeypatch.setattr(security_event_export, "ROOT", repo)
    monkeypatch.setattr(security_event_export, "INCIDENT_POLICY", repo / "governance/security/incident_response_policy.json")
    monkeypatch.setattr(security_event_export, "evidence_root", lambda: repo / "evidence")
    assert security_event_export.main([]) == 0
    lines = (sec / "security_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    event = json.loads(lines[0])
    event2 = json.loads(lines[1])
    assert event["api_contract_version"] == "v1"
    assert event["event_type"] == "security_gate_status"
    assert event["pager_channel"] == "oncall@example.test"
    assert event["operator_id_pseudonym"].startswith("op_")
    assert event2["operator_id_pseudonym"] == event["operator_id_pseudonym"]
    assert "alice.operator" not in json.dumps(event, sort_keys=True)
