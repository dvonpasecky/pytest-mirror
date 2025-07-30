"""Edge case and error handling tests for pytest_mirror.core."""

import sys

import pytest

from pytest_mirror.core import find_missing_tests, generate_missing_tests


def test_generate_missing_tests_invalid_package_dir(tmp_path):
    """Should raise FileNotFoundError if package_dir does not exist."""
    pkg = tmp_path / "not_a_real_dir"
    tests = tmp_path / "tests"
    with pytest.raises(FileNotFoundError):
        generate_missing_tests(pkg, tests)


def test_generate_missing_tests_file_instead_of_dir(tmp_path):
    """Should raise NotADirectoryError if package_dir is a file."""
    pkg = tmp_path / "pkg.py"
    pkg.write_text("# dummy\n")
    tests = tmp_path / "tests"
    with pytest.raises(NotADirectoryError):
        generate_missing_tests(pkg, tests)


def test_generate_missing_tests_permission_error(tmp_path):
    """Should handle permission errors gracefully when creating test dirs."""
    pkg = tmp_path / "pkg"
    foo = pkg / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    tests = tmp_path / "tests"

    tests.mkdir()
    # On Windows, permission errors for directories are unreliable; skip this test.
    if sys.platform.startswith("win"):
        pytest.skip("Permission error test is unreliable on Windows.")
    tests.chmod(0o444)
    try:
        with pytest.raises(PermissionError):
            generate_missing_tests(pkg, tests)
    finally:
        tests.chmod(0o755)


def test_find_missing_tests_symlink(tmp_path):
    """Should follow symlinks if present in package_dir."""
    pkg = tmp_path / "pkg"
    real = tmp_path / "real"
    real.mkdir()
    foo = real / "foo.py"
    foo.write_text("# dummy\n")

    try:
        pkg.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks not supported or insufficient privileges.")
    tests = tmp_path / "tests"
    missing = find_missing_tests(pkg, tests)
    assert tests / "test_foo.py" in missing
