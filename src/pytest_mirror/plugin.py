"""Pytest plugin integration for pytest-mirror.

Provides pytest hooks for test structure validation and auto-generation.
"""

import os
from pathlib import Path

import pytest

from .plugin_manager import get_plugin_manager
from .validator import MirrorValidator

# Constants
MIRROR_PREFIX = "[MIRROR]"
MIRROR_DEBUG_PREFIX = "[MIRROR][DEBUG]"
DEFAULT_TEST_CONTENT = """import pytest


def test_placeholder():
    assert False, 'This is a placeholder test. Please implement.'
"""
MISSING_TESTS_MESSAGE = "Missing tests detected (auto-generate disabled):"
VALIDATION_SUCCESS_MESSAGE = "Test structure validated successfully."
VALIDATION_FAILED_MESSAGE = "Test structure validation failed"


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add pytest-mirror options to pytest CLI and config.

    Args:
        parser (pytest.Parser): The pytest parser object.
    """
    group = parser.getgroup("pytest-mirror")
    group.addoption(
        "--mirror-no-generate",
        action="store_true",
        help="Disable automatic generation of missing test stubs.",
    )

    group.addoption(
        "--mirror-package-dir",
        action="store",
        default=None,
        help="Path to the main package directory to mirror (default: auto-detect)",
    )
    group.addoption(
        "--mirror-tests-dir",
        action="store",
        default=None,
        help="Path to the tests directory (default: auto-detect)",
    )


def _get_path_option(optval) -> str | None:
    """Extract valid path from option value, ignoring bool/None/other types."""
    # Only accept str or os.PathLike, ignore bool/None/other
    if isinstance(optval, str | os.PathLike) and optval:
        return str(optval)
    return None


def _detect_package_dir(project_root: Path) -> Path:
    """Auto-detect the package directory from project structure."""
    # Try to auto-detect: prefer src/pytest_mirror, then pytest_mirror, then first subdir
    src_dir = project_root / "src" / "pytest_mirror"
    if src_dir.exists():
        return src_dir

    fallback = project_root / "pytest_mirror"
    if fallback.exists():
        return fallback

    # fallback: first subdir
    subdirs = (
        [d for d in (project_root / "src").iterdir() if d.is_dir()]
        if (project_root / "src").exists()
        else []
    )
    if not subdirs:
        subdirs = [d for d in project_root.iterdir() if d.is_dir()]
    return subdirs[0] if subdirs else project_root


def _resolve_package_dir(config: pytest.Config, project_root: Path) -> Path:
    """Resolve package directory from config options, environment, or auto-detection."""
    package_dir = _get_path_option(
        config.getoption("--mirror-package-dir")
    ) or os.environ.get("PYTEST_MIRROR_PACKAGE_DIR")

    if not package_dir:
        return _detect_package_dir(project_root)
    return Path(package_dir)


def _resolve_tests_dir(config: pytest.Config, project_root: Path) -> Path:
    """Resolve tests directory from config options, environment, or auto-detection."""
    tests_dir = _get_path_option(
        config.getoption("--mirror-tests-dir")
    ) or os.environ.get("PYTEST_MIRROR_TESTS_DIR")

    if not tests_dir:
        # Try to auto-detect: prefer tests/ under project root
        return project_root / "tests"
    return Path(tests_dir)


def _print_debug_info(
    config: pytest.Config, package_dir: Path, tests_dir: Path
) -> None:
    """Print debug information if verbose mode is enabled."""
    verbose = getattr(config.option, "verbose", 0) > 0
    if verbose:
        print(f"{MIRROR_DEBUG_PREFIX} CWD: {Path.cwd()}")
        print(f"{MIRROR_DEBUG_PREFIX} package_dir: {package_dir}")
        print(f"{MIRROR_DEBUG_PREFIX} tests_dir: {tests_dir}")


def _handle_missing_tests(
    missing_tests: list[Path], auto_generate: bool, config: pytest.Config
) -> None:
    """Handle missing tests by either generating them or reporting the error."""
    verbose = getattr(config.option, "verbose", 0) > 0

    if auto_generate and not config.getoption("--mirror-no-generate"):
        for test_path in missing_tests:
            test_path.parent.mkdir(parents=True, exist_ok=True)
            if not test_path.exists():
                test_path.write_text(DEFAULT_TEST_CONTENT)
                if verbose:
                    print(f"{MIRROR_PREFIX} Created: {test_path}")
    else:
        print(f"{MIRROR_PREFIX} {MISSING_TESTS_MESSAGE}")
        for path in missing_tests:
            print(f"  - {path}")
        pytest.exit(VALIDATION_FAILED_MESSAGE, returncode=1)


def _get_auto_generate_config(config: pytest.Config) -> bool:
    """Read auto-generate setting from pyproject.toml.

    By default, auto-generate is enabled. To disable, set:

        [tool.pytest-mirror]
        auto-generate = false

    in your pyproject.toml.

    Args:
        config (pytest.Config): The pytest config object.

    Returns:
        bool: True if auto-generate is enabled, False otherwise.
    """
    try:
        # pytest stores all loaded ini-like configs in config.inicfg
        # Support both [tool.pytest-mirror] auto-generate and disable-auto-generate
        raw_value = config.inicfg.get("tool.pytest-mirror.auto-generate")
        disable_value = config.inicfg.get("tool.pytest-mirror.disable-auto-generate")
        if disable_value is not None:
            # If disable-auto-generate is set to true/1/yes, force disable
            return str(disable_value).lower() not in {"true", "1", "yes"}
        # If not set or set to anything except false/0/no, auto-generate is enabled
        return str(raw_value).lower() not in {"false", "0", "no"}
    except Exception:
        return True  # default to auto-generate if missing


def pytest_sessionstart(session: pytest.Session) -> None:
    """Validate and optionally generate missing tests on pytest startup.

    Args:
        session (pytest.Session): The pytest session object.
    """
    config = session.config
    project_root = Path(config.rootpath)

    package_dir = _resolve_package_dir(config, project_root)
    tests_dir = _resolve_tests_dir(config, project_root)

    _print_debug_info(config, package_dir, tests_dir)

    # Check pyproject.toml config
    auto_generate = _get_auto_generate_config(config)
    # Register the MirrorValidator plugin if not already registered
    pm = get_plugin_manager()
    pm.register(MirrorValidator(), name="mirror_validator")

    # pm.hook returns a list of lists (one per plugin), flatten it
    missing_tests_nested = pm.hook.validate_test_structure(
        package_dir=package_dir, tests_dir=tests_dir
    )
    missing_tests = [item for sublist in missing_tests_nested for item in sublist]

    verbose = getattr(config.option, "verbose", 0) > 0
    if verbose:
        print(f"{MIRROR_DEBUG_PREFIX} missing_tests: {missing_tests}")

    if missing_tests:
        _handle_missing_tests(missing_tests, auto_generate, config)
    elif verbose:
        print(f"{MIRROR_PREFIX} {VALIDATION_SUCCESS_MESSAGE}")
