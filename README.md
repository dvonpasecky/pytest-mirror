# pytest-mirror

A pluggy-based pytest plugin and CLI tool for ensuring your test suite mirrors your source code structure.

## Overview

**pytest-mirror** helps you:

- Ensure every Python module in your package has a corresponding test file.
- Quickly generate missing test stubs for new or existing code.
- Validate that your test suite structure matches your package structure.
- Integrate with pytest as a plugin or use as a standalone CLI.

Built with [pluggy](https://pluggy.readthedocs.io/) for extensible plugin architecture.

## Features

- **Test Structure Validation**: Checks for missing test files that should correspond to your package modules.
- **Test Stub Generation**: Automatically creates test files and `__init__.py` as needed, with a failing test stub.
- **CLI and Plugin**: Use as a command-line tool or as a pytest plugin.
- **Customizable**: Specify package and test directories.

## Installation

```bash
pip install pytest-mirror
```

For local development:

```bash
# Clone the repository and install in development mode
git clone https://github.com/dvonpasecky/pytest-mirror.git
cd pytest-mirror
pip install -e .
```

Or with uv:

```bash
uv sync
```

## Usage

### CLI

```bash
# With explicit directories:
pytest-mirror generate --package-dir src/your_package --tests-dir tests
pytest-mirror validate --package-dir src/your_package --tests-dir tests

# Or let pytest-mirror auto-detect your package and tests directories:
pytest-mirror generate
pytest-mirror validate
```

- `generate`: Creates missing test files for all modules in your package.
- `validate`: Checks for missing test files and reports any discrepancies.

### As a pytest Plugin

Add `pytest-mirror` to your test dependencies. The plugin will automatically:

1. **Validate** your test structure when running pytest
2. **Auto-generate** missing test files (unless disabled)

```bash
pytest
```

#### Plugin Configuration

You can customize the plugin behavior using:

- **Command-line flags:**
  - `--mirror-package-dir` (path to your package)
  - `--mirror-tests-dir` (path to your tests)
  - `--mirror-no-generate` (disable automatic test generation)

If package and tests directories are not specified, the plugin will auto-detect the most likely directories.

**Auto-generation behavior**: By default, the plugin will automatically create missing test files when pytest runs. Use `--mirror-no-generate` to disable this and only validate structure.

## API

You can also use the core functions in your own scripts:

```python
from pytest_mirror import generate_missing_tests, find_missing_tests

# Generate missing test files
generate_missing_tests('src/your_package', 'tests')

# Find missing test files without creating them
missing = find_missing_tests('src/your_package', 'tests')
print(missing)
```

## Development

- All code is in `src/pytest_mirror/`.
- Tests are in `tests/` with 1:1 module mirroring.
- Run tests with:

```bash
pytest
# or with uv:
uv run pytest
```

- Lint and check style with:

```bash
ruff check src/ tests/
# or with uv:
uv run ruff check src/ tests/
```

## Contributing

Contributions are welcome! Please:

- Add or update tests for your changes.
- Ensure all tests and linters pass.
- Update this README if needed.

## License

MIT License. See [LICENSE](LICENSE).

---

*This project is not affiliated with pytest or pluggy, but is built to extend and complement them.*
