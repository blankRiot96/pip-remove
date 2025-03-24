import argparse
from .remove import verify_and_remove


def main():
    parser = argparse.ArgumentParser(
        prog="pip-remove",
        description="Removes both the specified package and its orphans from the current environment.",
    )

    _ = parser.add_argument(
        "package_name", nargs="?", help="the name of the package to remove"
    )
    _ = parser.add_argument(
        "-y", action="store_true", help="skip questions and do the job"
    )

    args = parser.parse_args()
    package_name: str = args.package_name

    if package_name:
        verify_and_remove(package_name, getattr(args, "y"))
    else:
        parser.print_help()
