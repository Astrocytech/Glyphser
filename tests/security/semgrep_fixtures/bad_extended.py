import os
import subprocess
import tempfile
import yaml


def reason_shell_true(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=False)


def reason_dynamic_eval(expr: str) -> object:
    return eval(expr)


def reason_dynamic_exec(code: str) -> None:
    exec(code)


def reason_unsafe_yaml(blob: str) -> object:
    return yaml.load(blob, Loader=yaml.Loader)


def reason_tempfile_delete_false() -> str:
    handle = tempfile.NamedTemporaryFile(prefix="glyphser-", delete=False)
    handle.close()
    return handle.name


def reason_world_writable_makedirs(path: str) -> None:
    os.makedirs(path, mode=0o777, exist_ok=True)
