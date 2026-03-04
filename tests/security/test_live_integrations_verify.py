from __future__ import annotations

import json
from pathlib import Path

import pytest

from tooling.security import live_integrations_verify


def test_live_integrations_verify_dry_run(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(live_integrations_verify, "evidence_root", lambda: tmp_path / "evidence")
    rc = live_integrations_verify.main(["--dry-run"])
    assert rc == 0
    payload = json.loads((tmp_path / "evidence" / "security" / "live_integrations.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["mode"] == "dry_run"
    assert "checked_at_utc" in payload


def test_live_integrations_verify_live_requires_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(live_integrations_verify, "evidence_root", lambda: tmp_path / "evidence")
    with pytest.raises(ValueError, match="missing required live integration env vars"):
        live_integrations_verify.main([])


def test_live_integrations_verify_live_rejects_placeholder_urls(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(live_integrations_verify, "evidence_root", lambda: tmp_path / "evidence")
    monkeypatch.setenv("GLYPHSER_WAF_HEALTH_URL", "https://example.com/waf")
    monkeypatch.setenv("GLYPHSER_SIEM_HEALTH_URL", "https://siem.internal/health")
    monkeypatch.setenv("GLYPHSER_PAGING_HEALTH_URL", "https://pager.internal/health")
    with pytest.raises(ValueError, match="placeholder"):
        live_integrations_verify.main([])
