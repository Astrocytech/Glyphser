from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _split_csv(raw: str) -> list[str]:
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


def _default_cors_origins() -> list[str]:
    return (
        ["*"]
        if not os.environ.get("GLYPHSER_HTTP_CORS_ORIGINS")
        else _split_csv(os.environ["GLYPHSER_HTTP_CORS_ORIGINS"])
    )


_REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class HttpApiSettings:
    host: str = os.environ.get("GLYPHSER_HTTP_HOST", "127.0.0.1")
    port: int = int(os.environ.get("GLYPHSER_HTTP_PORT", "8000"))
    reload: bool = _env_bool("GLYPHSER_HTTP_RELOAD", False)
    require_https: bool = _env_bool("GLYPHSER_HTTP_REQUIRE_HTTPS", False)

    cors_origins: list[str] = field(default_factory=_default_cors_origins)

    runtime_root: Path = Path(os.environ.get("GLYPHSER_RUNTIME_API_ROOT", str(_REPO_ROOT)))
    runtime_state_path: Path = Path(
        os.environ.get("GLYPHSER_RUNTIME_API_STATE_PATH", "/tmp/glyphser_runtime_api/state.json")
    )
    runtime_audit_log_path: Path | None = (
        Path(os.environ["GLYPHSER_RUNTIME_API_AUDIT_LOG_PATH"])
        if os.environ.get("GLYPHSER_RUNTIME_API_AUDIT_LOG_PATH")
        else None
    )

    snapshot_root: Path = Path(os.environ.get("GLYPHSER_HTTP_SNAPSHOT_ROOT", str(_REPO_ROOT / "workspace" / "snapshots")))
    work_root: Path = Path(os.environ.get("GLYPHSER_HTTP_WORK_ROOT", str(_REPO_ROOT / "workspace")))


settings = HttpApiSettings()
