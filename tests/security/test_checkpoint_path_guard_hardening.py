from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.checkpoint.migrate_checkpoint import checkpoint_migrate
from runtime.glyphser.trace.migrate_trace import migrate_trace


def test_checkpoint_migrate_enforces_allowed_root(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir(parents=True)
    src = allowed / "in.json"
    src.write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    outside = tmp_path / "outside.json"
    with pytest.raises(ValueError, match="escapes allowed root"):
        checkpoint_migrate(
            {
                "allowed_root": str(allowed),
                "source_path": str(src),
                "target_path": str(outside),
            }
        )


def test_checkpoint_migrate_rejects_absolute_without_allowed_root(tmp_path: Path) -> None:
    src = tmp_path / "in.json"
    src.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="absolute path requires allowed_root"):
        checkpoint_migrate({"source_path": str(src), "target_path": str(tmp_path / "out.json")})


def test_trace_migrate_rejects_mixed_separators(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir(parents=True)
    src = allowed / "trace.json"
    src.write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mixed separators"):
        migrate_trace(
            {
                "allowed_root": str(allowed),
                "trace_path": str(src).replace("/", "\\/"),
                "output_path": "trace/out.json",
            }
        )
