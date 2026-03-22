"""Tests for compliance standards module."""

import pytest

from gh_audit.models import OrganizationData, RepositoryData
from gh_audit.standards import GitHubStandards


def test_org_standards_defined() -> None:
    """Test that organization standards are defined."""
    assert GitHubStandards.ORG_STANDARDS
    assert len(GitHubStandards.ORG_STANDARDS) > 0


def test_repo_standards_defined() -> None:
    """Test that repository standards are defined."""
    assert GitHubStandards.REPO_STANDARDS
    assert len(GitHubStandards.REPO_STANDARDS) > 0


def test_check_repo_branch_protection() -> None:
    """Test checking branch protection rule."""
    repo_without_protection = RepositoryData(
        name="unprotected-repo",
        visibility="private",
        description="Test",
        is_archived=False,
        is_fork=False,
        default_branch="main",
        url="https://github.com/test/repo",
        owner="test",
        branch_protection=None,
    )

    findings = GitHubStandards.check_repo_rules(repo_without_protection)

    # Should have finding about branch protection
    branch_protection_findings = [
        f for f in findings if "Branch Protection" in f.title
    ]
    assert len(branch_protection_findings) > 0


def test_check_repo_secret_scanning() -> None:
    """Test checking secret scanning rule."""
    repo_without_scanning = RepositoryData(
        name="no-scanning-repo",
        visibility="private",
        description="Test",
        is_archived=False,
        is_fork=False,
        default_branch="main",
        url="https://github.com/test/repo",
        owner="test",
        has_secret_scanning=False,
    )

    findings = GitHubStandards.check_repo_rules(repo_without_scanning)

    # Should have finding about secret scanning
    scanning_findings = [f for f in findings if "Secret Scanning" in f.title]
    assert len(scanning_findings) > 0


def test_check_org_outside_collaborators() -> None:
    """Test checking outside collaborators rule."""
    org_data = OrganizationData(
        login="test-org",
        name="Test Organization",
        plan="free",
        created_at="2024-01-01T00:00:00Z",
        members_count=5,
        public_repos_count=2,
    )

    outside_collab = [
        {"login": "external-user", "id": 999}
    ]

    findings = GitHubStandards.check_org_rules(org_data, outside_collab)

    # Should have finding about outside collaborators
    collab_findings = [
        f for f in findings if "Outside Collaborators" in f.title
    ]
    assert len(collab_findings) > 0
