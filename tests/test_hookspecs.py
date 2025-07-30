"""Unit tests for pytest_mirror.hookspecs.

Tests that the MirrorSpecs class, hookspec marker, and validate_test_structure hook exist and are correctly defined.
"""

import inspect

import pluggy
import pytest

from pytest_mirror import hookspecs


def test_hookspec_marker_type():
    """Test that hookspec is a pluggy.HookspecMarker instance."""
    assert hasattr(hookspecs, "hookspec")
    assert isinstance(hookspecs.hookspec, pluggy.HookspecMarker)


def test_hookspec_marker_callable():
    """Test that hookspec marker is callable (for marking functions)."""
    assert callable(hookspecs.hookspec)


def test_mirrorspecs_exists():
    """Test that MirrorSpecs class exists in hookspecs."""
    assert hasattr(hookspecs, "MirrorSpecs")
    assert inspect.isclass(hookspecs.MirrorSpecs)


def test_mirrorspecs_docstring():
    """Test that MirrorSpecs has a docstring."""
    assert hookspecs.MirrorSpecs.__doc__


def test_mirrorspecs_has_validate_test_structure():
    """Test that MirrorSpecs defines validate_test_structure hook method."""
    assert hasattr(hookspecs.MirrorSpecs, "validate_test_structure")
    method = hookspecs.MirrorSpecs.validate_test_structure
    assert callable(method)


def test_validate_test_structure_signature():
    """Test the signature of validate_test_structure matches expectations (package_dir, tests_dir)."""
    method = hookspecs.MirrorSpecs.validate_test_structure
    sig = inspect.signature(method)
    params = list(sig.parameters.values())
    # Should have self, package_dir, tests_dir
    assert params[0].name == "self"
    assert params[1].name == "package_dir"
    assert params[2].name == "tests_dir"


def test_hookspec_marker_negative():
    """Test that hookspec marker does not exist under a wrong name."""
    assert not hasattr(hookspecs, "not_a_hookspec")


def test_mirrorspecs_missing_method():
    """Test that MirrorSpecs does not define a non-existent method."""
    assert not hasattr(hookspecs.MirrorSpecs, "not_a_real_hook")


def test_mirrorspecs_validate_test_structure_invocation():
    """Directly invoke MirrorSpecs.validate_test_structure to ensure coverage."""
    from pathlib import Path

    specs = hookspecs.MirrorSpecs()
    # Should raise NotImplementedError since it's a stub
    with pytest.raises(NotImplementedError):
        specs.validate_test_structure(Path("foo"), Path("bar"))
