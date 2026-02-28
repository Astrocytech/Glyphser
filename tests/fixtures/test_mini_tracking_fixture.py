from __future__ import annotations

import json
from pathlib import Path

from src.glyphser.tracking.run_create import run_create
from src.glyphser.tracking.metric_log import metric_log
from src.glyphser.monitor.emit import monitor_emit

ROOT = Path(__file__).resolve().parents[2]


def test_mini_tracking_fixture():
    inputs = json.loads((ROOT / "artifacts" / "inputs" / "fixtures" / "mini-tracking" / "inputs.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "artifacts" / "expected" / "goldens" / "mini-tracking" / "expected.json").read_text(encoding="utf-8"))

    run_resp = run_create(inputs["run"])
    metric_resp = metric_log(inputs["metric"])
    monitor_resp = monitor_emit(inputs["monitor"])

    assert run_resp == expected["run_create"]
    assert metric_resp == expected["metric_log"]
    assert monitor_resp == expected["monitor_emit"]
