"""Tests for security analyzer module."""

from datetime import datetime

import pytest

from gh_audit.analyzer import SecurityAnalyzer
from gh_audit.models import OrganizationData, RepositoryData


def test_analyzer_initialization() -> None:
    """Test analyzer initialization."""
    analyzer = SecurityAnalyzer()
    assert analyzer.findings == []
    assert analyzer.org_findings == []
    assert analyzer.repo_findings == []


def test_analyzer_calculate_compliance_score() -> None:
    """Test compliance score calculation."""
    analyzer = SecurityAnalyzer()

    org_data = OrganizationData(
        login="test-org",
        name="Test Organization",
        plan="free",
        created_at="2024-01-01T00:00:00Z",
        members_count=5,
        public_repos_count=2,
    )

    repo_data = RepositoryData(
        name="test-repo",
        visibility="private",
        description="Test repo",
        is_archived=False,
        is_fork=False,
        default_branch="main",
        url="https://github.com/test-org/test-repo",
        owner="test-org",
    )

    findings, summary = analyzer.analyze(org_data, [repo_data], [])

    assert summary.organization == "test-org"
    assert summary.compliance_score >= 0
    assert summary.compliance_score <= 100


def test_analyzer_remediation_priorities() -> None:
    """Test remediation priority generation."""
    analyzer = SecurityAnalyzer()

    org_data = OrganizationData(
        login="test-org",
        name="Test Organization",
        plan="free",
        created_at="2024-01-01T00:00:00Z",
        members_count=5,
        public_repos_count=2,
    )

    repo_data = RepositoryData(
        name="test-repo",
        visibility="private",
        description="Test repo",
        is_archived=False,
        is_fork=False,
        default_branch="main",
        url="https://github.com/test-org/test-repo",
        owner="test-org",
    )

    findings, summary = analyzer.analyze(org_data, [repo_data], [])
    priorities = analyzer.get_remediation_priorities()

    assert isinstance(priorities, list)
    if priorities:
        assert hasattr(priorities[0], "priority")
        assert hasattr(priorities[0], "risk_level")
