import subprocess

from pathlib import Path
import os


def test_python_path_detection():
    # unix only for now..

    env = os.environ.copy()
    env["VIRTUAL_ENV"] = "_temp/.venv/"
    env["PATH"] = f"_temp/.venv/bin:{env['PATH']}"

    python_path = subprocess.run(
        [".venv/bin/pip-remove", "getenv"], env=env, text=True, capture_output=True
    ).stdout.strip()

    assert Path(python_path).resolve(strict=True) == Path(
        "_temp/.venv/bin/python"
    ).resolve(strict=True)
