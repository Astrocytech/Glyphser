"""Deterministic PyTorch CPU backend driver."""
from __future__ import annotations

import hashlib
import json
import os
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
            "MatMul",
            "ReduceSum",
            "Reshape",
            "Transpose",
            "Softmax",
            "LayerNorm",
            "MSELoss",
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
        if instr == "MatMul":
            a = _to_tensor(inputs[0])
            b = _to_tensor(inputs[1])
            return _to_python(_torch.matmul(a, b)), rng_state
        if instr == "ReduceSum":
            a = _to_tensor(inputs[0])
            return _to_python(_torch.reshape(_torch.sum(a), (1,))), rng_state
        if instr == "Reshape":
            a = _to_tensor(inputs[0])
            shape = params.get("shape")
            if not isinstance(shape, list) or not shape:
                raise ValueError("Reshape shape missing")
            return _to_python(_torch.reshape(a, shape)), rng_state
        if instr == "Transpose":
            a = _to_tensor(inputs[0])
            perm = params.get("perm", [1, 0])
            if not isinstance(perm, list) or len(perm) != a.ndim:
                raise ValueError("Transpose perm mismatch")
            return _to_python(_torch.permute(a, tuple(int(x) for x in perm))), rng_state
        if instr == "Softmax":
            a = _to_tensor(inputs[0])
            axis = int(params.get("axis", -1))
            return _to_python(_torch.softmax(a, dim=axis)), rng_state
        if instr == "LayerNorm":
            a = _to_tensor(inputs[0])
            eps = float(params.get("eps", 1e-5))
            gamma = params.get("gamma")
            beta = params.get("beta")
            normalized_shape = (a.shape[-1],)
            weight = _to_tensor(gamma) if gamma is not None else None
            bias = _to_tensor(beta) if beta is not None else None
            out = _torch.nn.functional.layer_norm(a, normalized_shape, weight=weight, bias=bias, eps=eps)
            return _to_python(out), rng_state
        if instr == "MSELoss":
            pred = _to_tensor(inputs[0])
            target = _to_tensor(inputs[1])
            out = _torch.mean((pred - target) ** 2)
            return _to_python(_torch.reshape(out, (1,))), rng_state
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


class PyTorchGPUDriver:
    driver_id = "pytorch_gpu"

    def __init__(self) -> None:
        if _torch is None:
            raise RuntimeError("pytorch is not available")
        if not _torch.cuda.is_available():
            raise RuntimeError("cuda is not available")
        # Required by PyTorch for deterministic CUDA matmul kernels.
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        _torch.use_deterministic_algorithms(True)
        _torch.backends.cudnn.deterministic = True
        _torch.backends.cudnn.benchmark = False
        self.backend_binary_hash = _hash_payload({"runtime": "pytorch", "device": "cuda", "version": _torch.__version__})
        self.runtime_fingerprint_hash = _hash_payload(
            {
                "runtime": "pytorch",
                "device": "cuda",
                "version": _torch.__version__,
                "deterministic_algorithms": True,
                "cudnn_deterministic": True,
                "cudnn_benchmark": False,
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
            "MatMul",
            "ReduceSum",
            "Reshape",
            "Transpose",
            "Softmax",
            "LayerNorm",
            "MSELoss",
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
            a, b = (_to_tensor_cuda(inputs[0]), _to_tensor_cuda(inputs[1]))
            return _to_python(a + b), rng_state
        if instr == "Mul":
            a, b = (_to_tensor_cuda(inputs[0]), _to_tensor_cuda(inputs[1]))
            return _to_python(a * b), rng_state
        if instr == "Relu":
            a = _to_tensor_cuda(inputs[0])
            return _to_python(_torch.relu(a)), rng_state
        if instr == "Sigmoid":
            a = _to_tensor_cuda(inputs[0])
            return _to_python(_torch.sigmoid(a)), rng_state
        if instr == "MatMul":
            a = _to_tensor_cuda(inputs[0])
            b = _to_tensor_cuda(inputs[1])
            return _to_python(_torch.matmul(a, b)), rng_state
        if instr == "ReduceSum":
            a = _to_tensor_cuda(inputs[0])
            return _to_python(_torch.reshape(_torch.sum(a), (1,))), rng_state
        if instr == "Reshape":
            a = _to_tensor_cuda(inputs[0])
            shape = params.get("shape")
            if not isinstance(shape, list) or not shape:
                raise ValueError("Reshape shape missing")
            return _to_python(_torch.reshape(a, shape)), rng_state
        if instr == "Transpose":
            a = _to_tensor_cuda(inputs[0])
            perm = params.get("perm", [1, 0])
            if not isinstance(perm, list) or len(perm) != a.ndim:
                raise ValueError("Transpose perm mismatch")
            return _to_python(_torch.permute(a, tuple(int(x) for x in perm))), rng_state
        if instr == "Softmax":
            a = _to_tensor_cuda(inputs[0])
            axis = int(params.get("axis", -1))
            return _to_python(_torch.softmax(a, dim=axis)), rng_state
        if instr == "LayerNorm":
            a = _to_tensor_cuda(inputs[0])
            eps = float(params.get("eps", 1e-5))
            gamma = params.get("gamma")
            beta = params.get("beta")
            normalized_shape = (a.shape[-1],)
            weight = _to_tensor_cuda(gamma) if gamma is not None else None
            bias = _to_tensor_cuda(beta) if beta is not None else None
            out = _torch.nn.functional.layer_norm(a, normalized_shape, weight=weight, bias=bias, eps=eps)
            return _to_python(out), rng_state
        if instr == "MSELoss":
            pred = _to_tensor_cuda(inputs[0])
            target = _to_tensor_cuda(inputs[1])
            out = _torch.mean((pred - target) ** 2)
            return _to_python(_torch.reshape(out, (1,))), rng_state
        if instr == "Dense":
            x = _to_tensor_cuda(inputs[0])
            weights = params.get("weights") or theta.get("weights") or []
            bias = params.get("bias") or theta.get("bias") or 0.0
            if not weights:
                raise ValueError("Dense weights missing")
            w = _to_tensor_cuda(weights)
            if w.ndim == 1:
                out = (x * w).sum().reshape(1)
            else:
                out = _torch.matmul(w, x)
            b = _to_tensor_cuda(bias)
            out = out + b
            return _to_python(out), rng_state
        raise ValueError(f"unsupported instr: {instr}")


def _to_tensor_cuda(value: Any) -> Any:
    if _torch is None:
        raise RuntimeError("pytorch is not available")
    if isinstance(value, _torch.Tensor):
        return value.to(dtype=_torch.float64, device="cuda")
    return _torch.tensor(value, dtype=_torch.float64, device="cuda")


def get_pytorch_gpu_driver() -> PyTorchGPUDriver:
    return PyTorchGPUDriver()
