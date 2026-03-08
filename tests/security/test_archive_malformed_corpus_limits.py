from __future__ import annotations

import io
import tarfile
from pathlib import Path

from tooling.security import audit_archive_verify


def _build_archive(path: Path, members: list[tuple[str, bytes]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as tf:
        for name, payload in members:
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            tf.addfile(info, fileobj=None if not payload else io.BytesIO(payload))


def test_extract_archive_safely_flags_nested_archive_member(tmp_path: Path) -> None:
    archive = tmp_path / "nested.tar.gz"
    _build_archive(
        archive,
        [
            ("audit.log.jsonl", b""),
            ("nested.tar.gz", b"not-really-an-archive"),
        ],
    )
    findings = audit_archive_verify._extract_archive_safely(archive, tmp_path / "extract", expected_member="audit.log.jsonl")
    assert any(item.startswith("nested_archive_member:nested.tar.gz") for item in findings)


def test_extract_archive_safely_flags_member_count_limit(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / "many.tar.gz"
    _build_archive(archive, [("audit.log.jsonl", b"")] + [(f"f{i}.txt", b"") for i in range(5)])
    monkeypatch.setattr(audit_archive_verify, "MAX_ARCHIVE_MEMBERS", 3)
    findings = audit_archive_verify._extract_archive_safely(archive, tmp_path / "extract", expected_member="audit.log.jsonl")
    assert any(item.startswith("archive_member_count_exceeded:") for item in findings)


def test_extract_archive_safely_flags_total_uncompressed_limit(monkeypatch, tmp_path: Path) -> None:
    archive = tmp_path / "big.tar.gz"
    _build_archive(
        archive,
        [
            ("audit.log.jsonl", b""),
            ("one.txt", b"abcde"),
            ("two.txt", b"fghij"),
        ],
    )
    monkeypatch.setattr(audit_archive_verify, "MAX_TOTAL_UNCOMPRESSED_BYTES", 6)
    findings = audit_archive_verify._extract_archive_safely(archive, tmp_path / "extract", expected_member="audit.log.jsonl")
    assert any(item.startswith("archive_total_uncompressed_exceeded:") for item in findings)
