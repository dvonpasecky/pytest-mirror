"""Unit tests for pytest_mirror.cli CLI logic.

Tests the generate_missing_tests and validate_missing_tests functions.
"""

import sys

from pytest_mirror import cli
from pytest_mirror.cli import generate_missing_tests, validate_missing_tests


def test_generate_missing_tests_creates_test_and_init(tmp_path):
    """Test that generate_missing_tests creates test stubs and __init__.py files."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    generate_missing_tests(pkg, tests)
    test_file = tests / "test_foo.py"
    assert test_file.exists()
    assert (tests / "__init__.py").exists()
    # The test file should contain assert False
    content = test_file.read_text()
    assert "assert False" in content


def test_generate_missing_tests_nested(tmp_path):
    """Test that nested test directories and __init__.py are created."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    sub = pkg / "sub"
    foo = sub / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    generate_missing_tests(pkg, tests)
    test_file = tests / "sub" / "test_foo.py"
    assert test_file.exists()
    assert (tests / "sub" / "__init__.py").exists()


def test_validate_missing_tests_reports_missing(capsys, tmp_path):
    """Test that validate_missing_tests prints missing test files."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    validate_missing_tests(pkg, tests)
    out = capsys.readouterr().out
    assert "Missing tests detected" in out
    assert "test_foo.py" in out


def test_generate_missing_tests_no_modules(tmp_path, capsys):
    """Test generate_missing_tests when there are no modules to mirror."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    pkg.mkdir()
    generate_missing_tests(pkg, tests)
    out = capsys.readouterr().out
    assert "All tests are in place" in out


def test_generate_missing_tests_existing_tests(tmp_path, capsys):
    """Test generate_missing_tests does not overwrite existing test files."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    test_file = tests / "test_foo.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# existing test\n")
    generate_missing_tests(pkg, tests)
    content = test_file.read_text()
    assert "existing test" in content


def test_validate_missing_tests_no_missing(tmp_path, capsys):
    """Test validate_missing_tests when all tests are present."""
    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    foo = pkg / "foo.py"
    foo.parent.mkdir(parents=True, exist_ok=True)
    foo.write_text("# dummy\n")
    test_file = tests / "test_foo.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# test\n")
    validate_missing_tests(pkg, tests)
    out = capsys.readouterr().out
    assert "All tests are in place" in out


def test_cli_main_generate_and_validate(monkeypatch, tmp_path, capsys):
    """Test cli.main() for both generate and validate commands."""
    import sys

    from pytest_mirror import cli

    pkg = tmp_path / "pkg"
    tests = tmp_path / "tests"
    (pkg / "foo.py").parent.mkdir(parents=True, exist_ok=True)
    (pkg / "foo.py").write_text("# dummy\n")

    # Test generate
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pytest-mirror",
            "generate",
            "--package-dir",
            str(pkg),
            "--tests-dir",
            str(tests),
        ],
    )
    cli.main()
    out = capsys.readouterr().out
    assert "Created" in out or "All tests are in place" in out

    # Remove test file to test validate
    test_file = tests / "test_foo.py"
    if test_file.exists():
        test_file.unlink()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pytest-mirror",
            "validate",
            "--package-dir",
            str(pkg),
            "--tests-dir",
            str(tests),
        ],
    )
    cli.main()
    out = capsys.readouterr().out
    assert "Missing tests detected" in out


def test_cli_main_help(monkeypatch, capsys):
    """Test cli.main() with --help prints usage."""
    monkeypatch.setattr(sys, "argv", ["pytest-mirror", "--help"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 0
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_cli_main_no_command(monkeypatch):
    """Test cli.main() with no command prints usage and exits."""
    import sys

    from pytest_mirror import cli

    monkeypatch.setattr(sys, "argv", ["pytest-mirror"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code != 0


def test_cli_main_invalid_command(monkeypatch, capsys):
    """Test cli.main() with an invalid command prints error and exits (with capsys)."""
    import sys

    from pytest_mirror import cli

    monkeypatch.setattr(sys, "argv", ["pytest-mirror", "notarealcommand"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code != 0
    err = capsys.readouterr().err
    assert "usage" in err.lower() or "error" in err.lower()


def test_cli_main_missing_required_args(monkeypatch, capsys):
    """Test cli.main() with missing required args prints usage and exits."""
    import sys

    from pytest_mirror import cli

    # Only the program name, no command
    monkeypatch.setattr(sys, "argv", ["pytest-mirror"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code != 0
    err = capsys.readouterr().err
    assert "usage" in err.lower()
