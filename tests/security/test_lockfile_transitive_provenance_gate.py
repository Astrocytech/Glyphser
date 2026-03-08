from __future__ import annotations

import json
from pathlib import Path

from tooling.security import lockfile_transitive_provenance_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_lockfile_transitive_provenance_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "requirements.lock",
        "\n".join(
            [
                "bandit==1.9.4 --hash=sha256:" + "a" * 64,
                "pip-audit==2.9.0 --hash=sha256:" + "b" * 64,
                "semgrep==1.95.0 --hash=sha256:" + "c" * 64,
                "setuptools==75.8.0 --hash=sha256:" + "d" * 64,
            ]
        )
        + "\n",
    )

    monkeypatch.setattr(lockfile_transitive_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_transitive_provenance_gate, "LOCKFILE", repo / "requirements.lock")
    monkeypatch.setattr(lockfile_transitive_provenance_gate, "evidence_root", lambda: repo / "evidence")

    assert lockfile_transitive_provenance_gate.main([]) == 0


def test_lockfile_transitive_provenance_gate_fails_without_hashes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "requirements.lock",
        "\n".join(
            [
                "bandit==1.9.4",
                "pip-audit==2.9.0 --hash=sha256:" + "b" * 64,
                "semgrep==1.95.0",
                "setuptools==75.8.0 --hash=sha256:" + "d" * 64,
            ]
        )
        + "\n",
    )

    monkeypatch.setattr(lockfile_transitive_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_transitive_provenance_gate, "LOCKFILE", repo / "requirements.lock")
    monkeypatch.setattr(lockfile_transitive_provenance_gate, "evidence_root", lambda: repo / "evidence")

    assert lockfile_transitive_provenance_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "lockfile_transitive_provenance_gate.json").read_text(encoding="utf-8"))
    assert "missing_transitive_hash_provenance:bandit" in report["findings"]
    assert "missing_transitive_hash_provenance:semgrep" in report["findings"]
