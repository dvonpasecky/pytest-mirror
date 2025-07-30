"""Hook specifications for pytest-mirror plugin.

Defines the MirrorSpecs class for pluggy hook specifications.
"""

from pathlib import Path

import pluggy

hookspec = pluggy.HookspecMarker("pytest_mirror")


class MirrorSpecs:
    """Hook specifications for pytest-mirror plugin."""

    @hookspec
    def validate_test_structure(self, package_dir: Path, tests_dir: Path) -> list[Path]:
        """Validate that each module in package_dir has a corresponding test module.

        Args:
            package_dir (Path): Path to the main package directory.
            tests_dir (Path): Path to the tests directory.

        Returns:
            list[Path]: List of paths to missing test files.
        """
        raise NotImplementedError("This is a hook specification stub.")
