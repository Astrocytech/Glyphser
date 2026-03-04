from __future__ import annotations

from pathlib import Path

import pytest

from runtime.glyphser.security.audit import append_event
from runtime.glyphser.storage.state_store import DurableStateStore


def test_audit_append_fails_closed_on_fsync_error(monkeypatch, tmp_path: Path) -> None:
    log = tmp_path / "audit.log.jsonl"

    def _boom(_fd: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("os.fsync", _boom)
    with pytest.raises(OSError, match="disk full"):
        append_event(log, {"op": "submit"})


def test_state_store_append_event_fails_on_atomic_replace_error(monkeypatch, tmp_path: Path) -> None:
    store = DurableStateStore(tmp_path / "store")
    orig_replace = Path.replace

    def _replace_fail(self: Path, target: Path):  # type: ignore[override]
        if self.name.endswith(".tmp"):
            raise OSError("permission denied")
        return orig_replace(self, target)

    monkeypatch.setattr(Path, "replace", _replace_fail, raising=True)
    with pytest.raises(OSError, match="permission denied"):
        store.append_event({"op": "submit"})
