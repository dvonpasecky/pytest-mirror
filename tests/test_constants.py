"""Tests for pytest_mirror.constants module."""

from pytest_mirror.constants import (
    DEFAULT_TEST_CONTENT,
    MIRROR_PREFIX,
    PACKAGE_NAME,
    PROJECT_NAME,
)


class TestConstants:
    """Test constant values and their properties."""

    def test_project_name(self):
        """Test PROJECT_NAME constant."""
        assert PROJECT_NAME == "pytest-mirror"
        assert isinstance(PROJECT_NAME, str)

    def test_package_name(self):
        """Test PACKAGE_NAME constant."""
        assert PACKAGE_NAME == "pytest_mirror"
        assert isinstance(PACKAGE_NAME, str)

    def test_project_vs_package_naming_convention(self):
        """Test that project and package names follow Python conventions."""
        # Project names use dashes for PyPI
        assert "-" in PROJECT_NAME
        assert "_" not in PROJECT_NAME

        # Package names use underscores for Python imports
        assert "_" in PACKAGE_NAME
        assert "-" not in PACKAGE_NAME

        # They should be equivalent when accounting for naming conventions
        assert PROJECT_NAME.replace("-", "_") == PACKAGE_NAME

    def test_mirror_prefix(self):
        """Test MIRROR_PREFIX constant."""
        assert MIRROR_PREFIX == "[MIRROR]"
        assert isinstance(MIRROR_PREFIX, str)

    def test_default_test_content(self):
        """Test DEFAULT_TEST_CONTENT constant."""
        assert isinstance(DEFAULT_TEST_CONTENT, str)
        assert "import pytest" in DEFAULT_TEST_CONTENT
        assert "def test_placeholder():" in DEFAULT_TEST_CONTENT
        assert "assert False" in DEFAULT_TEST_CONTENT
        assert "This is a placeholder test" in DEFAULT_TEST_CONTENT

    def test_default_test_content_is_valid_python(self):
        """Test that DEFAULT_TEST_CONTENT is valid Python code."""
        # This should compile without raising an exception
        compile(DEFAULT_TEST_CONTENT, "<string>", "exec")

    def test_constants_are_immutable_types(self):
        """Test that all constants are immutable types."""
        assert isinstance(PROJECT_NAME, str)
        assert isinstance(PACKAGE_NAME, str)
        assert isinstance(MIRROR_PREFIX, str)
        assert isinstance(DEFAULT_TEST_CONTENT, str)
