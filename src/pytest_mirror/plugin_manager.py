"""Plugin manager setup for pytest-mirror."""

import pluggy

from .hookspecs import MirrorSpecs
from .validator import MirrorValidator


def get_plugin_manager() -> pluggy.PluginManager:
    """Create and configure a pluggy plugin manager for pytest-mirror."""
    pm = pluggy.PluginManager("pytest_mirror")
    pm.add_hookspecs(MirrorSpecs)
    pm.register(MirrorValidator())
    return pm
