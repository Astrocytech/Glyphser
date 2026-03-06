from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_publish_rollback_order_gate


def _write_release(repo: Path, text: str) -> None:
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "release.yml").write_text(text, encoding="utf-8")


def test_release_publish_rollback_order_gate_passes_when_publish_depends_on_verify_and_rollback_gate_present(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        "\n".join(
            [
                "jobs:",
                "  verify-signatures:",
                "    steps:",
                "      - run: python tooling/security/release_rollback_provenance_gate.py",
                "  publish-pypi:",
                "    needs: [build, verify-signatures]",
            ]
        )
        + "\n",
    )
    monkeypatch.setattr(release_publish_rollback_order_gate, "ROOT", repo)
    monkeypatch.setattr(
        release_publish_rollback_order_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml"
    )
    monkeypatch.setattr(release_publish_rollback_order_gate, "evidence_root", lambda: repo / "evidence")
    assert release_publish_rollback_order_gate.main([]) == 0


def test_release_publish_rollback_order_gate_fails_when_publish_not_blocked_by_verify(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        "\n".join(
            [
                "jobs:",
                "  verify-signatures:",
                "    steps:",
                "      - run: python tooling/security/release_rollback_provenance_gate.py",
                "  publish-pypi:",
                "    needs: [build]",
            ]
        )
        + "\n",
    )
    monkeypatch.setattr(release_publish_rollback_order_gate, "ROOT", repo)
    monkeypatch.setattr(
        release_publish_rollback_order_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml"
    )
    monkeypatch.setattr(release_publish_rollback_order_gate, "evidence_root", lambda: repo / "evidence")
    assert release_publish_rollback_order_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "release_publish_rollback_order_gate.json").read_text(encoding="utf-8")
    )
    assert "publish_job_not_blocked_by_verify_signatures" in report["findings"]
