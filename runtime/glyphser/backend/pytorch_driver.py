"""Deterministic PyTorch CPU backend driver."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

try:
    import torch as _torch
except Exception:  # pragma: no cover - exercised in runtime environments without torch
    _torch = None


class PyTorchCPUDriver:
    driver_id = "pytorch_cpu"

    def __init__(self) -> None:
        if _torch is None:
            raise RuntimeError("pytorch is not available")
        _torch.use_deterministic_algorithms(True)
        _torch.set_num_threads(1)
        self.backend_binary_hash = _hash_payload({"runtime": "pytorch", "device": "cpu", "version": _torch.__version__})
        self.runtime_fingerprint_hash = _hash_payload(
            {
                "runtime": "pytorch",
                "device": "cpu",
                "version": _torch.__version__,
                "deterministic_algorithms": True,
                "num_threads": 1,
            }
        )

    def supports(self, instr: str, mode: str) -> bool:
        return instr in {
            "Input",
            "Dense",
            "Add",
            "Mul",
            "Relu",
            "Sigmoid",
            "Identity",
            "Output",
        }

    def dispatch(
        self,
        instr: str,
        inputs: List[Any],
        params: Dict[str, Any],
        theta: Dict[str, Any],
        mode: str,
        rng_state: int,
    ) -> Tuple[Any, int]:
        if _torch is None:
            raise RuntimeError("pytorch is not available")
        if instr == "Input":
            if not inputs:
                raise ValueError("Input node missing input data")
            return _to_python(inputs[0]), rng_state
        if instr == "Identity":
            return _to_python(inputs[0]), rng_state
        if instr == "Output":
            return _to_python(inputs[0]), rng_state
        if instr == "Add":
            a, b = (_to_tensor(inputs[0]), _to_tensor(inputs[1]))
            return _to_python(a + b), rng_state
        if instr == "Mul":
            a, b = (_to_tensor(inputs[0]), _to_tensor(inputs[1]))
            return _to_python(a * b), rng_state
        if instr == "Relu":
            a = _to_tensor(inputs[0])
            return _to_python(_torch.relu(a)), rng_state
        if instr == "Sigmoid":
            a = _to_tensor(inputs[0])
            return _to_python(_torch.sigmoid(a)), rng_state
        if instr == "Dense":
            x = _to_tensor(inputs[0])
            weights = params.get("weights") or theta.get("weights") or []
            bias = params.get("bias") or theta.get("bias") or 0.0
            if not weights:
                raise ValueError("Dense weights missing")
            w = _to_tensor(weights)
            if w.ndim == 1:
                out = (x * w).sum().reshape(1)
            else:
                out = _torch.matmul(w, x)
            b = _to_tensor(bias)
            out = out + b
            return _to_python(out), rng_state
        raise ValueError(f"unsupported instr: {instr}")


def _hash_payload(payload: Dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _to_tensor(value: Any) -> Any:
    if _torch is None:
        raise RuntimeError("pytorch is not available")
    if isinstance(value, _torch.Tensor):
        return value.to(dtype=_torch.float64, device="cpu")
    return _torch.tensor(value, dtype=_torch.float64, device="cpu")


def _to_python(value: Any) -> Any:
    if _torch is not None and isinstance(value, _torch.Tensor):
        return value.detach().cpu().tolist()
    return value


def get_pytorch_cpu_driver() -> PyTorchCPUDriver:
    return PyTorchCPUDriver()
