"""Compliance standards and rules engine."""

from dataclasses import dataclass
from typing import Any, Callable

from .config import Category, RiskLevel
from .models import Finding, OrganizationData, RepositoryData


@dataclass
class ComplianceRule:
    """Represents a compliance rule to check."""

    rule_id: str
    risk_level: RiskLevel
    category: Category
    title: str
    description: str
    check: Callable[[Any], tuple[bool, list[str]]]  # Returns (passed, affected_items)
    remediation: str
    template_available: bool = False
    template_url: str | None = None


class GitHubStandards:
    """GitHub security and compliance standards."""

    # Organization-level rules
    ORG_STANDARDS: list[ComplianceRule] = [
        ComplianceRule(
            rule_id="ORG-001",
            risk_level=RiskLevel.INFO,
            category=Category.ORG_SECURITY,
            title="Organization Overview",
            description="Organization basic information",
            check=lambda data: (True, []),
            remediation="This is informational.",
        ),
        ComplianceRule(
            rule_id="ORG-002",
            risk_level=RiskLevel.MEDIUM,
            category=Category.ACCESS_CONTROL,
            title="Outside Collaborators Present",
            description="Organization has outside collaborators with repository access",
            check=lambda data: (
                len(data.get("outside_collaborators", [])) == 0,
                [c.get("login", "unknown") for c in data.get("outside_collaborators", [])],
            ),
            remediation="Review and audit all outside collaborators. Remove those no longer needed.",
        ),
    ]

    # Repository-level rules
    REPO_STANDARDS: list[ComplianceRule] = [
        ComplianceRule(
            rule_id="REPO-001",
            risk_level=RiskLevel.HIGH,
            category=Category.REPO_SECURITY,
            title="Branch Protection Not Enabled",
            description="Default branch has no protection rules",
            check=lambda repo: (
                repo.branch_protection is not None,
                [repo.name] if repo.branch_protection is None else [],
            ),
            remediation="Enable branch protection on the default branch. "
            "See templates/branch-protection/ for recommended configurations.",
            template_available=True,
            template_url="templates/branch-protection/",
        ),
        ComplianceRule(
            rule_id="REPO-002",
            risk_level=RiskLevel.MEDIUM,
            category=Category.REPO_SECURITY,
            title="Secret Scanning Not Enabled",
            description="Repository does not have secret scanning enabled",
            check=lambda repo: (
                repo.has_secret_scanning or repo.visibility == "private",
                [repo.name] if not repo.has_secret_scanning else [],
            ),
            remediation="Enable secret scanning to detect accidentally committed secrets. "
            "Visit: Settings > Code security and analysis",
        ),
        ComplianceRule(
            rule_id="REPO-003",
            risk_level=RiskLevel.MEDIUM,
            category=Category.REPO_SECURITY,
            title="Dependabot Not Enabled",
            description="Repository does not have Dependabot enabled",
            check=lambda repo: (
                repo.has_dependabot,
                [repo.name] if not repo.has_dependabot else [],
            ),
            remediation="Enable Dependabot to automatically update dependencies and "
            "receive security alerts.",
        ),
        ComplianceRule(
            rule_id="REPO-004",
            risk_level=RiskLevel.LOW,
            category=Category.COMPLIANCE,
            title="Public Repository Found",
            description="Repository is publicly accessible",
            check=lambda repo: (
                repo.visibility == "private",
                [repo.name] if repo.visibility == "public" else [],
            ),
            remediation="Verify that public repositories do not contain sensitive information. "
            "Consider making private if not needed for community contribution.",
        ),
        ComplianceRule(
            rule_id="REPO-005",
            risk_level=RiskLevel.INFO,
            category=Category.COMPLIANCE,
            title="Archived Repository Found",
            description="Repository is archived and read-only",
            check=lambda repo: (
                not repo.is_archived,
                [repo.name] if repo.is_archived else [],
            ),
            remediation="Archived repositories are safe. Consider removing if no longer needed.",
        ),
    ]

    @staticmethod
    def check_org_rules(org_data: OrganizationData, outside_collab: list[dict]) -> list[Finding]:
        """Check organization-level compliance rules.

        Args:
            org_data: Organization data.
            outside_collab: List of outside collaborators.

        Returns:
            List of findings.
        """
        findings = []
        org_context = {
            "org_data": org_data,
            "outside_collaborators": outside_collab,
        }

        for rule in GitHubStandards.ORG_STANDARDS:
            passed, affected = rule.check(org_context)
            if not passed:
                finding = Finding(
                    rule_id=rule.rule_id,
                    risk_level=rule.risk_level,
                    category=rule.category,
                    title=rule.title,
                    description=rule.description,
                    affected_items=affected,
                    remediation=rule.remediation,
                    template_url=rule.template_url,
                )
                findings.append(finding)

        return findings

    @staticmethod
    def check_repo_rules(repo_data: RepositoryData) -> list[Finding]:
        """Check repository-level compliance rules.

        Args:
            repo_data: Repository data.

        Returns:
            List of findings.
        """
        findings = []

        for rule in GitHubStandards.REPO_STANDARDS:
            passed, affected = rule.check(repo_data)
            if not passed:
                finding = Finding(
                    rule_id=rule.rule_id,
                    risk_level=rule.risk_level,
                    category=rule.category,
                    title=rule.title,
                    description=rule.description,
                    affected_items=affected,
                    remediation=rule.remediation,
                    template_url=rule.template_url,
                )
                findings.append(finding)

        return findings
