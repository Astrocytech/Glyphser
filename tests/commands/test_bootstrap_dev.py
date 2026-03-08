from __future__ import annotations

import json
from pathlib import Path

from tooling.commands import bootstrap_dev

ROOT = Path(__file__).resolve().parents[2]


def test_bootstrap_dev_verify_only():
    rc = bootstrap_dev.main([])
    assert rc in (0, 1)

    out = json.loads((ROOT / "evidence" / "dev" / "bootstrap.json").read_text(encoding="utf-8"))
    assert "status" in out
    assert isinstance(out["results"], list)
