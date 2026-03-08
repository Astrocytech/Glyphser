from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exception_registry_gate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_exception_registry_gate_passes_renewal_with_new_signature_and_reason_delta(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {
            "closed_exceptions": [
                {
                    "id": "EX-OLD",
                    "ticket": "SEC-1",
                    "owner": "sec",
                    "reason": "legacy reason",
                    "created_at_utc": "2026-01-01T00:00:00+00:00",
                    "expires_at_utc": "2026-02-01T00:00:00+00:00",
                    "approval_signature": "sig-old",
                }
            ],
            "exceptions": [
                {
                    "id": "EX-NEW",
                    "ticket": "SEC-2",
                    "owner": "sec",
                    "reason": "updated compensating control rationale",
                    "created_at_utc": "2026-02-15T00:00:00+00:00",
                    "expires_at_utc": "2099-01-01T00:00:00+00:00",
                    "renewal_of": "EX-OLD",
                    "approval_signature": "sig-new",
                }
            ],
        },
    )

    monkeypatch.setattr(exception_registry_gate, "ROOT", repo)
    monkeypatch.setattr(exception_registry_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        exception_registry_gate,
        "load_policy",
        lambda: {"exception_registry_path": "governance/security/temporary_exceptions.json", "max_active_exceptions": 3},
    )
    assert exception_registry_gate.main([]) == 0


def test_exception_registry_gate_fails_renewal_without_new_signature_or_reason_delta(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {
            "closed_exceptions": [
                {
                    "id": "EX-OLD",
                    "ticket": "SEC-1",
                    "owner": "sec",
                    "reason": "same reason text",
                    "created_at_utc": "2026-01-01T00:00:00+00:00",
                    "expires_at_utc": "2026-02-01T00:00:00+00:00",
                    "approval_signature": "sig-reused",
                }
            ],
            "exceptions": [
                {
                    "id": "EX-NEW",
                    "ticket": "SEC-2",
                    "owner": "sec",
                    "reason": "same reason text",
                    "created_at_utc": "2026-02-15T00:00:00+00:00",
                    "expires_at_utc": "2099-01-01T00:00:00+00:00",
                    "renewal_of": "EX-OLD",
                    "approval_signature": "sig-reused",
                }
            ],
        },
    )

    monkeypatch.setattr(exception_registry_gate, "ROOT", repo)
    monkeypatch.setattr(exception_registry_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        exception_registry_gate,
        "load_policy",
        lambda: {"exception_registry_path": "governance/security/temporary_exceptions.json", "max_active_exceptions": 3},
    )
    assert exception_registry_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "exception_registry_gate.json").read_text(encoding="utf-8"))
    assert "renewal_reuses_approval_signature:0:EX-OLD" in report["findings"]
    assert "renewal_reason_delta_missing:0:EX-OLD" in report["findings"]
