import os
import tarfile
import tempfile


def bad_extract(tf: tarfile.TarFile, target: str) -> None:
    tf.extractall(target)


def bad_temp() -> str:
    return tempfile.mktemp(prefix="glyphser-")


def bad_mode(path: str) -> None:
    os.chmod(path, 0o777)
