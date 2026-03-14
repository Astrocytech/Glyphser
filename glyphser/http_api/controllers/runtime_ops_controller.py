from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from runtime.glyphser.checkpoint.restore import restore_checkpoint
from runtime.glyphser.checkpoint.write import save_checkpoint
from runtime.glyphser.checkpoint.migrate_checkpoint import checkpoint_migrate
from runtime.glyphser.config.migrate_manifest import manifest_migrate
from runtime.glyphser.dp.apply import dp_apply
from runtime.glyphser.legacy_import.legacy_framework import legacy_framework_import
from runtime.glyphser.monitor.drift_compute import drift_compute
from runtime.glyphser.monitor.emit import monitor_emit
from runtime.glyphser.monitor.register import monitor_register
from runtime.glyphser.registry.stage_transition import stage_transition
from runtime.glyphser.registry.version_create import version_create
from runtime.glyphser.tmmu.commit_execution import commit_execution
from runtime.glyphser.trace.migrate_trace import migrate_trace
from runtime.glyphser.tracking.artifact_get import artifact_get
from runtime.glyphser.tracking.artifact_list import artifact_list
from runtime.glyphser.tracking.artifact_put import artifact_put
from runtime.glyphser.tracking.artifact_tombstone import artifact_tombstone
from runtime.glyphser.tracking.metric_log import metric_log
from runtime.glyphser.tracking.run_create import run_create
from runtime.glyphser.tracking.run_end import run_end
from runtime.glyphser.tracking.run_start import run_start


OpFn = Callable[[dict[str, Any]], dict[str, Any]]


def _safe_name(name: str, *, suffix: str = ".json") -> str:
    clean = name.strip()
    if not clean:
        raise ValueError("name must be non-empty")
    if "/" in clean or "\\" in clean:
        raise ValueError("name must not contain path separators")
    if clean.startswith("."):
        raise ValueError("name must not start with '.'")
    if not clean.endswith(suffix):
        clean += suffix
    return clean


class RuntimeOpsController:
    def __init__(self, *, work_root: Path) -> None:
        self._work_root = work_root.resolve()
        self._ops: dict[str, OpFn] = {
            "tracking.run_create": run_create,
            "tracking.run_start": run_start,
            "tracking.run_end": run_end,
            "tracking.artifact_put": artifact_put,
            "tracking.artifact_get": artifact_get,
            "tracking.artifact_list": artifact_list,
            "tracking.artifact_tombstone": artifact_tombstone,
            "tracking.metric_log": metric_log,
            "monitor.register": monitor_register,
            "monitor.emit": monitor_emit,
            "monitor.drift_compute": drift_compute,
            "registry.version_create": version_create,
            "registry.stage_transition": stage_transition,
            "config.manifest_migrate": manifest_migrate,
            "trace.migrate_trace": self._migrate_trace_wrapped,
            "dp.apply": dp_apply,
            "checkpoint.restore": self._restore_checkpoint_wrapped,
            "checkpoint.migrate_checkpoint": self._migrate_checkpoint_wrapped,
            "legacy_import.legacy_framework_import": legacy_framework_import,
            "tmmu.commit_execution": commit_execution,
        }

    def list_ops(self) -> list[str]:
        return sorted(self._ops.keys())

    def call(self, op: str, request: dict[str, Any]) -> dict[str, Any]:
        op = (op or "").strip()
        if op not in self._ops:
            raise ValueError("unknown op")
        fn = self._ops[op]
        return fn(request)

    def checkpoint_save(self, *, state: dict[str, Any], name: str) -> dict[str, Any]:
        filename = _safe_name(name, suffix=".json")
        out_path = (self._work_root / "checkpoints" / filename).resolve()
        if self._work_root not in out_path.parents:
            raise PermissionError("checkpoint path escapes workspace")
        digest = save_checkpoint(state, out_path)
        return {"status": "OK", "digest": digest, "path": str(out_path)}

    def _restore_checkpoint_wrapped(self, request: dict[str, Any]) -> dict[str, Any]:
        payload = dict(request)
        payload.setdefault("allowed_root", str(self._work_root))
        return restore_checkpoint(payload)

    def _migrate_trace_wrapped(self, request: dict[str, Any]) -> dict[str, Any]:
        payload = dict(request)
        payload.setdefault("allowed_root", str(self._work_root))
        return migrate_trace(payload)

    def _migrate_checkpoint_wrapped(self, request: dict[str, Any]) -> dict[str, Any]:
        payload = dict(request)
        payload.setdefault("allowed_root", str(self._work_root))
        return checkpoint_migrate(payload)
