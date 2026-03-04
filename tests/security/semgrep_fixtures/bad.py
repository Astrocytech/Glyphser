import os
import tarfile
import tempfile


def bad_extract(tf: tarfile.TarFile, target: str) -> None:
    tf.extractall(target)


def bad_temp() -> str:
    return tempfile.mktemp(prefix="glyphser-")


def bad_mode(path: str) -> None:
    os.chmod(path, 0o777)


def bad_tmp_handle() -> None:
    tempfile.NamedTemporaryFile(prefix="glyphser-", delete=False)


def bad_join(base: str, user: str) -> str:
    return os.path.join(base, user)


def bad_open_mode(path: str) -> int:
    return os.open(path, os.O_CREAT, 0o666)
