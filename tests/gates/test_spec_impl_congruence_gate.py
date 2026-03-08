from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import spec_impl_congruence_gate

ROOT = Path(__file__).resolve().parents[2]


def test_spec_impl_congruence_gate_passes():
    report = spec_impl_congruence_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads(
        (ROOT / "evidence" / "gates" / "structure" / "spec_impl_congruence.json").read_text(encoding="utf-8")
    )
    assert emitted["status"] == "PASS"
