from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import retention_legal_hold_exception_report


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_retention_legal_hold_exception_report_passes_with_signed_active_approvals(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    src = repo / "governance" / "security" / "retention_legal_hold_exceptions.json"
    _write(
        src,
        {
            "exceptions": [
                {
                    "exception_id": "lh-1",
                    "artifact_scope": "evidence/security/*",
                    "reason": "regulatory hold",
                    "approved_by": "security-team",
                    "approved_at_utc": "2026-03-05T00:00:00+00:00",
                    "expires_at_utc": "2026-12-31T00:00:00+00:00",
                    "approval_ticket": "SEC-LEGAL-1",
                }
            ]
        },
    )
    _sign(src)

    monkeypatch.setattr(retention_legal_hold_exception_report, "ROOT", repo)
    monkeypatch.setattr(retention_legal_hold_exception_report, "EXCEPTIONS", src)
    monkeypatch.setattr(retention_legal_hold_exception_report, "evidence_root", lambda: repo / "evidence")
    assert retention_legal_hold_exception_report.main([]) == 0


def test_retention_legal_hold_exception_report_fails_for_unsigned_or_invalid_entries(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    src = repo / "governance" / "security" / "retention_legal_hold_exceptions.json"
    _write(
        src,
        {
            "exceptions": [
                {
                    "exception_id": "lh-2",
                    "artifact_scope": "evidence/security/*",
                    "reason": "expired hold",
                    "approved_by": "",
                    "approved_at_utc": "bad-ts",
                    "expires_at_utc": "2020-01-01T00:00:00+00:00",
                    "approval_ticket": "",
                }
            ]
        },
    )
    src.with_suffix(".json.sig").write_text("bad-signature\n", encoding="utf-8")

    monkeypatch.setattr(retention_legal_hold_exception_report, "ROOT", repo)
    monkeypatch.setattr(retention_legal_hold_exception_report, "EXCEPTIONS", src)
    monkeypatch.setattr(retention_legal_hold_exception_report, "evidence_root", lambda: repo / "evidence")
    assert retention_legal_hold_exception_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "retention_legal_hold_exception_report.json").read_text(encoding="utf-8"))
    assert "invalid_retention_legal_hold_exceptions_signature" in report["findings"]
