from __future__ import annotations

import json
from pathlib import Path

from tooling.security import secret_scan_gate


def test_secret_scan_gate_passes_clean_tree(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "runtime").mkdir(parents=True)
    (repo / "runtime" / "clean.py").write_text("x = 1\n", encoding="utf-8")

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(secret_scan_gate, "ROOT", repo)
    monkeypatch.setattr(secret_scan_gate, "evidence_root", lambda: out_root)

    rc = secret_scan_gate.main()
    assert rc == 0
    report = json.loads((out_root / "security" / "secret_scan.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["finding_count"] == 0


def test_secret_scan_gate_fails_on_private_key(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "tooling").mkdir(parents=True)
    private_key_marker = "-----BEGIN " + "PRIVATE KEY-----"
    (repo / "tooling" / "bad.py").write_text(
        f'PRIVATE = "{private_key_marker}"\n',
        encoding="utf-8",
    )

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(secret_scan_gate, "ROOT", repo)
    monkeypatch.setattr(secret_scan_gate, "evidence_root", lambda: out_root)

    rc = secret_scan_gate.main()
    assert rc == 1
    report = json.loads((out_root / "security" / "secret_scan.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["finding_count"] == 1
