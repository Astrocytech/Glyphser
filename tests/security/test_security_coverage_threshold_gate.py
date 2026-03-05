from __future__ import annotations

from pathlib import Path

from tooling.security import security_coverage_threshold_gate


def _write_coverage(path: Path, *, covered: int, total: int) -> None:
    lines = []
    for ix in range(total):
        hits = 1 if ix < covered else 0
        lines.append(f'<line number="{ix + 1}" hits="{hits}"/>')
    xml = (
        "<coverage><packages><package><classes>"
        '<class filename="tooling/security/demo_gate.py"><lines>'
        + "".join(lines)
        + "</lines></class>"
        "</classes></package></packages></coverage>"
    )
    path.write_text(xml, encoding="utf-8")


def test_security_coverage_threshold_gate_passes(monkeypatch, tmp_path: Path) -> None:
    coverage = tmp_path / "coverage.xml"
    _write_coverage(coverage, covered=90, total=100)
    monkeypatch.setattr(security_coverage_threshold_gate, "evidence_root", lambda: tmp_path / "evidence")
    assert security_coverage_threshold_gate.main(["--coverage-file", str(coverage), "--min-pct", "85"]) == 0


def test_security_coverage_threshold_gate_fails_when_below_threshold(monkeypatch, tmp_path: Path) -> None:
    coverage = tmp_path / "coverage.xml"
    _write_coverage(coverage, covered=40, total=100)
    monkeypatch.setattr(security_coverage_threshold_gate, "evidence_root", lambda: tmp_path / "evidence")
    assert security_coverage_threshold_gate.main(["--coverage-file", str(coverage), "--min-pct", "85"]) == 1
