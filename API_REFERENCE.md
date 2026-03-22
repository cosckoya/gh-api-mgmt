# API Reference - GitHub Audit Framework v2.0

Complete API documentation for the GitHub Audit Framework.

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Python API](#python-api)
3. [Data Models](#data-models)
4. [Configuration Format](#configuration-format)
5. [Error Handling](#error-handling)

## CLI Commands

### `audit`

Run a complete audit of a GitHub organization.

**Usage:**
```bash
gh-audit audit ORGANIZATION [OPTIONS]
```

**Arguments:**
- `ORGANIZATION` - GitHub organization name

**Options:**
- `--token, -t TEXT` - GitHub personal access token (defaults to GITHUB_TOKEN env var)
- `--output, -o TEXT` - Output directory for reports (default: `reports`)
- `--no-html` - Skip HTML report generation

**Returns:**
- JSON report: `{org}_{timestamp}/audit-report.json`
- HTML report: `{org}_{timestamp}/audit-report.html`
- Text summary: `{org}_{timestamp}/executive-summary.txt`
- Remediation plan: `{org}_{timestamp}/remediation-plan.md`

**Example:**
```bash
gh-audit audit VoodoOps --output ./my-reports
```

**Output Structure:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "organization": "VoodoOps",
  "total_repos": 5,
  "total_findings": 3,
  "findings": [
    {
      "rule_id": "REPO-001",
      "risk_level": "HIGH",
      "title": "Branch Protection Missing",
      "affected_items": ["repo1", "repo2"]
    }
  ]
}
```

---

### `audit-deep`

Run a comprehensive 21-check deep-dive audit.

**Usage:**
```bash
gh-audit audit-deep ORGANIZATION [OPTIONS]
```

**Arguments:**
- `ORGANIZATION` - GitHub organization name

**Options:**
- `--token, -t TEXT` - GitHub personal access token
- `--output, -o TEXT` - Output directory for reports
- `--no-html` - Skip HTML report generation

**Checks Performed:** 21 total
- 7 organization-level checks
- 12 repository-level checks
- 2 member-level checks

**Example:**
```bash
gh-audit audit-deep VoodoOps --output ./reports
```

---

### `check`

Quick security check (faster than full audit).

**Usage:**
```bash
gh-audit check ORGANIZATION [REPOSITORY] [OPTIONS]
```

**Arguments:**
- `ORGANIZATION` - GitHub organization name
- `REPOSITORY` - Optional repository name

**Options:**
- `--token, -t TEXT` - GitHub personal access token

**Quick Checks:**
- Private/Public status
- Branch protection enabled
- Secret scanning enabled
- Dependabot enabled

**Example:**
```bash
# Check entire organization
gh-audit check VoodoOps

# Check specific repository
gh-audit check VoodoOps my-repo
```

---

### `remediate`

Apply security improvements to organization.

**Usage:**
```bash
gh-audit remediate ORGANIZATION [OPTIONS]
```

**Arguments:**
- `ORGANIZATION` - GitHub organization name

**Options:**
- `--token, -t TEXT` - GitHub personal access token
- `--config, -c TEXT` - Path to remediation plan JSON (default: `config/remediation-plan.json`)
- `--dry-run` - Simulate without applying changes

**Actions Applied:**
- Create governance files (CODEOWNERS, SECURITY.md, LICENSE)
- Configure GitHub workflows (security scanning, dependency checks)
- Apply branch protection rulesets
- Enable Dependabot automation

**Example:**
```bash
# Preview changes
gh-audit remediate VoodoOps --dry-run

# Apply changes
gh-audit remediate VoodoOps
```

---

### `config validate`

Validate configuration file against schema.

**Usage:**
```bash
gh-audit config validate --file FILE
```

**Options:**
- `--file, -f TEXT` - Configuration file path (required)

**Validation Checks:**
- Required fields present
- Field types correct
- Enum values valid
- Scope-specific requirements

**Example:**
```bash
gh-audit config validate --file config/examples/org-security-hardened.json
```

---

### `config apply`

Apply configuration to GitHub organization/repository.

**Usage:**
```bash
gh-audit config apply --file FILE [OPTIONS]
```

**Options:**
- `--file, -f TEXT` - Configuration file path (required)
- `--token, -t TEXT` - GitHub personal access token
- `--dry-run` - Simulate without applying changes

**Supported Scopes:**
- `org` - Organization settings
- `repo` - Repository settings
- `member` - Member management
- `team` - Team configuration

**Example:**
```bash
# Dry run
gh-audit config apply --file config/my-config.json --dry-run

# Apply
gh-audit config apply --file config/my-config.json
```

---

### `config list-templates`

List available configuration templates.

**Usage:**
```bash
gh-audit config list-templates
```

**Available Templates:**
- `org-security-hardened.json`
- `repo-production.json`
- `team-devsecops.json`
- `member-devsecops.json`

**Example:**
```bash
gh-audit config list-templates
```

---

### `config show`

Display configuration template content.

**Usage:**
```bash
gh-audit config show TEMPLATE
```

**Arguments:**
- `TEMPLATE` - Template name or file path

**Example:**
```bash
gh-audit config show org-security-hardened.json
gh-audit config show config/examples/repo-production.json
```

---

### `version`

Show version and feature information.

**Usage:**
```bash
gh-audit version
```

**Example Output:**
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

---

## Python API

### Core Modules

#### `gh_audit.Auditor`

```python
from gh_audit import Auditor

auditor = Auditor(token="ghp_...")
findings, summary = auditor.audit_organization("VoodoOps")

for finding in findings:
    print(f"{finding.rule_id}: {finding.title}")
    print(f"Risk: {finding.risk_level}")
    print(f"Affected: {finding.affected_items}")
```

#### `gh_audit.DeepDiveAuditor`

```python
from gh_audit import DeepDiveAuditor

auditor = DeepDiveAuditor(token="ghp_...")
findings, summary = auditor.perform_audit("VoodoOps")

print(f"Total checks: {len(auditor.checks)}")
print(f"Findings: {summary.total_findings}")
print(f"Critical: {summary.critical}")
```

#### `gh_audit.Configurator`

```python
from gh_audit import Configurator

configurator = Configurator(token="ghp_...")

# Load configuration
config = configurator.load_configuration("config/my-config.json")

# Validate
is_valid, errors = configurator.validate_configuration(config)
if not is_valid:
    print(f"Validation errors: {errors}")

# Apply
result = configurator.apply_configuration(config, dry_run=True)
print(f"Changes would be applied: {result.changes_applied}")

# Apply for real
result = configurator.apply_configuration(config)
print(f"Success: {result.success}")
```

#### `gh_audit.SecurityAnalyzer`

```python
from gh_audit import SecurityAnalyzer

analyzer = SecurityAnalyzer()
findings, summary = analyzer.analyze(org_data, repos_data, collaborators)

# Get detailed analysis
compliance_score = analyzer.get_detailed_compliance_score()
risk_matrix = analyzer.get_risk_matrix()
critical_path = analyzer.get_critical_path()
timeline = analyzer.get_remediation_timeline()

print(f"Compliance: {compliance_score.total_score}%")
print(f"Risk profile: {risk_matrix}")
```

#### `gh_audit.utils.GitHubAPI`

```python
from gh_audit.utils import GitHubAPI

api = GitHubAPI(token="ghp_...")

# Organization operations
org = api.get_org("VoodoOps")
members = api.get_org_members("VoodoOps")
teams = api.get_org_teams("VoodoOps")

# Repository operations
repo = api.get_repo("VoodoOps", "my-repo")
protection = api.get_repo_branch_protection("VoodoOps", "my-repo", "main")

# Update operations
api.update_org_settings("VoodoOps", {"two_factor_requirement_enabled": True})
api.create_file_in_repo("VoodoOps", "my-repo", "CODEOWNERS", "* @team", "msg")
```

---

## Data Models

### Finding

Represents a single audit finding.

```python
@dataclass
class Finding:
    rule_id: str              # e.g., "REPO-001"
    risk_level: RiskLevel     # CRITICAL, HIGH, MEDIUM, LOW
    category: Category        # SECURITY, GOVERNANCE, COMPLIANCE, etc.
    title: str                # "Branch Protection Missing"
    description: str          # Detailed explanation
    affected_items: list[str] # ["repo1", "repo2"]
    remediation: str          # How to fix
    template_url: str | None  # Link to remediation template
```

### OrganizationData

GitHub organization data.

```python
@dataclass
class OrganizationData:
    login: str                          # Organization handle
    name: str | None                    # Display name
    plan: str                           # free, pro, team, enterprise
    created_at: str                     # ISO format timestamp
    members_count: int                  # Total members
    public_repos_count: int             # Public repositories
    total_repos_count: int | None       # All repositories
    findings: list[Finding]             # Audit findings
```

### RepositoryData

GitHub repository data.

```python
@dataclass
class RepositoryData:
    name: str                           # Repository name
    visibility: str                     # public, private, internal
    description: str | None             # Repository description
    is_archived: bool                   # Archived status
    is_fork: bool                       # Fork status
    default_branch: str                 # Default branch name
    url: str                            # Repository URL
    owner: str                          # Owner login
    branch_protection: dict | None      # Branch protection rules
    has_secret_scanning: bool           # Secret scanning enabled
    has_dependabot: bool                # Dependabot enabled
    findings: list[Finding]             # Repository findings
```

### AuditSummary

Overall audit results summary.

```python
@dataclass
class AuditSummary:
    timestamp: datetime         # When audit ran
    organization: str           # Organization audited
    total_repos: int            # Total repositories
    repos_audited: int          # Repositories successfully audited
    total_findings: int         # Total findings
    critical: int               # Critical findings
    high: int                   # High severity findings
    medium: int                 # Medium severity findings
    low: int                    # Low severity findings
    compliance_score: float     # 0-100 compliance percentage
    scan_duration_seconds: float # How long audit took
```

### ConfigResult

Configuration application result.

```python
@dataclass
class ConfigResult:
    success: bool               # Whether application succeeded
    message: str                # Result message
    changes_applied: int        # Number of changes applied
    errors: list[ValidationError]  # Any errors encountered
```

---

## Configuration Format

### Organization Configuration

```json
{
  "scope": "org",
  "organization": "VoodoOps",
  "description": "Organization security config",
  "two_factor_required": true,
  "default_member_permission": "pull",
  "members_can_create_repositories": false,
  "members_can_create_internal_repositories": false,
  "members_can_create_private_repositories": false,
  "members_can_create_public_repositories": false,
  "members_can_fork_private_repositories": false,
  "web_commit_signoff_required": true
}
```

**Scope: `org`**

Fields:
- `organization` (required) - Organization name
- `two_factor_required` - Require 2FA for all members
- `default_member_permission` - Default permission: pull, push, admin, maintain, triage
- `members_can_create_repositories` - Allow repo creation
- `members_can_fork_private_repositories` - Allow forking private repos
- `web_commit_signoff_required` - Require commit signatures

---

### Repository Configuration

```json
{
  "scope": "repo",
  "owner": "VoodoOps",
  "repository": "my-repo",
  "description": "Repository protection setup",
  "branch_protection": {
    "name": "main-protection",
    "target": "branch",
    "pattern": "main",
    "enforce_admins": true
  },
  "files": [
    {
      "path": ".github/CODEOWNERS",
      "content": "* @team-lead",
      "message": "Add CODEOWNERS"
    }
  ],
  "webhooks": [],
  "visibility": "private"
}
```

**Scope: `repo`**

Fields:
- `owner` (required) - Repository owner
- `repository` (required) - Repository name
- `branch_protection` - Branch protection ruleset
- `files` - Files to create (CODEOWNERS, SECURITY.md, LICENSE, etc.)
- `webhooks` - Webhook configurations
- `visibility` - Repository visibility: private, public, internal

---

### Member Configuration

```json
{
  "scope": "member",
  "organization": "VoodoOps",
  "username": "alice",
  "role": "admin",
  "teams": ["DevSecOps", "Infrastructure"],
  "permissions": {
    "org_level": "admin"
  }
}
```

**Scope: `member`**

Fields:
- `organization` (required) - Organization name
- `username` (required) - GitHub username
- `role` - Role: member, maintainer, admin
- `teams` - Teams to add member to
- `permissions` - Permission settings

---

### Team Configuration

```json
{
  "scope": "team",
  "organization": "VoodoOps",
  "team_name": "DevSecOps",
  "description": "DevSecOps team",
  "privacy": "closed",
  "repositories": [
    {
      "name": "security-tools",
      "permission": "admin"
    },
    {
      "name": "infrastructure",
      "permission": "maintain"
    }
  ],
  "members": [
    {
      "username": "alice",
      "role": "maintainer"
    }
  ]
}
```

**Scope: `team`**

Fields:
- `organization` (required) - Organization name
- `team_name` (required) - Team name
- `privacy` - Team privacy: closed, secret
- `repositories` - Repository access settings
- `members` - Team members

---

## Error Handling

### GitHubAPIError

Raised when GitHub API calls fail.

```python
from gh_audit.utils import GitHubAPIError

try:
    auditor = Auditor(token="invalid_token")
    auditor.audit_organization("org")
except GitHubAPIError as e:
    print(f"API Error: {e}")
    # Handle API error
```

### ConfigValidationError

Raised when configuration validation fails.

```python
from gh_audit.utils import ConfigValidationError

try:
    configurator = Configurator(token="ghp_...")
    configurator.validate_configuration(config)
except ConfigValidationError as e:
    print(f"Validation Error: {e}")
    # Handle validation error
```

### ValidationError

Configuration field validation error.

```python
@dataclass
class ValidationError:
    field: str                  # Field name
    message: str                # Error message
    value: Any | None = None    # Invalid value
```

---

## Rate Limiting

The framework automatically handles GitHub API rate limiting:

- **Detection**: Monitors response headers
- **Backoff**: Exponential backoff strategy
- **Retry**: Automatic retry after delay
- **Limit**: Respects 5000 requests/hour (authenticated)

---

## Example Workflows

### Complete Audit and Remediation

```python
from gh_audit import Auditor, Configurator

# 1. Audit
auditor = Auditor(token="ghp_...")
findings, summary = auditor.audit_organization("VoodoOps")

# 2. Generate remediation plan
remediation_config = {
    "scope": "org",
    "organization": "VoodoOps",
    "two_factor_required": True
}

# 3. Apply remediation
configurator = Configurator(token="ghp_...")
result = configurator.apply_configuration(remediation_config, dry_run=True)
print(f"Would apply {result.changes_applied} changes")

# 4. Apply for real
result = configurator.apply_configuration(remediation_config)
print(f"Applied {result.changes_applied} changes")

# 5. Re-audit to verify
findings, summary = auditor.audit_organization("VoodoOps")
print(f"Remaining findings: {summary.total_findings}")
```

### Configuration from Template

```python
import json
from gh_audit import Configurator

# Load template
with open("config/examples/org-security-hardened.json") as f:
    config = json.load(f)

# Customize
config["organization"] = "my-org"

# Apply
configurator = Configurator(token="ghp_...")
result = configurator.apply_configuration(config)
print(f"Success: {result.success}")
```

---

See [GETTING_STARTED.md](GETTING_STARTED.md) for practical examples and workflows.
