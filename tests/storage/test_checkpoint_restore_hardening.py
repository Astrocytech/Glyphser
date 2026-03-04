from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.checkpoint.restore import restore_checkpoint


def test_restore_checkpoint_allows_root_constrained_paths(tmp_path: Path) -> None:
    ckpt = tmp_path / "checkpoint.json"
    ckpt.write_text(json.dumps({"ok": True}), encoding="utf-8")
    out = restore_checkpoint({"path": str(ckpt), "allowed_root": str(tmp_path)})
    assert out["state"]["ok"] is True


def test_restore_checkpoint_rejects_escape_outside_allowed_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.json"
    outside.write_text(json.dumps({"ok": True}), encoding="utf-8")
    with pytest.raises(ValueError, match="path escapes allowed root"):
        restore_checkpoint({"path": str(outside), "allowed_root": str(tmp_path)})
