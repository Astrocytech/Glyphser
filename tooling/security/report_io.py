from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _normalize_report_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    if "status" in normalized:
        normalized.setdefault("schema_version", SCHEMA_VERSION)
        normalized.setdefault("findings", [])
        normalized.setdefault("summary", {})
        normalized.setdefault("metadata", {})
    return normalized


def write_json_report(path: Path, payload: dict[str, Any]) -> None:
    """Write a canonical report using atomic replace + fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(_normalize_report_payload(payload), indent=2, sort_keys=True) + "\n"

    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        tmp_path.replace(path)
        dir_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
