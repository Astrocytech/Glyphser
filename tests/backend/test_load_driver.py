from __future__ import annotations

import pytest

from runtime.glyphser.backend import load_driver as load_driver_module
from runtime.glyphser.model.model_ir_executor import execute


def test_load_driver_default_is_stable() -> None:
    result = load_driver_module.load_driver({"driver_id": "default"})
    assert result["status"] == "OK"
    assert result["driver_id"] == "default"
    assert result["backend_binary_hash"] == "sha256:reference"
    assert result["driver_runtime_fingerprint_hash"] == "sha256:reference-runtime"


def test_load_driver_pytorch_cpu_route(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeDriver:
        backend_binary_hash = "sha256:fake-pytorch"
        runtime_fingerprint_hash = "sha256:fake-pytorch-runtime"

    monkeypatch.setattr(load_driver_module, "get_pytorch_cpu_driver", lambda: _FakeDriver())
    result = load_driver_module.load_driver({"driver_id": "pytorch_cpu"})
    assert result["status"] == "OK"
    assert result["driver_id"] == "pytorch_cpu"
    assert result["backend_binary_hash"] == "sha256:fake-pytorch"
    assert result["driver_runtime_fingerprint_hash"] == "sha256:fake-pytorch-runtime"


def test_load_driver_rejects_unknown_driver() -> None:
    with pytest.raises(ValueError, match="unsupported driver_id"):
        load_driver_module.load_driver({"driver_id": "unknown"})


def test_resolve_driver_reference_alias() -> None:
    driver = load_driver_module.resolve_driver("reference")
    assert driver.driver_id == "reference"


def test_model_executor_reports_unsupported_driver_id() -> None:
    ir = {
        "ir_schema_hash": "sha256:uml_model_ir_demo",
        "nodes": [
            {"node_id": "input", "instr": "Input", "inputs": [], "shape_out": [1], "dtype": "float32"},
            {"node_id": "output", "instr": "Output", "inputs": [{"node_id": "input", "output_idx": 0}], "shape_out": [1], "dtype": "float32"},
        ],
        "outputs": [{"node_id": "output", "output_idx": 0}],
    }
    result = execute({"ir_dag": ir, "input_data": {"input": [1.0]}, "driver_id": "unknown"})
    assert "error" in result
    assert result["error"]["code_id"] == "PRIMITIVE_UNSUPPORTED"
