"""Scikit-learn reproducibility sketch for Glyphser users."""

from __future__ import annotations

import hashlib
import json

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("Install requirements: python -m pip install numpy scikit-learn") from exc


def digest(payload: dict) -> str:
    blob = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run(seed: int) -> str:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(32, 2))
    y = x[:, 0] * 2.0 + x[:, 1] * -0.5
    model = LinearRegression().fit(x, y)
    payload = {
        "coef": model.coef_.round(8).tolist(),
        "intercept": float(round(model.intercept_, 8)),
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
