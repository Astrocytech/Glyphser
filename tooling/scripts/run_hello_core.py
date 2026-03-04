#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

from runtime.glyphser.certificate.build import write_execution_certificate
from runtime.glyphser.checkpoint.write import save_checkpoint
from runtime.glyphser.data.next_batch import next_batch
from runtime.glyphser.model.model_ir_executor import execute
from runtime.glyphser.serialization.canonical_cbor import encode_canonical
from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash
from runtime.glyphser.trace.trace_sidecar import write_trace
from tooling.lib.path_config import fixtures_root

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


FIXTURES = fixtures_root() / "hello-core"
GOLDEN = ROOT / "specs" / "examples" / "hello-core" / "hello-core-golden.json"


def _canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_dataset(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _normalize_hello_ir(ir: dict) -> dict:
    if "nodes" in ir and "ir_schema_hash" in ir:
        return ir

    ops = ir.get("operators")
    if not isinstance(ops, list):
        return ir

    normalized_nodes = []
    last_node_id = None
    last_shape = None
    for raw in ops:
        op = str(raw.get("op", "")).upper()
        node_id = raw.get("id")
        if not isinstance(node_id, str) or not node_id:
            continue

        if op == "INPUT":
            shape = raw.get("shape", [1])
            node = {
                "node_id": node_id,
                "instr": "Input",
                "inputs": [],
                "shape_out": shape,
                "dtype": "float32",
            }
            last_shape = shape
        elif op == "DENSE":
            params = {"weights": raw.get("weights", []), "bias": raw.get("bias", 0.0)}
            node = {
                "node_id": node_id,
                "instr": "Dense",
                "inputs": [{"node_id": last_node_id, "output_idx": 0}] if last_node_id else [],
                "params": params,
                "shape_out": [1],
                "dtype": "float32",
            }
            last_shape = [1]
        elif op == "OUTPUT":
            node = {
                "node_id": node_id,
                "instr": "Output",
                "inputs": [{"node_id": last_node_id, "output_idx": 0}] if last_node_id else [],
                "shape_out": last_shape or [1],
                "dtype": "float32",
            }
        else:
            continue

        normalized_nodes.append(node)
        last_node_id = node_id

    outputs = [{"node_id": last_node_id, "output_idx": 0}] if last_node_id else []
    return {
        "ir_schema_hash": ir.get("ir_schema_hash", "sha256:uml_model_ir_demo"),
        "nodes": normalized_nodes,
        "outputs": outputs,
    }


def _record_hash(record: dict) -> str:
    return _sha256_hex(encode_canonical(record))


def main() -> int:
    driver_id = os.environ.get("GLYPHSER_DRIVER_ID", "default")

    if not GOLDEN.exists():
        print(f"missing golden file: {GOLDEN}")
        return 1

    dataset_path = FIXTURES / "tiny_synth_dataset.jsonl"
    model_ir_path = FIXTURES / "model_ir.json"
    if not dataset_path.exists() or not model_ir_path.exists():
        print("missing fixture inputs in artifacts/inputs/fixtures/hello-core")
        return 1

    dataset = _load_dataset(dataset_path)
    model_ir = _normalize_hello_ir(json.loads(model_ir_path.read_text(encoding="utf-8")))

    cursor = 0
    batch, cursor = next_batch(dataset, cursor, batch_size=1)
    if not batch:
        print("empty batch")
        return 1

    inputs = batch[0]["x"]
    response = execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": "hello-core-replay-token",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )
    if "error" in response:
        print(json.dumps(response, indent=2, sort_keys=True))
        return 1
    outputs = response.get("outputs")

    base_records = [
        {"step": 1, "operator_id": "Glyphser.Data.NextBatch", "batch": batch[0]},
        {
            "step": 1,
            "operator_id": "Glyphser.Model.ModelIR_Executor",
            "inputs": inputs,
            "outputs": outputs,
        },
    ]
    trace_records = [{**rec, "event_hash": _record_hash(rec)} for rec in base_records]

    trace_path = FIXTURES / "trace.json"
    _ = write_trace(trace_records, trace_path)
    trace_final_hash = compute_trace_hash(trace_records)

    manifest_hash = _sha256_hex((FIXTURES / "manifest.core.yaml").read_bytes())
    operator_registry_root_hash = json.loads(
        (ROOT / "specs" / "contracts" / "catalog-manifest.json").read_text(encoding="utf-8")
    )["derived_identities"]["operator_registry_root_hash"]

    checkpoint_header = {
        "checkpoint_id": "hello-core-ckpt-v1",
        "global_step": 1,
        "manifest_hash": manifest_hash,
        "operator_registry_root_hash": operator_registry_root_hash,
    }
    checkpoint_path = FIXTURES / "checkpoint.json"
    _ = save_checkpoint(checkpoint_header, checkpoint_path)
    checkpoint_hash = _sha256_hex(_canonical_json_bytes(checkpoint_header))

    execution_certificate = {
        "certificate_id": "hello-core-cert-v1",
        "run_id": "hello-core-run-v1",
        "trace_final_hash": trace_final_hash,
        "checkpoint_hash": checkpoint_hash,
        "operator_contracts_root_hash": operator_registry_root_hash,
        "policy_gate_hash": "5a5e629c6f1bece7ef8d0b20f8ee99153f7eda4e2ec03eaa7b65db06d20fca67",
    }
    certificate_path = FIXTURES / "execution_certificate.json"
    _ = write_execution_certificate(execution_certificate, certificate_path)
    certificate_hash = _sha256_hex(_canonical_json_bytes(execution_certificate))

    interface_hash = json.loads((ROOT / "specs" / "contracts" / "interface_hash.json").read_text(encoding="utf-8"))[
        "interface_hash"
    ]

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    expected = golden["expected_identities"]

    results = {
        "trace_final_hash": trace_final_hash,
        "certificate_hash": certificate_hash,
        "interface_hash": interface_hash,
    }

    print("Glyphser hello-core: RUN")
    print(json.dumps(results, indent=2, sort_keys=True))

    ok = True
    for key, expected_value in expected.items():
        actual_value = results.get(key)
        if actual_value != expected_value:
            print(f"MISMATCH {key}: expected={expected_value} got={actual_value}")
            ok = False

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
