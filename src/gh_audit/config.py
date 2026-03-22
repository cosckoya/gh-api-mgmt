"""Configuration and constants for GitHub audit framework."""

from enum import Enum
from typing import Final

# API Configuration
API_VERSION: Final[str] = "2024-10-01"
BASE_URL: Final[str] = "https://api.github.com"
TIMEOUT: Final[int] = 30

# Risk Levels
class RiskLevel(str, Enum):
    """Risk severity levels for audit findings."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    @property
    def score(self) -> int:
        """Score for sorting (lower = higher priority)."""
        return {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4, "INFO": 5}[self.value]


# Categories
class Category(str, Enum):
    """Finding categories."""

    ORG_SECURITY = "org-security"
    REPO_SECURITY = "repo-security"
    ACCESS_CONTROL = "access-control"
    COMPLIANCE = "compliance"
    GITHUB_ACTIONS = "github-actions"


# Risk Level Ordering
RISK_LEVEL_ORDER = {
    RiskLevel.CRITICAL: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.MEDIUM: 3,
    RiskLevel.LOW: 4,
    RiskLevel.INFO: 5,
}

# Recommendation Context
RECOMMENDATIONS_CONTEXT = {
    RiskLevel.CRITICAL: "Debe implementarse inmediatamente",
    RiskLevel.HIGH: "Debe implementarse en corto plazo",
    RiskLevel.MEDIUM: "Debería implementarse",
    RiskLevel.LOW: "Considera implementar",
    RiskLevel.INFO: "Información para conocimiento",
}

# Organization Security Checks
ORG_SECURITY_CHECKS: Final[list[str]] = [
    "two_factor_required",
    "verified_email_required",
    "member_inactive_check",
    "outside_collaborators_audit",
    "member_roles_compliance",
    "org_security_policy",
]

# Repository Security Checks
REPO_SECURITY_CHECKS: Final[list[str]] = [
    "private_visibility",
    "branch_protection_enabled",
    "require_pr_reviews",
    "require_code_owner_review",
    "require_status_checks",
    "allow_force_pushes_disabled",
    "allow_deletions_disabled",
    "secret_scanning",
    "dependabot_enabled",
    "deployment_protection",
    "no_direct_commits",
    "codeowners_exists",
    "security_policy_exists",
]

# Security Policy Files
SECURITY_POLICY_FILES: Final[list[str]] = [
    "SECURITY.md",
    ".github/SECURITY.md",
]

# Code Owner File
CODEOWNER_FILES: Final[list[str]] = [
    "CODEOWNERS",
    ".github/CODEOWNERS",
]

# License Files
LICENSE_FILES: Final[list[str]] = [
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "COPYING",
]
