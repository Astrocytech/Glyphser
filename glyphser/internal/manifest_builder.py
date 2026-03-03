"""Internal manifest assembly helpers (unstable)."""

from __future__ import annotations

from typing import Any


def build_manifest(
    *,
    model: dict[str, Any],
    input_data: dict[str, Any],
    output: dict[str, Any],
    digest: str,
) -> dict[str, Any]:
    return {
        "model": model,
        "input_data": input_data,
        "output": output,
        "digest": digest,
    }
