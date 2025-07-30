"""Unit tests for pytest_mirror.validator.MirrorValidator.

Tests detection of missing test files, __init__.py handling, and nested modules.
"""

from pytest_mirror.validator import MirrorValidator


def test_validate_test_structure_finds_missing(tmp_path, create_file):
    """Test that missing test files are detected for package modules."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    create_file(foo)
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert len(missing) == 1
    assert missing[0] == tests / "test_foo.py"


def test_validate_test_structure_ignores_init(tmp_path, create_file):
    """Test that __init__.py is ignored by the validator."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    create_file(pkg / "__init__.py")
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert missing == []


def test_validate_test_structure_nested(tmp_path, create_file):
    """Test that nested modules are checked and mapped to nested test files."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    sub = pkg / "sub"
    foo = sub / "foo.py"
    create_file(foo)
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert missing == [tests / "sub" / "test_foo.py"]


def test_validate_test_structure_empty_dirs(tmp_path):
    """Test that empty package and tests dirs return no missing tests."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    pkg.mkdir()
    tests.mkdir()
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert missing == []


def test_validate_test_structure_non_py_files(tmp_path):
    """Test that non-Python files are ignored by the validator."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    (pkg / "foo.txt").parent.mkdir(parents=True, exist_ok=True)
    (pkg / "foo.txt").write_text("not python")
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert missing == []


def test_validate_test_structure_test_file_exists(tmp_path, create_file):
    """Test that if the test file already exists, it is not reported missing."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    create_file(foo)
    test_file = tests / "test_foo.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# test\n")
    validator = MirrorValidator()
    missing = validator.validate_test_structure(pkg, tests)
    assert missing == []
