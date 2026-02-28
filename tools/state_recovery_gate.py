#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from path_config import evidence_root
sys.path.insert(0, str(ROOT))

from src.glyphser.storage.state_store import DurableStateStore, SCHEMA_VERSION

OUT_DIR = evidence_root() / "recovery"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="glyphser-recovery-") as td:
        work = Path(td)
        store_dir = work / "state"
        store = DurableStateStore(store_dir)
        store.append_event({"op": "run_create", "run_id": "run-001"})
        store.append_event({"op": "run_start", "run_id": "run-001"})
        store.append_event({"op": "run_end", "run_id": "run-001"})
        first = store.write_checkpoint()
        backup = store.backup_checkpoint()

        # restart recovery check
        restarted = DurableStateStore(store_dir)
        restart_state = restarted.recover()
        restart_ok = restart_state["state_hash"] == first["state_hash"]

        # corruption quarantine check
        restarted.state_file.write_text("{bad-json", encoding="utf-8")
        corrupted = DurableStateStore(store_dir)
        post_corrupt = corrupted.recover()
        quarantine_ok = any(corrupted.quarantine_dir.glob("state.json.corrupt.*"))

        # backup/restore drill
        restore_dir = work / "restore"
        restore_store = DurableStateStore(restore_dir)
        restored = restore_store.restore_from_checkpoint(backup)
        drill_ok = restored["state_hash"] == first["state_hash"]

        verdict = restart_ok and quarantine_ok and drill_ok and (post_corrupt["state_hash"] == first["state_hash"])
        result = {
            "status": "PASS" if verdict else "FAIL",
            "schema_version": SCHEMA_VERSION,
            "restart_ok": restart_ok,
            "quarantine_ok": quarantine_ok,
            "backup_restore_ok": drill_ok,
            "state_hash_initial": first["state_hash"],
            "checkpoint_hash_initial": first["checkpoint_hash"],
            "state_hash_after_restart": restart_state["state_hash"],
            "state_hash_after_corruption_recovery": post_corrupt["state_hash"],
            "state_hash_after_restore": restored["state_hash"],
            "backup_checkpoint_file": backup.name,
            "rpo_target_seconds": 300,
            "rto_target_seconds": 300,
        }
        _write(OUT_DIR / "latest.json", result)
        (OUT_DIR / "replay-proof.txt").write_text(
            f"state_hash={first['state_hash']}\ncheckpoint_hash={first['checkpoint_hash']}\n",
            encoding="utf-8",
        )
        _write(
            OUT_DIR / "backup-restore-drill.json",
            {
                "status": "PASS" if drill_ok else "FAIL",
                "backup_checkpoint_file": backup.name,
                "restored_state_hash": restored["state_hash"],
                "expected_state_hash": first["state_hash"],
            },
        )

        # keep a copy of the backup artifact for evidence review
        shutil.copy2(backup, OUT_DIR / "checkpoint-backup.json")

    if verdict:
        print("STATE_RECOVERY_GATE: PASS")
        return 0
    print("STATE_RECOVERY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
