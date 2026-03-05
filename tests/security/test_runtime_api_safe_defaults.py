from __future__ import annotations

from pathlib import Path

import pytest

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService


def test_runtime_api_rejects_risky_defaults_in_production_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GLYPHSER_ENV", "production")
    cfg = RuntimeApiConfig(root=tmp_path, state_path=tmp_path / "state.json")
    with pytest.raises(ValueError, match="unsafe runtime api defaults"):
        RuntimeApiService(cfg)


def test_runtime_api_accepts_explicit_secure_config_in_production_env(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GLYPHSER_ENV", "production")
    cfg = RuntimeApiConfig(
        root=tmp_path,
        state_path=tmp_path / "state.json",
        enforce_signed_tokens=True,
        enforce_token_jti_replay_protection=True,
        enforce_replay_token_binding=True,
    )
    RuntimeApiService(cfg)


def test_runtime_api_allows_temporary_override_for_risky_defaults(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GLYPHSER_ENV", "production")
    monkeypatch.setenv("GLYPHSER_ALLOW_RISKY_RUNTIME_DEFAULTS", "1")
    cfg = RuntimeApiConfig(root=tmp_path, state_path=tmp_path / "state.json")
    RuntimeApiService(cfg)
