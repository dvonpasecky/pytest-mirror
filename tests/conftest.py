"""Pytest configuration and shared fixtures for pytest-mirror test suite.

Validates test structure before running tests using pytest-mirror plugin.
Provides shared test fixtures for file creation.
"""

import pytest


@pytest.fixture
def create_file():
    """Fixture to create a dummy Python file at the given path."""

    def _create_file(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# dummy\n")

    return _create_file
