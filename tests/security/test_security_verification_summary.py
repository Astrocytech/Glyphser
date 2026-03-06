from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import security_verification_summary


def _write(path: Path, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": status, "findings": [], "summary": {}, "metadata": {}}) + "\n", encoding="utf-8")


def test_security_verification_summary_passes_and_is_signed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "key_provenance_continuity_gate.json",
        "signature_algorithm_policy_gate.json",
        "security_unsigned_json_gate.json",
    ]:
        _write(sec / name, "PASS")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "strict-env-key")
    monkeypatch.setattr(security_verification_summary, "ROOT", repo)
    monkeypatch.setattr(security_verification_summary, "evidence_root", lambda: repo / "evidence")
    assert security_verification_summary.main([]) == 0
    report = sec / "security_verification_summary.json"
    sig = sec / "security_verification_summary.json.sig"
    assert report.exists() and sig.exists()
    assert verify_file(report, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False))
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["summary"]["verification_mode"] == "non_strict"
    assert payload["metadata"]["verification_mode"] == "non_strict"


def test_security_verification_summary_fails_when_required_check_is_non_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "policy_signature.json", "FAIL")
    _write(sec / "provenance_signature.json", "PASS")
    _write(sec / "evidence_attestation_gate.json", "PASS")
    _write(sec / "key_provenance_continuity_gate.json", "PASS")
    _write(sec / "signature_algorithm_policy_gate.json", "PASS")
    _write(sec / "security_unsigned_json_gate.json", "PASS")
    monkeypatch.setattr(security_verification_summary, "ROOT", repo)
    monkeypatch.setattr(security_verification_summary, "evidence_root", lambda: repo / "evidence")
    assert security_verification_summary.main([]) == 1
    payload = json.loads((sec / "security_verification_summary.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("non_pass_required_verification:policy_signature") for item in payload["findings"])


def test_security_verification_summary_strict_mode_is_explicit(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    for name in [
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "key_provenance_continuity_gate.json",
        "signature_algorithm_policy_gate.json",
        "security_unsigned_json_gate.json",
    ]:
        _write(sec / name, "PASS")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "strict-env-key")
    monkeypatch.setattr(security_verification_summary, "ROOT", repo)
    monkeypatch.setattr(security_verification_summary, "evidence_root", lambda: repo / "evidence")
    assert security_verification_summary.main(["--strict-key"]) == 0
    payload = json.loads((sec / "security_verification_summary.json").read_text(encoding="utf-8"))
    assert payload["summary"]["verification_mode"] == "strict"
    assert payload["metadata"]["verification_mode"] == "strict"
