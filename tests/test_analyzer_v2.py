"""Tests for enhanced SecurityAnalyzer with detailed scoring."""

import pytest

from gh_audit.analyzer import (
    ComplianceScore,
    RemediationEffortCalculator,
    RiskMatrix,
    SecurityAnalyzer,
)
from gh_audit.config import RiskLevel
from gh_audit.models import Finding


class TestComplianceScore:
    """Test ComplianceScore class."""

    def test_compliance_score_initialization(self) -> None:
        """Test compliance score creation."""
        score = ComplianceScore()
        assert score.total_score == 0.0
        assert len(score.category_scores) == 0

    def test_compliance_score_calculation(self) -> None:
        """Test compliance score calculation."""
        score = ComplianceScore()

        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Issue 1",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                title="Issue 2",
                description="Description",
                affected_items=["item2"],
            ),
        ]

        score.calculate(findings)
        assert score.total_score >= 0
        assert score.total_score <= 100
        assert "repo-security" in score.category_scores
        assert "compliance" in score.category_scores

    def test_compliance_score_empty_findings(self) -> None:
        """Test compliance score with no findings."""
        score = ComplianceScore()
        score.calculate([])
        assert score.total_score >= 0


class TestRiskMatrix:
    """Test RiskMatrix class."""

    def test_risk_matrix_calculation(self) -> None:
        """Test risk matrix calculation."""
        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="High",
                description="Description",
                affected_items=["item2"],
            ),
            Finding(
                rule_id="TEST-003",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                title="Medium",
                description="Description",
                affected_items=["item3"],
            ),
        ]

        matrix = RiskMatrix.calculate_matrix(findings)
        assert matrix["critical_count"] == 1
        assert matrix["high_count"] == 1
        assert matrix["medium_count"] == 1
        assert matrix["total"] == 3

    def test_critical_path_identification(self) -> None:
        """Test critical path identification."""
        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.LOW,
                category="repo-security",
                title="Low",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical",
                description="Description",
                affected_items=["item2", "item3"],
            ),
            Finding(
                rule_id="TEST-003",
                risk_level=RiskLevel.HIGH,
                category="compliance",
                title="High",
                description="Description",
                affected_items=["item4"],
            ),
        ]

        critical_path = RiskMatrix.get_critical_path(findings)
        assert len(critical_path) == 2
        # Critical should come first
        assert critical_path[0].risk_level == RiskLevel.CRITICAL


class TestRemediationEffortCalculator:
    """Test RemediationEffortCalculator class."""

    def test_effort_estimation(self) -> None:
        """Test effort estimation."""
        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Branch Protection",
                description="Description",
                affected_items=["repo1", "repo2"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                title="Documentation",
                description="Description",
                affected_items=["repo3"],
            ),
        ]

        effort = RemediationEffortCalculator.estimate_effort(findings)
        assert effort["total_findings"] == 2
        assert effort["estimated_hours"] > 0
        assert "repo-security" in effort["effort_by_category"]
        assert "HIGH" in effort["effort_by_risk"]

    def test_effort_scaling_with_items(self) -> None:
        """Test that effort scales with affected items."""
        findings_small = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Issue",
                description="Description",
                affected_items=["repo1"],
            ),
        ]

        findings_large = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Issue",
                description="Description",
                affected_items=[f"repo{i}" for i in range(1, 11)],
            ),
        ]

        effort_small = RemediationEffortCalculator.estimate_effort(findings_small)
        effort_large = RemediationEffortCalculator.estimate_effort(findings_large)

        assert effort_large["estimated_hours"] > effort_small["estimated_hours"]


class TestSecurityAnalyzerEnhancements:
    """Test SecurityAnalyzer enhancements."""

    def test_detailed_compliance_score(self) -> None:
        """Test getting detailed compliance score."""
        analyzer = SecurityAnalyzer()
        analyzer.findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Issue 1",
                description="Description",
                affected_items=["item1"],
            ),
        ]

        score = analyzer.get_detailed_compliance_score()
        assert isinstance(score, ComplianceScore)
        assert score.total_score >= 0

    def test_risk_matrix(self) -> None:
        """Test risk matrix generation."""
        analyzer = SecurityAnalyzer()
        analyzer.findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical",
                description="Description",
                affected_items=["item1"],
            ),
        ]

        matrix = analyzer.get_risk_matrix()
        assert matrix["critical_count"] == 1
        assert matrix["total"] == 1

    def test_critical_path(self) -> None:
        """Test critical path retrieval."""
        analyzer = SecurityAnalyzer()
        analyzer.findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.LOW,
                category="repo-security",
                title="Low",
                description="Description",
                affected_items=["item2"],
            ),
        ]

        critical = analyzer.get_critical_path()
        assert len(critical) == 1
        assert critical[0].risk_level == RiskLevel.CRITICAL

    def test_remediation_effort_estimate(self) -> None:
        """Test remediation effort estimation."""
        analyzer = SecurityAnalyzer()
        analyzer.findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Issue",
                description="Description",
                affected_items=["repo1", "repo2"],
            ),
        ]

        effort = analyzer.estimate_remediation_effort()
        assert effort["total_findings"] == 1
        assert effort["estimated_hours"] > 0

    def test_remediation_timeline(self) -> None:
        """Test remediation timeline generation."""
        analyzer = SecurityAnalyzer()
        analyzer.findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="High",
                description="Description",
                affected_items=["item2"],
            ),
            Finding(
                rule_id="TEST-003",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                title="Medium",
                description="Description",
                affected_items=["item3"],
            ),
        ]

        timeline = analyzer.get_remediation_timeline()
        assert "phase_1_critical" in timeline
        assert "phase_2_high" in timeline
        assert "phase_3_medium" in timeline
        assert "phase_4_low" in timeline

        assert timeline["phase_1_critical"]["count"] == 1
        assert timeline["phase_2_high"]["count"] == 1
        assert timeline["phase_3_medium"]["count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
