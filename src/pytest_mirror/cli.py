"""Command-line interface for pytest-mirror.

Provides commands to generate and validate mirrored test structure for a package.
"""

import argparse
import sys
import tomllib
from pathlib import Path

from .core import generate_missing_tests
from .plugin_manager import get_plugin_manager

# Constants
MIRROR_PREFIX = "[MIRROR]"
ERROR_PREFIX = "[ERROR]"
USAGE_MESSAGE = (
    "usage: pytest-mirror [generate|validate] [--package-dir ...] [--tests-dir ...]"
)


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
        print(f"{MIRROR_PREFIX} Missing tests detected:")
        for path in missing_tests:
            print(f"  - {path}")
    else:
        print(f"{MIRROR_PREFIX} All tests are in place!")


def _find_subdirs(path: Path, exclude_names: set[str] | None = None) -> list[Path]:
    """Find non-hidden subdirectories, excluding specified names."""
    if exclude_names is None:
        exclude_names = set()
    return [
        d
        for d in path.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in exclude_names
    ]


def detect_default_package_dir() -> Path:
    """Detect the default package directory to mirror.

    Returns:
        Path: Path to the detected package directory.
    """
    cwd = Path.cwd()
    src = cwd / "src"
    if src.exists() and src.is_dir():
        subdirs = _find_subdirs(src)
        if subdirs:
            return subdirs[0]
    # fallback: first subdir in cwd (excluding src)
    subdirs = _find_subdirs(cwd, exclude_names={"src"})
    if subdirs:
        return subdirs[0]
    # fallback: cwd
    return cwd


def _get_pyproject_config(cwd: Path | None = None) -> dict:
    """Read pytest-mirror config from pyproject.toml if present."""
    if cwd is None:
        cwd = Path.cwd()
    pyproject = cwd / "pyproject.toml"

    if not pyproject.exists():
        return {}
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        return data.get("tool", {}).get("pytest-mirror", {})
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def parse_cli_args(cwd: Path | None = None) -> argparse.Namespace:
    """Parse CLI arguments for pytest-mirror, supporting pyproject.toml defaults.

    Optionally specify cwd for testability.
    """
    config = _get_pyproject_config(cwd=cwd)

    parser = argparse.ArgumentParser(
        prog="pytest-mirror", description="Mirror test structure enforcement tool."
    )

    default_command = config.get("default-command")
    parser.add_argument(
        "command",
        choices=["generate", "validate"],
        nargs="?",
        default=default_command,
        help="Command to run: 'generate' missing tests or 'validate' only.",
    )

    parser.add_argument(
        "--package-dir",
        type=Path,
        default=config.get("package-dir", detect_default_package_dir()),
        help="Path to the main package directory (default: first subdir in ./src or ./)",
    )

    parser.add_argument(
        "--tests-dir",
        type=Path,
        default=config.get("tests-dir", Path.cwd() / "tests"),
        help="Path to the tests directory (default: ./tests)",
    )

    return parser.parse_args()


def process_command(args: argparse.Namespace) -> None:
    """Process the CLI command using match-case for extensibility."""
    if args.command is None:
        print(USAGE_MESSAGE, file=sys.stderr)
        sys.exit(2)
    match args.command:
        case "generate":
            generate_missing_tests(args.package_dir, args.tests_dir)
        case "validate":
            validate_missing_tests(args.package_dir, args.tests_dir)
        case _:
            print(f"{ERROR_PREFIX} Unknown command: {args.command}", file=sys.stderr)
            sys.exit(2)


def main(cwd: Path | None = None) -> None:
    """CLI entry point for pytest-mirror.

    Handles argument parsing and dispatches to generate or validate commands.
    Optionally specify cwd for testability.
    """
    args = parse_cli_args(cwd=cwd)

    print(f"{MIRROR_PREFIX} Using package_dir: {args.package_dir}")
    print(f"{MIRROR_PREFIX} Using tests_dir: {args.tests_dir}")

    process_command(args)
