from __future__ import annotations

import json
from pathlib import Path

from tooling.security import live_integrations_verify


def test_live_integrations_verify_dry_run(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(live_integrations_verify, "evidence_root", lambda: tmp_path / "evidence")
    rc = live_integrations_verify.main(["--dry-run"])
    assert rc == 0
    payload = json.loads((tmp_path / "evidence" / "security" / "live_integrations.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
