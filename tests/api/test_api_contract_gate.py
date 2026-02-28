from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "tools" / "api_contract_gate.py"
SPEC = importlib.util.spec_from_file_location("api_contract_gate", MOD_PATH)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_api_contract_gate_contract_is_valid():
    MOD.validate_contract(MOD.load_contract())


def test_api_contract_gate_rejects_invalid_major():
    doc = MOD.load_contract()
    doc["info"]["version"] = "2.0.0"
    try:
        MOD.validate_contract(doc)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "major version" in str(exc)
