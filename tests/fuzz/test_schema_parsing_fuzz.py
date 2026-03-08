from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_schema_parsing_fuzz():
    schema_files = sorted((ROOT / "specs" / "schemas").rglob("*.schema.json"))
    assert schema_files
    for path in schema_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "$schema" in data
        assert "type" in data
