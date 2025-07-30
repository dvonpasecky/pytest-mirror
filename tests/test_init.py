"""Tests for pytest_mirror.__init__ module.

Tests the main package API and public function exports.
"""


class TestInitModule:
    """Test __init__.py module coverage."""

    def test_module_imports(self):
        """Test that the module can be imported and exposes the API."""
        import pytest_mirror

        # This triggers import execution for coverage
        assert hasattr(pytest_mirror, "find_missing_tests")
        assert hasattr(pytest_mirror, "generate_missing_tests")
        assert hasattr(pytest_mirror, "__all__")

    def test_public_functions_available(self):
        """Test that public functions are available."""
        from pytest_mirror import find_missing_tests, generate_missing_tests

        assert callable(find_missing_tests)
        assert callable(generate_missing_tests)

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        from pytest_mirror import __all__

        expected = {"find_missing_tests", "generate_missing_tests"}
        assert set(__all__) == expected

    def test_find_missing_tests_integration(self, tmp_path, project_structure):
        """Test find_missing_tests function."""
        from pytest_mirror import find_missing_tests

        pkg, tests = project_structure(tmp_path)
        missing = find_missing_tests(pkg, tests)
        assert isinstance(missing, list)

    def test_generate_missing_tests_integration(self, tmp_path, project_structure):
        """Test generate_missing_tests function."""
        from pytest_mirror import generate_missing_tests

        pkg, tests = project_structure(tmp_path)
        generate_missing_tests(pkg, tests)
        # Should not raise any exceptions
