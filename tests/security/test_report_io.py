from __future__ import annotations

import json
from pathlib import Path

from tooling.security.report_io import write_json_report


def test_write_json_report_writes_sorted_json_with_newline(tmp_path: Path) -> None:
    out = tmp_path / "security" / "report.json"
    write_json_report(out, {"b": 1, "a": {"z": 2, "y": 3}})
    content = out.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert content.index('"a"') < content.index('"b"')
    parsed = json.loads(content)
    assert parsed["a"]["y"] == 3


def test_write_json_report_replaces_existing_file_atomically(tmp_path: Path) -> None:
    out = tmp_path / "security" / "report.json"
    write_json_report(out, {"version": 1})
    first = out.read_text(encoding="utf-8")
    write_json_report(out, {"version": 2})
    second = out.read_text(encoding="utf-8")
    assert first != second
    assert json.loads(second)["version"] == 2


def test_write_json_report_auto_normalizes_security_report_shape(tmp_path: Path) -> None:
    out = tmp_path / "security" / "gate.json"
    write_json_report(out, {"status": "PASS"})
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == 1
    assert parsed["findings"] == []
    assert parsed["summary"] == {}
    assert parsed["metadata"] == {}
