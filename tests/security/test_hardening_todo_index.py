from __future__ import annotations

from pathlib import Path

from tooling.security import hardening_todo_index


def test_hardening_todo_index_inserts_index_block(tmp_path: Path) -> None:
    todo = tmp_path / "todo.txt"
    todo.write_text("A. Section\n[ ] p\n[~] ip\n[x] d\n", encoding="utf-8")
    assert hardening_todo_index.main(["--todo", str(todo)]) == 0
    out = todo.read_text(encoding="utf-8")
    assert "<HARDENING_INDEX_BEGIN>" in out
    assert "A 1/1/1" in out


def test_hardening_todo_index_updates_existing_block(tmp_path: Path) -> None:
    todo = tmp_path / "todo.txt"
    todo.write_text(
        "\n".join(
            [
                "<HARDENING_INDEX_BEGIN>",
                "old",
                "<HARDENING_INDEX_END>",
                "",
                "B. Section",
                "[ ] p",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    assert hardening_todo_index.main(["--todo", str(todo)]) == 0
    out = todo.read_text(encoding="utf-8")
    assert "old" not in out
    assert "B 1/0/0" in out
