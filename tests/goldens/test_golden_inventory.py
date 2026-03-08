from __future__ import annotations

import json
from pathlib import Path


def test_golden_inventory_required_ids():
    root = Path(__file__).resolve().parents[2]
    inventory = json.loads(
        (root / "artifacts" / "expected" / "goldens" / "golden_inventory.json").read_text(encoding="utf-8")
    )
    required = {entry["golden_id"] for entry in inventory.get("required", [])}
    expected = {
        "golden_kernel_train",
        "golden_data_nextbatch",
        "golden_modelir_exec",
        "golden_dp_apply",
    }
    assert expected.issubset(required)
