import shutil
import subprocess
from pathlib import Path
from typing import cast
import ast
import git
from rich.console import Console


console = Console()


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
) -> set[str]:
    orphans = get_package_requires(package_name, environment_python_path)
    orphans = [
        orphan
        for orphan in orphans
        if len(get_package_parents(orphan, environment_python_path)) <= 1
    ]

    for orphan in orphans[:]:
        orphans.extend(get_package_requires(orphan, environment_python_path))

    return {orphan for orphan in orphans if orphan}


def get_python_env_directory(environment_python_path: Path) -> Path:
    source = "import sys;print(sys.prefix)"

    return Path(
        subprocess.check_output(
            [environment_python_path, "-c", source], text=True
        ).strip()
    )


def get_imported_modules_in_directory(
    directory: Path, environment_python_path: Path
) -> dict[str, set[str]]:
    try:
        repo = git.Repo(directory)
        source_files = repo.git.ls_files().splitlines()
    except git.InvalidGitRepositoryError:
        console.print(
            "no git repo found in current directory! scanning ALL non-venv files",
            style="yellow",
        )
        source_files = [str(file) for file in directory.rglob("*.py")]
    imported_packages: dict[str, set[str]] = {}

    current_file_name = ""

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import):
            nonlocal current_file_name
            imported_packages[current_file_name].add(node.names[0].name)
            return node

    visitor = ImportVisitor()

    env_path = get_python_env_directory(environment_python_path)
    for file in source_files:
        if not file.endswith(".py"):
            continue
        p = Path(file)
        if env_path.resolve() in p.resolve().parents:
            continue

        current_file_name = file
        imported_packages[current_file_name] = set()
        source = Path(directory / file).read_text()
        tree = ast.parse(source)
        visitor.visit(tree)

    return imported_packages


def is_python_in_venv(environment_python_path: Path) -> bool:
    source = "import sys;print(sys.prefix != sys.base_prefix)"

    result = subprocess.check_output(
        [environment_python_path, "-c", source], text=True
    ).strip()

    return True if result == "True" else False


def get_orphans(
    package_name: str, environment_python_path: Path, project_directory: Path
) -> tuple[dict[str, set[str]], set[str]]:
    all_orphans = get_orphans_of_package(package_name, environment_python_path)

    used_orphans: dict[str, set[str]] = {}
    unused_orphans: set[str] = set(all_orphans)

    if is_python_in_venv(environment_python_path):
        imported_modules = get_imported_modules_in_directory(
            project_directory, environment_python_path
        )
        for file, imported_modules in imported_modules.items():
            for orphan in set(all_orphans):
                for imported_module in imported_modules:
                    if orphan == imported_module:
                        if used_orphans.get(file) is None:
                            used_orphans[file] = set()
                        used_orphans[file].add(orphan)
                        unused_orphans.remove(orphan)
    else:
        console.print(
            "not inside a virtual environment, skipping orphan usage checks",
            style="yellow",
        )

    return used_orphans, unused_orphans


if __name__ == "__main__":
    print(
        get_orphans(
            "flask",
            Path("/home/axis/p/pip-remove/_temp/.venv/bin/python"),
            project_directory=Path("/home/axis/p/pip-remove/_temp/"),
        )
    )
