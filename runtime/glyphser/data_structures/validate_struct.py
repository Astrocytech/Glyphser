"""Minimal struct validation scaffolding (stub)."""
from __future__ import annotations

from typing import Any


def _require_int(obj: dict[str, Any], key: str) -> None:
    if key not in obj or not isinstance(obj[key], int):
        raise ValueError(f"missing or invalid int: {key}")


def _require_str(obj: dict[str, Any], key: str) -> None:
    if key not in obj or not isinstance(obj[key], str):
        raise ValueError(f"missing or invalid str: {key}")


def validate_trace_iter_record(record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")
    _require_int(record, "t")
    _require_str(record, "operator_id")


def validate_checkpoint_header(header: dict[str, Any]) -> None:
    if not isinstance(header, dict):
        raise TypeError("header must be a dict")
    _require_str(header, "checkpoint_id")
    _require_int(header, "step")
