"""5-minute proof demo for Glyphser determinism.

Demonstrates:
1) Same seed => same digest
2) Different seed => different digest
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import numpy as np
except Exception as exc:  # pragma: no cover - optional dependency
    raise SystemExit("This demo requires numpy. Install with: python -m pip install numpy") from exc

try:
    import cbor2
except Exception:  # pragma: no cover - optional dependency
    cbor2 = None

from glyphser.internal.hashing import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "demo"


@dataclass(frozen=True)
class DemoEvidence:
    seed: int
    final_loss: float
    weight: float
    bias: float


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def run_train(seed: int) -> DemoEvidence:
    set_seed(seed)
    x = np.array([[0.0], [1.0], [2.0], [3.0]], dtype=np.float64)
    y = np.array([[1.0], [3.0], [5.0], [7.0]], dtype=np.float64)

    rng = np.random.default_rng(seed)
    weight = rng.normal()
    bias = rng.normal()
    lr = 0.05

    loss = 0.0
    for _ in range(120):
        pred = x * weight + bias
        error = pred - y
        grad_weight = float((2.0 / len(x)) * np.sum(error * x))
        grad_bias = float((2.0 / len(x)) * np.sum(error))
        weight -= lr * grad_weight
        bias -= lr * grad_bias
        loss = float(np.mean(error**2))

    return DemoEvidence(
        seed=seed,
        final_loss=loss,
        weight=float(weight),
        bias=float(bias),
    )


def write_manifest(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    (OUT / f"{name}.json").write_text(manifest_json, encoding="utf-8")
    if cbor2 is not None:
        (OUT / f"{name}.cbor").write_bytes(cbor2.dumps(payload))


def digest(ev: DemoEvidence) -> str:
    return canonical_sha256(asdict(ev))


def main() -> int:
    same_a = run_train(7)
    same_b = run_train(7)
    diff = run_train(99)

    d_same_a = digest(same_a)
    d_same_b = digest(same_b)
    d_diff = digest(diff)

    summary = {
        "same_seed_match": d_same_a == d_same_b,
        "different_seed_diverges": d_same_a != d_diff,
        "digest_same_a": d_same_a,
        "digest_same_b": d_same_b,
        "digest_diff": d_diff,
        "evidence_dir": str(OUT),
    }

    write_manifest("same_seed_run_a", asdict(same_a) | {"digest": d_same_a})
    write_manifest("same_seed_run_b", asdict(same_b) | {"digest": d_same_b})
    write_manifest("different_seed_run", asdict(diff) | {"digest": d_diff})
    write_manifest("summary", summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["same_seed_match"] or not summary["different_seed_diverges"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
