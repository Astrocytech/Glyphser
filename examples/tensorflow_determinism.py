"""TensorFlow reproducibility sketch for Glyphser users."""

from __future__ import annotations

import hashlib
import json
import random

try:
    import numpy as np
    import tensorflow as tf
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("Install requirements: python -m pip install numpy tensorflow") from exc


def digest(payload: dict) -> str:
    blob = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run(seed: int) -> str:
    random.seed(seed)
    np.random.seed(seed)
    tf.keras.utils.set_random_seed(seed)

    x = np.array([[0.0], [1.0], [2.0], [3.0]], dtype=np.float32)
    y = np.array([[1.0], [3.0], [5.0], [7.0]], dtype=np.float32)

    model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(1,))])
    model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.05), loss="mse")
    model.fit(x, y, epochs=60, verbose=0)

    w, b = model.layers[0].get_weights()
    payload = {
        "weight": float(np.round(w.flatten()[0], 8)),
        "bias": float(np.round(b.flatten()[0], 8)),
    }
    return digest(payload)


def main() -> int:
    d1 = run(7)
    d2 = run(7)
    d3 = run(99)
    result = {
        "same_seed_match": d1 == d2,
        "different_seed_diverges": d1 != d3,
        "digest_same_a": d1,
        "digest_same_b": d2,
        "digest_diff": d3,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["same_seed_match"] and result["different_seed_diverges"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
