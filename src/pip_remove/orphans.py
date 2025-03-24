import shutil
import subprocess
from pathlib import Path
from typing import Any, cast
import ast
import os
import shlex
import git


def get_environment_python_path() -> Path:
    unix_python = shutil.which("python")
    windows_python = shutil.which("py")

    if unix_python is not None:
        return Path(unix_python)
    elif windows_python is not None:
        return Path(windows_python)

    print("No Python found in the environment!")
    exit(1)


def get_site_packages_dir() -> Path:
    python_path = get_environment_python_path()
    source = (
        "import site;"
        "site_packages_dir, *_ = site.getsitepackages();"
        "print(site_packages_dir)"
    )

    output = subprocess.run(
        [python_path.absolute().__str__(), "-c", source],
        capture_output=True,
        text=True,
        shell=True,
    ).stdout.strip()

    return Path(output)


def get_pip_show_fields(
    package_name: str, python_executable_path: Path
) -> dict[str, str | list[str]]:
    completed_process = subprocess.run(
        [
            python_executable_path.absolute().__str__(),
            "-m",
            "pip",
            "show",
            package_name,
        ],
        capture_output=True,
        text=True,
    )
    pip_show_output = completed_process.stdout.strip()

    lines = pip_show_output.splitlines()
    fields: dict[str, str | list[str]] = {}
    for line in lines:
        field, *values = line.split(":")
        value = ":".join(values)
        value = value.strip()

        if field in ("Required-By", "Requires"):
            value = [package.strip() for package in value.split(",")]
        fields[field] = value

    return fields


def get_package_parents(package_name: str, environment_python_path: Path) -> list[str]:
    fields = get_pip_show_fields(package_name, environment_python_path)

    return cast(list[str], fields.get("Required-By", []))


def get_package_requires(package_name: str, environment_python_path: Path) -> list[str]:
    fields = get_pip_show_fields(package_name, environment_python_path)

    return cast(list[str], fields.get("Requires", []))


def get_orphans_of_package(
    package_name: str, environment_python_path: Path
) -> list[str]:
    orphans = get_package_requires(package_name, environment_python_path)
    orphans = [
        orphan
        for orphan in orphans
        if len(get_package_parents(orphan, environment_python_path)) <= 1
    ]

    for orphan in orphans[:]:
        orphans.extend(get_package_requires(orphan, environment_python_path))

    return [orphan for orphan in orphans if orphan]


def get_imported_modules_in_directory(directory: Path) -> list[str]:
    imported_packages: list[str] = []

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import):
            imported_packages.append(node.names[0].name)
            return node

    visitor = ImportVisitor()

    repo = git.Repo(directory)
    source_files = repo.git.ls_files().splitlines()
    print(source_files)
    for file in source_files:
        if not file.endswith(".py"):
            continue
        source = Path(directory / file).read_text()
        tree = ast.parse(source)
        visitor.visit(tree)

    return imported_packages


def get_unused_orphans_of_package(
    package_name: str, environment_python_path: Path, project_directory: Path
) -> list[str]:
    all_orphans = get_orphans_of_package(package_name, environment_python_path)
    imported_modules = get_imported_modules_in_directory(project_directory)
    print(imported_modules)

    for orphan in all_orphans[:]:
        for imported_module in imported_modules:
            if orphan == imported_module:
                all_orphans.remove(orphan)

    return all_orphans


if __name__ == "__main__":
    print(
        get_unused_orphans_of_package(
            "flask",
            Path("/home/axis/p/pip-remove/_temp/.venv/bin/python"),
            project_directory=Path("/home/axis/p/pip-remove/_temp/"),
        )
    )
