from __future__ import absolute_import
import os
import pytest
from pathlib import Path
import venv
import sys
import subprocess
import git


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
GITIGNORE_SOURCE = """
.venv/
__pycache__/
"""


@pytest.fixture(scope="session", autouse=True)
def create_dummy_project():
    if not TEMP_DIR.exists():
        os.mkdir(TEMP_DIR)

    main_file_path = TEMP_DIR / "main.py"

    if not main_file_path.exists():
        __ = main_file_path.write_text(DUMMY_SOURCE)

    gitignore_file_path = TEMP_DIR / ".gitignore"
    if not gitignore_file_path.exists():
        _ = gitignore_file_path.write_text(GITIGNORE_SOURCE)

    git_dir_path = TEMP_DIR / ".git"
    if not git_dir_path.exists():
        repo = git.Repo.init(TEMP_DIR)
        repo.git.add(str(main_file_path.absolute()))
        repo.git.add(str(gitignore_file_path.absolute()))

        _ = repo.index.commit("initial commit")


@pytest.fixture(scope="session", autouse=True)
def create_venv_for_dummy_project():
    if VENV_PATH.exists():
        return

    venv.create(VENV_PATH, with_pip=True)
    install_dummy_packages()


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
