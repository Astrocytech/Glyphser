"""Deterministic Keras/TensorFlow CPU backend driver."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

_tf: Any
try:
    import tensorflow as _tf
except Exception:  # pragma: no cover - exercised when tensorflow is unavailable
    _tf = None


def _hash_payload(payload: Dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _to_tensor_cpu(value: Any) -> Any:
    if _tf is None:
        raise RuntimeError("tensorflow is not available")
    with _tf.device("/CPU:0"):
        return _tf.convert_to_tensor(value, dtype=_tf.float64)


def _to_python(value: Any) -> Any:
    if _tf is not None and isinstance(value, _tf.Tensor):
        return value.numpy().tolist()
    return value


class KerasCPUDriver:
    driver_id = "keras_cpu"

    def __init__(self) -> None:
        if _tf is None:
            raise RuntimeError("tensorflow is not available")
        _tf.random.set_seed(0)
        try:
            _tf.config.experimental.enable_op_determinism()
        except Exception:
            pass
        self.backend_binary_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "cpu",
                "version": _tf.__version__,
            }
        )
        self.runtime_fingerprint_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "cpu",
                "version": _tf.__version__,
                "deterministic_ops": True,
                "seed": 0,
            }
        )

    def supports(self, instr: str, mode: str) -> bool:
        return instr in {
            "Input",
            "Dense",
            "Conv1D",
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
        if _tf is None:
            raise RuntimeError("tensorflow is not available")

        if instr == "Input":
            if not inputs:
                raise ValueError("Input node missing input data")
            return _to_python(inputs[0]), rng_state
        if instr == "Identity":
            return _to_python(inputs[0]), rng_state
        if instr == "Output":
            return _to_python(inputs[0]), rng_state
        if instr == "Add":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                b = _to_tensor_cpu(inputs[1])
                return _to_python(a + b), rng_state
        if instr == "Mul":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                b = _to_tensor_cpu(inputs[1])
                return _to_python(a * b), rng_state
        if instr == "Relu":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                return _to_python(_tf.nn.relu(a)), rng_state
        if instr == "Sigmoid":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                return _to_python(_tf.math.sigmoid(a)), rng_state
        if instr == "MatMul":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                b = _to_tensor_cpu(inputs[1])
                return _to_python(_tf.linalg.matmul(a, b)), rng_state
        if instr == "ReduceSum":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                return _to_python(_tf.reshape(_tf.reduce_sum(a), [1])), rng_state
        if instr == "Reshape":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                shape = params.get("shape")
                if not isinstance(shape, list) or not shape:
                    raise ValueError("Reshape shape missing")
                return _to_python(_tf.reshape(a, shape)), rng_state
        if instr == "Transpose":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                perm = params.get("perm", [1, 0])
                if not isinstance(perm, list) or len(perm) != len(a.shape):
                    raise ValueError("Transpose perm mismatch")
                return _to_python(_tf.transpose(a, perm=perm)), rng_state
        if instr == "Softmax":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                axis = int(params.get("axis", -1))
                return _to_python(_tf.nn.softmax(a, axis=axis)), rng_state
        if instr == "LayerNorm":
            with _tf.device("/CPU:0"):
                a = _to_tensor_cpu(inputs[0])
                eps = float(params.get("eps", 1e-5))
                gamma = params.get("gamma")
                beta = params.get("beta")
                if gamma is None:
                    gamma = [1.0] * int(a.shape[-1])
                if beta is None:
                    beta = [0.0] * int(a.shape[-1])
                mean = _tf.reduce_mean(a, axis=-1, keepdims=True)
                var = _tf.reduce_mean(_tf.math.squared_difference(a, mean), axis=-1, keepdims=True)
                out = ((a - mean) / _tf.sqrt(var + eps)) * _to_tensor_cpu(gamma) + _to_tensor_cpu(beta)
                return _to_python(out), rng_state
        if instr == "MSELoss":
            with _tf.device("/CPU:0"):
                pred = _to_tensor_cpu(inputs[0])
                target = _to_tensor_cpu(inputs[1])
                out = _tf.reduce_mean(_tf.math.squared_difference(pred, target))
                return _to_python(_tf.reshape(out, [1])), rng_state
        if instr == "Dense":
            with _tf.device("/CPU:0"):
                x = _to_tensor_cpu(inputs[0])
                weights = params.get("weights") or theta.get("weights") or []
                bias = params.get("bias") or theta.get("bias") or 0.0
                if not weights:
                    raise ValueError("Dense weights missing")
                w = _to_tensor_cpu(weights)
                if len(w.shape) == 1:
                    out = _tf.reshape(_tf.reduce_sum(x * w), [1])
                else:
                    out = _tf.linalg.matvec(w, x)
                b = _to_tensor_cpu(bias)
                out = out + b
                return _to_python(out), rng_state
        if instr == "Conv1D":
            with _tf.device("/CPU:0"):
                x = _tf.reshape(_to_tensor_cpu(inputs[0]), [-1])
                kernel = _tf.reshape(_to_tensor_cpu(params.get("kernel") or []), [-1])
                if int(kernel.shape[0]) <= 0:
                    raise ValueError("Conv1D kernel missing")
                if int(x.shape[0]) < int(kernel.shape[0]):
                    raise ValueError("Conv1D input shorter than kernel")
                bias = float(params.get("bias", 0.0))
                out_len = int(x.shape[0] - kernel.shape[0] + 1)
                elems: list[Any] = []
                for i in range(out_len):
                    elems.append(_tf.reduce_sum(x[i : i + int(kernel.shape[0])] * kernel) + bias)
                out = _tf.stack(elems, axis=0)
                return _to_python(out), rng_state
        raise ValueError(f"unsupported instr: {instr}")


def get_keras_cpu_driver() -> KerasCPUDriver:
    return KerasCPUDriver()


def _to_tensor_gpu(value: Any) -> Any:
    if _tf is None:
        raise RuntimeError("tensorflow is not available")
    with _tf.device("/GPU:0"):
        return _tf.convert_to_tensor(value, dtype=_tf.float64)


class KerasGPUDriver:
    driver_id = "keras_gpu"

    def __init__(self) -> None:
        if _tf is None:
            raise RuntimeError("tensorflow is not available")
        gpus = _tf.config.list_physical_devices("GPU")
        if not gpus:
            raise RuntimeError("tensorflow gpu is not available")
        try:
            for gpu in gpus:
                _tf.config.experimental.set_memory_growth(gpu, True)
        except Exception:
            pass
        _tf.random.set_seed(0)
        try:
            _tf.config.experimental.enable_op_determinism()
        except Exception:
            pass
        self.backend_binary_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "gpu",
                "version": _tf.__version__,
                "gpu_count": len(gpus),
            }
        )
        self.runtime_fingerprint_hash = _hash_payload(
            {
                "runtime": "tensorflow",
                "device": "gpu",
                "version": _tf.__version__,
                "deterministic_ops": True,
                "seed": 0,
                "gpu_count": len(gpus),
            }
        )

    def supports(self, instr: str, mode: str) -> bool:
        return instr in {
            "Input",
            "Dense",
            "Conv1D",
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
        if _tf is None:
            raise RuntimeError("tensorflow is not available")
        if instr == "Input":
            if not inputs:
                raise ValueError("Input node missing input data")
            return _to_python(inputs[0]), rng_state
        if instr == "Identity":
            return _to_python(inputs[0]), rng_state
        if instr == "Output":
            return _to_python(inputs[0]), rng_state
        if instr == "Add":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                b = _to_tensor_gpu(inputs[1])
                return _to_python(a + b), rng_state
        if instr == "Mul":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                b = _to_tensor_gpu(inputs[1])
                return _to_python(a * b), rng_state
        if instr == "Relu":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                return _to_python(_tf.nn.relu(a)), rng_state
        if instr == "Sigmoid":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                return _to_python(_tf.math.sigmoid(a)), rng_state
        if instr == "MatMul":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                b = _to_tensor_gpu(inputs[1])
                return _to_python(_tf.linalg.matmul(a, b)), rng_state
        if instr == "ReduceSum":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                return _to_python(_tf.reshape(_tf.reduce_sum(a), [1])), rng_state
        if instr == "Reshape":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                shape = params.get("shape")
                if not isinstance(shape, list) or not shape:
                    raise ValueError("Reshape shape missing")
                return _to_python(_tf.reshape(a, shape)), rng_state
        if instr == "Transpose":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                perm = params.get("perm", [1, 0])
                if not isinstance(perm, list) or len(perm) != len(a.shape):
                    raise ValueError("Transpose perm mismatch")
                return _to_python(_tf.transpose(a, perm=perm)), rng_state
        if instr == "Softmax":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                axis = int(params.get("axis", -1))
                return _to_python(_tf.nn.softmax(a, axis=axis)), rng_state
        if instr == "LayerNorm":
            with _tf.device("/GPU:0"):
                a = _to_tensor_gpu(inputs[0])
                eps = float(params.get("eps", 1e-5))
                gamma = params.get("gamma")
                beta = params.get("beta")
                if gamma is None:
                    gamma = [1.0] * int(a.shape[-1])
                if beta is None:
                    beta = [0.0] * int(a.shape[-1])
                mean = _tf.reduce_mean(a, axis=-1, keepdims=True)
                var = _tf.reduce_mean(_tf.math.squared_difference(a, mean), axis=-1, keepdims=True)
                out = ((a - mean) / _tf.sqrt(var + eps)) * _to_tensor_gpu(gamma) + _to_tensor_gpu(beta)
                return _to_python(out), rng_state
        if instr == "MSELoss":
            with _tf.device("/GPU:0"):
                pred = _to_tensor_gpu(inputs[0])
                target = _to_tensor_gpu(inputs[1])
                out = _tf.reduce_mean(_tf.math.squared_difference(pred, target))
                return _to_python(_tf.reshape(out, [1])), rng_state
        if instr == "Dense":
            with _tf.device("/GPU:0"):
                x = _to_tensor_gpu(inputs[0])
                weights = params.get("weights") or theta.get("weights") or []
                bias = params.get("bias") or theta.get("bias") or 0.0
                if not weights:
                    raise ValueError("Dense weights missing")
                w = _to_tensor_gpu(weights)
                if len(w.shape) == 1:
                    out = _tf.reshape(_tf.reduce_sum(x * w), [1])
                else:
                    out = _tf.linalg.matvec(w, x)
                b = _to_tensor_gpu(bias)
                out = out + b
                return _to_python(out), rng_state
        if instr == "Conv1D":
            with _tf.device("/GPU:0"):
                x = _tf.reshape(_to_tensor_gpu(inputs[0]), [-1])
                kernel = _tf.reshape(_to_tensor_gpu(params.get("kernel") or []), [-1])
                if int(kernel.shape[0]) <= 0:
                    raise ValueError("Conv1D kernel missing")
                if int(x.shape[0]) < int(kernel.shape[0]):
                    raise ValueError("Conv1D input shorter than kernel")
                bias = float(params.get("bias", 0.0))
                out_len = int(x.shape[0] - kernel.shape[0] + 1)
                elems: list[Any] = []
                for i in range(out_len):
                    elems.append(_tf.reduce_sum(x[i : i + int(kernel.shape[0])] * kernel) + bias)
                out = _tf.stack(elems, axis=0)
                return _to_python(out), rng_state
        raise ValueError(f"unsupported instr: {instr}")


def get_keras_gpu_driver() -> KerasGPUDriver:
    return KerasGPUDriver()
