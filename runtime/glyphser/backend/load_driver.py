"""Deterministic backend driver load (minimal)."""

from __future__ import annotations

from typing import Any, Dict

from runtime.glyphser.backend.keras_driver import (
    get_keras_cpu_driver,
    get_keras_gpu_driver,
)
from runtime.glyphser.backend.pytorch_driver import (
    get_pytorch_cpu_driver,
    get_pytorch_gpu_driver,
)
from runtime.glyphser.backend.reference_driver import get_default_driver

DIRECT_DRIVER_IDS = {
    "default",
    "reference",
    "pytorch_cpu",
    "pytorch_gpu",
    "keras_cpu",
    "keras_gpu",
}
UNSUPPORTED_LANGUAGE_ROUTES = {"java_cpu", "rust_cpu"}
UNIVERSAL_PROFILE_MODES = {
    "strict_universal",
    "balanced",
    "optimized_native",
    "pinned_profile",
}
PINNED_PROFILES: dict[str, list[str]] = {
    "universal_v1": ["pytorch_cpu", "keras_cpu", "pytorch_gpu", "keras_gpu"],
    "universal_v1_gpu": ["pytorch_gpu", "keras_gpu", "pytorch_cpu", "keras_cpu"],
    "balanced_v1": ["pytorch_cpu", "keras_cpu", "pytorch_gpu", "keras_gpu"],
}


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


def _parse_profile_mode(request: Dict[str, Any]) -> tuple[str, str]:
    raw_mode = str(request.get("profile_mode", "balanced")).strip()
    profile_id = str(request.get("profile_id", "")).strip()
    if raw_mode.startswith("pinned_profile:"):
        mode = "pinned_profile"
        profile_id = raw_mode.split(":", 1)[1].strip() or profile_id
        return mode, profile_id
    if raw_mode not in UNIVERSAL_PROFILE_MODES:
        raise ValueError(f"unsupported profile_mode: {raw_mode}")
    return raw_mode, profile_id


def universal_profile_mode_policy(request: Dict[str, Any]) -> dict[str, Any]:
    mode, profile_id = _parse_profile_mode(request)
    framework = str(request.get("universal_framework", "pytorch")).strip().lower()
    prefer_gpu = bool(request.get("universal_prefer_gpu", True))
    explicit = str(request.get("universal_route", "")).strip()
    return {
        "version": "v1",
        "profile_mode": mode,
        "profile_id": profile_id,
        "universal_framework": framework,
        "universal_prefer_gpu": prefer_gpu,
        "universal_route": explicit,
        "pinned_profiles_available": sorted(PINNED_PROFILES.keys()),
    }


def _universal_route_candidates(request: Dict[str, Any]) -> list[str]:
    explicit = str(request.get("universal_route", "")).strip()
    mode, profile_id = _parse_profile_mode(request)
    if explicit:
        if explicit in UNSUPPORTED_LANGUAGE_ROUTES:
            raise ValueError(f"unsupported universal_route: {explicit}")
        if explicit not in DIRECT_DRIVER_IDS:
            raise ValueError(f"unsupported universal_route: {explicit}")
        return [explicit]

    if mode == "pinned_profile":
        if not profile_id:
            raise ValueError("profile_mode pinned_profile requires profile_id")
        if profile_id not in PINNED_PROFILES:
            raise ValueError(f"unsupported profile_id: {profile_id}")
        return list(PINNED_PROFILES[profile_id])

    framework = str(request.get("universal_framework", "pytorch")).strip().lower()
    prefer_gpu = bool(request.get("universal_prefer_gpu", True))
    if framework not in {"pytorch", "keras"}:
        raise ValueError(f"unsupported universal_framework: {framework}")
    if mode == "strict_universal":
        if framework == "pytorch":
            return ["pytorch_gpu", "pytorch_cpu"] if prefer_gpu else ["pytorch_cpu", "pytorch_gpu"]
        return ["keras_gpu", "keras_cpu"] if prefer_gpu else ["keras_cpu", "keras_gpu"]
    if mode == "optimized_native":
        if framework == "pytorch":
            return (
                ["pytorch_gpu", "pytorch_cpu", "keras_gpu", "keras_cpu"]
                if prefer_gpu
                else ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"]
            )
        return (
            ["keras_gpu", "keras_cpu", "pytorch_gpu", "pytorch_cpu"]
            if prefer_gpu
            else ["keras_cpu", "keras_gpu", "pytorch_cpu", "pytorch_gpu"]
        )

    # balanced mode: prefer framework, then portability-biased CPU fallback on secondary framework.
    if framework == "pytorch":
        return (
            ["pytorch_gpu", "pytorch_cpu", "keras_cpu", "keras_gpu"]
            if prefer_gpu
            else ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"]
        )
    return (
        ["keras_gpu", "keras_cpu", "pytorch_cpu", "pytorch_gpu"]
        if prefer_gpu
        else ["keras_cpu", "keras_gpu", "pytorch_cpu", "pytorch_gpu"]
    )


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
        result["routing_policy"] = universal_profile_mode_policy(request)
    return result
