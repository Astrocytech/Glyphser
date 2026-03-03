"""Internal hashing helpers (unstable)."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_sha256(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
