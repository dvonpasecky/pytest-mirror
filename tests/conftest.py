"""Pytest configuration and shared fixtures for pytest-mirror test suite.

Validates test structure before running tests using pytest-mirror plugin.
Provides shared test fixtures for file creation.
"""

from pathlib import Path

import pytest


@pytest.fixture
def create_file():
    """Fixture to create a dummy Python file at the given path."""

    def _create_file(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# dummy\n")

    return _create_file


@pytest.fixture
def project_structure():
    """Fixture to create a standard project structure for testing."""

    def _create_structure(
        tmp_path, package_name="pkg", modules=None, tests_exist=False
    ):
        if modules is None:
            modules = ["foo.py", "bar.py"]

        pkg_dir = tmp_path / package_name
        tests_dir = tmp_path / "tests"

        # Create package modules
        for module in modules:
            if "/" in module:  # nested module
                module_path = pkg_dir / module
            else:
                module_path = pkg_dir / module
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("# dummy module\n")

        # Optionally create corresponding test files
        if tests_exist:
            for module in modules:
                if module.endswith(".py") and not module.endswith("__init__.py"):
                    test_name = f"test_{Path(module).name}"
                    if "/" in module:
                        test_path = tests_dir / Path(module).parent / test_name
                    else:
                        test_path = tests_dir / test_name
                    test_path.parent.mkdir(parents=True, exist_ok=True)
                    test_path.write_text("# test file\n")

        return pkg_dir, tests_dir

    return _create_structure


@pytest.fixture
def mock_config():
    """Fixture to create mock pytest config objects."""
    from unittest.mock import Mock

    def _create_config(inicfg=None, options=None):
        config = Mock()
        config.inicfg = inicfg or {}
        config.getoption = lambda key: (options or {}).get(key, False)
        config.rootpath = Path.cwd()
        return config

    return _create_config


@pytest.fixture
def temp_pyproject(tmp_path):
    """Fixture to create temporary pyproject.toml files for testing."""

    def _create_pyproject(config_dict):
        pyproject = tmp_path / "pyproject.toml"
        lines = ["[tool.pytest-mirror]"]
        for key, value in config_dict.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            elif isinstance(value, bool):
                lines.append(f"{key} = {str(value).lower()}")
            else:
                lines.append(f"{key} = {value}")
        pyproject.write_text("\n".join(lines) + "\n")
        return pyproject

    return _create_pyproject
