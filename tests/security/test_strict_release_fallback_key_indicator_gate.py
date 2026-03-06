from __future__ import annotations

import json
from pathlib import Path

from tooling.security import strict_release_fallback_key_indicator_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_strict_release_fallback_key_indicator_gate_passes_without_fallback_indicators(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "fallback_secret_usage_policy.json",
        {"fallback_literal": "glyphser-provenance-hmac-fallback-v1"},
    )
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "release.yml").write_text("name: release\n", encoding="utf-8")
    _write_json(
        ev / "security" / "key_provenance_continuity_gate.json",
        {"status": "PASS", "findings": []},
    )

    monkeypatch.setattr(strict_release_fallback_key_indicator_gate, "ROOT", repo)
    monkeypatch.setattr(
        strict_release_fallback_key_indicator_gate,
        "FALLBACK_POLICY",
        repo / "governance" / "security" / "fallback_secret_usage_policy.json",
    )
    monkeypatch.setattr(
        strict_release_fallback_key_indicator_gate,
        "RELEASE_WORKFLOW",
        repo / ".github" / "workflows" / "release.yml",
    )
    monkeypatch.setattr(strict_release_fallback_key_indicator_gate, "evidence_root", lambda: ev)
    assert strict_release_fallback_key_indicator_gate.main([]) == 0


def test_strict_release_fallback_key_indicator_gate_fails_on_fallback_indicator(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "governance" / "security" / "fallback_secret_usage_policy.json",
        {"fallback_literal": "glyphser-provenance-hmac-fallback-v1"},
    )
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "release.yml").write_text(
        "env:\n  GLYPHSER_PROVENANCE_HMAC_KEY: glyphser-provenance-hmac-fallback-v1\n",
        encoding="utf-8",
    )
    _write_json(
        ev / "security" / "key_provenance_continuity_gate.json",
        {"status": "FAIL", "findings": ["fallback_signing_used:policy_signature"]},
    )

    monkeypatch.setattr(strict_release_fallback_key_indicator_gate, "ROOT", repo)
    monkeypatch.setattr(
        strict_release_fallback_key_indicator_gate,
        "FALLBACK_POLICY",
        repo / "governance" / "security" / "fallback_secret_usage_policy.json",
    )
    monkeypatch.setattr(
        strict_release_fallback_key_indicator_gate,
        "RELEASE_WORKFLOW",
        repo / ".github" / "workflows" / "release.yml",
    )
    monkeypatch.setattr(strict_release_fallback_key_indicator_gate, "evidence_root", lambda: ev)
    assert strict_release_fallback_key_indicator_gate.main([]) == 1
    report = json.loads((ev / "security" / "strict_release_fallback_key_indicator_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "release_workflow_contains_fallback_key_literal" in report["findings"]
    assert any(str(item).startswith("fallback_signing_indicator_in_release_lane:") for item in report["findings"])
