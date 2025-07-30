"""Integration and edge-case tests for pytest_mirror.plugin."""

import types
from pathlib import Path
from unittest.mock import Mock, PropertyMock

import pytest

from pytest_mirror import plugin


class DummyConfig:
    """Mock configuration object for testing."""

    def __init__(self, ini=None, opts=None, rootpath="/proj"):
        """Initialize with optional ini and opts."""
        self.inicfg = ini or {}
        self._opts = opts or {}
        self.rootpath = rootpath

    def getoption(self, name):
        """Mock getoption method to return configured options."""
        return self._opts.get(name, False)


class DummyPM:
    """Mock plugin manager for testing."""

    def __init__(self, missing=None):
        """Initialize with optional missing tests."""
        self._missing = missing or []
        self.hook = types.SimpleNamespace(
            validate_test_structure=lambda **kwargs: [self._missing]
        )

    def register(self, plugin, name=None):
        """Mock register method to simulate plugin registration."""
        self._registered = (plugin, name)


@pytest.mark.parametrize(
    "missing_factory,auto,flag,should_exit",
    [
        (lambda tmp_path: [tmp_path / "tests" / "foo.py"], True, False, False),
        (lambda tmp_path: [tmp_path / "tests" / "foo.py"], False, False, True),
        (lambda tmp_path: [tmp_path / "tests" / "foo.py"], True, True, True),
        (lambda tmp_path: [], True, False, False),
    ],
)
def test_pytest_sessionstart_paths(
    monkeypatch, tmp_path, missing_factory, auto, flag, should_exit, capsys
):
    """Test all code paths in pytest_sessionstart."""
    missing = missing_factory(tmp_path)
    # Patch get_plugin_manager to return DummyPM
    monkeypatch.setattr(plugin, "get_plugin_manager", lambda: DummyPM(missing))
    monkeypatch.setattr(plugin, "MirrorValidator", object)
    # Patch only the project root Path
    monkeypatch.setattr(plugin, "Path", Path)
    # Patch _get_auto_generate_config
    monkeypatch.setattr(plugin, "_get_auto_generate_config", lambda c: auto)
    # Use Mock for config and session to satisfy type checkers
    config = Mock()
    config.inicfg = {}
    config._opts = {"--mirror-no-generate": flag}
    config.rootpath = tmp_path
    config.getoption = lambda name: config._opts.get(name, False)
    # Set verbose=1 if we expect 'Created' in output, else 0
    expect_created = bool(missing and not should_exit)
    config.option = Mock(verbose=1 if expect_created else 0)
    session = Mock()
    session.config = config
    try:
        if should_exit:
            # Patch pytest.exit to raise SystemExit silently (no error message)
            def silent_exit(msg=None, returncode=1):
                raise SystemExit(returncode)

            monkeypatch.setattr("pytest.exit", silent_exit)
            with pytest.raises(SystemExit):
                plugin.pytest_sessionstart(session)
        else:
            plugin.pytest_sessionstart(session)
        out = capsys.readouterr().out
        if missing and not should_exit:
            assert "Created" in out
        if missing and should_exit:
            # No error message should be present now
            assert "Test structure validation failed" not in out
    finally:
        # Clean up any generated test files
        for path in missing:
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass


def test_pytest_configure_runs():
    """Test that pytest_configure runs without error."""
    config = Mock()
    config.pluginmanager = Mock(register=Mock())
    plugin.pytest_configure(config)


def test_get_auto_generate_config_exception():
    """Test _get_auto_generate_config returns True on exception."""
    bad_config = Mock()
    type(bad_config).inicfg = PropertyMock(side_effect=RuntimeError("fail"))
    assert plugin._get_auto_generate_config(bad_config) is True


def test_dummyconfig_getoption():
    """Test DummyConfig.getoption returns correct values."""
    cfg = DummyConfig(opts={"foo": 123})
    assert cfg.getoption("foo") == 123
    assert cfg.getoption("bar") is False


def test_dummypm_register():
    """Test DummyPM.register stores plugin and name."""
    pm = DummyPM()
    pm.register("plugin_obj", name="name")
    assert pm._registered == ("plugin_obj", "name")


def test_pytest_configure_no_pluginmanager():
    """Test pytest_configure does nothing if no pluginmanager attribute."""
    config = Mock()
    if hasattr(config, "pluginmanager"):
        delattr(config, "pluginmanager")
    plugin.pytest_configure(config)  # Should not raise


def test_pytest_addoption_option_already_exists():
    """Test pytest_addoption when option already exists in group."""
    from unittest.mock import Mock

    group = Mock()
    parser = Mock()
    parser.getgroup.return_value = group
    plugin.pytest_addoption(parser)
    parser.getgroup.assert_called_with("pytest-mirror")
    group.addoption.assert_called()


def test_get_auto_generate_config_false_cases():
    """Test _get_auto_generate_config with various false-like values and exceptions."""
    from pytest_mirror import plugin as plugin_mod

    cfg = Mock()
    cfg.inicfg = {"tool.pytest-mirror.auto-generate": "false"}
    cfg.getoption = lambda name: False
    assert plugin_mod._get_auto_generate_config(cfg) is False
    cfg.inicfg = {"tool.pytest-mirror.auto-generate": "0"}
    assert plugin_mod._get_auto_generate_config(cfg) is False
    cfg.inicfg = {"tool.pytest-mirror.auto-generate": "no"}
    assert plugin_mod._get_auto_generate_config(cfg) is False
    # Exception path
    bad_cfg = Mock()
    from unittest.mock import PropertyMock

    type(bad_cfg).inicfg = PropertyMock(side_effect=RuntimeError("fail"))
    assert plugin_mod._get_auto_generate_config(bad_cfg) is True
