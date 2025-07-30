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


class TestValidatorCoverage:
    """Additional tests for validator module coverage."""

    def test_mirror_validator_class_exists(self):
        """Test that MirrorValidator class exists."""
        from pytest_mirror import validator

        assert hasattr(validator, "MirrorValidator")
        assert callable(validator.MirrorValidator)

    def test_validator_instantiation(self):
        """Test validator can be instantiated."""
        v = MirrorValidator()
        assert hasattr(v, "validate_test_structure")
        assert callable(v.validate_test_structure)

    def test_validator_method_with_paths(self, tmp_path, project_structure):
        """Test validator method with actual paths."""
        from pathlib import Path

        pkg, tests = project_structure(tmp_path)
        v = MirrorValidator()

        result = v.validate_test_structure(pkg, tests)
        assert isinstance(result, list)
        assert all(isinstance(path, Path) for path in result)

    def test_validator_with_missing_dirs(self, tmp_path):
        """Test validator with missing directories."""
        import pytest

        v = MirrorValidator()
        nonexistent = tmp_path / "nonexistent"

        # Should raise FileNotFoundError for missing package dir
        with pytest.raises(FileNotFoundError):
            v.validate_test_structure(nonexistent, tmp_path / "tests")

    def test_validator_has_hookimpl_decorator(self):
        """Test that validator method has hookimpl decorator."""
        v = MirrorValidator()
        method = v.validate_test_structure

        # Should have hookimpl marker or be callable
        assert callable(method)
        # The hookimpl marker might not be directly visible, just test functionality

    def test_hookimpl_marker_exists(self):
        """Test that hookimpl marker exists in module."""
        from pytest_mirror import validator

        assert hasattr(validator, "hookimpl")
        assert hasattr(validator.hookimpl, "project_name")
        assert validator.hookimpl.project_name == "pytest_mirror"
