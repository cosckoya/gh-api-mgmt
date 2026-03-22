"""Security analyzer - analyzes risks and generates findings with detailed scoring."""

from datetime import datetime
from typing import Any

from .config import RISK_LEVEL_ORDER, RiskLevel
from .models import AuditSummary, Finding, OrganizationData, RemediationPriority, RepositoryData
from .standards import GitHubStandards
from .utils import audit_logger


class ComplianceScore:
    """Detailed compliance scoring by category and risk level."""

    def __init__(self) -> None:
        """Initialize compliance score calculator."""
        self.category_scores: dict[str, float] = {}
        self.risk_scores: dict[str, float] = {}
        self.total_score: float = 0.0

    def calculate(self, findings: list[Finding]) -> None:
        """Calculate compliance scores.

        Args:
            findings: List of findings
        """
        # Score by category
        categories = {
            "org-security": 0,
            "repo-security": 0,
            "access-control": 0,
            "compliance": 0,
            "github-actions": 0,
        }
        category_passed = {cat: 0 for cat in categories}

        for finding in findings:
            category = finding.category
            if category not in categories:
                categories[category] = 0
                category_passed[category] = 0
            categories[category] += 1

        # Calculate category scores (passed / total)
        for category, total in categories.items():
            if total > 0:
                passed = total - sum(
                    1 for f in findings if f.category == category
                )
                self.category_scores[category] = (passed / total * 100) if total > 0 else 100.0
            else:
                self.category_scores[category] = 100.0

        # Score by risk level (weighted)
        weights = {
            "CRITICAL": 5,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "INFO": 0.5,
        }

        total_weight = 0
        risk_weight = 0
        for finding in findings:
            risk = finding.risk_level.value
            weight = weights.get(risk, 1)
            total_weight += weight
            risk_weight += weight

        self.risk_scores = {
            risk_level.value: len([f for f in findings if f.risk_level == risk_level])
            for risk_level in RiskLevel
        }

        # Calculate total score (0-100)
        max_impact = sum(weights.values()) * 10  # Theoretical maximum
        actual_impact = risk_weight
        self.total_score = max(0, 100 - (actual_impact / max_impact * 100))


class RiskMatrix:
    """Risk matrix calculation and analysis."""

    @staticmethod
    def calculate_matrix(findings: list[Finding]) -> dict[str, Any]:
        """Calculate risk matrix from findings.

        Args:
            findings: List of findings

        Returns:
            Risk matrix with impact and likelihood
        """
        matrix = {
            "critical_count": sum(1 for f in findings if f.risk_level == RiskLevel.CRITICAL),
            "high_count": sum(1 for f in findings if f.risk_level == RiskLevel.HIGH),
            "medium_count": sum(1 for f in findings if f.risk_level == RiskLevel.MEDIUM),
            "low_count": sum(1 for f in findings if f.risk_level == RiskLevel.LOW),
            "info_count": sum(1 for f in findings if f.risk_level == RiskLevel.INFO),
            "total": len(findings),
        }

        # Calculate risk profile
        if matrix["total"] > 0:
            matrix["risk_profile"] = (
                (matrix["critical_count"] * 5 + matrix["high_count"] * 3)
                / matrix["total"]
            )
        else:
            matrix["risk_profile"] = 0

        return matrix

    @staticmethod
    def get_critical_path(findings: list[Finding]) -> list[Finding]:
        """Identify critical findings that block remediation.

        Args:
            findings: List of findings

        Returns:
            Critical findings in priority order
        """
        critical = [f for f in findings if f.risk_level == RiskLevel.CRITICAL]
        high = [f for f in findings if f.risk_level == RiskLevel.HIGH]

        # Sort by number of affected items (more affected = higher priority)
        critical.sort(key=lambda f: len(f.affected_items), reverse=True)
        high.sort(key=lambda f: len(f.affected_items), reverse=True)

        return critical + high


class RemediationEffortCalculator:
    """Calculates effort required for remediation."""

    @staticmethod
    def estimate_effort(findings: list[Finding]) -> dict[str, Any]:
        """Estimate remediation effort.

        Args:
            findings: List of findings

        Returns:
            Effort estimation with categories
        """
        effort = {
            "total_findings": len(findings),
            "effort_by_category": {},
            "effort_by_risk": {},
            "estimated_hours": 0.0,
            "priority_actions": [],
        }

        # Effort by category (rough estimates)
        category_effort = {
            "org-security": 0.5,
            "repo-security": 1.0,
            "access-control": 1.5,
            "compliance": 0.5,
            "github-actions": 2.0,
        }

        for finding in findings:
            category = finding.category
            base_effort = category_effort.get(category, 1.0)
            num_items = len(finding.affected_items)

            # Effort scales with number of affected items
            item_effort = base_effort * min(num_items, 5)  # Cap scaling

            if category not in effort["effort_by_category"]:
                effort["effort_by_category"][category] = 0

            effort["effort_by_category"][category] += item_effort

            # Risk-based effort
            risk = finding.risk_level.value
            if risk not in effort["effort_by_risk"]:
                effort["effort_by_risk"][risk] = 0
            effort["effort_by_risk"][risk] += item_effort

            effort["estimated_hours"] += item_effort

        return effort


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
            if finding.category not in grouped:
                grouped[finding.category] = []
            grouped[finding.category].append(finding)
        return grouped

    def get_detailed_compliance_score(self) -> ComplianceScore:
        """Get detailed compliance score by category.

        Returns:
            Compliance score object with category breakdown
        """
        score = ComplianceScore()
        score.calculate(self.findings)
        return score

    def get_risk_matrix(self) -> dict[str, Any]:
        """Get risk matrix analysis.

        Returns:
            Risk matrix with impact analysis
        """
        return RiskMatrix.calculate_matrix(self.findings)

    def get_critical_path(self) -> list[Finding]:
        """Get critical findings that block remediation.

        Returns:
            Critical and high-priority findings in order
        """
        return RiskMatrix.get_critical_path(self.findings)

    def estimate_remediation_effort(self) -> dict[str, Any]:
        """Estimate effort required for remediation.

        Returns:
            Effort estimation with breakdown by category and risk
        """
        return RemediationEffortCalculator.estimate_effort(self.findings)

    def get_remediation_timeline(self) -> dict[str, Any]:
        """Generate remediation timeline based on priority and effort.

        Returns:
            Timeline with phases and priorities
        """
        effort = self.estimate_remediation_effort()
        risk_matrix = self.get_risk_matrix()

        return {
            "phase_1_critical": {
                "priority": "CRITICAL",
                "timeframe": "1-3 days",
                "count": risk_matrix["critical_count"],
                "estimated_hours": effort["effort_by_risk"].get("CRITICAL", 0),
            },
            "phase_2_high": {
                "priority": "HIGH",
                "timeframe": "1-2 weeks",
                "count": risk_matrix["high_count"],
                "estimated_hours": effort["effort_by_risk"].get("HIGH", 0),
            },
            "phase_3_medium": {
                "priority": "MEDIUM",
                "timeframe": "2-4 weeks",
                "count": risk_matrix["medium_count"],
                "estimated_hours": effort["effort_by_risk"].get("MEDIUM", 0),
            },
            "phase_4_low": {
                "priority": "LOW",
                "timeframe": "1 month+",
                "count": risk_matrix["low_count"],
                "estimated_hours": effort["effort_by_risk"].get("LOW", 0),
            },
        }
