"""Unit tests for pytest_mirror.plugin hooks and config logic.

Tests pytest_addoption, pytest_configure, and _get_auto_generate_config.
"""

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
