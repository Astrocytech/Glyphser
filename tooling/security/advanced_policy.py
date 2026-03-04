from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_policy() -> dict[str, Any]:
    path = ROOT / "governance" / "security" / "advanced_hardening_policy.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("advanced hardening policy must be an object")
    return payload
