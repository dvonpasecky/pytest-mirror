"""Command-line interface for pytest-mirror.

Provides commands to generate and validate mirrored test structure for a package.
"""

import argparse
from pathlib import Path

from .core import generate_missing_tests
from .plugin_manager import get_plugin_manager


def validate_missing_tests(package_dir: Path, tests_dir: Path) -> None:
    """Validate if any tests are missing without generating files.

    Args:
        package_dir (Path): Path to the package directory to check.
        tests_dir (Path): Path to the tests directory to check against.
    """
    pm = get_plugin_manager()
    missing_tests_nested = pm.hook.validate_test_structure(
        package_dir=package_dir,
        tests_dir=tests_dir,
    )
    missing_tests = [item for sublist in missing_tests_nested for item in sublist]

    if missing_tests:
        print("[MIRROR] Missing tests detected:")
        for path in missing_tests:
            print(f"  - {path}")
    else:
        print("[MIRROR] All tests are in place!")


def detect_default_package_dir() -> Path:
    """Detect the default package directory to mirror.

    Returns:
        Path: Path to the detected package directory.
    """
    cwd = Path.cwd()
    src = cwd / "src"
    if src.exists() and src.is_dir():
        subdirs = [
            d for d in src.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        if subdirs:
            return subdirs[0]
    # fallback: first subdir in cwd
    subdirs = [
        d
        for d in cwd.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "src"
    ]
    if subdirs:
        return subdirs[0]
    # fallback: cwd
    return cwd


def parse_cli_args():
    """Parse CLI arguments for pytest-mirror."""
    parser = argparse.ArgumentParser(
        prog="pytest-mirror", description="Mirror test structure enforcement tool."
    )

    parser.add_argument(
        "command",
        choices=["generate", "validate"],
        help="Command to run: 'generate' missing tests or 'validate' only.",
    )

    parser.add_argument(
        "--package-dir",
        type=Path,
        default=detect_default_package_dir(),
        help="Path to the main package directory (default: first subdir in ./src or ./)",
    )

    parser.add_argument(
        "--tests-dir",
        type=Path,
        default=Path.cwd() / "tests",
        help="Path to the tests directory (default: ./tests)",
    )

    return parser.parse_args()


def main() -> None:
    """CLI entry point for pytest-mirror.

    Handles argument parsing and dispatches to generate or validate commands.
    """
    args = parse_cli_args()

    print(f"[MIRROR] Using package_dir: {args.package_dir}")
    print(f"[MIRROR] Using tests_dir: {args.tests_dir}")

    if args.command == "generate":
        generate_missing_tests(args.package_dir, args.tests_dir)
    elif args.command == "validate":
        validate_missing_tests(args.package_dir, args.tests_dir)
