from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tooling.security import report_io
from tooling.security.report_io import write_json_report


def test_write_json_report_concurrent_writers_keep_valid_json(tmp_path: Path) -> None:
    out = tmp_path / "security" / "concurrent.json"

    def _writer(worker: int) -> None:
        for idx in range(50):
            write_json_report(out, {"status": "PASS", "summary": {"worker": worker, "idx": idx}})

    with ThreadPoolExecutor(max_workers=8) as pool:
        for worker in range(8):
            pool.submit(_writer, worker)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert 0 <= int(payload["summary"]["worker"]) < 8
    assert 0 <= int(payload["summary"]["idx"]) < 50


def test_write_json_report_concurrent_writers_leave_no_temp_files(tmp_path: Path) -> None:
    out = tmp_path / "security" / "concurrent.json"

    def _writer(worker: int) -> None:
        write_json_report(out, {"status": "PASS", "summary": {"worker": worker}})

    with ThreadPoolExecutor(max_workers=4) as pool:
        for worker in range(20):
            pool.submit(_writer, worker)

    orphaned = [
        p
        for p in (out.parent).glob(f".{out.name}.*")
        if p.name != f".{out.name}.lock"
    ]
    assert orphaned == []


def test_write_json_report_tempfile_creation_and_cleanup_race_probe(monkeypatch, tmp_path: Path) -> None:
    out = tmp_path / "security" / "concurrent.json"
    seen_temp_names: list[str] = []
    original_mkstemp = report_io.tempfile.mkstemp

    def _mkstemp(*args, **kwargs):  # type: ignore[no-untyped-def]
        fd, name = original_mkstemp(*args, **kwargs)
        seen_temp_names.append(name)
        return fd, name

    monkeypatch.setattr(report_io.tempfile, "mkstemp", _mkstemp)

    def _writer(worker: int) -> None:
        for idx in range(20):
            write_json_report(out, {"status": "PASS", "summary": {"worker": worker, "idx": idx}})

    with ThreadPoolExecutor(max_workers=6) as pool:
        for worker in range(6):
            pool.submit(_writer, worker)

    assert len(seen_temp_names) > 0
    assert len(set(seen_temp_names)) == len(seen_temp_names)
    assert all(not Path(name).exists() for name in seen_temp_names)
