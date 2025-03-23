import shutil
import subprocess
from pathlib import Path
from typing import cast


import libcst as cst
from libcst._nodes.statement import ImportFrom


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


class Visitor(cst.CSTVisitor):
    def __init__(self, user_defined_modules: set[str]) -> None:
        super().__init__()
        self.user_defined_modules = user_defined_modules
        self.imports = set()

    def recursive_value(self, node) -> str:
        if isinstance(node, str):
            return node
        return self.recursive_value(node.value)

    def visit_Import(self, node: cst.CSTNode):
        for alias in node.names:
            package = self.recursive_value(alias.name.value)
            if package not in self.user_defined_modules:
                self.imports.add(package)

    def visit_ImportFrom(self, node: ImportFrom) -> bool | None:
        if not hasattr(node.module, "value"):
            return
        package = self.recursive_value(node.module.value)
        if package not in self.user_defined_modules:
            self.imports.add(package)


def is_ignored_folder(path, ignored_folders):
    return any(folder in path.parts for folder in ignored_folders)


def get_non_builtin_imports(directory: Path = Path()) -> list[str]:
    ignored_folders = {"venv", "__pycache__"}
    files = [
        file
        for file in directory.rglob("*.py")
        if not is_ignored_folder(file, ignored_folders)
    ]
    user_defined_modules = {
        str(file.parent.stem)
        for file in files
        if file.name in {"__main__.py", "__init__.py"}
    }
    user_defined_modules.update({file.stem for file in files})

    imports = set()
    for file in files:
        try:
            node = cst.parse_module(file.read_text())
        except UnicodeDecodeError:
            continue
        visitor = Visitor(user_defined_modules)
        node.visit(visitor)
        imports.update(visitor.imports)

    return sorted(imports)


# TODO
def get_unused_orphans_of_package(
    package_name: str, environment_python_path: Path
) -> list[str]:
    all_orphans = get_orphans_of_package(package_name, environment_python_path)

    return [orphan for orphan in all_orphans]


if __name__ == "__main__":
    print(
        get_unused_orphans_of_package(
            "flask", Path("/home/axis/p/pip-remove/_temp/.venv/bin/python")
        )
    )
