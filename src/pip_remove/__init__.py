import argparse
from .remove import remove_package_and_unused_orphans
from .orphans import get_environment_python_path


def main():
    parser = argparse.ArgumentParser(
        prog="pip-remove",
        description="Removes both the specified package and its orphans from the current environment.",
    )

    _ = parser.add_argument(
        "package_name", nargs="?", help="The name of the package to remove"
    )
    _ = parser.add_argument(
        "command",
        nargs="?",
        choices=["getenv"],
        help="Show the Python interpreter path of the current environment",
    )

    args = parser.parse_args()
    package_name: str = args.package_name

    if args.command == "getenv":
        print(get_environment_python_path().absolute())
    elif package_name:
        remove_package_and_unused_orphans(package_name)
