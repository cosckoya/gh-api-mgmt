# Getting Started with GitHub Audit Framework v2.0

Welcome to the GitHub Audit Framework! This guide will help you get up and running quickly.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Workflows](#core-workflows)
4. [Configuration](#configuration)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.12 or higher
- GitHub personal access token with admin access to organizations

### From Source

```bash
git clone https://github.com/VoodoOps/gh-api-mgmt.git
cd gh-api-mgmt
pip install -e .
```

### Using uv (Recommended)

```bash
uv sync
uv run gh-audit --version
```

### Using pip

```bash
pip install gh-audit-framework
gh-audit --version
```

## Quick Start

### 1. Set Your GitHub Token

```bash
export GITHUB_TOKEN="ghp_your_personal_access_token_here"
```

### 2. Run a Quick Security Check

```bash
gh-audit check VoodoOps
```

Expected output:
```
Quick Security Check
Organization: VoodoOps

Total Repositories: 2
Total Members: 5

Organization Overview
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ Metric            ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━┩
│ Private Repos     │ 1/2   │
│ Branch Protection │ 0/2   │
│ Secret Scanning   │ 0/2   │
└───────────────────┴───────┘
```

### 3. Run a Complete Audit

```bash
gh-audit audit VoodoOps --output ./reports
```

This generates:
- `audit-report.json` - Programmatic results
- `audit-report.html` - Interactive dashboard
- `executive-summary.txt` - For stakeholders
- `remediation-plan.md` - Action items

### 4. Deep-Dive Audit (21 Comprehensive Checks)

```bash
gh-audit audit-deep VoodoOps --output ./reports
```

Performs 21 checks across:
- Organization security settings
- Repository configuration
- Member access patterns
- Team structure and permissions

## Core Workflows

### Workflow 1: Audit → Remediate

```bash
# 1. Audit your organization
gh-audit audit VoodoOps --output ./reports

# 2. Review findings
cat reports/VoodoOps_20240101_120000/remediation-plan.md

# 3. Apply improvements
gh-audit remediate VoodoOps --dry-run  # Preview changes
gh-audit remediate VoodoOps            # Apply changes

# 4. Verify improvements
gh-audit audit VoodoOps
```

### Workflow 2: Configuration as Code

```bash
# 1. View available templates
gh-audit config list-templates

# 2. Show a template
gh-audit config show org-security-hardened.json

# 3. Validate configuration
gh-audit config validate --file config/examples/org-security-hardened.json

# 4. Apply configuration (dry-run first!)
gh-audit config apply --file config/examples/org-security-hardened.json --dry-run
gh-audit config apply --file config/examples/org-security-hardened.json
```

### Workflow 3: Continuous Monitoring

Set up GitHub Actions to run audits on schedule:

```yaml
name: Weekly Security Audit
on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2 AM UTC

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -e .
      - run: gh-audit audit VoodoOps --output ./reports
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: audit-reports
          path: reports/
```

## Configuration

### Understanding Scopes

Configurations have different scopes:

| Scope | Purpose | Example |
|-------|---------|---------|
| `org` | Organization-wide settings | 2FA requirement, member permissions |
| `repo` | Repository-specific settings | Branch protection, governance files |
| `member` | Individual member management | Role assignment, team membership |
| `team` | Team configuration | Team creation, repository access |

### Configuration Structure

```json
{
  "scope": "org",
  "organization": "VoodoOps",
  "two_factor_required": true,
  "default_member_permission": "pull",
  "web_commit_signoff_required": true
}
```

### Available Configuration Templates

1. **org-security-hardened.json**
   - Strict security policies
   - 2FA required
   - Limited repository creation
   - Signed commits required

2. **repo-production.json**
   - Production-grade repository
   - Branch protection rules
   - Required code reviews
   - Status checks

3. **team-devsecops.json**
   - DevSecOps team setup
   - Infrastructure repository access
   - Admin permissions for sensitive repos

4. **member-devsecops.json**
   - Team member onboarding
   - Role assignment
   - Team membership setup

## Common Tasks

### Task 1: Enable 2FA Organization-Wide

```bash
cat > config/my-config.json << 'EOF'
{
  "scope": "org",
  "organization": "VoodoOps",
  "two_factor_required": true
}
EOF

gh-audit config apply --file config/my-config.json --dry-run
gh-audit config apply --file config/my-config.json
```

### Task 2: Set Up Branch Protection

```bash
cat > config/branch-protection.json << 'EOF'
{
  "scope": "repo",
  "owner": "VoodoOps",
  "repository": "main-api",
  "branch_protection": {
    "name": "main-protection",
    "target": "branch",
    "pattern": "main"
  }
}
EOF

gh-audit config apply --file config/branch-protection.json
```

### Task 3: Create Governance Files

```bash
cat > config/add-governance.json << 'EOF'
{
  "scope": "repo",
  "owner": "VoodoOps",
  "repository": "main-api",
  "files": [
    {
      "path": ".github/CODEOWNERS",
      "content": "* @security-team",
      "message": "Add CODEOWNERS"
    },
    {
      "path": "SECURITY.md",
      "content": "# Security Policy\n\nReport vulnerabilities to security@voodoops.com",
      "message": "Add security policy"
    }
  ]
}
EOF

gh-audit config apply --file config/add-governance.json
```

### Task 4: Export Audit Results

```bash
# JSON format (programmatic access)
gh-audit audit VoodoOps --output ./reports
cat reports/VoodoOps_20240101_120000/audit-report.json

# HTML format (visual dashboard)
open reports/VoodoOps_20240101_120000/audit-report.html

# Text format (email/chat)
cat reports/VoodoOps_20240101_120000/executive-summary.txt
```

## Troubleshooting

### Issue: "Token not found" error

```bash
# Set token explicitly
gh-audit audit VoodoOps --token ghp_your_token_here

# Or export environment variable
export GITHUB_TOKEN="ghp_your_token_here"
gh-audit audit VoodoOps
```

### Issue: "Permission denied" error

Check your token has required scopes:
- `admin:org_hook` - Organization webhooks
- `admin:org` - Organization administration
- `admin:repo_hook` - Repository webhooks
- `repo` - Repository access

### Issue: "API rate limit exceeded"

The framework includes exponential backoff. Wait a few minutes or:

```bash
# Generate a new token with different scopes
export GITHUB_TOKEN="ghp_new_token"
gh-audit audit VoodoOps
```

### Issue: Configuration validation fails

```bash
# Validate configuration first
gh-audit config validate --file config/my-config.json

# View template to check structure
gh-audit config show org-security-hardened.json
```

### Issue: Changes not visible in GitHub

Some settings require a page refresh in GitHub web UI. Also check:

1. Required scopes on token
2. Organization permissions
3. GitHub free vs. paid tier limitations

## Getting Help

### View Help for Any Command

```bash
# Main help
gh-audit --help

# Command-specific help
gh-audit audit --help
gh-audit config --help
gh-audit remediate --help
```

### View Command Examples

```bash
gh-audit config show org-security-hardened.json
gh-audit config show repo-production.json
gh-audit config show team-devsecops.json
```

### Check Version

```bash
gh-audit version
```

Output:
```
GitHub Audit Framework
Version: 2.0.0
Python: 3.12+

Features:
  • Deep-dive audit with 21+ compliance checks
  • JSON-driven configuration management
  • Comprehensive HTML reports with remediation roadmap
  • Dry-run mode for safe testing
```

## Next Steps

1. **Review Audit Results** - Start with `audit` to see your organization's current state
2. **Plan Improvements** - Look at `remediation-plan.md` for prioritized actions
3. **Test Configurations** - Use `--dry-run` to preview changes before applying
4. **Apply Incrementally** - Start with high-impact, low-risk configurations
5. **Monitor Progress** - Run audits regularly to track improvements

## Advanced Usage

### Custom Configuration Files

Create your organization-specific configuration:

```bash
cat > config/org-config.json << 'EOF'
{
  "scope": "org",
  "organization": "VoodoOps",
  "description": "Custom organization security config",
  "two_factor_required": true,
  "default_member_permission": "pull",
  "members_can_create_repositories": false,
  "members_can_fork_private_repositories": false,
  "web_commit_signoff_required": true
}
EOF

gh-audit config apply --file config/org-config.json
```

### Batch Operations

Apply multiple configurations:

```bash
for config in config/examples/*.json; do
  echo "Applying $config..."
  gh-audit config apply --file "$config" --dry-run
done
```

### Integration with CI/CD

See [DEVELOPMENT.md](DEVELOPMENT.md) for GitHub Actions setup and CI/CD integration.

---

**Ready to get started? Run:**

```bash
gh-audit version
gh-audit check VoodoOps
```

For detailed API documentation, see [API_REFERENCE.md](API_REFERENCE.md).
