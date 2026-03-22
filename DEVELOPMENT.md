# Development Guide

Guide for developers contributing to the GitHub Audit Framework.

## Table of Contents

1. [Setting Up Development Environment](#setting-up-development-environment)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Testing](#testing)
5. [Running the Code](#running-the-code)
6. [Building and Packaging](#building-and-packaging)
7. [CI/CD Integration](#cicd-integration)
8. [Contributing](#contributing)

## Setting Up Development Environment

### Prerequisites

- Python 3.12 or higher
- Git
- uv (recommended package manager)
- GitHub account with admin access to test organization

### Clone Repository

```bash
git clone https://github.com/VoodoOps/gh-api-mgmt.git
cd gh-api-mgmt
```

### Install Dependencies

**Using uv (Recommended):**
```bash
uv sync
```

**Using pip:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Verify Installation

```bash
uv run python -m gh_audit version
# or
python -m gh_audit version
```

### Set Environment Variables

```bash
export GITHUB_TOKEN="ghp_your_token_here"
export PYTHONPATH="$(pwd)/src"
```

## Project Structure

```
gh-api-mgmt/
├── src/gh_audit/                    # Main package
│   ├── __init__.py                  # Package exports
│   ├── __main__.py                  # CLI entry point
│   ├── cli.py                       # Typer CLI commands
│   ├── models.py                    # Data classes
│   ├── config.py                    # Constants and enums
│   ├── analyzer.py                  # Analysis engine
│   ├── auditor.py                   # Deep-dive audit checks
│   ├── collector.py                 # Data collection
│   ├── reporter.py                  # Report generation
│   ├── configurator.py              # Configuration management
│   ├── remediator.py                # Remediation execution
│   ├── standards.py                 # Audit standards
│   └── utils/                       # Utility modules
│       ├── api.py                   # GitHub API wrapper
│       ├── validation.py            # Schema validation
│       ├── templates.py             # Template engine
│       ├── logging.py               # Structured logging
│       └── __init__.py              # Exports
│
├── tests/                           # Test suite
│   ├── conftest.py                  # Shared fixtures
│   ├── test_auditor.py             # Auditor tests
│   ├── test_analyzer_v2.py         # Analyzer tests
│   ├── test_configurator.py        # Configurator tests
│   ├── test_integration.py         # CLI integration tests
│
├── config/                          # Configuration
│   ├── schemas/                     # JSON schemas
│   │   ├── org-config.schema.json
│   │   ├── repo-config.schema.json
│   │   ├── member-config.schema.json
│   │   └── team-config.schema.json
│   ├── examples/                    # Configuration examples
│   │   ├── org-security-hardened.json
│   │   ├── repo-production.json
│   │   ├── team-devsecops.json
│   │   └── member-devsecops.json
│   └── remediation-plan.json        # Default remediation
│
├── templates/                       # GitHub templates
│   ├── branch-protection/
│   ├── workflows/
│   └── governance/
│
├── .github/workflows/               # GitHub Actions
│   ├── test.yml
│   ├── lint.yml
│   └── release.yml
│
├── pyproject.toml                   # Project configuration
├── README.md                        # Project overview
├── GETTING_STARTED.md              # User guide
├── API_REFERENCE.md                # API documentation
├── DEVELOPMENT.md                  # This file
├── CHANGELOG.md                    # Version history
└── .gitignore                      # Git exclusions
```

## Coding Standards

### Style Guide

We follow **PEP 8** and **Python 3.12+ best practices**.

**Tools:**
- **Formatter**: `ruff format` (enforced via pre-commit)
- **Linter**: `ruff check` (800+ rules)
- **Type Checker**: `pyright` (strict mode)

### Code Style Rules

```python
# Line length
MAX_LINE_LENGTH = 120

# Type hints (100% coverage)
def process_data(org: str, limit: int = 10) -> list[str]:
    """Process organization data.

    Args:
        org: Organization name
        limit: Max results

    Returns:
        List of processed items
    """
    return []

# Imports (sorted)
from typing import Any
import json
from pathlib import Path

from requests import get
from pydantic import BaseModel

from gh_audit.models import Finding
from gh_audit.utils import GitHubAPI

# Constants (UPPERCASE)
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

# Classes (PascalCase)
class SecurityAnalyzer:
    pass

# Methods/Functions (snake_case)
def analyze_org(org_name: str) -> dict[str, Any]:
    pass
```

### Pre-commit Hooks

Install pre-commit hooks to enforce standards:

```bash
uv run pre-commit install
```

Hooks will run automatically on commit:
- Ruff format check
- Ruff lint check
- Pyright type checking
- YAML validation
- JSON validation

Manually run hooks:
```bash
uv run pre-commit run --all-files
```

## Testing

### Test Organization

Tests are organized by module:

```
tests/
├── conftest.py              # Shared fixtures
├── test_auditor.py          # DeepDiveAuditor tests
├── test_analyzer_v2.py      # Analyzer enhancement tests
├── test_configurator.py     # Configurator tests
└── test_integration.py      # CLI integration tests
```

### Running Tests

**All tests:**
```bash
uv run pytest tests/ -v
```

**Specific test file:**
```bash
uv run pytest tests/test_configurator.py -v
```

**Specific test class:**
```bash
uv run pytest tests/test_configurator.py::TestConfigurator -v
```

**Specific test:**
```bash
uv run pytest tests/test_configurator.py::TestConfigurator::test_validation -v
```

**With coverage:**
```bash
uv run pytest tests/ -v --cov=src/gh_audit --cov-report=html
```

### Writing Tests

Example test structure:

```python
"""Tests for my_module.py"""

import pytest
from unittest.mock import MagicMock, patch

from gh_audit.my_module import MyClass
from gh_audit.models import Finding


class TestMyClass:
    """Test MyClass functionality."""

    @pytest.fixture
    def my_instance(self) -> MyClass:
        """Create test instance."""
        return MyClass()

    def test_initialization(self, my_instance: MyClass) -> None:
        """Test class initialization."""
        assert my_instance is not None

    @patch("gh_audit.my_module.external_function")
    def test_with_mocking(self, mock_external: MagicMock) -> None:
        """Test with mocked external dependency."""
        mock_external.return_value = {"status": "ok"}

        instance = MyClass()
        result = instance.do_something()

        assert result is not None
        mock_external.assert_called_once()

    def test_error_handling(self) -> None:
        """Test error handling."""
        with pytest.raises(ValueError):
            MyClass().invalid_operation()
```

### Test Coverage

Target: **80%+ coverage**

Current coverage:
```bash
uv run pytest tests/ --cov=src/gh_audit --cov-report=term
```

View HTML coverage report:
```bash
uv run pytest tests/ --cov=src/gh_audit --cov-report=html
open htmlcov/index.html
```

## Running the Code

### From Command Line

```bash
# Run with uv
uv run gh-audit --help

# Or activate venv first
source venv/bin/activate
gh-audit --help
```

### From Python

```python
from gh_audit import Auditor, Configurator

# Audit
auditor = Auditor(token="ghp_...")
findings, summary = auditor.audit_organization("my-org")

# Configure
configurator = Configurator(token="ghp_...")
result = configurator.apply_from_file("config/my-config.json")
```

### Debug Logging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gh_audit")

from gh_audit import Auditor
auditor = Auditor(token="ghp_...")
# Now get detailed logs
```

## Building and Packaging

### Build Distribution

```bash
# Using build package
uv run python -m build

# Output:
# dist/gh-audit-framework-2.0.0.tar.gz
# dist/gh_audit_framework-2.0.0-py3-none-any.whl
```

### Install Locally

```bash
# Development install (editable)
pip install -e .

# Production install
pip install dist/gh_audit_framework-2.0.0-py3-none-any.whl
```

### Publish to PyPI

```bash
# Test PyPI first
uv run twine upload --repository testpypi dist/*

# Production
uv run twine upload dist/*
```

## CI/CD Integration

### GitHub Actions Workflows

#### `.github/workflows/test.yml`

```yaml
name: Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13']

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[dev]
      - run: pytest tests/ -v --cov=src/gh_audit
      - uses: codecov/codecov-action@v3
```

#### `.github/workflows/lint.yml`

```yaml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install ruff pyright
      - run: ruff format --check src/ tests/
      - run: ruff check src/ tests/
      - run: pyright src/
```

### Local Validation

```bash
# Format code
uv run ruff format src/ tests/

# Check linting
uv run ruff check src/ tests/

# Type checking
uv run pyright src/

# Run all tests
uv run pytest tests/ -v

# Check everything
uv run pre-commit run --all-files
```

## Contributing

### Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**
   - Write code following style guide
   - Add tests for new functionality
   - Update documentation

3. **Test Locally**
   ```bash
   uv run pytest tests/ -v
   uv run ruff check src/ tests/
   uv run pyright src/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-feature
   ```
   Create pull request on GitHub

6. **Address Review Comments**
   - Make requested changes
   - Push updates
   - Respond to comments

7. **Merge**
   - Squash and merge to main
   - Delete feature branch

### Commit Message Format

```
[TYPE] Brief description

Longer explanation of changes:
- What was changed
- Why it was changed
- How it works

Fixes: #123
Related: #456
```

**Types**: feat, fix, docs, test, refactor, perf, chore

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Test

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes
```

## Release Process

### Version Numbering

We use **Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

1. **Update Version**
   ```bash
   # Update pyproject.toml
   # version = "2.1.0"
   ```

2. **Update CHANGELOG**
   ```markdown
   ## [2.1.0] - 2024-01-15

   ### Added
   - New feature X

   ### Fixed
   - Bug fix Y
   ```

3. **Commit Release**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release v2.1.0"
   git tag v2.1.0
   git push origin main --tags
   ```

4. **Build and Publish**
   ```bash
   uv run python -m build
   uv run twine upload dist/*
   ```

## Getting Help

- **Issues**: https://github.com/VoodoOps/gh-api-mgmt/issues
- **Discussions**: https://github.com/VoodoOps/gh-api-mgmt/discussions
- **Documentation**: See README.md and API_REFERENCE.md

---

Happy coding! 🚀
