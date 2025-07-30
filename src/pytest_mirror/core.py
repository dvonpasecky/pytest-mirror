"""Core logic for pytest-mirror: validation and generation of test structure."""

from pathlib import Path

from .constants import DEFAULT_TEST_CONTENT

# Module-specific constants
INIT_FILE_NAME = "__init__.py"
TEST_FILE_PREFIX = "test_"
ALL_TESTS_PRESENT_MESSAGE = "All tests are in place"


def _validate_package_dir(package_dir: Path) -> None:
    """Validate that package_dir exists and is a directory.

    Raises:
        FileNotFoundError: If package_dir does not exist.
        NotADirectoryError: If package_dir is not a directory.
    """
    if not package_dir.exists():
        raise FileNotFoundError(f"Package directory does not exist: {package_dir}")
    if not package_dir.is_dir():
        raise NotADirectoryError(f"Package directory is not a directory: {package_dir}")


def _get_test_path(py_file: Path, package_dir: Path, tests_dir: Path) -> Path:
    """Generate the corresponding test file path for a Python module."""
    relative = py_file.relative_to(package_dir)
    return tests_dir.joinpath(relative.parent, f"{TEST_FILE_PREFIX}{relative.name}")


def find_missing_tests(package_dir: Path, tests_dir: Path) -> list[Path]:
    """Return missing test file paths for all modules in package_dir."""
    _validate_package_dir(package_dir)
    missing_tests: list[Path] = []
    for py_file in package_dir.rglob("*.py"):
        if py_file.name == INIT_FILE_NAME:
            continue
        test_path = _get_test_path(py_file, package_dir, tests_dir)
        if not test_path.exists():
            missing_tests.append(test_path)
    return missing_tests


def _ensure_test_dir_structure(test_dir: Path, created_dirs: set[Path]) -> None:
    """Ensure test directory exists with __init__.py file."""
    if test_dir not in created_dirs:
        test_dir.mkdir(parents=True, exist_ok=True)
        init_file = test_dir / INIT_FILE_NAME
        if not init_file.exists():
            init_file.touch()
        created_dirs.add(test_dir)


def generate_missing_tests(package_dir: Path, tests_dir: Path) -> None:
    """Generate missing test files and mirror package structure in tests."""
    _validate_package_dir(package_dir)
    created_dirs: set[Path] = set()
    created_any = False

    for py_file in package_dir.rglob("*.py"):
        if py_file.name == INIT_FILE_NAME:
            continue
        test_path = _get_test_path(py_file, package_dir, tests_dir)
        test_dir = test_path.parent

        _ensure_test_dir_structure(test_dir, created_dirs)

        if not test_path.exists():
            test_path.write_text(DEFAULT_TEST_CONTENT)
            print(f"Created: {test_path}")
            created_any = True

    if not created_any:
        print(ALL_TESTS_PRESENT_MESSAGE)
