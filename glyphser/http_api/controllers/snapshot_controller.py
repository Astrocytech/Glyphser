from __future__ import annotations

from typing import Any

from glyphser.internal.manifest_builder import build_manifest
from glyphser.public.verify import verify


class SnapshotController:
    def build_snapshot(self, model: dict[str, Any], input_data: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
        inputs = input_data or {}
        result = verify(model=model, input_data=inputs)
        manifest = build_manifest(model=model, input_data=inputs, output=result.output, digest=result.digest)
        return result.digest, manifest

