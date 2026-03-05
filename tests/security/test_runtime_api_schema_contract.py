from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_api_request_schemas_reject_unknown_fields() -> None:
    payload = json.loads((ROOT / "runtime" / "glyphser" / "api" / "schemas" / "runtime_api_schemas.json").read_text("utf-8"))
    assert isinstance(payload, dict)
    request_schemas = ["submit_request", "status_request", "evidence_request", "replay_request"]
    for name in request_schemas:
        schema = payload.get(name)
        assert isinstance(schema, dict), f"missing schema: {name}"
        assert schema.get("type") == "object", f"{name} must be object"
        assert schema.get("additionalProperties") is False, f"{name} must reject unknown fields"
        assert isinstance(schema.get("properties"), dict) and schema.get("properties"), f"{name} properties missing"
