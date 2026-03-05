from __future__ import annotations

import json
from pathlib import Path

from tooling.security import codeowners_security_coverage_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_codeowners_security_coverage_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "review_policy.json",
        {"required_codeowners_paths": ["/tooling/security/**", "/.github/workflows/**"]},
    )
    _write(
        repo / ".github" / "CODEOWNERS",
        "/tooling/security/** @sec\n/.github/workflows/** @sec\n",
    )

    monkeypatch.setattr(codeowners_security_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(codeowners_security_coverage_gate, "POLICY", repo / "governance/security/review_policy.json")
    monkeypatch.setattr(codeowners_security_coverage_gate, "CODEOWNERS", repo / ".github/CODEOWNERS")
    monkeypatch.setattr(codeowners_security_coverage_gate, "evidence_root", lambda: repo / "evidence")

    assert codeowners_security_coverage_gate.main([]) == 0


def test_codeowners_security_coverage_gate_fails_on_missing_critical_path(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "review_policy.json",
        {"required_codeowners_paths": ["/tooling/security/**", "/.github/workflows/**"]},
    )
    _write(repo / ".github" / "CODEOWNERS", "/tooling/security/** @sec\n")

    monkeypatch.setattr(codeowners_security_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(codeowners_security_coverage_gate, "POLICY", repo / "governance/security/review_policy.json")
    monkeypatch.setattr(codeowners_security_coverage_gate, "CODEOWNERS", repo / ".github/CODEOWNERS")
    monkeypatch.setattr(codeowners_security_coverage_gate, "evidence_root", lambda: repo / "evidence")

    assert codeowners_security_coverage_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "codeowners_security_coverage_gate.json").read_text(encoding="utf-8"))
    assert "missing_codeowners_coverage:/.github/workflows/**" in report["findings"]
