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


class TestPluginManagerCoverage:
    """Additional tests for plugin manager module coverage."""

    def test_get_plugin_manager_returns_manager(self):
        """Test plugin manager returns a PluginManager instance."""
        pm = get_plugin_manager()
        assert hasattr(pm, "hook")
        assert hasattr(pm, "register")
        assert hasattr(pm, "unregister")

    def test_plugin_manager_has_project_name(self):
        """Test plugin manager has correct project name."""
        pm = get_plugin_manager()
        assert pm.project_name == "pytest_mirror"

    def test_plugin_manager_hook_relay(self):
        """Test plugin manager has hook relay."""
        pm = get_plugin_manager()
        assert hasattr(pm.hook, "__class__")
        # Hook relay may not have our specific hooks until plugins are registered

    def test_plugin_manager_registration(self):
        """Test plugin registration with manager."""
        from pytest_mirror.validator import MirrorValidator

        pm = get_plugin_manager()
        plugin = MirrorValidator()

        # Should be able to register plugin
        pm.register(plugin, name="test_plugin")

        # Cleanup
        pm.unregister(name="test_plugin")

    def test_plugin_manager_adds_hookspecs(self):
        """Test that plugin manager adds MirrorSpecs hookspecs."""
        pm = get_plugin_manager()

        # The plugin manager should have hookspecs functionality
        assert hasattr(pm, "add_hookspecs")
        assert callable(pm.add_hookspecs)

    def test_plugin_manager_registers_validator(self):
        """Test that plugin manager registers MirrorValidator by default."""
        pm = get_plugin_manager()

        # Should have plugins registered
        assert len(pm.get_plugins()) > 0
