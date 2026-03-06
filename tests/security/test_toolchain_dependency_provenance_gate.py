from __future__ import annotations

import json
from pathlib import Path

from tooling.security import toolchain_dependency_provenance_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_toolchain_dependency_provenance_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "tooling" / "security" / "security_toolchain_lock.json",
        {
            "bandit": {"version": "1.9.4", "version_hash": "sha256:abc"},
        },
    )
    _write_json(
        ev / "security" / "security_toolchain_install_report.json",
        {
            "install": [
                {
                    "metadata": {"name": "bandit", "version": "1.9.4"},
                    "download_info": {
                        "url": "https://files.pythonhosted.org/packages/bandit-1.9.4-py3-none-any.whl",
                        "archive_info": {"hashes": {"sha256": "abc"}},
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_dependency_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "evidence_root", lambda: ev)

    assert toolchain_dependency_provenance_gate.main([]) == 0


def test_toolchain_dependency_provenance_gate_fails_on_hash_and_source(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "tooling" / "security" / "security_toolchain_lock.json",
        {
            "bandit": {"version": "1.9.4", "version_hash": "sha256:abc"},
        },
    )
    _write_json(
        ev / "security" / "security_toolchain_install_report.json",
        {
            "install": [
                {
                    "metadata": {"name": "bandit", "version": "1.9.4"},
                    "download_info": {
                        "url": "http://evil.example/bandit.whl",
                        "archive_info": {"hashes": {"sha256": "zzz"}},
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_dependency_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "evidence_root", lambda: ev)

    assert toolchain_dependency_provenance_gate.main([]) == 1
    report = json.loads((ev / "security" / "toolchain_dependency_provenance_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("hash_mismatch:bandit") for item in report["findings"])
    assert any(item.startswith("unapproved_download_source:bandit") for item in report["findings"])


def test_toolchain_dependency_provenance_gate_fails_on_wheel_metadata_mismatch(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    _write_json(
        repo / "tooling" / "security" / "security_toolchain_lock.json",
        {
            "bandit": {"version": "1.9.4", "version_hash": "sha256:abc"},
        },
    )
    _write_json(
        ev / "security" / "security_toolchain_install_report.json",
        {
            "install": [
                {
                    "metadata": {"name": "bandit", "version": "1.9.4"},
                    "download_info": {
                        "url": "https://files.pythonhosted.org/packages/pip_audit-2.9.0-py3-none-any.whl",
                        "archive_info": {"hashes": {"sha256": "abc"}},
                    },
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_dependency_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "LOCK", repo / "tooling" / "security" / "security_toolchain_lock.json")
    monkeypatch.setattr(toolchain_dependency_provenance_gate, "evidence_root", lambda: ev)

    assert toolchain_dependency_provenance_gate.main([]) == 1
    report = json.loads((ev / "security" / "toolchain_dependency_provenance_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("wheel_metadata_name_mismatch:bandit") for item in report["findings"])
