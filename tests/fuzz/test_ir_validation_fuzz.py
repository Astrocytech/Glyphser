from __future__ import annotations

import random

import pytest

from runtime.glyphser.model.ir_schema import IRValidationError, validate_ir_dag


def _make_ir(seed: int, nodes: int) -> dict:
    rng = random.Random(seed)
    node_list = []
    for i in range(nodes):
        node_id = f"n{i}"
        instr = rng.choice(["Input", "Dense", "Output"])
        inputs = []
        if i > 0 and instr != "Input":
            inputs.append({"node_id": f"n{rng.randrange(0, i)}", "output_idx": 0})
        node_list.append(
            {
                "node_id": node_id,
                "instr": instr,
                "inputs": inputs,
                "shape_out": [rng.choice([1, 2, 4])],
                "dtype": "float32",
            }
        )
    return {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": node_list,
        "outputs": [{"node_id": node_list[-1]["node_id"], "output_idx": 0}] if node_list else [],
    }


def test_ir_validation_fuzz_deterministic():
    for seed in range(10):
        ir = _make_ir(seed, nodes=5)
        try:
            validated = validate_ir_dag(ir)
        except IRValidationError:
            continue
        assert validated["ir_hash"]
        # determinism check
        validated_again = validate_ir_dag(ir)
        assert validated_again["ir_hash"] == validated["ir_hash"]
