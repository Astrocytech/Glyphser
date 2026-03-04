from __future__ import annotations

import tarfile
from pathlib import Path

from tooling.security import audit_archive_verify


def test_audit_archive_verify_passes_for_default_archive(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(audit_archive_verify, "ROOT", repo)
    monkeypatch.setattr(audit_archive_verify, "evidence_root", lambda: repo / "evidence")
    assert audit_archive_verify.main([]) == 0


def test_extract_archive_safely_blocks_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "bad.tar.gz"
    src = tmp_path / "src"
    src.mkdir()
    good = src / "audit.log.jsonl"
    good.write_text("", encoding="utf-8")
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(good, arcname="audit.log.jsonl")
        ti = tarfile.TarInfo("../escape.txt")
        ti.size = 0
        tf.addfile(ti)
    findings = audit_archive_verify._extract_archive_safely(
        archive,
        tmp_path / "extract",
        expected_member="audit.log.jsonl",
    )
    assert any(item.startswith("unsafe_tar_member:") for item in findings)
