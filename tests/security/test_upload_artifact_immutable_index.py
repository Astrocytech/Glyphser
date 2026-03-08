from __future__ import annotations

import json
from pathlib import Path

from tooling.security import upload_artifact_immutable_index


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_upload_artifact_immutable_index_records_name_size_and_digest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_text(repo / "dist" / "glyphser-1.0.0.tar.gz", "artifact-bytes")
    _write_text(repo / "evidence" / "security" / "security_super_gate.json", '{"status": "PASS"}\n')

    monkeypatch.setattr(upload_artifact_immutable_index, "ROOT", repo)
    monkeypatch.setattr(upload_artifact_immutable_index, "evidence_root", lambda: repo / "evidence")
    assert upload_artifact_immutable_index.main([]) == 0

    out = repo / "evidence" / "security" / "upload_artifact_immutable_index.json"
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["summary"]["artifact_count"] == 2
    assert len(payload["summary"]["index_root"]) == 64
    item = next(entry for entry in payload["items"] if entry["path"].endswith("glyphser-1.0.0.tar.gz"))
    assert item["size_bytes"] == len("artifact-bytes")
    assert (repo / "evidence" / "security" / "upload_artifact_immutable_index.json.sig").exists()


def test_upload_artifact_immutable_index_fails_when_no_artifacts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(upload_artifact_immutable_index, "ROOT", repo)
    monkeypatch.setattr(upload_artifact_immutable_index, "evidence_root", lambda: repo / "evidence")
    assert upload_artifact_immutable_index.main([]) == 1

    payload = json.loads((repo / "evidence" / "security" / "upload_artifact_immutable_index.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert "missing_upload_artifacts" in payload["findings"]
