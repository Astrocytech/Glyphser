"""Stable public API surface for Glyphser.

Only modules under ``glyphser.public`` are considered stable.
"""

from __future__ import annotations

import warnings

from glyphser.public.runtime import RuntimeApiConfig, RuntimeService
from glyphser.public.verify import VerificationResult, verify

__all__ = [
    "RuntimeApiConfig",
    "RuntimeService",
    "VerificationResult",
    "verify",
]


def __getattr__(name: str):
    if name == "RuntimeApiService":
        warnings.warn(
            "glyphser.RuntimeApiService is deprecated; use glyphser.RuntimeService instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return RuntimeService
    if name == "verify_model":
        warnings.warn(
            "glyphser.verify_model is deprecated; use glyphser.verify instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return verify
    raise AttributeError(f"module 'glyphser' has no attribute {name!r}")
