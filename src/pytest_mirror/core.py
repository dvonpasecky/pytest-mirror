"""Core logic for pytest-mirror: validation and generation of test structure."""

from pathlib import Path


def find_missing_tests(package_dir: Path, tests_dir: Path) -> list[Path]:
    """Return missing test file paths for all modules in package_dir."""
    if not package_dir.exists():
        raise FileNotFoundError(f"Package directory does not exist: {package_dir}")
    if not package_dir.is_dir():
        raise NotADirectoryError(f"Package directory is not a directory: {package_dir}")
    missing_tests: list[Path] = []
    for py_file in package_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        relative = py_file.relative_to(package_dir)
        test_path = tests_dir.joinpath(relative.parent, f"test_{relative.name}")
        if not test_path.exists():
            missing_tests.append(test_path)
    return missing_tests


def generate_missing_tests(package_dir: Path, tests_dir: Path) -> None:
    """Generate missing test files and mirror package structure in tests."""
    if not package_dir.exists():
        raise FileNotFoundError(f"Package directory does not exist: {package_dir}")
    if not package_dir.is_dir():
        raise NotADirectoryError(f"Package directory is not a directory: {package_dir}")
    created_dirs = set()
    created_any = False
    for py_file in package_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        relative = py_file.relative_to(package_dir)
        test_dir = tests_dir / relative.parent
        test_path = test_dir / f"test_{relative.name}"
        if test_dir not in created_dirs:
            test_dir.mkdir(parents=True, exist_ok=True)
            init_file = test_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            created_dirs.add(test_dir)
        if not test_path.exists():
            test_path.write_text(
                "import pytest\n\ndef test_placeholder():\n    assert False, 'This is a placeholder test. Please implement.'\n"
            )
            print(f"Created: {test_path}")
            created_any = True
    if not created_any:
        print("All tests are in place")
