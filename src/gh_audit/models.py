"""Data models for GitHub audit framework."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .config import Category, RiskLevel


@dataclass
class Finding:
    """Represents a security finding from the audit."""

    rule_id: str
    risk_level: RiskLevel
    category: Category
    title: str
    description: str
    affected_items: list[str] = field(default_factory=list)
    remediation: str = ""
    template_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "risk_level": self.risk_level.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "affected_items": self.affected_items,
            "remediation": self.remediation,
            "template_url": self.template_url,
        }


@dataclass
class OrganizationData:
    """Organization data from GitHub API."""

    login: str
    name: str | None
    plan: str
    created_at: str
    members_count: int
    public_repos_count: int
    total_repos_count: int | None = None
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "login": self.login,
            "name": self.name,
            "plan": self.plan,
            "created_at": self.created_at,
            "members_count": self.members_count,
            "public_repos_count": self.public_repos_count,
            "total_repos_count": self.total_repos_count,
            "findings": [f.to_dict() for f in self.findings],
            "findings_count": len(self.findings),
        }


@dataclass
class RepositoryData:
    """Repository data from GitHub API."""

    name: str
    visibility: str
    description: str | None
    is_archived: bool
    is_fork: bool
    default_branch: str
    url: str
    owner: str
    findings: list[Finding] = field(default_factory=list)
    branch_protection: dict[str, Any] | None = None
    has_secret_scanning: bool = False
    has_dependabot: bool = False
    workflows_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "visibility": self.visibility,
            "description": self.description,
            "is_archived": self.is_archived,
            "is_fork": self.is_fork,
            "default_branch": self.default_branch,
            "url": self.url,
            "owner": self.owner,
            "branch_protection": self.branch_protection,
            "has_secret_scanning": self.has_secret_scanning,
            "has_dependabot": self.has_dependabot,
            "workflows_count": self.workflows_count,
            "findings": [f.to_dict() for f in self.findings],
            "findings_count": len(self.findings),
        }


@dataclass
class TeamData:
    """Team data from GitHub API."""

    name: str
    slug: str
    description: str | None
    members_count: int
    privacy: str  # "closed" or "open"
    parent_team: str | None = None
    permissions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "members_count": self.members_count,
            "privacy": self.privacy,
            "parent_team": self.parent_team,
            "permissions": self.permissions,
        }


@dataclass
class MemberData:
    """Organization member data."""

    username: str
    url: str
    avatar_url: str | None
    is_admin: bool = False
    is_active: bool = True
    created_at: str | None = None
    last_activity: str | None = None
    mfa_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "username": self.username,
            "url": self.url,
            "avatar_url": self.avatar_url,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "mfa_enabled": self.mfa_enabled,
        }


@dataclass
class RemediationPriority:
    """Remediation action priority."""

    priority: int
    risk_level: RiskLevel
    action: str
    template_available: bool = False
    template_url: str | None = None
    affected_items_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "priority": self.priority,
            "risk_level": self.risk_level.value,
            "action": self.action,
            "template_available": self.template_available,
            "template_url": self.template_url,
            "affected_items_count": self.affected_items_count,
        }


@dataclass
class AuditSummary:
    """Summary statistics of the audit."""

    timestamp: datetime
    organization: str
    total_findings: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    compliance_score: float = 0.0
    scan_duration_seconds: float = 0.0
    repos_audited: int = 0
    members_audited: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "organization": self.organization,
            "total_findings": self.total_findings,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "info": self.info,
            "compliance_score": round(self.compliance_score, 2),
            "scan_duration_seconds": round(self.scan_duration_seconds, 2),
            "repos_audited": self.repos_audited,
            "members_audited": self.members_audited,
        }


@dataclass
class ConfigChange:
    """Represents a configuration change to be applied."""

    change_id: str
    scope: str  # "org", "repo", "member", "team"
    target: str  # org name, repo name, username, etc.
    action: str  # "create", "update", "delete"
    config: dict[str, Any]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "scope": self.scope,
            "target": self.target,
            "action": self.action,
            "config": self.config,
            "description": self.description,
        }


@dataclass
class ValidationError:
    """Represents a validation error."""

    field: str
    message: str
    value: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "message": self.message,
            "value": self.value,
        }


@dataclass
class ConfigResult:
    """Result of configuration application."""

    success: bool
    message: str
    changes_applied: int = 0
    errors: list[ValidationError] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "changes_applied": self.changes_applied,
            "errors": [e.to_dict() for e in self.errors],
            "details": self.details,
        }
