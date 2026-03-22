"""Security analyzer - analyzes risks and generates findings."""

from datetime import datetime
from typing import Any

from .config import RISK_LEVEL_ORDER, RiskLevel
from .models import AuditSummary, Finding, OrganizationData, RemediationPriority, RepositoryData
from .standards import GitHubStandards


class SecurityAnalyzer:
    """Analyzes audit data and generates security findings."""

    def __init__(self) -> None:
        """Initialize analyzer."""
        self.findings: list[Finding] = []
        self.org_findings: list[Finding] = []
        self.repo_findings: list[Finding] = []

    def analyze(
        self,
        org_data: OrganizationData,
        repo_list: list[RepositoryData],
        outside_collaborators: list[dict[str, Any]],
    ) -> tuple[list[Finding], AuditSummary]:
        """Analyze complete audit data.

        Args:
            org_data: Organization data.
            repo_list: List of repository data.
            outside_collaborators: List of outside collaborators.

        Returns:
            Tuple of (all findings, audit summary).
        """
        start_time = datetime.now()

        # Analyze organization
        self.org_findings = GitHubStandards.check_org_rules(org_data, outside_collaborators)
        org_data.findings = self.org_findings

        # Analyze repositories
        self.repo_findings = []
        for repo in repo_list:
            repo_findings = GitHubStandards.check_repo_rules(repo)
            repo.findings = repo_findings
            self.repo_findings.extend(repo_findings)

        # Combine all findings
        self.findings = self.org_findings + self.repo_findings
        self.findings.sort(key=lambda f: RISK_LEVEL_ORDER.get(f.risk_level, 999))

        # Calculate summary
        duration = (datetime.now() - start_time).total_seconds()
        summary = self._calculate_summary(org_data, duration, len(repo_list), len(outside_collaborators))

        return self.findings, summary

    def _calculate_summary(
        self, org_data: OrganizationData, duration: float, repos_count: int, members_count: int
    ) -> AuditSummary:
        """Calculate audit summary.

        Args:
            org_data: Organization data.
            duration: Scan duration in seconds.
            repos_count: Number of repositories audited.
            members_count: Number of members audited.

        Returns:
            Audit summary.
        """
        # Count findings by risk level
        critical = sum(1 for f in self.findings if f.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for f in self.findings if f.risk_level == RiskLevel.HIGH)
        medium = sum(1 for f in self.findings if f.risk_level == RiskLevel.MEDIUM)
        low = sum(1 for f in self.findings if f.risk_level == RiskLevel.LOW)
        info = sum(1 for f in self.findings if f.risk_level == RiskLevel.INFO)

        # Calculate compliance score
        # Total possible checks per repo: 5 (current standards)
        # Organization checks: 2
        total_checks = 2 + (len(GitHubStandards.REPO_STANDARDS) * repos_count)
        total_passed = total_checks - len(self.findings)
        compliance_score = (total_passed / total_checks * 100) if total_checks > 0 else 100.0

        return AuditSummary(
            timestamp=datetime.now(),
            organization=org_data.login,
            total_findings=len(self.findings),
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

    def get_remediation_priorities(self) -> list[RemediationPriority]:
        """Get remediation priorities sorted by risk.

        Returns:
            List of remediation priorities.
        """
        priorities = []
        seen_actions = set()
        priority_num = 1

        # Sort by risk level
        sorted_findings = sorted(self.findings, key=lambda f: RISK_LEVEL_ORDER.get(f.risk_level, 999))

        for finding in sorted_findings:
            action_key = (finding.risk_level, finding.title)
            if action_key not in seen_actions:
                priority = RemediationPriority(
                    priority=priority_num,
                    risk_level=finding.risk_level,
                    action=finding.title,
                    template_available=finding.template_url is not None,
                    template_url=finding.template_url,
                    affected_items_count=len(finding.affected_items),
                )
                priorities.append(priority)
                priority_num += 1
                seen_actions.add(action_key)

        return priorities

    def get_findings_by_risk(self) -> dict[RiskLevel, list[Finding]]:
        """Get findings grouped by risk level.

        Returns:
            Dictionary of findings by risk level.
        """
        grouped = {level: [] for level in RiskLevel}
        for finding in self.findings:
            grouped[finding.risk_level].append(finding)
        return grouped

    def get_findings_by_category(self) -> dict[str, list[Finding]]:
        """Get findings grouped by category.

        Returns:
            Dictionary of findings by category.
        """
        grouped: dict[str, list[Finding]] = {}
        for finding in self.findings:
            if finding.category.value not in grouped:
                grouped[finding.category.value] = []
            grouped[finding.category.value].append(finding)
        return grouped
