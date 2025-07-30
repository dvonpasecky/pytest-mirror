"""Unit tests for pytest_mirror.plugin hooks and config logic."""

import pytest

from pytest_mirror import plugin


def test_get_auto_generate_config_true():
    """Test _get_auto_generate_config returns True by default or for 'true'."""
    from unittest.mock import Mock

    cfg = Mock()
    cfg.inicfg = {"tool.pytest-mirror.auto-generate": "true"}
    cfg.getoption = lambda name: False
    assert plugin._get_auto_generate_config(cfg) is True
    cfg2 = Mock()
    cfg2.inicfg = {}
    cfg2.getoption = lambda name: False
    assert plugin._get_auto_generate_config(cfg2) is True


def test_get_auto_generate_config_false():
    """Test _get_auto_generate_config returns False for 'false', '0', 'no'."""
    from unittest.mock import Mock

    for val in ["false", "0", "no"]:
        cfg = Mock()
        cfg.inicfg = {"tool.pytest-mirror.auto-generate": val}
        cfg.getoption = lambda name: False
        assert plugin._get_auto_generate_config(cfg) is False


def test_pytest_addoption_adds_option():
    """Test pytest_addoption adds the --mirror-no-generate option."""
    from unittest.mock import Mock

    groups = {}

    def addoption(*args, **kwargs):
        groups["added"] = (args, kwargs)

    mock_group = Mock(addoption=addoption)
    parser = Mock()
    parser.getgroup = Mock(side_effect=lambda name: groups.setdefault(name, mock_group))

    plugin.pytest_addoption(parser)
    assert "pytest-mirror" in groups
    assert "added" in groups


def test_pytest_sessionstart_missing_tests_exit(monkeypatch, tmp_path):
    """Test pytest_sessionstart exits when missing tests and auto-generate is off."""
    from unittest.mock import Mock

    config = Mock()
    config.rootpath = tmp_path
    config.getoption = lambda name: True
    config.option = Mock(verbose=0)
    config.inicfg = {}
    session = Mock()
    session.config = config
    pm = Mock()
    pm.hook.validate_test_structure.return_value = [[tmp_path / "tests" / "foo.py"]]
    pm.register = Mock()
    monkeypatch.setattr(plugin, "get_plugin_manager", lambda: pm)
    monkeypatch.setattr(plugin, "_get_auto_generate_config", lambda c: False)
    monkeypatch.setattr(
        "pytest.exit", lambda *a, **k: (_ for _ in ()).throw(SystemExit(1))
    )
    try:
        plugin.pytest_sessionstart(session)
    except SystemExit as e:
        assert e.code == 1


def test_pytest_sessionstart_no_missing_tests(monkeypatch, tmp_path, capsys):
    """Test pytest_sessionstart with no missing tests and verbose output."""
    from unittest.mock import Mock

    config = Mock()
    config.rootpath = tmp_path
    config.getoption = lambda name: False
    config.option = Mock(verbose=1)
    config.inicfg = {}
    session = Mock()
    session.config = config
    pm = Mock()
    pm.hook.validate_test_structure.return_value = [[]]
    pm.register = Mock()
    monkeypatch.setattr(plugin, "get_plugin_manager", lambda: pm)
    monkeypatch.setattr(plugin, "_get_auto_generate_config", lambda c: True)
    plugin.pytest_sessionstart(session)
    out = capsys.readouterr().out
    assert "Test structure validated successfully" in out


def test_pytest_sessionstart_verbose_debug(monkeypatch, tmp_path, capsys):
    """Test pytest_sessionstart with verbose output and missing tests triggers debug prints."""
    # No imports needed
    from unittest.mock import Mock

    config = Mock()
    config.rootpath = tmp_path
    config.getoption = lambda name: False
    config.option = Mock(verbose=1)
    config.inicfg = {}
    session = Mock()
    session.config = config
    test_path = tmp_path / "tests" / "foo.py"
    pm = Mock()
    pm.hook.validate_test_structure.return_value = [[test_path]]
    pm.register = Mock()
    monkeypatch.setattr(plugin, "get_plugin_manager", lambda: pm)
    monkeypatch.setattr(plugin, "_get_auto_generate_config", lambda c: True)
    # Remove test file if it exists
    if test_path.exists():
        test_path.unlink()
    plugin.pytest_sessionstart(session)
    out = capsys.readouterr().out
    assert "[MIRROR][DEBUG]" in out
    assert "Created" in out


def test_pytest_sessionstart_auto_generate_disabled(monkeypatch, tmp_path, capsys):
    """Test pytest_sessionstart with auto-generate disabled prints missing tests and exits."""
    from unittest.mock import Mock

    config = Mock()
    config.rootpath = tmp_path
    config.getoption = lambda name: False
    config.option = Mock(verbose=0)
    config.inicfg = {}
    session = Mock()
    session.config = config
    test_path = tmp_path / "tests" / "foo.py"
    pm = Mock()
    pm.hook.validate_test_structure.return_value = [[test_path]]
    pm.register = Mock()
    monkeypatch.setattr(plugin, "get_plugin_manager", lambda: pm)
    monkeypatch.setattr(plugin, "_get_auto_generate_config", lambda c: False)
    monkeypatch.setattr(
        "pytest.exit", lambda *a, **k: (_ for _ in ()).throw(SystemExit(1))
    )
    try:
        plugin.pytest_sessionstart(session)
    except SystemExit as e:
        assert e.code == 1
    out = capsys.readouterr().out
    assert "Missing tests detected" in out


def test_get_auto_generate_config_exception(monkeypatch):
    """Test _get_auto_generate_config returns True on exception."""
    from unittest.mock import Mock, PropertyMock

    cfg = Mock()
    type(cfg).inicfg = PropertyMock(side_effect=RuntimeError("fail"))
    assert plugin._get_auto_generate_config(cfg) is True


def test_get_auto_generate_config_disable(monkeypatch):
    """Test _get_auto_generate_config returns False if disable-auto-generate is set true/1/yes."""
    from unittest.mock import Mock

    for val in ["true", "1", "yes"]:
        cfg = Mock()
        cfg.inicfg = {"tool.pytest-mirror.disable-auto-generate": val}
        cfg.getoption = lambda name: False
        from pytest_mirror import plugin as plugin_mod

        assert plugin_mod._get_auto_generate_config(cfg) is False


class TestPluginEdgeCases:
    """Test additional edge cases in plugin.py module."""

    def test_pytest_addoption_function(self):
        """Test pytest_addoption function exists and is callable."""
        from pytest_mirror import plugin

        assert hasattr(plugin, "pytest_addoption")
        assert callable(plugin.pytest_addoption)

    def test_pytest_sessionstart_function(self):
        """Test pytest_sessionstart function exists."""
        from pytest_mirror import plugin

        assert hasattr(plugin, "pytest_sessionstart")
        assert callable(plugin.pytest_sessionstart)

    def test_get_plugin_manager_returns_pluginmanager(self):
        """Test that get_plugin_manager returns a PluginManager instance."""
        from pytest_mirror.plugin_manager import get_plugin_manager

        pm = get_plugin_manager()
        assert hasattr(pm, "hook")
        assert hasattr(pm, "register")
        assert hasattr(pm, "get_plugins")

    def test_plugin_manager_hook_registration(self):
        """Test that hook specifications are properly registered."""
        from pytest_mirror.plugin_manager import get_plugin_manager

        pm = get_plugin_manager()
        assert hasattr(pm.hook, "validate_test_structure")
        hook = pm.hook.validate_test_structure
        assert callable(hook)

    def test_plugin_manager_validator_registration(self):
        """Test that MirrorValidator is registered with plugin manager."""
        from pytest_mirror.plugin_manager import get_plugin_manager

        pm = get_plugin_manager()
        plugins = list(pm.get_plugins())

        # Should have at least one plugin
        assert len(plugins) > 0

        # Should have a MirrorValidator instance
        validator_found = False
        for plugin_instance in plugins:
            if "MirrorValidator" in str(type(plugin_instance)):
                validator_found = True
                break
        assert validator_found, (
            f"MirrorValidator not found in plugins: {[type(p) for p in plugins]}"
        )

    def test_plugin_manager_hook_execution(self, tmp_path):
        """Test that registered hooks can be executed."""
        from pytest_mirror.plugin_manager import get_plugin_manager

        pm = get_plugin_manager()
        pkg = tmp_path / "pkg"
        tests = tmp_path / "tests"

        # Create a module to test
        (pkg / "foo.py").parent.mkdir(parents=True, exist_ok=True)
        (pkg / "foo.py").write_text("# module\n")

        # Execute the hook
        results = pm.hook.validate_test_structure(package_dir=pkg, tests_dir=tests)

        # Should return list of lists (one per registered plugin)
        assert isinstance(results, list)
        assert len(results) > 0

        # Flatten results
        missing_tests = [item for sublist in results for item in sublist]
        assert len(missing_tests) == 1
        assert missing_tests[0] == tests / "test_foo.py"


class TestPluginIntegration:
    """Integration tests for plugin.py with comprehensive mocking and parametrized scenarios."""

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
            import types

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
        self, monkeypatch, tmp_path, missing_factory, auto, flag, should_exit, capsys
    ):
        """Test all code paths in pytest_sessionstart."""
        from pathlib import Path
        from unittest.mock import Mock

        missing = missing_factory(tmp_path)
        # Patch get_plugin_manager to return DummyPM
        monkeypatch.setattr(plugin, "get_plugin_manager", lambda: self.DummyPM(missing))
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

    def test_dummyconfig_getoption(self):
        """Test DummyConfig.getoption returns correct values."""
        cfg = self.DummyConfig(opts={"foo": 123})
        assert cfg.getoption("foo") == 123
        assert cfg.getoption("bar") is False

    def test_dummypm_register(self):
        """Test DummyPM.register stores plugin and name."""
        pm = self.DummyPM()
        pm.register("plugin_obj", name="name")
        assert pm._registered == ("plugin_obj", "name")

    def test_pytest_addoption_option_already_exists(self):
        """Test pytest_addoption when option already exists in group."""
        from unittest.mock import Mock

        group = Mock()
        parser = Mock()
        parser.getgroup.return_value = group
        plugin.pytest_addoption(parser)
        parser.getgroup.assert_called_with("pytest-mirror")
        group.addoption.assert_called()

    def test_get_auto_generate_config_false_cases(self):
        """Test _get_auto_generate_config with various false-like values and exceptions."""
        from unittest.mock import Mock, PropertyMock

        cfg = Mock()
        cfg.inicfg = {"tool.pytest-mirror.auto-generate": "false"}
        cfg.getoption = lambda name: False
        assert plugin._get_auto_generate_config(cfg) is False
        cfg.inicfg = {"tool.pytest-mirror.auto-generate": "0"}
        assert plugin._get_auto_generate_config(cfg) is False
        cfg.inicfg = {"tool.pytest-mirror.auto-generate": "no"}
        assert plugin._get_auto_generate_config(cfg) is False
        # Exception path
        bad_cfg = Mock()
        type(bad_cfg).inicfg = PropertyMock(side_effect=RuntimeError("fail"))
        assert plugin._get_auto_generate_config(bad_cfg) is True
