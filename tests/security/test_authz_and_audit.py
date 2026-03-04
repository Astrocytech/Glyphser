from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.audit import append_event, verify_chain
from runtime.glyphser.security.authz import authorize


def test_rbac_negative_and_positive():
    assert authorize("jobs:write", ["operator"]) is True
    assert authorize("jobs:write", ["viewer"]) is False
    assert authorize("security:admin", ["auditor"]) is False
    assert authorize("security:admin", ["admin"]) is True


def test_audit_tamper_detection(tmp_path: Path):
    log = tmp_path / "audit.log.jsonl"
    append_event(log, {"op": "submit"})
    append_event(log, {"op": "status"})
    assert verify_chain(log)["status"] == "PASS"

    lines = log.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[1])
    record["event"]["op"] = "tampered"
    lines[1] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert verify_chain(log)["status"] == "FAIL"


def test_audit_append_rejects_corrupt_tail(tmp_path: Path):
    log = tmp_path / "audit.log.jsonl"
    log.write_text('{"event":{"op":"submit"},"prev_hash":"","hash":"h"}\nnot-json\n', encoding="utf-8")
    try:
        append_event(log, {"op": "status"})
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid JSON" in str(exc)


def test_verify_chain_fails_closed_on_invalid_json(tmp_path: Path):
    log = tmp_path / "audit.log.jsonl"
    log.write_text("not-json\n", encoding="utf-8")
    result = verify_chain(log)
    assert result["status"] == "FAIL"
    assert result["reason"] == "invalid_json"
