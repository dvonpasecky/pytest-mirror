"""Unit tests for pytest_mirror.manager.get_plugin_manager.

Tests plugin manager creation and registration of hooks and plugins.
"""

from pytest_mirror.plugin_manager import get_plugin_manager


def test_get_plugin_manager_registers_validator():
    """Test that get_plugin_manager registers MirrorValidator and hooks."""
    pm = get_plugin_manager()
    # Should have the validate_test_structure hook registered
    assert hasattr(pm.hook, "validate_test_structure")
    # Should have a MirrorValidator instance registered
    assert any("MirrorValidator" in str(p) for p in pm.get_plugins())


def test_get_plugin_manager_multiple_calls():
    """Test that get_plugin_manager can be called multiple times and returns new managers."""
    pm1 = get_plugin_manager()
    pm2 = get_plugin_manager()
    assert pm1 is not pm2
    assert hasattr(pm2.hook, "validate_test_structure")


def test_get_plugin_manager_plugin_registration():
    """Test that the plugin manager registers the correct plugin type."""
    pm = get_plugin_manager()
    plugins = list(pm.get_plugins())
    # There should be at least one plugin and it should be a MirrorValidator
    assert any("MirrorValidator" in str(p) for p in plugins)
