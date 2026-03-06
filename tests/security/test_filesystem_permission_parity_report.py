from __future__ import annotations

import json
from pathlib import Path

from tooling.security import filesystem_permission_parity_report


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_filesystem_permission_parity_report_passes_when_hashes_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    left = repo / "parity" / "ubuntu" / "file_permission_matrix_gate.json"
    right = repo / "parity" / "macos" / "file_permission_matrix_gate.json"
    _write_json(left, {"status": "PASS", "parity_hash": "abc123"})
    _write_json(right, {"status": "PASS", "parity_hash": "abc123"})

    monkeypatch.setattr(filesystem_permission_parity_report, "ROOT", repo)
    monkeypatch.setattr(filesystem_permission_parity_report, "evidence_root", lambda: repo / "evidence")
    assert (
        filesystem_permission_parity_report.main(
            ["--left", str(left), "--right", str(right), "--left-label", "ubuntu", "--right-label", "macos"]
        )
        == 0
    )

    report = json.loads((repo / "evidence" / "security" / "filesystem_permission_parity_report.json").read_text("utf-8"))
    assert report["status"] == "PASS"
    assert report["findings"] == []


def test_filesystem_permission_parity_report_fails_on_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    left = repo / "parity" / "ubuntu" / "file_permission_matrix_gate.json"
    right = repo / "parity" / "macos" / "file_permission_matrix_gate.json"
    _write_json(left, {"status": "PASS", "parity_hash": "abc123"})
    _write_json(right, {"status": "PASS", "parity_hash": "def456"})

    monkeypatch.setattr(filesystem_permission_parity_report, "ROOT", repo)
    monkeypatch.setattr(filesystem_permission_parity_report, "evidence_root", lambda: repo / "evidence")
    assert filesystem_permission_parity_report.main(["--left", str(left), "--right", str(right)]) == 1

    report = json.loads((repo / "evidence" / "security" / "filesystem_permission_parity_report.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "parity_hash_mismatch:left:right" in report["findings"]


def test_filesystem_permission_parity_report_fails_on_mode_and_presence_drift(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    left = repo / "parity" / "ubuntu" / "file_permission_matrix_gate.json"
    right = repo / "parity" / "macos" / "file_permission_matrix_gate.json"
    _write_json(
        left,
        {
            "status": "PASS",
            "parity_hash": "samehash",
            "summary": {
                "matrix": {
                    "evidence/security/sbom.json": {"mode": "0o640", "platform": "posix"},
                    "governance/security/review_policy.json": {"mode": "0o644", "platform": "posix"},
                }
            },
        },
    )
    _write_json(
        right,
        {
            "status": "PASS",
            "parity_hash": "samehash",
            "summary": {"matrix": {"evidence/security/sbom.json": {"mode": "0o600", "platform": "posix"}}},
        },
    )

    monkeypatch.setattr(filesystem_permission_parity_report, "ROOT", repo)
    monkeypatch.setattr(filesystem_permission_parity_report, "evidence_root", lambda: repo / "evidence")
    assert (
        filesystem_permission_parity_report.main(
            ["--left", str(left), "--right", str(right), "--left-label", "ubuntu", "--right-label", "macos"]
        )
        == 1
    )

    report = json.loads((repo / "evidence" / "security" / "filesystem_permission_parity_report.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "mode_mismatch:evidence/security/sbom.json:ubuntu=0o640:macos=0o600" in report["findings"]
    assert "missing_sensitive_output:macos:governance/security/review_policy.json" in report["findings"]
