import os
import subprocess
import tempfile
import yaml


def safe_subprocess(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=False, shell=False, capture_output=True, text=True)


def safe_yaml(blob: str) -> object:
    return yaml.safe_load(blob)


def safe_exec_free(text: str) -> str:
    return text.upper()


def safe_tempfile() -> str:
    fd, path = tempfile.mkstemp(prefix="glyphser-")
    os.close(fd)
    return path
