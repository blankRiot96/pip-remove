import shutil
import os
import pytest
from pathlib import Path
import venv
import sys
import subprocess


DUMMY_SOURCE = """
import flask
import click
"""
DUMMY_PACKAGES = ["flask==3.1.0"]

CACHE_DIR = (
    Path.home() / "AppData" / "Local" / "test_venv_cache"
    if sys.platform == "win32"
    else Path.home() / ".cache"
)
ROOT_DIR = Path(".")
TEMP_DIR = ROOT_DIR / "_temp/"
VENV_PATH = TEMP_DIR / ".venv/"
VENV_PYTHON_PATH = (
    VENV_PATH / "Scripts/python.exe"
    if sys.platform == "win32"
    else VENV_PATH / "bin/python"
)


@pytest.fixture(scope="session", autouse=True)
def create_dummy_project():
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    os.mkdir(TEMP_DIR)
    main_file_path = TEMP_DIR / "main.py"

    __ = main_file_path.write_text(DUMMY_SOURCE)


@pytest.fixture(scope="session", autouse=True)
def create_venv_for_dummy_project():
    venv.create(VENV_PATH, with_pip=True)


@pytest.fixture(scope="session", autouse=True)
def install_dummy_packages():
    for package in DUMMY_PACKAGES:
        _ = subprocess.run(
            [
                VENV_PYTHON_PATH,
                "-m",
                "pip",
                "install",
                package,
                "--cache-dir",
                str(CACHE_DIR),
            ]
        )


@pytest.fixture(scope="session", autouse=True)
def delete_dummy_project():
    yield

    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
