from __future__ import annotations

import json
from pathlib import Path

from tooling.security import evidence_chain_of_custody


def test_chain_of_custody_build_and_verify_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    (ev / "security").mkdir(parents=True)
    (ev / "conformance").mkdir(parents=True)
    (ev / "security" / "a.json").write_text('{"a":1}\n', encoding="utf-8")
    (ev / "conformance" / "b.json").write_text('{"b":1}\n', encoding="utf-8")

    monkeypatch.setattr(evidence_chain_of_custody, "ROOT", repo)
    monkeypatch.setattr(evidence_chain_of_custody, "evidence_root", lambda: ev)
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "unit-test-key")

    assert evidence_chain_of_custody.main([]) == 0
    assert evidence_chain_of_custody.main(["--verify"]) == 0


def test_chain_of_custody_verify_fails_on_tamper(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    (ev / "security").mkdir(parents=True)
    p = ev / "security" / "a.json"
    p.write_text('{"a":1}\n', encoding="utf-8")

    monkeypatch.setattr(evidence_chain_of_custody, "ROOT", repo)
    monkeypatch.setattr(evidence_chain_of_custody, "evidence_root", lambda: ev)
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "unit-test-key")

    assert evidence_chain_of_custody.main([]) == 0
    p.write_text('{"a":2}\n', encoding="utf-8")
    assert evidence_chain_of_custody.main(["--verify"]) == 1
    report = json.loads((ev / "security" / "evidence_chain_of_custody_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"


def test_chain_of_custody_verify_fails_on_duplicate_sequence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    (ev / "security").mkdir(parents=True)
    (ev / "security" / "a.json").write_text('{"a":1}\n', encoding="utf-8")
    (ev / "security" / "b.json").write_text('{"b":1}\n', encoding="utf-8")

    monkeypatch.setattr(evidence_chain_of_custody, "ROOT", repo)
    monkeypatch.setattr(evidence_chain_of_custody, "evidence_root", lambda: ev)
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "unit-test-key")

    assert evidence_chain_of_custody.main([]) == 0
    idx = ev / "security" / "evidence_chain_of_custody.json"
    payload = json.loads(idx.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    assert isinstance(items, list) and len(items) >= 2
    first_seq = items[0]["seq"]
    items[1]["seq"] = first_seq
    idx.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert evidence_chain_of_custody.main(["--verify"]) == 1
    report = json.loads((ev / "security" / "evidence_chain_of_custody_gate.json").read_text(encoding="utf-8"))
    assert "duplicate_sequence_id" in report.get("findings", [])
