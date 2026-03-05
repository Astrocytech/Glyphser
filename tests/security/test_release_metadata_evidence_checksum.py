from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_metadata_evidence_checksum


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_release_metadata_checksum_is_embedded_and_stable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "a.json", {"status": "PASS"})
    _write(sec / "b.json", {"status": "WARN"})

    monkeypatch.setattr(release_metadata_evidence_checksum, "ROOT", repo)
    monkeypatch.setattr(release_metadata_evidence_checksum, "evidence_root", lambda: repo / "evidence")

    assert release_metadata_evidence_checksum.main([]) == 0
    meta1 = json.loads((sec / "release_metadata.json").read_text(encoding="utf-8"))
    checksum1 = meta1["evidence_package_checksum"]

    assert release_metadata_evidence_checksum.main([]) == 0
    meta2 = json.loads((sec / "release_metadata.json").read_text(encoding="utf-8"))
    checksum2 = meta2["evidence_package_checksum"]
    assert checksum1 == checksum2


def test_release_metadata_checksum_changes_when_evidence_changes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "a.json", {"status": "PASS"})

    monkeypatch.setattr(release_metadata_evidence_checksum, "ROOT", repo)
    monkeypatch.setattr(release_metadata_evidence_checksum, "evidence_root", lambda: repo / "evidence")

    assert release_metadata_evidence_checksum.main([]) == 0
    first = json.loads((sec / "release_metadata.json").read_text(encoding="utf-8"))["evidence_package_checksum"]

    _write(sec / "a.json", {"status": "FAIL"})
    assert release_metadata_evidence_checksum.main([]) == 0
    second = json.loads((sec / "release_metadata.json").read_text(encoding="utf-8"))["evidence_package_checksum"]
    assert first != second
