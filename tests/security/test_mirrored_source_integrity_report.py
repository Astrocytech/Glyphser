from __future__ import annotations

import json
from pathlib import Path

from tooling.security import mirrored_source_integrity_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_mirrored_source_integrity_report_passes_for_consistent_hashes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    report = repo / "evidence" / "security" / "security_toolchain_install_report.json"
    _write_json(
        report,
        {
            "install": [
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {
                        "url": "https://pypi.org/packages/semgrep.whl",
                        "archive_info": {"hashes": {"sha256": "a" * 64}},
                    },
                },
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {
                        "url": "https://mirror.local/packages/semgrep.whl",
                        "archive_info": {"hashes": {"sha256": "a" * 64}},
                    },
                },
            ]
        },
    )

    monkeypatch.setattr(mirrored_source_integrity_report, "ROOT", repo)
    monkeypatch.setattr(mirrored_source_integrity_report, "INSTALL_REPORT", report)
    monkeypatch.setattr(mirrored_source_integrity_report, "evidence_root", lambda: repo / "evidence")

    assert mirrored_source_integrity_report.main([]) == 0


def test_mirrored_source_integrity_report_fails_for_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    report = repo / "evidence" / "security" / "security_toolchain_install_report.json"
    _write_json(
        report,
        {
            "install": [
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {
                        "url": "https://pypi.org/packages/semgrep.whl",
                        "archive_info": {"hashes": {"sha256": "a" * 64}},
                    },
                },
                {
                    "metadata": {"name": "semgrep", "version": "1.95.0"},
                    "download_info": {
                        "url": "https://mirror.local/packages/semgrep.whl",
                        "archive_info": {"hashes": {"sha256": "b" * 64}},
                    },
                },
            ]
        },
    )

    monkeypatch.setattr(mirrored_source_integrity_report, "ROOT", repo)
    monkeypatch.setattr(mirrored_source_integrity_report, "INSTALL_REPORT", report)
    monkeypatch.setattr(mirrored_source_integrity_report, "evidence_root", lambda: repo / "evidence")

    assert mirrored_source_integrity_report.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "mirrored_source_integrity_report.json").read_text(encoding="utf-8"))
    assert "mirrored_source_hash_mismatch:semgrep==1.95.0" in payload["findings"]
