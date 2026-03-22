# GitHub Organization Audit Framework

Professional framework for auditing GitHub organizations against best practices, community standards, and compliance requirements.

## 🎯 Features

✅ **Complete Organization Audit**
- Organization security settings
- Repository configurations
- Member and access control
- Compliance posture

✅ **Risk Analysis**
- CRITICAL, HIGH, MEDIUM, LOW, INFO severity levels
- Automatic compliance scoring (0-100%)
- Remediation priorities

✅ **Multiple Report Formats**
- JSON (programmatic access)
- HTML (visual dashboard)
- Executive Summary (text)
- Remediation Plan (markdown)

✅ **Ready-to-Use Templates**
- 3 branch protection profiles (sensitive/production/standard)
- 3 security workflows (security-scan, dependency-check, secret-scan)
- 4 governance templates (CODEOWNERS, SECURITY.md, dependabot, settings)
- Organization configuration guides

✅ **Automation**
- Manual CLI for ad-hoc audits
- GitHub Actions for scheduled audits
- Webhook integration ready

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/VoodoOps/gh-api-mgmt.git
cd gh-api-mgmt/organization

# Install dependencies
pip install -r requirements.txt
# or with dev dependencies
pip install -r requirements-dev.txt
```

### Usage

#### Manual Audit

```bash
# Basic audit (uses GITHUB_TOKEN env var)
python -m gh_audit audit VoodoOps

# Specify token
python -m gh_audit audit VoodoOps --token $GITHUB_TOKEN

# Custom output directory
python -m gh_audit audit VoodoOps --output ./my-reports

# Skip HTML generation
python -m gh_audit audit VoodoOps --no-html
```

#### Quick Security Check

```bash
# Check entire organization
python -m gh_audit check VoodoOps

# Check specific repository
python -m gh_audit check VoodoOps Lab4PurpleSec
```

#### GitHub Actions (Automated)

Scheduled audits run automatically every Sunday at 2 AM UTC.

To run manually:
1. Go to Actions tab in GitHub
2. Select "Organization Audit - Manual"
3. Click "Run workflow"
4. Enter organization name
5. Download reports as artifacts

## 📊 Reports

After running an audit, you'll find:

```
reports/VoodoOps_20260322_140000/
├── audit-report.json          # Complete audit data (programmatic)
├── audit-report.html          # Visual dashboard
├── executive-summary.txt      # Summary for stakeholders
└── remediation-plan.md        # Prioritized action items
```

### Compliance Score Interpretation

- **90-100%**: Excellent - Following best practices
- **70-89%**: Good - Minor improvements needed
- **50-69%**: Fair - Address high-priority items
- **<50%**: Poor - Critical security gaps

## 📋 Audit Standards

### Organization-Level Checks
- 2FA enforcement status
- Member verification requirements
- Outside collaborators audit
- Member roles compliance
- Security policy presence

### Repository-Level Checks
- Private visibility enforcement
- Branch protection on default branch
- Pull request review requirements
- Code owner review requirements
- Status checks requirement
- Force push restrictions
- Secret scanning enabled
- Dependabot enabled
- CODEOWNERS file presence

## 🔧 Using Templates

### Branch Protection

Choose template based on repository risk:

```bash
# For sensitive repos (2 approvals, CODEOWNERS required)
templates/branch-protection/sensitive-repos.json

# For production repos (1 approval, standard checks)
templates/branch-protection/production-repos.json

# For experimental/docs (1 approval, minimal checks)
templates/branch-protection/standard-repos.json
```

Apply via GitHub UI:
1. Repository > Settings > Rules > New branch ruleset
2. Upload JSON and configure

### Governance Files

Copy and customize templates:

```bash
# Add code ownership rules
cp templates/governance/CODEOWNERS.template CODEOWNERS

# Add security policy
cp templates/governance/SECURITY.md.template .github/SECURITY.md

# Enable Dependabot
cp templates/governance/dependabot.yml.template .github/dependabot.yml
```

### GitHub Actions Workflows

Add security checks to repositories:

```bash
mkdir -p .github/workflows

# Security scanning
cp templates/workflows/security-scan.yml .github/workflows/

# Dependency checking
cp templates/workflows/dependency-check.yml .github/workflows/

# Secret detection
cp templates/workflows/secret-scan.yml .github/workflows/
```

## 🔍 Understanding Findings

Each finding includes:

- **Risk Level**: Severity (CRITICAL → INFO)
- **Category**: Type (org-security, repo-security, access-control, compliance)
- **Title**: Brief description
- **Description**: Detailed explanation
- **Affected Items**: Repos/members impacted
- **Remediation**: How to fix
- **Template**: Reference to applicable template (if available)

## 📈 Best Practices

1. **Regular Audits**: Run weekly to track compliance progress
2. **Address Critical First**: Fix CRITICAL/HIGH findings immediately
3. **Use Templates**: Leverage provided templates for consistency
4. **Review Changes**: Always review proposed changes before applying
5. **Document**: Keep SECURITY.md updated with your policies

## 🤖 GitHub Actions Integration

### Scheduled Audit
Runs every Sunday at 2 AM UTC:
- Generates full audit reports
- Posts summary to issues
- Stores artifacts for 30 days

### Manual Audit
Triggered on-demand:
- Supports custom organization
- Optional HTML generation
- 90-day artifact retention

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/gh_audit

# Only integration tests (requires GITHUB_TOKEN)
pytest -m integration

# Specific test file
pytest tests/test_collector.py
```

## 📝 Configuration

Environment variables:

```bash
# GitHub personal access token (required)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Optional: custom API version
export GH_API_VERSION=2024-10-01
```

## 🛠️ Development

Setup development environment:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check src/

# Format code
ruff format src/

# Type checking
pyright src/
```

## 📖 Documentation

- [FRAMEWORK.md](FRAMEWORK.md) - Complete framework specification
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Architecture details
- [templates/](templates/) - Reusable configuration templates

## 🤝 Contributing

1. Report issues via GitHub Issues
2. Fork and create feature branches
3. Run tests before submitting PRs
4. Update documentation

## 📄 License

MIT License - See LICENSE file

## 🔒 Security

Found a security issue? Please email security@voodoops.com

See [SECURITY.md](templates/governance/SECURITY.md.template) for disclosure guidelines.

## 📞 Support

- GitHub Issues: Report bugs or suggest features
- Security: security@voodoops.com
- Questions: Use GitHub Discussions

---

**Framework Version**: 1.0.0
**Python**: 3.13+
**Last Updated**: 2026-03-22
