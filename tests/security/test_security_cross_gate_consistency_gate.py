from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_cross_gate_consistency_gate


def test_security_cross_gate_consistency_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "security_super_gate.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "results": [
                    {"cmd": ["python", "tooling/security/workflow_risky_patterns_gate.py"], "status": "PASS"}
                ],
                "metadata": {"generated_at_utc": "2026-01-01T00:00:00+00:00"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "workflow_risky_patterns_gate.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 0


def test_security_cross_gate_consistency_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "security_super_gate.json").write_text(
        json.dumps(
            {"results": [{"cmd": ["python", "tooling/security/workflow_risky_patterns_gate.py"], "status": "PASS"}]}
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "workflow_risky_patterns_gate.json").write_text('{"status":"FAIL"}\n', encoding="utf-8")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 1


def test_security_cross_gate_consistency_gate_fails_when_policy_pass_lacks_verified_files(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True, exist_ok=True)
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/a.json"]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate.json").write_text('{"results":[]}\n', encoding="utf-8")
    (sec / "policy_signature.json").write_text(
        json.dumps({"status": "PASS", "checks": {"governance/security/a.json": {"ok": False}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_cross_gate_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 1
    report = json.loads((sec / "security_cross_gate_consistency_gate.json").read_text(encoding="utf-8"))
    assert "policy_pass_missing_verified_file:governance/security/a.json" in report["findings"]


def test_security_cross_gate_consistency_gate_fails_when_provenance_pass_has_invalid_signature(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    artifact = sec / "sbom.json"
    signature = sec / "sbom.json.sig"
    artifact.write_text("{}\n", encoding="utf-8")
    signature.write_text("not-a-valid-signature\n", encoding="utf-8")
    (sec / "security_super_gate.json").write_text('{"results":[]}\n', encoding="utf-8")
    (sec / "provenance_signature.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "checks": {
                    "sbom": {
                        "ok": True,
                        "artifact": "evidence/security/sbom.json",
                        "signature": "evidence/security/sbom.json.sig",
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_cross_gate_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "current_key", lambda strict=False: b"test-key")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "verify_file", lambda *args, **kwargs: False)
    assert security_cross_gate_consistency_gate.main([]) == 1
    report = json.loads((sec / "security_cross_gate_consistency_gate.json").read_text(encoding="utf-8"))
    assert "provenance_pass_hash_or_signature_mismatch:sbom" in report["findings"]


def test_security_cross_gate_consistency_gate_fails_when_super_status_disagrees_with_components(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "security_super_gate.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "results": [
                    {"cmd": ["python", "tooling/security/workflow_risky_patterns_gate.py"], "status": "FAIL"}
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "workflow_risky_patterns_gate.json").write_text('{"status":"FAIL"}\n', encoding="utf-8")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 1
    report = json.loads((sec / "security_cross_gate_consistency_gate.json").read_text(encoding="utf-8"))
    assert "super_gate_status_component_mismatch:expected:FAIL:actual:PASS" in report["findings"]


def test_security_cross_gate_consistency_gate_fails_on_stale_timestamp_skew(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    gov.mkdir(parents=True, exist_ok=True)
    (gov / "security_cross_report_consistency_policy.json").write_text(
        json.dumps({"max_timestamp_skew_seconds": 60, "related_reports": ["security_super_gate.json", "policy_signature.json"]})
        + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate.json").write_text(
        json.dumps({"status": "PASS", "results": [], "metadata": {"generated_at_utc": "2026-01-01T00:00:00+00:00"}}) + "\n",
        encoding="utf-8",
    )
    (sec / "policy_signature.json").write_text(
        json.dumps({"status": "PASS", "checks": {}, "metadata": {"generated_at_utc": "2026-01-01T00:10:00+00:00"}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_cross_gate_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_cross_gate_consistency_gate,
        "POLICY",
        gov / "security_cross_report_consistency_policy.json",
    )
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 1
    report = json.loads((sec / "security_cross_gate_consistency_gate.json").read_text(encoding="utf-8"))
    assert "stale_timestamp_skew:600>60" in report["findings"]
