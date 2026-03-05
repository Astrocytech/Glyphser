from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import governance_compliance_quarterly_snapshot


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_quarterly_snapshot_is_signed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "tooling" / "security").mkdir(parents=True, exist_ok=True)
    sec.mkdir(parents=True, exist_ok=True)

    (repo / "tooling" / "security" / "security_super_gate_manifest.json").write_text("{}\n", encoding="utf-8")
    (repo / "governance" / "security" / "GATE_RUNBOOK_INDEX.md").write_text("# index\n", encoding="utf-8")
    (repo / "glyphser_security_hardening_master_todo.txt").write_text("[x] done\n", encoding="utf-8")
    _write(
        repo / "governance" / "security" / "governance_compliance_baseline.json",
        {
            "schema_version": 1,
            "controls": [
                {
                    "id": "CTRL-MANIFEST",
                    "type": "file_exists",
                    "path": "tooling/security/security_super_gate_manifest.json",
                }
            ],
        },
    )

    monkeypatch.setattr(governance_compliance_quarterly_snapshot, "ROOT", repo)
    monkeypatch.setattr(governance_compliance_quarterly_snapshot, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(governance_compliance_quarterly_snapshot.compliance_delta, "ROOT", repo)
    monkeypatch.setattr(
        governance_compliance_quarterly_snapshot.compliance_delta,
        "BASELINE_POLICY",
        repo / "governance/security/governance_compliance_baseline.json",
    )
    monkeypatch.setattr(governance_compliance_quarterly_snapshot.compliance_delta, "evidence_root", lambda: repo / "evidence")

    assert governance_compliance_quarterly_snapshot.main([]) == 0
    snapshot = sec / "governance_compliance_quarterly_snapshot.json"
    signature = (sec / "governance_compliance_quarterly_snapshot.json.sig").read_text(encoding="utf-8").strip()
    assert verify_file(snapshot, signature, key=current_key(strict=False))


def test_quarterly_snapshot_warns_when_source_is_warn(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(governance_compliance_quarterly_snapshot, "ROOT", repo)
    monkeypatch.setattr(governance_compliance_quarterly_snapshot, "evidence_root", lambda: repo / "evidence")

    # Replace source generator with a deterministic WARN source.
    def _fake_main(argv):
        _ = argv
        _write(sec / "governance_compliance_delta_report.json", {"status": "WARN"})
        return 0

    monkeypatch.setattr(governance_compliance_quarterly_snapshot.compliance_delta, "main", _fake_main)

    assert governance_compliance_quarterly_snapshot.main([]) == 0
    report = json.loads((sec / "governance_compliance_quarterly_snapshot.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert "source_compliance_status:WARN" in report["findings"]
