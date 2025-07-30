"""Shared constants for pytest-mirror package."""

# Project identification
PROJECT_NAME = "pytest-mirror"  # PyPI/distribution name
PACKAGE_NAME = "pytest_mirror"  # Python package name (for pluggy)

# Logging prefixes
MIRROR_PREFIX = "[MIRROR]"

# Default test file content
DEFAULT_TEST_CONTENT = """import pytest


def test_placeholder():
    assert False, 'This is a placeholder test. Please implement.'
"""
