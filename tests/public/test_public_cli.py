from __future__ import annotations

import json

from glyphser.cli import main


def _write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_verify_cli_json_output(tmp_path, capsys):
    model_path = tmp_path / "model.json"
    input_path = tmp_path / "input.json"

    _write_json(
        model_path,
        {
            "ir_hash": "cli-ir",
            "nodes": [{"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"}],
            "outputs": [{"node_id": "x", "output_idx": 0}],
        },
    )
    _write_json(input_path, {"x": [1.0]})

    rc = main(
        [
            "verify",
            "--model",
            str(model_path),
            "--input",
            str(input_path),
            "--format",
            "json",
        ]
    )
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert rc == 0
    assert payload["status"] == "PASS"
    assert len(payload["digest"]) == 64


def test_verify_hello_core_target(capsys):
    rc = main(["verify", "hello-core", "--format", "json"])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["fixture"] == "hello-core"


def test_run_hello_alias(capsys):
    rc = main(["run", "--example", "hello", "--format", "json"])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert rc == 0
    assert payload["status"] == "PASS"
    assert payload["fixture"] == "hello-core"


def test_snapshot_cli_writes_manifest(tmp_path):
    model_path = tmp_path / "model.json"
    input_path = tmp_path / "input.json"
    out_path = tmp_path / "snapshot.json"

    _write_json(
        model_path,
        {
            "ir_hash": "cli-ir",
            "nodes": [{"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"}],
            "outputs": [{"node_id": "x", "output_idx": 0}],
        },
    )
    _write_json(input_path, {"x": [1.0]})

    rc = main(
        [
            "snapshot",
            "--model",
            str(model_path),
            "--input",
            str(input_path),
            "--out",
            str(out_path),
        ]
    )
    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert len(payload["digest"]) == 64
    assert payload["input_data"] == {"x": [1.0]}
