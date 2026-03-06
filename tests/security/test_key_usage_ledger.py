from __future__ import annotations

import json
from pathlib import Path

from tooling.security import key_usage_ledger


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_signature_reports(sec: Path, *, fallback_used: bool) -> None:
    key_provenance = {"key_id": "k1", "adapter": "hmac", "source": "env", "fallback_used": fallback_used}
    _write(sec / "policy_signature.json", {"status": "PASS", "metadata": {"key_provenance": key_provenance}})
    _write(sec / "provenance_signature.json", {"status": "PASS", "metadata": {"key_provenance": key_provenance}})
    _write(sec / "evidence_attestation_index.json", {"status": "PASS", "key_provenance": key_provenance})
    _write(sec / "evidence_attestation_gate.json", {"status": "PASS", "metadata": {"key_provenance": key_provenance}})


def test_key_usage_ledger_passes_with_complete_signature_key_provenance(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _seed_signature_reports(sec, fallback_used=False)

    monkeypatch.setattr(key_usage_ledger, "ROOT", repo)
    monkeypatch.setattr(key_usage_ledger, "evidence_root", lambda: repo / "evidence")
    assert key_usage_ledger.main([]) == 0

    report = json.loads((sec / "key_usage_ledger.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["ledger_entries"] == 4
    assert report["summary"]["fallback_entries"] == 0
    assert all(item["gate"] for item in report["ledger"])


def test_key_usage_ledger_fails_when_signature_report_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _seed_signature_reports(sec, fallback_used=True)
    (sec / "provenance_signature.json").unlink()

    monkeypatch.setattr(key_usage_ledger, "ROOT", repo)
    monkeypatch.setattr(key_usage_ledger, "evidence_root", lambda: repo / "evidence")
    assert key_usage_ledger.main([]) == 1

    report = json.loads((sec / "key_usage_ledger.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_signature_report:provenance_signature_gate:") for item in report["findings"])
