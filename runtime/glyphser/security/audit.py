"""Tamper-evident audit log with deterministic hash chaining."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List

try:
    import fcntl
except Exception:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _lock_exclusive(fh: Any) -> None:
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)


def _unlock(fh: Any) -> None:
    if fcntl is not None:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def append_event(path: Path, event: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(event, dict):
        raise TypeError("event must be dict")
    path.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = ""
    with path.open("a+", encoding="utf-8") as fh:
        _lock_exclusive(fh)
        try:
            fh.seek(0)
            raw_text = fh.read()
            if raw_text and not raw_text.endswith("\n"):
                raise ValueError("audit log corrupt: partial line suffix")
            lines = [ln for ln in raw_text.splitlines() if ln.strip()]
            if lines:
                try:
                    tail = json.loads(lines[-1])
                except json.JSONDecodeError as exc:
                    raise ValueError("audit log corrupt: invalid JSON") from exc
                tail_hash = tail.get("hash")
                if not isinstance(tail_hash, str):
                    raise ValueError("audit log corrupt: invalid hash field")
                if not isinstance(tail.get("prev_hash", ""), str):
                    raise ValueError("audit log corrupt: invalid prev_hash field")
                if not isinstance(tail.get("event", {}), dict):
                    raise ValueError("audit log corrupt: invalid event field")
                prev_hash = tail_hash
            payload = {"event": event, "prev_hash": prev_hash}
            record_hash = _sha256(_canonical(payload))
            record = {"event": event, "prev_hash": prev_hash, "hash": record_hash}
            fh.seek(0, os.SEEK_END)
            fh.write(_canonical(record) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            # Ensure directory entry metadata reaches stable storage.
            dir_flag = getattr(os, "O_DIRECTORY", 0)
            try:
                dfd = os.open(str(path.parent), dir_flag)
            except OSError:
                dfd = -1
            if dfd >= 0:
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
        finally:
            _unlock(fh)
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
    try:
        events = load_events(path)
    except Exception:
        return {"status": "FAIL", "index": -1, "reason": "invalid_json"}
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
