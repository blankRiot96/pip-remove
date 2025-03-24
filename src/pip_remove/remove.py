from .orphans import get_unused_orphans_of_package, get_environment_python_path
from pathlib import Path

import subprocess


def remove_package_and_unused_orphans(package_name: str):
    python_path = get_environment_python_path()
    orphans = get_unused_orphans_of_package(package_name, python_path, Path("."))

    _ = subprocess.run([python_path, "-m", "pip", "uninstall", package_name])
    for orphan in orphans:
        _ = subprocess.run([python_path, "-m", "pip", "uninstall", orphan])
