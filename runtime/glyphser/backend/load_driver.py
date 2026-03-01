"""Deterministic backend driver load (minimal)."""
from __future__ import annotations

from typing import Any, Dict

from runtime.glyphser.backend.keras_driver import get_keras_cpu_driver, get_keras_gpu_driver
from runtime.glyphser.backend.pytorch_driver import get_pytorch_cpu_driver, get_pytorch_gpu_driver
from runtime.glyphser.backend.reference_driver import get_default_driver


DIRECT_DRIVER_IDS = {"default", "reference", "pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"}


def _resolve_direct_driver(driver_id: str) -> Any:
    if driver_id in {"default", "reference"}:
        return get_default_driver()
    if driver_id == "pytorch_cpu":
        return get_pytorch_cpu_driver()
    if driver_id == "pytorch_gpu":
        return get_pytorch_gpu_driver()
    if driver_id == "keras_cpu":
        return get_keras_cpu_driver()
    if driver_id == "keras_gpu":
        return get_keras_gpu_driver()
    raise ValueError(f"unsupported driver_id: {driver_id}")


def _universal_route_candidates(request: Dict[str, Any]) -> list[str]:
    explicit = str(request.get("universal_route", "")).strip()
    if explicit:
        if explicit in {"java_cpu", "rust_cpu"}:
            raise ValueError(f"unsupported universal_route: {explicit}")
        if explicit not in DIRECT_DRIVER_IDS:
            raise ValueError(f"unsupported universal_route: {explicit}")
        return [explicit]

    framework = str(request.get("universal_framework", "pytorch")).strip().lower()
    prefer_gpu = bool(request.get("universal_prefer_gpu", True))
    if framework not in {"pytorch", "keras"}:
        raise ValueError(f"unsupported universal_framework: {framework}")
    if framework == "pytorch":
        return ["pytorch_gpu", "pytorch_cpu", "keras_gpu", "keras_cpu"] if prefer_gpu else ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"]
    return ["keras_gpu", "keras_cpu", "pytorch_gpu", "pytorch_cpu"] if prefer_gpu else ["keras_cpu", "keras_gpu", "pytorch_cpu", "pytorch_gpu"]


def _resolve_universal_driver(request: Dict[str, Any]) -> tuple[str, Any]:
    attempts: list[str] = []
    for candidate in _universal_route_candidates(request):
        try:
            return candidate, _resolve_direct_driver(candidate)
        except Exception as exc:
            attempts.append(f"{candidate}:{exc}")
    raise RuntimeError("universal_driver could not resolve route; attempts=" + "; ".join(attempts))


def resolve_driver(driver_id: str, request: Dict[str, Any] | None = None) -> Any:
    if driver_id == "universal_driver":
        _, driver = _resolve_universal_driver(request or {})
        return driver
    return _resolve_direct_driver(driver_id)


def load_driver(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be dict")
    driver_id = request.get("driver_id") or "default"
    selected_route = driver_id
    if driver_id == "universal_driver":
        selected_route, driver = _resolve_universal_driver(request)
    else:
        driver = resolve_driver(driver_id)
    result = {
        "status": "OK",
        "driver_id": driver_id,
        "backend_binary_hash": driver.backend_binary_hash,
        "driver_runtime_fingerprint_hash": driver.runtime_fingerprint_hash,
    }
    if driver_id == "universal_driver":
        result["selected_route"] = selected_route
        result["routing_policy"] = {
            "version": "v1",
            "universal_framework": str(request.get("universal_framework", "pytorch")).strip().lower(),
            "universal_prefer_gpu": bool(request.get("universal_prefer_gpu", True)),
            "universal_route": str(request.get("universal_route", "")).strip(),
        }
    return result
