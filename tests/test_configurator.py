"""Tests for Configurator module."""

import json
import pytest
from unittest.mock import MagicMock, patch

from gh_audit.configurator import (
    BaseConfigurator,
    Configurator,
    ConfigChange,
    MemberConfigurator,
    OrgConfigurator,
    RepoConfigurator,
    TeamConfigurator,
)
from gh_audit.models import ConfigResult, ValidationError
from gh_audit.utils import GitHubAPI


class TestConfigChange:
    """Test ConfigChange dataclass."""

    def test_config_change_creation(self) -> None:
        """Test ConfigChange instantiation."""
        change = ConfigChange(
            change_id="CFG-001",
            scope="repo",
            target="test-repo",
            action="create",
            config={"key": "value"},
            description="Test change",
        )

        assert change.change_id == "CFG-001"
        assert change.scope == "repo"
        assert change.target == "test-repo"

    def test_config_change_to_dict(self) -> None:
        """Test ConfigChange serialization."""
        change = ConfigChange(
            change_id="CFG-001",
            scope="org",
            target="test-org",
            action="update",
            config={"two_factor_required": True},
        )

        d = change.to_dict()
        assert d["change_id"] == "CFG-001"
        assert d["scope"] == "org"
        assert d["config"]["two_factor_required"] is True


class TestOrgConfigurator:
    """Test OrgConfigurator."""

    def test_org_config_missing_org(self) -> None:
        """Test org configuration with missing organization field."""
        api = MagicMock(spec=GitHubAPI)
        configurator = OrgConfigurator(api)

        result = configurator.apply({})
        assert not result.success
        assert len(result.errors) > 0

    def test_org_config_2fa_enabled(self) -> None:
        """Test enabling 2FA for organization."""
        api = MagicMock(spec=GitHubAPI)
        configurator = OrgConfigurator(api)

        config = {
            "organization": "test-org",
            "two_factor_required": True,
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success
        api.update_org_settings.assert_called_once()

    def test_org_config_dry_run(self) -> None:
        """Test dry run mode (no actual changes)."""
        api = MagicMock(spec=GitHubAPI)
        configurator = OrgConfigurator(api)

        config = {
            "organization": "test-org",
            "two_factor_required": True,
            "default_member_permission": "pull",
        }

        result = configurator.apply(config, dry_run=True)
        assert result.success
        # No API calls should be made in dry run
        api.update_org_settings.assert_not_called()


class TestRepoConfigurator:
    """Test RepoConfigurator."""

    def test_repo_config_missing_fields(self) -> None:
        """Test repo configuration with missing fields."""
        api = MagicMock(spec=GitHubAPI)
        configurator = RepoConfigurator(api)

        result = configurator.apply({})
        assert not result.success
        assert len(result.errors) > 0

    def test_repo_config_branch_protection(self) -> None:
        """Test branch protection configuration."""
        api = MagicMock(spec=GitHubAPI)
        configurator = RepoConfigurator(api)

        config = {
            "owner": "test-org",
            "repository": "test-repo",
            "branch_protection": {
                "name": "main-protection",
                "target": "branch",
            },
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success
        api.create_branch_protection_ruleset.assert_called_once()

    def test_repo_config_file_creation(self) -> None:
        """Test creating files in repository."""
        api = MagicMock(spec=GitHubAPI)
        api.create_file_in_repo.return_value = True
        configurator = RepoConfigurator(api)

        config = {
            "owner": "test-org",
            "repository": "test-repo",
            "files": [
                {
                    "path": ".github/CODEOWNERS",
                    "content": "* @owner",
                    "message": "Add CODEOWNERS",
                },
            ],
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success
        api.create_file_in_repo.assert_called_once()


class TestMemberConfigurator:
    """Test MemberConfigurator."""

    def test_member_config_missing_fields(self) -> None:
        """Test member configuration with missing fields."""
        api = MagicMock(spec=GitHubAPI)
        configurator = MemberConfigurator(api)

        result = configurator.apply({})
        assert not result.success
        assert len(result.errors) > 0

    def test_member_config_set_role(self) -> None:
        """Test setting member role."""
        api = MagicMock(spec=GitHubAPI)
        configurator = MemberConfigurator(api)

        config = {
            "organization": "test-org",
            "username": "alice",
            "role": "admin",
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success

    def test_member_config_add_to_teams(self) -> None:
        """Test adding member to teams."""
        api = MagicMock(spec=GitHubAPI)
        configurator = MemberConfigurator(api)

        config = {
            "organization": "test-org",
            "username": "alice",
            "teams": ["DevSecOps", "Infrastructure"],
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success


class TestTeamConfigurator:
    """Test TeamConfigurator."""

    def test_team_config_missing_fields(self) -> None:
        """Test team configuration with missing fields."""
        api = MagicMock(spec=GitHubAPI)
        configurator = TeamConfigurator(api)

        result = configurator.apply({})
        assert not result.success
        assert len(result.errors) > 0

    def test_team_config_create_team(self) -> None:
        """Test creating a team."""
        api = MagicMock(spec=GitHubAPI)
        configurator = TeamConfigurator(api)

        config = {
            "organization": "test-org",
            "team_name": "DevSecOps",
            "privacy": "closed",
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success

    def test_team_config_with_repos(self) -> None:
        """Test team configuration with repository access."""
        api = MagicMock(spec=GitHubAPI)
        configurator = TeamConfigurator(api)

        config = {
            "organization": "test-org",
            "team_name": "DevSecOps",
            "repositories": [
                {"name": "aws-cdk", "permission": "admin"},
                {"name": "terraform", "permission": "push"},
            ],
        }

        result = configurator.apply(config, dry_run=False)
        assert result.success


class TestConfigurator:
    """Test main Configurator class."""

    def test_configurator_initialization(self) -> None:
        """Test configurator initialization."""
        with patch("gh_audit.configurator.GitHubAPI"):
            configurator = Configurator.__new__(Configurator)
            configurator.api = MagicMock(spec=GitHubAPI)
            configurator.org_configurator = OrgConfigurator(configurator.api)
            configurator.repo_configurator = RepoConfigurator(configurator.api)
            configurator.member_configurator = MemberConfigurator(configurator.api)
            configurator.team_configurator = TeamConfigurator(configurator.api)
            configurator.results = []

            assert configurator.org_configurator is not None
            assert configurator.repo_configurator is not None

    def test_load_configuration(self) -> None:
        """Test loading configuration from file."""
        import tempfile

        configurator = Configurator.__new__(Configurator)
        configurator.api = MagicMock(spec=GitHubAPI)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"scope": "org", "organization": "test-org"}, f)
            f.flush()

            config = configurator.load_configuration(f.name)
            assert config["scope"] == "org"
            assert config["organization"] == "test-org"

    def test_validate_configuration_org(self) -> None:
        """Test configuration validation for org scope."""
        configurator = Configurator.__new__(Configurator)

        config = {"scope": "org", "organization": "test-org"}
        is_valid, errors = configurator.validate_configuration(config)
        assert is_valid
        assert len(errors) == 0

    def test_validate_configuration_repo(self) -> None:
        """Test configuration validation for repo scope."""
        configurator = Configurator.__new__(Configurator)

        config = {"scope": "repo", "owner": "test-org", "repository": "test-repo"}
        is_valid, errors = configurator.validate_configuration(config)
        assert is_valid

    def test_validate_configuration_invalid_scope(self) -> None:
        """Test configuration validation with invalid scope."""
        configurator = Configurator.__new__(Configurator)

        config = {"scope": "invalid"}
        is_valid, errors = configurator.validate_configuration(config)
        assert not is_valid
        assert len(errors) > 0

    def test_apply_configuration_org(self) -> None:
        """Test applying org configuration."""
        configurator = Configurator.__new__(Configurator)
        configurator.api = MagicMock(spec=GitHubAPI)
        configurator.org_configurator = OrgConfigurator(configurator.api)
        configurator.repo_configurator = RepoConfigurator(configurator.api)
        configurator.member_configurator = MemberConfigurator(configurator.api)
        configurator.team_configurator = TeamConfigurator(configurator.api)
        configurator.results = []

        config = {
            "scope": "org",
            "organization": "test-org",
            "two_factor_required": True,
        }

        result = configurator.apply_configuration(config, dry_run=True)
        assert result.success

    def test_get_results_summary(self) -> None:
        """Test results summary."""
        configurator = Configurator.__new__(Configurator)
        configurator.results = [
            ConfigResult(success=True, message="OK", changes_applied=1),
            ConfigResult(success=True, message="OK", changes_applied=1),
            ConfigResult(success=False, message="Failed", errors=[]),
        ]

        summary = configurator.get_results_summary()
        assert summary["total"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["total_changes"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
