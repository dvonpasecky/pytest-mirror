"""Pytest plugin integration for pytest-mirror.

Provides pytest hooks for test structure validation and auto-generation.
"""

import os
from pathlib import Path

import pytest

from .plugin_manager import get_plugin_manager
from .validator import MirrorValidator


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


def pytest_configure(config: pytest.Config) -> None:
    """Register pytest-mirror configuration defaults.

    Args:
        config (pytest.Config): The pytest config object.
    """
    # Removed invalid config.addinivalue_line usage. Add custom config support if needed.


def pytest_sessionstart(session: pytest.Session) -> None:
    """Validate and optionally generate missing tests on pytest startup.

    Args:
        session (pytest.Session): The pytest session object.
    """
    config = session.config
    project_root = Path(config.rootpath)

    def _get_path_option(optval):
        # Only accept str or os.PathLike, ignore bool/None/other
        if isinstance(optval, str | os.PathLike) and optval:
            return optval
        return None

    package_dir = _get_path_option(
        config.getoption("--mirror-package-dir")
    ) or os.environ.get("PYTEST_MIRROR_PACKAGE_DIR")
    tests_dir = _get_path_option(
        config.getoption("--mirror-tests-dir")
    ) or os.environ.get("PYTEST_MIRROR_TESTS_DIR")

    if not package_dir:
        # Try to auto-detect: prefer src/pytest_mirror, then pytest_mirror, then first subdir
        src_dir = project_root / "src" / "pytest_mirror"
        if src_dir.exists():
            package_dir = src_dir
        else:
            fallback = project_root / "pytest_mirror"
            if fallback.exists():
                package_dir = fallback
            else:
                # fallback: first subdir
                subdirs = (
                    [d for d in (project_root / "src").iterdir() if d.is_dir()]
                    if (project_root / "src").exists()
                    else []
                )
                if not subdirs:
                    subdirs = [d for d in project_root.iterdir() if d.is_dir()]
                package_dir = subdirs[0] if subdirs else project_root
    else:
        package_dir = Path(package_dir)

    if not tests_dir:
        # Try to auto-detect: prefer tests/ under project root
        tests_dir = project_root / "tests"
    else:
        tests_dir = Path(tests_dir)

    verbose = getattr(config.option, "verbose", 0) > 0
    if verbose:
        print(f"[MIRROR][DEBUG] CWD: {Path.cwd()}")
        print(f"[MIRROR][DEBUG] package_dir: {package_dir}")
        print(f"[MIRROR][DEBUG] tests_dir: {tests_dir}")

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

    if verbose:
        print(f"[MIRROR][DEBUG] missing_tests: {missing_tests}")

    if missing_tests:
        if auto_generate and not config.getoption("--mirror-no-generate"):
            for test_path in missing_tests:
                test_path.parent.mkdir(parents=True, exist_ok=True)
                if not test_path.exists():
                    test_path.write_text(
                        "import pytest\n\ndef test_placeholder():\n    assert False, 'This is a placeholder test. Please implement.'\n"
                    )
                    if verbose:
                        print(f"[MIRROR] Created: {test_path}")
        else:
            print("[MIRROR] Missing tests detected (auto-generate disabled):")
            for path in missing_tests:
                print(f"  - {path}")
            pytest.exit("Test structure validation failed", returncode=1)
    elif verbose:
        print("[MIRROR] Test structure validated successfully.")


def _get_auto_generate_config(config: pytest.Config) -> bool:
    """Read auto-generate setting from pyproject.toml.

    Args:
        config (pytest.Config): The pytest config object.

    Returns:
        bool: True if auto-generate is enabled, False otherwise.
    """
    """
    By default, auto-generate is enabled. To disable, set:

        [tool.pytest-mirror]
        auto-generate = false

    in your pyproject.toml.
    """
    try:
        # pytest stores all loaded ini-like configs in config.inicfg
        raw_value = config.inicfg.get("tool.pytest-mirror.auto-generate")
        # If not set or set to anything except false/0/no, auto-generate is enabled
        return str(raw_value).lower() not in {"false", "0", "no"}
    except Exception:
        return True  # default to auto-generate if missing
