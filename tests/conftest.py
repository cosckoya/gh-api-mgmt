"""Shared test fixtures and configuration."""

import pytest

from gh_audit.models import (
    AuditSummary,
    Finding,
    OrganizationData,
    RepositoryData,
)
from gh_audit.config import RiskLevel


@pytest.fixture
def sample_organization() -> OrganizationData:
    """Create sample organization for testing."""
    return OrganizationData(
        login="test-org",
        name="Test Organization",
        plan="free",
        created_at="2024-01-01T00:00:00Z",
        members_count=5,
        public_repos_count=3,
        total_repos_count=8,
    )


@pytest.fixture
def sample_repository() -> RepositoryData:
    """Create sample repository for testing."""
    return RepositoryData(
        name="test-repo",
        visibility="private",
        description="Test repository",
        is_archived=False,
        is_fork=False,
        default_branch="main",
        url="https://github.com/test-org/test-repo",
        owner="test-org",
    )


@pytest.fixture
def sample_finding() -> Finding:
    """Create sample finding for testing."""
    return Finding(
        rule_id="TEST-001",
        risk_level=RiskLevel.HIGH,
        category="repo-security",
        title="Test Finding",
        description="This is a test finding",
        affected_items=["item1", "item2"],
        remediation="Fix this issue by doing X",
        template_url="templates/fix.json",
    )


@pytest.fixture
def sample_findings() -> list[Finding]:
    """Create sample findings for testing."""
    return [
        Finding(
            rule_id="TEST-001",
            risk_level=RiskLevel.CRITICAL,
            category="org-security",
            title="Critical Issue",
            description="A critical issue",
            affected_items=["critical-item"],
        ),
        Finding(
            rule_id="TEST-002",
            risk_level=RiskLevel.HIGH,
            category="repo-security",
            title="High Issue",
            description="A high priority issue",
            affected_items=["repo1", "repo2"],
        ),
        Finding(
            rule_id="TEST-003",
            risk_level=RiskLevel.MEDIUM,
            category="compliance",
            title="Medium Issue",
            description="A medium priority issue",
            affected_items=["repo3"],
        ),
        Finding(
            rule_id="TEST-004",
            risk_level=RiskLevel.LOW,
            category="access-control",
            title="Low Issue",
            description="A low priority issue",
            affected_items=["user1"],
        ),
    ]


@pytest.fixture
def sample_audit_summary() -> AuditSummary:
    """Create sample audit summary for testing."""
    from datetime import datetime

    return AuditSummary(
        timestamp=datetime.now(),
        organization="test-org",
        total_findings=4,
        critical=1,
        high=1,
        medium=1,
        low=1,
        info=0,
        compliance_score=75.0,
        scan_duration_seconds=15.5,
        repos_audited=5,
        members_audited=3,
    )
