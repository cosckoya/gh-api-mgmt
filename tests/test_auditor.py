"""Tests for DeepDiveAuditor module."""

import pytest

from gh_audit.auditor import AuditCheck, DeepDiveAuditor
from gh_audit.config import RiskLevel
from gh_audit.models import Finding, RepositoryData


class TestAuditCheck:
    """Test AuditCheck class."""

    def test_audit_check_creation(self) -> None:
        """Test audit check instantiation."""
        check = AuditCheck(
            check_id="TEST-001",
            title="Test Check",
            description="Test description",
            risk_level=RiskLevel.HIGH,
            category="repo-security",
            check_fn=lambda ctx: (True, []),
            remediation="Test remediation",
        )

        assert check.check_id == "TEST-001"
        assert check.title == "Test Check"
        assert check.risk_level == RiskLevel.HIGH

    def test_audit_check_execution(self) -> None:
        """Test audit check execution."""
        check = AuditCheck(
            check_id="TEST-001",
            title="Test Check",
            description="Test description",
            risk_level=RiskLevel.HIGH,
            category="repo-security",
            check_fn=lambda ctx: (False, ["item1", "item2"]),
        )

        passed, affected = check.execute({})
        assert not passed
        assert affected == ["item1", "item2"]

    def test_audit_check_error_handling(self) -> None:
        """Test audit check error handling."""
        def failing_check(ctx: dict) -> tuple[bool, list[str]]:
            raise ValueError("Test error")

        check = AuditCheck(
            check_id="TEST-001",
            title="Test Check",
            description="Test description",
            risk_level=RiskLevel.HIGH,
            category="repo-security",
            check_fn=failing_check,
        )

        passed, affected = check.execute({})
        assert not passed


class TestDeepDiveAuditor:
    """Test DeepDiveAuditor class."""

    def test_auditor_initialization(self) -> None:
        """Test auditor initialization."""
        # Create auditor without token (will fail due to env var, but we can test structure)
        try:
            # This will fail on GitHub token, but we can test the checks are loaded
            auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)
            auditor.checks = []
            auditor._initialize_checks()

            assert len(auditor.checks) > 0
            assert len(auditor.checks) >= 21
        except ValueError:
            # Expected if no token
            pass

    def test_org_checks_exist(self) -> None:
        """Test organization checks are created."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)
        auditor.checks = []

        org_checks = auditor._org_checks()
        assert len(org_checks) >= 7
        assert any(c.check_id.startswith("ORG-") for c in org_checks)

    def test_repo_checks_exist(self) -> None:
        """Test repository checks are created."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)
        auditor.checks = []

        repo_checks = auditor._repo_checks()
        assert len(repo_checks) >= 12
        assert any(c.check_id.startswith("REPO-") for c in repo_checks)

    def test_member_checks_exist(self) -> None:
        """Test member checks are created."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)
        auditor.checks = []

        member_checks = auditor._member_checks()
        assert len(member_checks) >= 2
        assert any(c.check_id.startswith("MEMBER-") for c in member_checks)

    def test_check_branch_protection(self) -> None:
        """Test branch protection check."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)

        repo_protected = RepositoryData(
            name="repo1",
            visibility="public",
            description=None,
            is_archived=False,
            is_fork=False,
            default_branch="main",
            url="https://example.com",
            owner="org",
            branch_protection={"enabled": True},
        )

        repo_unprotected = RepositoryData(
            name="repo2",
            visibility="public",
            description=None,
            is_archived=False,
            is_fork=False,
            default_branch="main",
            url="https://example.com",
            owner="org",
            branch_protection=None,
        )

        ctx = {"repos": [repo_protected, repo_unprotected]}
        passed, affected = auditor._check_branch_protection(ctx)

        assert not passed
        assert "repo2" in affected
        assert "repo1" not in affected

    def test_check_public_repo(self) -> None:
        """Test public repository detection."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)

        public_repo = RepositoryData(
            name="public-repo",
            visibility="public",
            description=None,
            is_archived=False,
            is_fork=False,
            default_branch="main",
            url="https://example.com",
            owner="org",
        )

        private_repo = RepositoryData(
            name="private-repo",
            visibility="private",
            description=None,
            is_archived=False,
            is_fork=False,
            default_branch="main",
            url="https://example.com",
            owner="org",
        )

        ctx = {"repos": [public_repo, private_repo]}
        passed, affected = auditor._check_public_repo(ctx)

        assert not passed
        assert "public-repo" in affected

    def test_findings_by_category(self) -> None:
        """Test grouping findings by category."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)

        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.HIGH,
                category="repo-security",
                title="Test 1",
                description="Description",
                affected_items=["item1"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.MEDIUM,
                category="compliance",
                title="Test 2",
                description="Description",
                affected_items=["item2"],
            ),
        ]

        grouped = auditor.get_findings_by_category(findings)
        assert "repo-security" in grouped
        assert "compliance" in grouped
        assert len(grouped["repo-security"]) == 1
        assert len(grouped["compliance"]) == 1

    def test_remediation_roadmap(self) -> None:
        """Test remediation roadmap generation."""
        auditor = DeepDiveAuditor.__new__(DeepDiveAuditor)

        findings = [
            Finding(
                rule_id="TEST-001",
                risk_level=RiskLevel.CRITICAL,
                category="repo-security",
                title="Critical Issue",
                description="Description",
                affected_items=["repo1", "repo2"],
            ),
            Finding(
                rule_id="TEST-002",
                risk_level=RiskLevel.HIGH,
                category="compliance",
                title="High Issue",
                description="Description",
                affected_items=["repo3"],
            ),
        ]

        roadmap = auditor.get_remediation_roadmap(findings)
        assert len(roadmap) == 2
        # Critical should come first
        assert roadmap[0][1] == RiskLevel.CRITICAL
        assert roadmap[1][1] == RiskLevel.HIGH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
