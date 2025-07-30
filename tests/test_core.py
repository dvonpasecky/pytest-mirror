"""Mainline tests for pytest_mirror.core (mirrored from core.py)."""

import sys

import pytest

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


class TestCoreModuleEdgeCases:
    """Test additional edge cases in core.py module."""

    def test_package_dir_validation_errors(self, tmp_path):
        """Test package directory validation edge cases."""
        from pytest_mirror.core import _validate_package_dir

        # Test with nonexistent directory
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError, match="Package directory does not exist"):
            _validate_package_dir(nonexistent)

        # Test with file instead of directory
        test_file = tmp_path / "test_file.py"
        test_file.write_text("# test")
        with pytest.raises(
            NotADirectoryError, match="Package directory.*is not a directory"
        ):
            _validate_package_dir(test_file)

    def test_ensure_test_dir_structure_creates_parents(self, tmp_path):
        """Test that _ensure_test_dir_structure creates parent directories."""
        from pytest_mirror.core import _ensure_test_dir_structure

        deep_test_dir = tmp_path / "very" / "deep" / "test" / "structure"
        created_dirs = set()
        _ensure_test_dir_structure(deep_test_dir, created_dirs)
        assert deep_test_dir.exists()
        assert deep_test_dir.is_dir()
        assert len(created_dirs) > 0


class TestCoreFunctionEdgeCases:
    """Test edge cases in core.py helper functions."""

    def test_validate_package_dir_edge_cases(self, tmp_path):
        """Test _validate_package_dir with various invalid inputs."""
        from pytest_mirror.core import _validate_package_dir

        # Test with file instead of directory
        file_path = tmp_path / "not_a_dir.py"
        file_path.write_text("# file\n")

        with pytest.raises(NotADirectoryError):
            _validate_package_dir(file_path)

        # Test with non-existent path
        with pytest.raises(FileNotFoundError):
            _validate_package_dir(tmp_path / "nonexistent")

    def test_get_test_path_various_structures(self, tmp_path):
        """Test _get_test_path with various module structures."""
        from pytest_mirror.core import _get_test_path

        pkg_dir = tmp_path / "pkg"
        tests_dir = tmp_path / "tests"

        # Test simple module
        simple_module = pkg_dir / "simple.py"
        result = _get_test_path(simple_module, pkg_dir, tests_dir)
        assert result == tests_dir / "test_simple.py"

        # Test nested module
        nested_module = pkg_dir / "sub" / "nested.py"
        result = _get_test_path(nested_module, pkg_dir, tests_dir)
        assert result == tests_dir / "sub" / "test_nested.py"

    def test_ensure_test_dir_structure_behavior(self, tmp_path):
        """Test _ensure_test_dir_structure creates directories correctly."""
        from pytest_mirror.core import _ensure_test_dir_structure

        test_dir = tmp_path / "new_test_dir"
        created_dirs = set()

        # First call should create directory and init file
        _ensure_test_dir_structure(test_dir, created_dirs)

        assert test_dir.exists()
        assert (test_dir / "__init__.py").exists()
        assert test_dir in created_dirs

        # Second call should not recreate (test caching)
        init_mtime = (test_dir / "__init__.py").stat().st_mtime
        _ensure_test_dir_structure(test_dir, created_dirs)

        # Init file should not be recreated
        assert (test_dir / "__init__.py").stat().st_mtime == init_mtime


class TestCoreEdgeCases:
    """Edge case and error handling tests for core.py functions."""

    def test_generate_missing_tests_invalid_package_dir(self, tmp_path):
        """Should raise FileNotFoundError if package_dir does not exist."""
        pkg = tmp_path / "not_a_real_dir"
        tests = tmp_path / "tests"
        with pytest.raises(FileNotFoundError):
            generate_missing_tests(pkg, tests)

    def test_generate_missing_tests_file_instead_of_dir(self, tmp_path):
        """Should raise NotADirectoryError if package_dir is a file."""
        pkg = tmp_path / "pkg.py"
        pkg.write_text("# dummy\n")
        tests = tmp_path / "tests"
        with pytest.raises(NotADirectoryError):
            generate_missing_tests(pkg, tests)

    def test_generate_missing_tests_permission_error(self, tmp_path):
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

    def test_find_missing_tests_symlink(self, tmp_path):
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
