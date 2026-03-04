from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_stage_s_policy() -> dict[str, Any]:
    payload = json.loads(
        (ROOT / "governance" / "security" / "stage_s_hardening_policy.json").read_text(encoding="utf-8")
    )
    if not isinstance(payload, dict):
        raise ValueError("stage_s_hardening_policy must be a dict")
    return payload
