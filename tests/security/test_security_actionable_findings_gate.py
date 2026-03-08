from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_actionable_findings_gate


def _metadata(extra: str = "") -> str:
    base = '"gate_version":"1.0.0","execution_context":{"lane":"unit"}'
    if extra:
        return "{" + base + "," + extra + "}"
    return "{" + base + "}"


def test_security_actionable_findings_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text('{"status":"PASS","findings":[]}\n', encoding="utf-8")
    (sec / "b.json").write_text(
        '{"status":"FAIL","findings":["code_one:detail","code_two:item"],"summary":{"finding_count":2},"metadata":'
        + _metadata()
        + "}\n",
        encoding="utf-8",
    )
    (sec / "c.json").write_text(
        '{"status":"WARN","findings":["warn_code:detail"],"summary":{"finding_count":1},"metadata":'
        + _metadata('"downgrade_rationale":"tracked risk accepted","downgrade_expiry":"2030-01-01"')
        + "}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 0


def test_security_actionable_findings_gate_fails_on_missing_codes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "b.json").write_text(
        '{"status":"FAIL","findings":["bad finding"],"summary":{"finding_count":1},"metadata":'
        + _metadata()
        + "}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("non_actionable_finding:") for item in payload["findings"])


def test_security_actionable_findings_gate_fails_on_invalid_reason_code(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "b.json").write_text(
        '{"status":"FAIL","findings":["Bad Code:detail"],"summary":{"finding_count":1},"metadata":'
        + _metadata()
        + "}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("invalid_reason_code:") for item in payload["findings"])


def test_security_actionable_findings_gate_fails_warn_without_downgrade_metadata(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "w.json").write_text(
        '{"status":"WARN","findings":["warn_code:detail"],"summary":{"finding_count":1},"metadata":'
        + _metadata()
        + "}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_warn_downgrade_rationale:") for item in payload["findings"])
    assert any(str(item).startswith("missing_or_invalid_warn_downgrade_expiry:") for item in payload["findings"])


def test_security_actionable_findings_gate_fails_when_summary_finding_count_mismatch(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "b.json").write_text(
        '{"status":"FAIL","findings":["code_one:detail","code_two:detail"],"summary":{"finding_count":1},"metadata":'
        + _metadata()
        + "}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("summary_finding_count_mismatch:") for item in payload["findings"])


def test_security_actionable_findings_gate_fails_when_metadata_missing_gate_version_or_execution_context(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "b.json").write_text(
        '{"status":"FAIL","findings":["code_one:detail"],"summary":{"finding_count":1},"metadata":{}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_gate_version:") for item in payload["findings"])
    assert any(str(item).startswith("missing_execution_context:") for item in payload["findings"])
