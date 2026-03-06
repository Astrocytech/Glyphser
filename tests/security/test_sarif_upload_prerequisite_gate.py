from __future__ import annotations

import json
from pathlib import Path

from tooling.security import sarif_upload_prerequisite_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_sarif_upload_prerequisite_gate_passes_when_outputs_exist_before_upload(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Convert Bandit JSON to SARIF",
                "        run: python tooling/security/bandit_json_to_sarif.py --input bandit.json --output bandit.sarif",
                "      - name: Semgrep (SARIF)",
                "        run: semgrep --sarif --output semgrep.sarif runtime",
                "      - name: Upload Bandit SARIF to Code Scanning",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: bandit.sarif",
                "      - name: Upload SARIF to Code Scanning",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: semgrep.sarif",
            ]
        )
        + "\n",
    )
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", "jobs:\n  security-maintenance:\n    steps:\n")

    monkeypatch.setattr(sarif_upload_prerequisite_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_upload_prerequisite_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_upload_prerequisite_gate.main([]) == 0


def test_sarif_upload_prerequisite_gate_fails_when_upload_precedes_producer(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Upload SARIF to Code Scanning",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          sarif_file: semgrep.sarif",
                "      - name: Semgrep (SARIF)",
                "        run: semgrep --sarif --output semgrep.sarif runtime",
            ]
        )
        + "\n",
    )
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", "jobs:\n  security-maintenance:\n    steps:\n")

    monkeypatch.setattr(sarif_upload_prerequisite_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_upload_prerequisite_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_upload_prerequisite_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "sarif_upload_prerequisite_gate.json").read_text(encoding="utf-8"))
    assert "missing_prior_sarif_output:.github/workflows/ci.yml:Upload SARIF to Code Scanning:semgrep.sarif" in report[
        "findings"
    ]


def test_sarif_upload_prerequisite_gate_fails_when_sarif_file_input_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Upload SARIF to Code Scanning",
                "        uses: github/codeql-action/upload-sarif@x",
                "        with:",
                "          category: semgrep",
            ]
        )
        + "\n",
    )
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", "jobs:\n  security-maintenance:\n    steps:\n")

    monkeypatch.setattr(sarif_upload_prerequisite_gate, "ROOT", repo)
    monkeypatch.setattr(sarif_upload_prerequisite_gate, "evidence_root", lambda: repo / "evidence")
    assert sarif_upload_prerequisite_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "sarif_upload_prerequisite_gate.json").read_text(encoding="utf-8"))
    assert "missing_sarif_file_input:.github/workflows/ci.yml:Upload SARIF to Code Scanning" in report["findings"]
