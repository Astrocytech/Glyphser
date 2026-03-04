from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.checkpoint.migrate_checkpoint import checkpoint_migrate
from runtime.glyphser.checkpoint.restore import restore_checkpoint
from runtime.glyphser.config.migrate_manifest import manifest_migrate
from runtime.glyphser.trace.migrate_trace import migrate_trace

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "tests" / "security" / "corpus"


def _run_restore_scenario(tmp_path: Path, scenario: str) -> dict[str, object]:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir(parents=True)
    if scenario == "escape_root":
        outside = tmp_path / "outside" / "checkpoint.json"
        outside.parent.mkdir(parents=True)
        outside.write_text(json.dumps({"ok": True}), encoding="utf-8")
        return {"path": str(outside), "allowed_root": str(allowed_root)}
    if scenario == "oversized_file":
        big = allowed_root / "big.json"
        big.write_text("{" + '"blob":"' + ("x" * (10 * 1024 * 1024 + 64)) + '"}', encoding="utf-8")
        return {"path": str(big), "allowed_root": str(allowed_root)}
    if scenario == "bad_suffix":
        bad = allowed_root / "bad.txt"
        bad.write_text("{}", encoding="utf-8")
        return {"path": str(bad), "allowed_root": str(allowed_root)}
    raise ValueError(f"unknown restore scenario: {scenario}")


@pytest.mark.parametrize("case_path", sorted(CORPUS.glob("*.json")))
def test_malicious_corpus_cases(case_path: Path, tmp_path: Path) -> None:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    kind = case["kind"]
    want = case["expected_error_substring"]

    with pytest.raises(Exception) as exc_info:
        if kind == "restore_checkpoint":
            req = _run_restore_scenario(tmp_path, str(case["scenario"]))
            restore_checkpoint(req)
        elif kind == "checkpoint_migrate":
            checkpoint_migrate(case["request"])
        elif kind == "manifest_migrate":
            manifest_migrate(case["request"])
        elif kind == "trace_migrate":
            migrate_trace(case["request"])
        else:
            raise ValueError(f"unknown case kind: {kind}")
    assert want in str(exc_info.value)
