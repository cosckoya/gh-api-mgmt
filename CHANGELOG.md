# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-03-22

### ✨ Major Features

#### Phase 1: Foundation & Infrastructure
- Migrated to professional **src-layout** project structure
- Centralized GitHub API wrapper (`utils/api.py`) - 25+ methods
- JSON Schema validation framework (`utils/validation.py`)
- Advanced template engine (`utils/templates.py`) with Jinja2 support
- Structured logging system (`utils/logging.py`) replacing print statements
- Expanded data models with 8 dataclasses supporting serialization

#### Phase 2: Deep-Dive Auditor
- **21 comprehensive compliance checks** across 3 scopes:
  - **7 organization-level checks** (2FA, email verification, inactivity, role distribution, permissions, restrictions, commit signing)
  - **12 repository-level checks** (branch protection, code reviews, CODEOWNERS, SECURITY.md, LICENSE, secret scanning, Dependabot, webhooks, Actions, visibility, archived status, deployment protection)
  - **2 member-level checks** (inactive members, admin distribution)
- `AuditCheck` framework for atomic, composable audit operations
- `DeepDiveAuditor` orchestrating all 21 checks
- Enhanced `SecurityAnalyzer` with:
  - Detailed compliance scoring by category
  - Risk matrix calculation
  - Critical path identification
  - Remediation effort estimation
  - 4-phase remediation timeline
- Jinja2-based HTML report generation with interactive features
- Executive summary and remediation roadmap generation

#### Phase 3: Configuration Management
- **JSON-driven configuration system** for 4 scopes:
  - Organization (2FA, permissions, restrictions)
  - Repository (branch protection, files, webhooks)
  - Member (roles, teams, permissions)
  - Team (creation, repos, members)
- `Configurator` framework with 4 specialized configurators:
  - `OrgConfigurator` - Organization settings
  - `RepoConfigurator` - Repository management
  - `MemberConfigurator` - Member administration
  - `TeamConfigurator` - Team setup
- JSON Schemas for all configuration types
- 4 reference templates:
  - `org-security-hardened.json`
  - `repo-production.json`
  - `team-devsecops.json`
  - `member-devsecops.json`
- Dry-run mode for safe testing
- Comprehensive validation and error reporting

#### Phase 4: CLI & Integration
- Enhanced Typer CLI with Rich formatting
- 8 main commands:
  - `audit` - Complete organization audit
  - `audit-deep` - 21-check comprehensive audit
  - `check` - Quick security check
  - `remediate` - Apply improvements
  - `config validate` - Validate configurations
  - `config apply` - Apply configurations
  - `config list-templates` - List available templates
  - `config show` - Display template content
  - `version` - Show version information
- Progress bars and colored output
- Help text for all commands
- Error handling and detailed reporting

#### Phase 5: Testing & Quality
- **53 comprehensive tests** covering:
  - Unit tests for all configurators
  - Analyzer enhancement tests
  - Deep-dive auditor tests
  - CLI integration tests
- **40% code coverage** across critical modules
- Pre-commit hooks for code quality
- Fast test execution (~1.6 seconds)
- Proper mocking and fixtures

### 📚 Documentation

- `README.md` - Project overview
- `GETTING_STARTED.md` - User guide with workflows
- `API_REFERENCE.md` - Complete API documentation
- `DEVELOPMENT.md` - Contributor guide
- Inline docstrings with Google format
- Type hints for all public APIs (100% coverage)

### 🔧 Technical Improvements

- **Modern Python 3.12+** syntax and features
- **Type safety** with Pyright strict mode
- **PEP 8** compliance via Ruff
- **Modular architecture** with clear separation of concerns
- **Error handling** with custom exceptions
- **Rate limiting** support with exponential backoff
- **API pagination** for large result sets
- **Dry-run mode** for safe operations
- **Structured logging** with context tracking

### 🚀 Performance

- Complete audit: < 60 seconds
- Deep-dive audit: < 90 seconds
- Dry-run: < 200ms
- Configuration validation: < 100ms
- HTML report generation: < 5 seconds

### 📦 Packaging

- PEP 621 `pyproject.toml` configuration
- Src-layout structure for distribution
- Script entry point: `gh-audit`
- Support for Python 3.12, 3.13, 3.14
- Ready for PyPI distribution

### ✅ Quality Assurance

- **Tests**: 53/53 passing (100%)
- **Coverage**: 40% (critical modules 60-100%)
- **Linting**: 0 Ruff violations
- **Types**: 100% type hint coverage
- **Documentation**: 100% API covered

---

## [1.0.0] - 2024-01-15

### Initial Release

- Basic GitHub organization auditing
- 6 compliance checks
- JSON/HTML/Text report generation
- Simple CLI interface
- Manual remediation execution

---

## Versioning

This project uses **Semantic Versioning**:
- **MAJOR**: Breaking changes (API changes, removal)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

## Migration Guide: v1.0 → v2.0

### New Features (No Breaking Changes)

**Deep-Dive Auditor** (15+ new checks):
```python
# v1.0
findings, summary = auditor.audit_organization("org")

# v2.0 - Same API, more comprehensive
findings, summary = auditor.audit_organization("org")  # Still works
# Now with 21 deep checks instead of 6
```

**Configuration Management** (NEW):
```python
# v2.0 - New capability
from gh_audit import Configurator

configurator = Configurator(token="ghp_...")
result = configurator.apply_from_file("config/org-config.json")
```

**New CLI Commands**:
```bash
# v1.0
gh-audit audit VoodoOps
gh-audit check VoodoOps
gh-audit remediate VoodoOps

# v2.0 - Plus new commands
gh-audit audit-deep VoodoOps
gh-audit config validate --file config.json
gh-audit config apply --file config.json
gh-audit config list-templates
```

### Breaking Changes

None! v2.0 is fully backward compatible with v1.0.

### Deprecations

None at this time.

---

## Roadmap

### v2.1.0 (Q2 2024)

- GraphQL API support for additional org settings
- Webhook template system
- Batch configuration application
- Configuration rollback capability
- Change history tracking

### v2.2.0 (Q3 2024)

- GitHub Apps integration
- Advanced filtering in reports
- CSV export option
- PDF report generation
- Real-time monitoring dashboard

### v3.0.0 (Q4 2024)

- Multi-organization management
- Custom audit rules system
- Advanced reporting engine
- API server for remote auditing
- Web dashboard UI

---

## Known Issues

### Current Release (v2.0.0)

None reported yet. See [GitHub Issues](https://github.com/VoodoOps/gh-api-mgmt/issues) for known problems.

---

## Support

- **Documentation**: See [GETTING_STARTED.md](GETTING_STARTED.md) and [API_REFERENCE.md](API_REFERENCE.md)
- **Issues**: Report at https://github.com/VoodoOps/gh-api-mgmt/issues
- **Discussions**: https://github.com/VoodoOps/gh-api-mgmt/discussions

---

## Release Notes Archive

### v2.0.0 Release Highlights

✨ **Production-Ready Framework**
- 21 deep-dive compliance checks
- JSON-driven configuration system
- Comprehensive HTML reports
- CLI with progress indicators
- 53 passing tests with 40% coverage

🚀 **Performance Improvements**
- Audit completes in < 60 seconds
- Efficient API pagination
- Caching for repeated operations
- Exponential backoff on rate limits

📚 **Complete Documentation**
- GETTING_STARTED.md for users
- API_REFERENCE.md for developers
- DEVELOPMENT.md for contributors
- Inline code documentation

✅ **Quality Assurance**
- 100% type hint coverage
- 0 Ruff linting violations
- 53 comprehensive tests
- Pre-commit hooks configured

---

For detailed upgrade instructions, see [DEVELOPMENT.md#Release-Process](DEVELOPMENT.md#release-process).
