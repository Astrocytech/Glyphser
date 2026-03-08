from __future__ import annotations

import json
from pathlib import Path

from tooling.security import conformance_security_coupling_gate


def test_coupling_gate_passes_when_conformance_and_security_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    (ev / "conformance" / "results").mkdir(parents=True)
    (ev / "security").mkdir(parents=True)
    (ev / "conformance" / "results" / "latest.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    (ev / "security" / "evidence_attestation_gate.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    (ev / "security" / "policy_signature.json").write_text('{"status":"PASS"}\n', encoding="utf-8")

    monkeypatch.setattr(conformance_security_coupling_gate, "ROOT", repo)
    monkeypatch.setattr(conformance_security_coupling_gate, "evidence_root", lambda: ev)
    assert conformance_security_coupling_gate.main([]) == 0


def test_coupling_gate_fails_when_conformance_passes_and_security_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    (ev / "conformance" / "results").mkdir(parents=True)
    (ev / "security").mkdir(parents=True)
    (ev / "conformance" / "results" / "latest.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    (ev / "security" / "evidence_attestation_gate.json").write_text('{"status":"FAIL"}\n', encoding="utf-8")
    (ev / "security" / "policy_signature.json").write_text('{"status":"PASS"}\n', encoding="utf-8")

    monkeypatch.setattr(conformance_security_coupling_gate, "ROOT", repo)
    monkeypatch.setattr(conformance_security_coupling_gate, "evidence_root", lambda: ev)
    assert conformance_security_coupling_gate.main([]) == 1
    report = json.loads((ev / "security" / "conformance_security_coupling.json").read_text(encoding="utf-8"))
    assert "conformance_pass_but_security_attestation_failed" in report["findings"]
