from __future__ import annotations

import json
from pathlib import Path

from tooling.security import toolchain_binary_source_consistency_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_toolchain_binary_source_consistency_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    lock = repo / "tooling" / "security" / "security_toolchain_lock.json"
    report = repo / "evidence" / "security" / "security_toolchain_install_report.json"

    _write_json(lock, {"semgrep": {"version": "1.95.0", "version_hash": "sha256:" + "a" * 64}})
    _write_json(
        report,
        {
            "install": [
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {"archive_info": {"hashes": {"sha256": "a" * 64}}},
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "LOCK", lock)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "INSTALL_REPORT", report)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "evidence_root", lambda: repo / "evidence")

    assert toolchain_binary_source_consistency_gate.main([]) == 0


def test_toolchain_binary_source_consistency_gate_fails_on_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    lock = repo / "tooling" / "security" / "security_toolchain_lock.json"
    report = repo / "evidence" / "security" / "security_toolchain_install_report.json"

    _write_json(lock, {"semgrep": {"version": "1.95.0", "version_hash": "sha256:" + "a" * 64}})
    _write_json(
        report,
        {
            "install": [
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {"archive_info": {"hashes": {"sha256": "b" * 64}}},
                }
            ]
        },
    )

    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "LOCK", lock)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "INSTALL_REPORT", report)
    monkeypatch.setattr(toolchain_binary_source_consistency_gate, "evidence_root", lambda: repo / "evidence")

    assert toolchain_binary_source_consistency_gate.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "toolchain_binary_source_consistency_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("binary_source_hash_mismatch:semgrep") for item in payload["findings"])
