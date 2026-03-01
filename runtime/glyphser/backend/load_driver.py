"""Deterministic backend driver load (minimal)."""
from __future__ import annotations

from typing import Any, Dict

from runtime.glyphser.backend.pytorch_driver import get_pytorch_cpu_driver
from runtime.glyphser.backend.reference_driver import get_default_driver


def resolve_driver(driver_id: str) -> Any:
    if driver_id in {"default", "reference"}:
        return get_default_driver()
    if driver_id == "pytorch_cpu":
        return get_pytorch_cpu_driver()
    raise ValueError(f"unsupported driver_id: {driver_id}")


def load_driver(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    driver_id = request.get("driver_id") or "default"
    driver = resolve_driver(driver_id)
    return {
        "status": "OK",
        "driver_id": driver_id,
        "backend_binary_hash": driver.backend_binary_hash,
        "driver_runtime_fingerprint_hash": driver.runtime_fingerprint_hash,
    }
