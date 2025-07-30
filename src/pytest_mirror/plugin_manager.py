"""Plugin manager setup for pytest-mirror."""

import pluggy

from .constants import PACKAGE_NAME
from .hookspecs import MirrorSpecs
from .validator import MirrorValidator


def get_plugin_manager() -> pluggy.PluginManager:
    """Create and configure a pluggy plugin manager for pytest-mirror."""
    pm = pluggy.PluginManager(PACKAGE_NAME)
    pm.add_hookspecs(MirrorSpecs)
    pm.register(MirrorValidator())
    return pm
