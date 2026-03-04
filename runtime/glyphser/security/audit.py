"""Tamper-evident audit log with deterministic hash chaining."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_event(path: Path, event: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    events = load_events(path)
    prev_hash = events[-1]["hash"] if events else ""
    payload = {"event": event, "prev_hash": prev_hash}
    record_hash = _sha256(_canonical(payload))
    record = {"event": event, "prev_hash": prev_hash, "hash": record_hash}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(_canonical(record) + "\n")
    return record


def load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        out.append(json.loads(line))
    return out


def verify_chain(path: Path) -> Dict[str, Any]:
    events = load_events(path)
    prev_hash = ""
    for idx, rec in enumerate(events):
        payload = {"event": rec.get("event"), "prev_hash": rec.get("prev_hash", "")}
        expected = _sha256(_canonical(payload))
        if rec.get("prev_hash", "") != prev_hash:
            return {"status": "FAIL", "index": idx, "reason": "prev_hash_mismatch"}
        if rec.get("hash", "") != expected:
            return {"status": "FAIL", "index": idx, "reason": "hash_mismatch"}
        prev_hash = rec.get("hash", "")
    return {"status": "PASS", "events": len(events), "tip_hash": prev_hash}
