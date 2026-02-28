"""Durable run-state persistence with deterministic restart recovery."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

SCHEMA_VERSION = 1


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DurableStateStore:
    """File-backed state store with WAL replay and corruption quarantine."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.state_file = self.root / "state.json"
        self.wal_file = self.root / "wal.jsonl"
        self.checkpoint_file = self.root / "checkpoint.json"
        self.backup_dir = self.root / "backup"
        self.quarantine_dir = self.root / "quarantine"
        self.root.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    def append_event(self, event: Dict[str, Any]) -> str:
        if not isinstance(event, dict):
            raise ValueError("event must be dict")
        event_record = {
            "schema_version": SCHEMA_VERSION,
            "event": event,
            "event_hash": _sha256_text(_canonical_json(event)),
        }
        with self.wal_file.open("a", encoding="utf-8") as fh:
            fh.write(_canonical_json(event_record) + "\n")
        self._state["events"].append(event_record)
        self._state["last_event_hash"] = event_record["event_hash"]
        self._persist_state()
        return event_record["event_hash"]

    def state_hash(self) -> str:
        return _sha256_text(_canonical_json(self._state))

    def write_checkpoint(self) -> Dict[str, str]:
        snapshot = {
            "schema_version": SCHEMA_VERSION,
            "state": self._state,
            "state_hash": self.state_hash(),
        }
        self._atomic_write_json(self.checkpoint_file, snapshot)
        cp_hash = _sha256_text(_canonical_json(snapshot))
        return {"checkpoint_hash": cp_hash, "state_hash": snapshot["state_hash"]}

    def backup_checkpoint(self) -> Path:
        if not self.checkpoint_file.exists():
            raise ValueError("checkpoint missing")
        data = self.checkpoint_file.read_bytes()
        name = f"checkpoint-{_sha256_bytes(data)[:16]}.json"
        out = self.backup_dir / name
        out.write_bytes(data)
        return out

    def restore_from_checkpoint(self, checkpoint_path: Path) -> Dict[str, str]:
        payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if int(payload.get("schema_version", 0)) != SCHEMA_VERSION:
            raise ValueError("unsupported checkpoint schema version")
        state = payload.get("state")
        if not isinstance(state, dict):
            raise ValueError("invalid checkpoint state")
        self._state = state
        self._persist_state()
        return {"state_hash": self.state_hash()}

    def recover(self) -> Dict[str, str]:
        """Load state from state file or deterministically replay WAL."""
        self._state = self._load_state()
        return {"state_hash": self.state_hash(), "last_event_hash": self._state.get("last_event_hash", "")}

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                payload = json.loads(self.state_file.read_text(encoding="utf-8"))
                if int(payload.get("schema_version", 0)) != SCHEMA_VERSION:
                    raise ValueError("unsupported state schema version")
                state = payload.get("state")
                if not isinstance(state, dict):
                    raise ValueError("invalid state shape")
                state.setdefault("events", [])
                state.setdefault("last_event_hash", "")
                return state
            except Exception:
                self._quarantine_file(self.state_file)
        return self._replay_from_wal()

    def _replay_from_wal(self) -> Dict[str, Any]:
        state: Dict[str, Any] = {"events": [], "last_event_hash": ""}
        if not self.wal_file.exists():
            self._atomic_write_json(self.state_file, {"schema_version": SCHEMA_VERSION, "state": state})
            return state
        for line in self.wal_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if int(rec.get("schema_version", 0)) != SCHEMA_VERSION:
                raise ValueError("unsupported WAL schema version")
            event = rec.get("event")
            event_hash = rec.get("event_hash")
            if not isinstance(event, dict) or not isinstance(event_hash, str):
                raise ValueError("invalid WAL record")
            if event_hash != _sha256_text(_canonical_json(event)):
                raise ValueError("WAL corruption")
            state["events"].append(rec)
            state["last_event_hash"] = event_hash
        self._atomic_write_json(self.state_file, {"schema_version": SCHEMA_VERSION, "state": state})
        return state

    def _persist_state(self) -> None:
        self._atomic_write_json(self.state_file, {"schema_version": SCHEMA_VERSION, "state": self._state})

    def _quarantine_file(self, path: Path) -> None:
        data = path.read_bytes()
        q_name = f"{path.name}.corrupt.{_sha256_bytes(data)[:16]}"
        shutil.move(str(path), str(self.quarantine_dir / q_name))

    @staticmethod
    def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(path)

