from __future__ import annotations

import json
from pathlib import Path

from tooling.security import fallback_secret_usage_gate


def _write_policy(repo: Path, allowlisted: list[str]) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "fallback_secret_usage_policy.json").write_text(
        json.dumps(
            {
                "fallback_literal": "glyphser-provenance-hmac-fallback-v1",
                "allowlisted_workflows": allowlisted,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_fallback_secret_usage_gate_passes_for_allowlisted_workflow(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, [".github/workflows/ci.yml"])
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("env:\n  GLYPHSER_PROVENANCE_HMAC_KEY: ${{ secrets.KEY || 'glyphser-provenance-hmac-fallback-v1' }}\n")

    monkeypatch.setattr(fallback_secret_usage_gate, "ROOT", repo)
    monkeypatch.setattr(fallback_secret_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert fallback_secret_usage_gate.main([]) == 0


def test_fallback_secret_usage_gate_fails_for_non_allowlisted_workflow(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, [".github/workflows/ci.yml"])
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "release.yml").write_text(
        "env:\n  GLYPHSER_PROVENANCE_HMAC_KEY: ${{ secrets.KEY || 'glyphser-provenance-hmac-fallback-v1' }}\n"
    )

    monkeypatch.setattr(fallback_secret_usage_gate, "ROOT", repo)
    monkeypatch.setattr(fallback_secret_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert fallback_secret_usage_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "fallback_secret_usage_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("fallback_literal_not_allowlisted:") for item in report["findings"])
