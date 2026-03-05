from __future__ import annotations

import json
from pathlib import Path

from tooling.security.report_io import write_json_report


def test_write_json_report_sanitizes_control_chars_and_newlines(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    write_json_report(
        out,
        {
            "status": "FAIL",
            "findings": ["line1\nline2", "cr\rvalue", "null:\x00", "tab\tvalue"],
            "summary": {"note": "multi\nline"},
            "metadata": {"source": "gate\rname"},
        },
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["findings"][0] == "line1\\nline2"
    assert payload["findings"][1] == "cr\\rvalue"
    assert payload["findings"][2] == "null:\\u0000"
    assert payload["findings"][3] == "tab\\tvalue"
    assert payload["summary"]["note"] == "multi\\nline"
    assert payload["metadata"]["source"] == "gate\\rname"


def test_write_json_report_keeps_clean_strings_unchanged(tmp_path: Path) -> None:
    out = tmp_path / "clean.json"
    write_json_report(
        out,
        {
            "status": "PASS",
            "findings": ["safe-value"],
            "summary": {"count": 1},
            "metadata": {"gate": "demo_gate"},
        },
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["findings"] == ["safe-value"]
    assert payload["metadata"]["gate"] == "demo_gate"

