"""pytest-mirror package root module.

Provides test structure mirroring and validation plugin for pytest.
Exposes main API functions for programmatic use.
"""

from .core import find_missing_tests, generate_missing_tests

__all__ = ["generate_missing_tests", "find_missing_tests"]
