from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_error_codes_manifest_present():
    path = ROOT / "contracts" / "error_codes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("entries"), "error codes must be present"
