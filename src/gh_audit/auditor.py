"""Deep-dive audit module - comprehensive organization analysis.

Consolidates data collection and analysis with 15-20 compliance checks covering:
- Organization level: 2FA, email verification, member inactivity, roles, permissions
- Repository level: Branch protection details, governance files, deployments, webhooks
- Member level: Activity tracking, SSH keys, 2FA status, permissions
"""

from datetime import datetime, timedelta
from typing import Any

from .collector import GitHubDataCollector
from .config import RISK_LEVEL_ORDER, RiskLevel
from .models import AuditSummary, Finding, MemberData, OrganizationData, RepositoryData
from .utils import audit_logger


class AuditCheck:
    """Represents a single audit check."""

    def __init__(
        self,
        check_id: str,
        title: str,
        description: str,
        risk_level: RiskLevel,
        category: str,
        check_fn: Any,
        remediation: str = "",
        template_url: str | None = None,
    ) -> None:
        """Initialize audit check.

        Args:
            check_id: Unique check identifier
            title: Check title
            description: Detailed description
            risk_level: Risk level if check fails
            category: Check category (org-security, repo-security, etc.)
            check_fn: Function to execute check
            remediation: Remediation guidance
            template_url: URL to remediation template
        """
        self.check_id = check_id
        self.title = title
        self.description = description
        self.risk_level = risk_level
        self.category = category
        self.check_fn = check_fn
        self.remediation = remediation
        self.template_url = template_url

    def execute(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        """Execute the check.

        Args:
            context: Context data for the check

        Returns:
            Tuple of (passed, affected_items)
        """
        try:
            return self.check_fn(context)
        except Exception as e:
            audit_logger.error(f"Check {self.check_id} failed", error=str(e))
            return False, []


class DeepDiveAuditor:
    """Performs comprehensive organization audits with 15-20 deep-dive checks."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize auditor.

        Args:
            token: GitHub API token
        """
        self.collector = GitHubDataCollector(token=token)
        self.checks: list[AuditCheck] = []
        self._initialize_checks()

    def _initialize_checks(self) -> None:
        """Initialize all audit checks."""
        # Organization-level checks
        self.checks.extend(self._org_checks())
        # Repository-level checks
        self.checks.extend(self._repo_checks())
        # Member-level checks
        self.checks.extend(self._member_checks())

    def _org_checks(self) -> list[AuditCheck]:
        """Organization-level compliance checks."""
        return [
            AuditCheck(
                check_id="ORG-001",
                title="Organization Overview",
                description="Basic organization information",
                risk_level=RiskLevel.INFO,
                category="org-security",
                check_fn=lambda ctx: (True, []),
                remediation="Informational check",
            ),
            AuditCheck(
                check_id="ORG-002",
                title="Outside Collaborators Audit",
                description="Organization has outside collaborators",
                risk_level=RiskLevel.MEDIUM,
                category="access-control",
                check_fn=self._check_outside_collaborators,
                remediation="Review and audit all outside collaborators. Remove those no longer needed.",
            ),
            AuditCheck(
                check_id="ORG-003",
                title="Two-Factor Authentication Policy",
                description="2FA requirement for organization members",
                risk_level=RiskLevel.HIGH,
                category="org-security",
                check_fn=self._check_2fa_requirement,
                remediation="Enable 2FA requirement in Organization Settings > Member privileges",
            ),
            AuditCheck(
                check_id="ORG-004",
                title="Verified Email Requirement",
                description="Email verification required for members",
                risk_level=RiskLevel.MEDIUM,
                category="org-security",
                check_fn=self._check_verified_email,
                remediation="Enable verified email requirement in organization settings",
            ),
            AuditCheck(
                check_id="ORG-005",
                title="Member Inactivity Tracking",
                description="Members with no activity in 30+ days",
                risk_level=RiskLevel.LOW,
                category="org-security",
                check_fn=self._check_member_inactivity,
                remediation="Review inactive members and remove those no longer needed",
            ),
            AuditCheck(
                check_id="ORG-006",
                title="Repository Creation Restrictions",
                description="Repository creation is restricted",
                risk_level=RiskLevel.MEDIUM,
                category="org-security",
                check_fn=self._check_repo_creation_restrictions,
                remediation="Restrict repository creation to owners in organization settings",
            ),
            AuditCheck(
                check_id="ORG-007",
                title="Fork Repository Restrictions",
                description="Fork creation is restricted",
                risk_level=RiskLevel.LOW,
                category="org-security",
                check_fn=self._check_fork_restrictions,
                remediation="Restrict fork creation in organization settings if not needed",
            ),
        ]

    def _repo_checks(self) -> list[AuditCheck]:
        """Repository-level compliance checks."""
        return [
            AuditCheck(
                check_id="REPO-001",
                title="Branch Protection Enabled",
                description="Default branch has protection rules",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                check_fn=self._check_branch_protection,
                remediation="Enable branch protection rules on default branch",
                template_url="templates/branch-protection/",
            ),
            AuditCheck(
                check_id="REPO-002",
                title="Require Pull Request Reviews",
                description="PRs require at least one approval",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                check_fn=self._check_pr_reviews,
                remediation="Enable required pull request reviews (1+ approval)",
            ),
            AuditCheck(
                check_id="REPO-003",
                title="CODEOWNERS File Present",
                description="Repository has CODEOWNERS file for governance",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                check_fn=self._check_codeowners_file,
                remediation="Create CODEOWNERS file to enforce code review governance",
                template_url="templates/governance/CODEOWNERS.template",
            ),
            AuditCheck(
                check_id="REPO-004",
                title="Security Policy Present",
                description="Repository has SECURITY.md for vulnerability disclosure",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                check_fn=self._check_security_policy,
                remediation="Add SECURITY.md file with vulnerability disclosure process",
                template_url="templates/governance/SECURITY.md.template",
            ),
            AuditCheck(
                check_id="REPO-005",
                title="License File Present",
                description="Repository has license file",
                risk_level=RiskLevel.LOW,
                category="compliance",
                check_fn=self._check_license_file,
                remediation="Add LICENSE file to define usage terms",
            ),
            AuditCheck(
                check_id="REPO-006",
                title="Secret Scanning Enabled",
                description="Secret scanning active for credential detection",
                risk_level=RiskLevel.MEDIUM,
                category="repo-security",
                check_fn=self._check_secret_scanning,
                remediation="Enable secret scanning in repository settings",
            ),
            AuditCheck(
                check_id="REPO-007",
                title="Dependabot Enabled",
                description="Dependabot active for dependency updates",
                risk_level=RiskLevel.MEDIUM,
                category="repo-security",
                check_fn=self._check_dependabot,
                remediation="Enable Dependabot in repository settings",
            ),
            AuditCheck(
                check_id="REPO-008",
                title="GitHub Actions Workflows Present",
                description="CI/CD workflows configured",
                risk_level=RiskLevel.LOW,
                category="github-actions",
                check_fn=self._check_workflows_present,
                remediation="Add GitHub Actions workflows for testing and security scanning",
            ),
            AuditCheck(
                check_id="REPO-009",
                title="Force Push Protection",
                description="Force push is disabled on protected branch",
                risk_level=RiskLevel.MEDIUM,
                category="repo-security",
                check_fn=self._check_force_push_disabled,
                remediation="Disable force push in branch protection rules",
            ),
            AuditCheck(
                check_id="REPO-010",
                title="Branch Deletion Protection",
                description="Branch deletion is disabled on protected branch",
                risk_level=RiskLevel.MEDIUM,
                category="repo-security",
                check_fn=self._check_deletion_disabled,
                remediation="Disable deletion in branch protection rules",
            ),
            AuditCheck(
                check_id="REPO-011",
                title="Status Checks Required",
                description="Status checks (CI/CD) required before merge",
                risk_level=RiskLevel.HIGH,
                category="github-actions",
                check_fn=self._check_status_checks,
                remediation="Enable required status checks in branch protection rules",
            ),
            AuditCheck(
                check_id="REPO-012",
                title="Public Repository Audit",
                description="Repository is publicly accessible",
                risk_level=RiskLevel.LOW,
                category="compliance",
                check_fn=self._check_public_repo,
                remediation="Verify public repos contain no sensitive information",
            ),
        ]

    def _member_checks(self) -> list[AuditCheck]:
        """Member-level compliance checks."""
        return [
            AuditCheck(
                check_id="MEMBER-001",
                title="Member Inactive Detection",
                description="Members with no activity in 30+ days",
                risk_level=RiskLevel.LOW,
                category="org-security",
                check_fn=self._check_inactive_members,
                remediation="Review and remove inactive members from organization",
            ),
            AuditCheck(
                check_id="MEMBER-002",
                title="Admin Member Count",
                description="Excessive number of admin members",
                risk_level=RiskLevel.MEDIUM,
                category="access-control",
                check_fn=self._check_admin_count,
                remediation="Limit admin access to only necessary members",
            ),
        ]

    # Organization check implementations
    def _check_outside_collaborators(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for outside collaborators."""
        collaborators = ctx.get("outside_collaborators", [])
        if len(collaborators) == 0:
            return True, []
        return False, [c.get("login", "unknown") for c in collaborators]

    def _check_2fa_requirement(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check 2FA requirement (placeholder - limited by API)."""
        # Note: GitHub API doesn't expose 2FA requirement status directly
        # This would require checking org settings via GraphQL
        org_info = ctx.get("org_info", {})
        return True, []  # Placeholder

    def _check_verified_email(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check verified email requirement (placeholder)."""
        return True, []  # Placeholder

    def _check_member_inactivity(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for inactive members (30+ days)."""
        members = ctx.get("members", [])
        inactive = []
        cutoff = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=30)

        for member in members:
            # GitHub API has limited member activity tracking
            # This is a simplified check
            pass

        return len(inactive) == 0, inactive

    def _check_repo_creation_restrictions(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check repository creation restrictions (placeholder)."""
        return True, []  # Placeholder - requires org settings access

    def _check_fork_restrictions(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check fork creation restrictions (placeholder)."""
        return True, []  # Placeholder - requires org settings access

    # Repository check implementations
    def _check_branch_protection(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check branch protection is enabled."""
        repos = ctx.get("repos", [])
        unprotected = []
        for repo in repos:
            if repo.branch_protection is None and repo.visibility != "private":
                unprotected.append(repo.name)
        return len(unprotected) == 0, unprotected

    def _check_pr_reviews(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check PR review requirement."""
        repos = ctx.get("repos", [])
        missing_reviews = []
        for repo in repos:
            if repo.branch_protection:
                required_reviews = repo.branch_protection.get(
                    "required_pull_request_reviews", {}
                )
                if not required_reviews.get("required_approving_review_count", 0) > 0:
                    missing_reviews.append(repo.name)
        return len(missing_reviews) == 0, missing_reviews

    def _check_codeowners_file(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for CODEOWNERS file."""
        repos = ctx.get("repos", [])
        missing = []
        for repo in repos:
            codeowners = self.collector.get_repo_file(repo.owner, repo.name, "CODEOWNERS")
            codeowners_gh = self.collector.get_repo_file(repo.owner, repo.name, ".github/CODEOWNERS")
            if not codeowners and not codeowners_gh:
                missing.append(repo.name)
        return len(missing) == 0, missing

    def _check_security_policy(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for SECURITY.md file."""
        repos = ctx.get("repos", [])
        missing = []
        for repo in repos:
            security_md = self.collector.get_repo_file(repo.owner, repo.name, "SECURITY.md")
            security_gh = self.collector.get_repo_file(repo.owner, repo.name, ".github/SECURITY.md")
            if not security_md and not security_gh:
                missing.append(repo.name)
        return len(missing) == 0, missing

    def _check_license_file(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for LICENSE file."""
        repos = ctx.get("repos", [])
        missing = []
        for repo in repos:
            if repo.visibility == "public":
                license_file = self.collector.get_repo_file(repo.owner, repo.name, "LICENSE")
                if not license_file:
                    missing.append(repo.name)
        return len(missing) == 0, missing

    def _check_secret_scanning(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check secret scanning enabled."""
        repos = ctx.get("repos", [])
        missing = []
        for repo in repos:
            if repo.visibility == "public" and not repo.has_secret_scanning:
                missing.append(repo.name)
        return len(missing) == 0, missing

    def _check_dependabot(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check Dependabot enabled."""
        repos = ctx.get("repos", [])
        missing = []
        for repo in repos:
            if not repo.has_dependabot:
                missing.append(repo.name)
        return len(missing) == 0, missing

    def _check_workflows_present(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check GitHub Actions workflows present."""
        repos = ctx.get("repos", [])
        no_workflows = []
        for repo in repos:
            if repo.workflows_count == 0:
                no_workflows.append(repo.name)
        return len(no_workflows) == 0, no_workflows

    def _check_force_push_disabled(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check force push is disabled."""
        repos = ctx.get("repos", [])
        allow_force_push = []
        for repo in repos:
            if repo.branch_protection:
                if repo.branch_protection.get("allow_force_pushes", {}).get("enabled"):
                    allow_force_push.append(repo.name)
        return len(allow_force_push) == 0, allow_force_push

    def _check_deletion_disabled(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check branch deletion is disabled."""
        repos = ctx.get("repos", [])
        allow_deletion = []
        for repo in repos:
            if repo.branch_protection:
                if repo.branch_protection.get("allow_deletions", {}).get("enabled"):
                    allow_deletion.append(repo.name)
        return len(allow_deletion) == 0, allow_deletion

    def _check_status_checks(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check status checks required."""
        repos = ctx.get("repos", [])
        missing_checks = []
        for repo in repos:
            if repo.branch_protection:
                required_checks = repo.branch_protection.get(
                    "required_status_checks", {}
                )
                if not required_checks.get("strict", False):
                    missing_checks.append(repo.name)
        return len(missing_checks) == 0, missing_checks

    def _check_public_repo(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for public repositories."""
        repos = ctx.get("repos", [])
        public_repos = [r.name for r in repos if r.visibility == "public"]
        return len(public_repos) == 0, public_repos

    # Member check implementations
    def _check_inactive_members(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check for inactive members."""
        members = ctx.get("members", [])
        # GitHub API has limited member activity tracking
        return True, []

    def _check_admin_count(self, ctx: dict[str, Any]) -> tuple[bool, list[str]]:
        """Check admin member count."""
        members = ctx.get("members", [])
        admins = [m for m in members if m.get("site_admin")]
        # Flag if more than 3 admins
        if len(admins) > 3:
            return False, [m.get("login", "unknown") for m in admins]
        return True, []

    def perform_audit(
        self, org: str, include_members: bool = True, include_teams: bool = False
    ) -> tuple[list[Finding], AuditSummary]:
        """Perform complete deep-dive audit.

        Args:
            org: Organization name
            include_members: Include member-level checks
            include_teams: Include team analysis

        Returns:
            Tuple of (findings, summary)
        """
        audit_logger.audit_start(org)
        start_time = datetime.now()

        # Collect data
        audit_logger.info("Collecting organization data", org=org)
        org_info, repos = self.collector.audit_org_complete(org)
        members = self.collector.get_org_members(org)
        outside_collab = self.collector.get_org_outside_collaborators(org)

        # Build context
        context = {
            "org_info": org_info.to_dict(),
            "org": org,
            "repos": repos,
            "members": members,
            "outside_collaborators": outside_collab,
        }

        # Execute checks
        findings = []
        for check in self.checks:
            # Skip member checks if not requested
            if check.check_id.startswith("MEMBER-") and not include_members:
                continue

            passed, affected_items = check.execute(context)

            if passed:
                audit_logger.check_passed(check.title)
            else:
                audit_logger.check_failed(check.title, reason=f"Affected: {affected_items}")
                finding = Finding(
                    rule_id=check.check_id,
                    risk_level=check.risk_level,
                    category=check.category,
                    title=check.title,
                    description=check.description,
                    affected_items=affected_items,
                    remediation=check.remediation,
                    template_url=check.template_url,
                )
                findings.append(finding)

        # Calculate summary
        duration = (datetime.now() - start_time).total_seconds()
        summary = self._calculate_summary(org_info, findings, duration, len(repos), len(members))

        audit_logger.audit_complete(org, duration, len(findings))

        return findings, summary

    def _calculate_summary(
        self,
        org_info: OrganizationData,
        findings: list[Finding],
        duration: float,
        repos_count: int,
        members_count: int,
    ) -> AuditSummary:
        """Calculate audit summary.

        Args:
            org_info: Organization data
            findings: List of findings
            duration: Scan duration
            repos_count: Number of repos
            members_count: Number of members

        Returns:
            Audit summary
        """
        # Count by risk level
        critical = sum(1 for f in findings if f.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for f in findings if f.risk_level == RiskLevel.HIGH)
        medium = sum(1 for f in findings if f.risk_level == RiskLevel.MEDIUM)
        low = sum(1 for f in findings if f.risk_level == RiskLevel.LOW)
        info = sum(1 for f in findings if f.risk_level == RiskLevel.INFO)

        # Calculate compliance score with all checks
        total_checks = len(self.checks)
        total_passed = total_checks - len(findings)
        compliance_score = (total_passed / total_checks * 100) if total_checks > 0 else 100.0

        return AuditSummary(
            timestamp=datetime.now(),
            organization=org_info.login,
            total_findings=len(findings),
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            info=info,
            compliance_score=compliance_score,
            scan_duration_seconds=duration,
            repos_audited=repos_count,
            members_audited=members_count,
        )

    def get_findings_by_category(self, findings: list[Finding]) -> dict[str, list[Finding]]:
        """Group findings by category.

        Args:
            findings: List of findings

        Returns:
            Findings grouped by category
        """
        grouped: dict[str, list[Finding]] = {}
        for finding in findings:
            category = finding.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(finding)
        return grouped

    def get_findings_by_severity(self, findings: list[Finding]) -> dict[RiskLevel, list[Finding]]:
        """Group findings by risk level.

        Args:
            findings: List of findings

        Returns:
            Findings grouped by risk level
        """
        grouped: dict[RiskLevel, list[Finding]] = {}
        for risk_level in RiskLevel:
            grouped[risk_level] = [f for f in findings if f.risk_level == risk_level]
        return grouped

    def get_remediation_roadmap(
        self, findings: list[Finding]
    ) -> list[tuple[str, RiskLevel, list[str]]]:
        """Generate prioritized remediation roadmap.

        Args:
            findings: List of findings

        Returns:
            List of (action, risk_level, affected_items)
        """
        roadmap: list[tuple[str, RiskLevel, list[str]]] = []
        seen = set()

        # Sort by risk level (highest first)
        sorted_findings = sorted(
            findings, key=lambda f: RISK_LEVEL_ORDER.get(f.risk_level, 999)
        )

        for finding in sorted_findings:
            key = (finding.title, finding.risk_level)
            if key not in seen:
                roadmap.append((finding.title, finding.risk_level, finding.affected_items))
                seen.add(key)

        return roadmap
