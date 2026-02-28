from __future__ import annotations

from pathlib import Path

from runtime.glyphser.storage.state_store import DurableStateStore


def test_restart_recovery_and_backup_restore(tmp_path: Path):
    store = DurableStateStore(tmp_path / "store")
    store.append_event({"step": 1, "run_id": "r1"})
    store.append_event({"step": 2, "run_id": "r1"})
    first = store.write_checkpoint()
    backup = store.backup_checkpoint()

    restarted = DurableStateStore(tmp_path / "store")
    recovered = restarted.recover()
    assert recovered["state_hash"] == first["state_hash"]

    restored = DurableStateStore(tmp_path / "restore")
    state = restored.restore_from_checkpoint(backup)
    assert state["state_hash"] == first["state_hash"]


def test_corruption_quarantine_and_wal_replay(tmp_path: Path):
    store = DurableStateStore(tmp_path / "store")
    store.append_event({"step": 1})
    first = store.write_checkpoint()
    store.state_file.write_text("{broken-json", encoding="utf-8")

    recovered = DurableStateStore(tmp_path / "store")
    current = recovered.recover()
    assert current["state_hash"] == first["state_hash"]
    assert list(recovered.quarantine_dir.glob("state.json.corrupt.*"))

