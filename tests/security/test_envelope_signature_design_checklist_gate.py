from __future__ import annotations

import json
from pathlib import Path

from tooling.security import envelope_signature_design_checklist_gate


def test_envelope_signature_design_checklist_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    gov.mkdir(parents=True)
    sec.mkdir(parents=True)
    checklist = gov / "ENVELOPE_SIGNATURE_MULTI_SIGNER_CHECKLIST.md"
    checklist.write_text(
        "\n".join(
            [
                "- [x] canonical envelope structure",
                "- [x] signer identity requirements",
                "- [x] deterministic signer ordering",
                "- [x] threshold policy (`M-of-N`)",
                "- [x] signer role separation constraints",
                "- [x] key rotation behavior",
                "- [x] revocation behavior",
                "- [x] partial signature failure semantics",
                "- [x] replay protection requirements",
                "- [x] verification evidence output format",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(envelope_signature_design_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(
        envelope_signature_design_checklist_gate,
        "CHECKLIST",
        checklist,
    )
    monkeypatch.setattr(envelope_signature_design_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert envelope_signature_design_checklist_gate.main([]) == 0


def test_envelope_signature_design_checklist_gate_fails_when_missing_requirements(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    gov.mkdir(parents=True)
    sec.mkdir(parents=True)
    checklist = gov / "ENVELOPE_SIGNATURE_MULTI_SIGNER_CHECKLIST.md"
    checklist.write_text("- [x] canonical envelope structure\n", encoding="utf-8")
    monkeypatch.setattr(envelope_signature_design_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(
        envelope_signature_design_checklist_gate,
        "CHECKLIST",
        checklist,
    )
    monkeypatch.setattr(envelope_signature_design_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert envelope_signature_design_checklist_gate.main([]) == 1
    report = json.loads((sec / "envelope_signature_design_checklist_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_checklist_requirement:") for item in report["findings"])
