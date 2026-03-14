from __future__ import annotations

from pathlib import Path
from typing import Any

from glyphser.http_api.controllers.snapshot_controller import SnapshotController
from glyphser.internal.evidence_writer import write_evidence


def _safe_snapshot_name(name: str) -> str:
    clean = name.strip()
    if not clean:
        raise ValueError("name must be non-empty")
    if "/" in clean or "\\" in clean:
        raise ValueError("name must not contain path separators")
    if clean.startswith("."):
        raise ValueError("name must not start with '.'")
    if not clean.endswith(".json"):
        clean += ".json"
    return clean


class SnapshotService:
    def __init__(self, controller: SnapshotController, *, snapshot_root: Path) -> None:
        self._controller = controller
        self._snapshot_root = snapshot_root

    def snapshot(self, model: dict[str, Any], input_data: dict[str, Any] | None) -> tuple[str, dict[str, Any]]:
        return self._controller.build_snapshot(model=model, input_data=input_data)

    def snapshot_to_disk(
        self,
        model: dict[str, Any],
        input_data: dict[str, Any] | None,
        *,
        name: str,
    ) -> tuple[str, Path]:
        digest, manifest = self._controller.build_snapshot(model=model, input_data=input_data)
        filename = _safe_snapshot_name(name)
        out_path = (self._snapshot_root / filename).resolve()
        root = self._snapshot_root.resolve()
        if root not in out_path.parents and out_path != root:
            raise PermissionError("snapshot path escapes snapshot root")
        write_evidence(out_path, manifest)
        return digest, out_path

