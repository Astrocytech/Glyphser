from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_schema_strict_readiness_gate


def _write_policy(repo: Path, pct: float) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "advanced_hardening_policy.json").write_text(
        json.dumps({"schema_strict_min_migration_pct": pct}) + "\n",
        encoding="utf-8",
    )


def test_security_schema_strict_readiness_gate_passes_when_not_strict(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_policy(repo, 95.0)
    (sec / "security_schema_migration_tracker.json").write_text(
        json.dumps({"summary": {"migration_pct": 75.0}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("GLYPHSER_SECURITY_SCHEMA_STRICT", raising=False)
    monkeypatch.setattr(security_schema_strict_readiness_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_strict_readiness_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_strict_readiness_gate.main([]) == 0


def test_security_schema_strict_readiness_gate_fails_when_strict_below_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_policy(repo, 95.0)
    (sec / "security_schema_migration_tracker.json").write_text(
        json.dumps({"summary": {"migration_pct": 80.0}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_SECURITY_SCHEMA_STRICT", "1")
    monkeypatch.setattr(security_schema_strict_readiness_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_strict_readiness_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_strict_readiness_gate.main([]) == 1
    report = json.loads((sec / "security_schema_strict_readiness_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("strict_mode_blocked_by_migration_pct:") for item in report["findings"])
