# gh-audit-framework

> Professional GitHub Organization Audit & Configuration Management Framework

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/VoodoOps/gh-api-mgmt.git
cd gh-api-mgmt
uv sync

# Set token and run audit
export GITHUB_TOKEN="ghp_your_token_here"
gh-audit audit <your-org>
```

---

## Key Features

- **21 deep-dive compliance checks** across org, repository, and member scopes
- **JSON-driven configuration management** — apply settings to org, repos, members, and teams via templates
- **Dry-run mode** — validate changes safely before applying
- **Rich HTML reports** with executive summary, risk matrix, and remediation roadmap
- **CLI with progress indicators** — colored output powered by Rich and Typer

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| Package Manager | uv | latest |
| CLI Framework | Typer + Rich | 0.9+ / 13.7+ |
| Validation | Pydantic | 2.5+ |
| Templates | Jinja2 | 3.1+ |
| Schema Validation | jsonschema | 4.0+ |
| Linter | Ruff | 0.1+ |
| Type Checker | Pyright | strict |
| Testing | pytest | 7.4+ |

---

## Project Structure

```
gh-api-mgmt/
├── src/gh_audit/          # Main package
│   ├── cli.py             # Typer CLI commands
│   ├── auditor.py         # 21 deep-dive audit checks
│   ├── analyzer.py        # Scoring and risk analysis
│   ├── configurator.py    # JSON-driven configuration
│   ├── collector.py       # GitHub API data collection
│   ├── reporter.py        # HTML/JSON/text report generation
│   ├── remediator.py      # Automated remediation
│   ├── models.py          # Data classes
│   └── utils/             # API wrapper, validation, templates, logging
├── config/
│   ├── schemas/           # JSON schemas for validation
│   └── examples/          # Reference configuration templates
├── tests/                 # 53 tests, pytest
└── pyproject.toml         # Project configuration
```

---

## Usage

### Run a full audit

```bash
gh-audit audit <org>
gh-audit audit-deep <org>    # 21-check comprehensive audit
gh-audit check <org>         # Quick security check
```

### Configuration management

```bash
# List available templates
gh-audit config list-templates

# Validate a config file
gh-audit config validate --file config/examples/org-security-hardened.json

# Apply with dry-run first
gh-audit config apply --file config/examples/org-security-hardened.json --dry-run
gh-audit config apply --file config/examples/org-security-hardened.json
```

### Python API

```python
from gh_audit import DeepDiveAuditor, Configurator

# Audit an organization
auditor = DeepDiveAuditor(token="ghp_...")
findings, summary = auditor.perform_audit("my-org")

# Apply configuration
configurator = Configurator(token="ghp_...")
result = configurator.apply_from_file("config/examples/org-security-hardened.json")
```

---

## Contributing

1. Fork the repository and create a feature branch
2. Install dev dependencies: `uv sync`
3. Run checks: `uv run pytest tests/ -v && uv run ruff check src/`
4. Submit a pull request

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
