"""Mainline tests for pytest_mirror.core (mirrored from core.py)."""

from pytest_mirror.core import find_missing_tests, generate_missing_tests


def test_find_missing_tests_returns_missing(tmp_path):
    """Should return missing test file for a module in package_dir."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    foo = pkg / "foo.py"
    foo.write_text("# dummy\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    missing = find_missing_tests(pkg, tests)
    assert len(missing) == 1
    assert missing[0] == tests / "test_foo.py"


def test_find_missing_tests_all_present(tmp_path):
    """Should return empty list if all tests are present."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    foo = pkg / "foo.py"
    foo.write_text("# dummy\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_foo.py").write_text("# test\n")
    missing = find_missing_tests(pkg, tests)
    assert missing == []


def test_generate_missing_tests_creates_files(tmp_path):
    """Should create missing test files for modules in package_dir."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    foo = pkg / "foo.py"
    foo.write_text("# dummy\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    generate_missing_tests(pkg, tests)
    test_file = tests / "test_foo.py"
    assert test_file.exists()
    content = test_file.read_text()
    assert "def test_placeholder" in content
