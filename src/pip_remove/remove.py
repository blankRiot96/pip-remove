from .orphans import get_orphans, get_environment_python_path
from pathlib import Path
from rich.console import Console

import subprocess


def verify_and_remove(package_name: str, skip: bool, scan: bool):
    python_path = get_environment_python_path()

    console = Console()
    console.print(f"environment python found: [green]{python_path}[/green]")

    used_orphans, unused_orphans = get_orphans(
        package_name, get_environment_python_path(), Path("."), scan
    )

    if used_orphans:
        print("some used orphans detected:")
        for file, orphans in used_orphans.items():
            print(f"    - {file}: ", end="")
            console.print(*orphans, sep=", ", style="bold green")

    console.print("\nall unused orphans: ", end="")
    console.print(*unused_orphans, sep=", ", style="bold red")

    if not skip:
        choice = (
            console.input(
                f"remove [bold red]{package_name}[/bold red] and its [bold red]{len(unused_orphans)}[/bold red] unused orphans? (Y/n): "
            )
            .strip()
            .lower()
            or "y"
        )
    else:
        choice = "y"

    if choice == "y":
        remove_package_and_unused_orphans(package_name, python_path, unused_orphans)
    else:
        console.print("\noperation cancelled by user.", style="yellow")


def uninstall_packages(python_path: Path, package_names: list[str]):
    command = [python_path, "-m", "pip", "uninstall", "-y"]
    command.extend(package_names)
    _ = subprocess.run(command)


def remove_package_and_unused_orphans(
    package_name: str, python_path: Path, orphans: set[str]
):
    packages = [package_name]
    packages.extend(orphans)
    uninstall_packages(python_path, packages)
