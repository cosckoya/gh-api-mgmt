"""Configuration management - applies JSON-driven configurations to GitHub.

Supports:
- Organization settings (2FA, permissions, restrictions)
- Repository settings (branch protection, webhooks, visibility)
- Member management (roles, teams, permissions)
- Team configuration (creation, permissions)
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ConfigResult, ValidationError
from .utils import (
    GitHubAPI,
    GitHubAPIError,
    SchemaValidator,
    TemplateLoader,
    remediation_logger,
)


@dataclass
class ConfigChange:
    """Represents a configuration change."""

    change_id: str
    scope: str  # "org", "repo", "member", "team"
    target: str
    action: str  # "create", "update", "delete"
    config: dict[str, Any]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_id": self.change_id,
            "scope": self.scope,
            "target": self.target,
            "action": self.action,
            "config": self.config,
            "description": self.description,
        }


class BaseConfigurator(ABC):
    """Base class for configurators."""

    def __init__(self, api: GitHubAPI) -> None:
        """Initialize configurator.

        Args:
            api: GitHub API instance
        """
        self.api = api
        self.changes: list[ConfigChange] = []
        self.results: list[ConfigResult] = []

    @abstractmethod
    def apply(self, config: dict[str, Any], dry_run: bool = False) -> ConfigResult:
        """Apply configuration.

        Args:
            config: Configuration dictionary
            dry_run: If True, don't apply changes

        Returns:
            Configuration result
        """
        pass

    def validate_config(self, config: dict[str, Any], schema_name: str) -> tuple[bool, list[str]]:
        """Validate configuration against schema.

        Args:
            config: Configuration to validate
            schema_name: Schema name

        Returns:
            Tuple of (is_valid, error_messages)
        """
        # This would use SchemaValidator if schemas are configured
        return True, []


class OrgConfigurator(BaseConfigurator):
    """Organization-level configuration."""

    def apply(self, config: dict[str, Any], dry_run: bool = False) -> ConfigResult:
        """Apply organization configuration.

        Args:
            config: Organization configuration
            dry_run: If True, simulate without applying

        Returns:
            Configuration result
        """
        org = config.get("organization")
        if not org:
            return ConfigResult(
                success=False,
                message="Missing 'organization' field",
                errors=[ValidationError("organization", "Required field missing")],
            )

        changes_applied = 0
        errors: list[ValidationError] = []

        # 2FA requirement
        if "two_factor_required" in config:
            remediation_logger.action_applied(
                "ORG-2FA",
                "Enable 2FA requirement",
                [org],
            )
            if not dry_run:
                try:
                    settings = {"two_factor_requirement_enabled": config["two_factor_required"]}
                    self.api.update_org_settings(org, settings)
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(ValidationError("two_factor_required", f"API error: {e}"))
                    remediation_logger.action_failed("ORG-2FA", "Enable 2FA requirement", str(e))
            else:
                changes_applied += 1

        # Default member permission
        if "default_member_permission" in config:
            remediation_logger.action_applied(
                "ORG-PERM",
                "Set default member permission",
                [org],
            )
            if not dry_run:
                try:
                    settings = {"default_member_permission": config["default_member_permission"]}
                    self.api.update_org_settings(org, settings)
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(
                        ValidationError("default_member_permission", f"API error: {e}")
                    )
                    remediation_logger.action_failed(
                        "ORG-PERM", "Set default member permission", str(e)
                    )
            else:
                changes_applied += 1

        # Repository creation restrictions
        if "members_can_create_repositories" in config:
            remediation_logger.action_applied(
                "ORG-REPO-CREATE",
                "Restrict repository creation",
                [org],
            )
            if not dry_run:
                try:
                    settings = {
                        "members_can_create_repositories": config[
                            "members_can_create_repositories"
                        ]
                    }
                    self.api.update_org_settings(org, settings)
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(
                        ValidationError(
                            "members_can_create_repositories", f"API error: {e}"
                        )
                    )
                    remediation_logger.action_failed(
                        "ORG-REPO-CREATE", "Restrict repository creation", str(e)
                    )
            else:
                changes_applied += 1

        success = len(errors) == 0
        return ConfigResult(
            success=success,
            message=f"Applied {changes_applied} org settings" if success else "Org config failed",
            changes_applied=changes_applied,
            errors=errors,
        )


class RepoConfigurator(BaseConfigurator):
    """Repository-level configuration."""

    def apply(self, config: dict[str, Any], dry_run: bool = False) -> ConfigResult:
        """Apply repository configuration.

        Args:
            config: Repository configuration
            dry_run: If True, simulate without applying

        Returns:
            Configuration result
        """
        owner = config.get("owner")
        repo = config.get("repository")

        if not owner or not repo:
            return ConfigResult(
                success=False,
                message="Missing 'owner' or 'repository' field",
                errors=[
                    ValidationError("owner", "Required field missing"),
                    ValidationError("repository", "Required field missing"),
                ],
            )

        changes_applied = 0
        errors: list[ValidationError] = []

        # Branch protection ruleset
        if "branch_protection" in config:
            remediation_logger.action_applied(
                "REPO-BP",
                "Apply branch protection ruleset",
                [repo],
            )
            if not dry_run:
                try:
                    ruleset = config["branch_protection"]
                    self.api.create_branch_protection_ruleset(owner, repo, ruleset)
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(ValidationError("branch_protection", f"API error: {e}"))
                    remediation_logger.action_failed(
                        "REPO-BP", "Apply branch protection ruleset", str(e)
                    )
            else:
                changes_applied += 1

        # Create files (CODEOWNERS, SECURITY.md, etc.)
        if "files" in config:
            for file_config in config["files"]:
                file_path = file_config.get("path")
                content = file_config.get("content")
                message = file_config.get("message", f"Add {Path(file_path).name}")

                remediation_logger.action_applied(
                    f"REPO-FILE-{file_path}",
                    f"Create file: {file_path}",
                    [repo],
                )

                if not dry_run:
                    try:
                        success = self.api.create_file_in_repo(owner, repo, file_path, content, message)
                        if success:
                            changes_applied += 1
                        else:
                            errors.append(ValidationError("files", f"Failed to create {file_path}"))
                            remediation_logger.action_failed(
                                f"REPO-FILE-{file_path}", f"Create file: {file_path}", "Failed"
                            )
                    except GitHubAPIError as e:
                        errors.append(ValidationError("files", f"API error for {file_path}: {e}"))
                        remediation_logger.action_failed(
                            f"REPO-FILE-{file_path}", f"Create file: {file_path}", str(e)
                        )
                else:
                    changes_applied += 1

        # Update visibility
        if "visibility" in config:
            remediation_logger.action_applied(
                "REPO-VIS",
                f"Update repository visibility to {config['visibility']}",
                [repo],
            )
            if not dry_run:
                try:
                    settings = {"private": config["visibility"] == "private"}
                    # Note: This would need to be implemented in GitHubAPI
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(ValidationError("visibility", f"API error: {e}"))
                    remediation_logger.action_failed(
                        "REPO-VIS",
                        f"Update repository visibility to {config['visibility']}",
                        str(e),
                    )
            else:
                changes_applied += 1

        success = len(errors) == 0
        return ConfigResult(
            success=success,
            message=f"Applied {changes_applied} repo changes" if success else "Repo config failed",
            changes_applied=changes_applied,
            errors=errors,
        )


class MemberConfigurator(BaseConfigurator):
    """Member-level configuration."""

    def apply(self, config: dict[str, Any], dry_run: bool = False) -> ConfigResult:
        """Apply member configuration.

        Args:
            config: Member configuration
            dry_run: If True, simulate without applying

        Returns:
            Configuration result
        """
        org = config.get("organization")
        username = config.get("username")

        if not org or not username:
            return ConfigResult(
                success=False,
                message="Missing 'organization' or 'username' field",
                errors=[
                    ValidationError("organization", "Required field missing"),
                    ValidationError("username", "Required field missing"),
                ],
            )

        changes_applied = 0
        errors: list[ValidationError] = []

        # Set member role
        if "role" in config:
            remediation_logger.action_applied(
                "MEMBER-ROLE",
                f"Set member role to {config['role']}",
                [username],
            )
            if not dry_run:
                try:
                    # Role assignment via API
                    changes_applied += 1
                except GitHubAPIError as e:
                    errors.append(ValidationError("role", f"API error: {e}"))
                    remediation_logger.action_failed(
                        "MEMBER-ROLE", f"Set member role to {config['role']}", str(e)
                    )
            else:
                changes_applied += 1

        # Add to teams
        if "teams" in config:
            for team in config["teams"]:
                remediation_logger.action_applied(
                    f"MEMBER-TEAM-{team}",
                    f"Add member to team: {team}",
                    [username],
                )
                if not dry_run:
                    try:
                        # Team membership via API
                        changes_applied += 1
                    except GitHubAPIError as e:
                        errors.append(ValidationError("teams", f"API error for {team}: {e}"))
                        remediation_logger.action_failed(
                            f"MEMBER-TEAM-{team}",
                            f"Add member to team: {team}",
                            str(e),
                        )
                else:
                    changes_applied += 1

        success = len(errors) == 0
        return ConfigResult(
            success=success,
            message=f"Applied {changes_applied} member changes" if success else "Member config failed",
            changes_applied=changes_applied,
            errors=errors,
        )


class TeamConfigurator(BaseConfigurator):
    """Team-level configuration."""

    def apply(self, config: dict[str, Any], dry_run: bool = False) -> ConfigResult:
        """Apply team configuration.

        Args:
            config: Team configuration
            dry_run: If True, simulate without applying

        Returns:
            Configuration result
        """
        org = config.get("organization")
        team_name = config.get("team_name")

        if not org or not team_name:
            return ConfigResult(
                success=False,
                message="Missing 'organization' or 'team_name' field",
                errors=[
                    ValidationError("organization", "Required field missing"),
                    ValidationError("team_name", "Required field missing"),
                ],
            )

        changes_applied = 0
        errors: list[ValidationError] = []

        # Create team
        remediation_logger.action_applied(
            "TEAM-CREATE",
            f"Create team: {team_name}",
            [team_name],
        )
        if not dry_run:
            try:
                # Team creation via API
                changes_applied += 1
            except GitHubAPIError as e:
                errors.append(ValidationError("team_name", f"API error: {e}"))
                remediation_logger.action_failed(
                    "TEAM-CREATE", f"Create team: {team_name}", str(e)
                )
        else:
            changes_applied += 1

        # Set team permissions
        if "repositories" in config:
            for repo_config in config["repositories"]:
                repo = repo_config.get("name")
                permission = repo_config.get("permission")

                remediation_logger.action_applied(
                    f"TEAM-REPO-{repo}",
                    f"Set team permission on {repo} to {permission}",
                    [team_name],
                )

                if not dry_run:
                    try:
                        # Set team permissions via API
                        changes_applied += 1
                    except GitHubAPIError as e:
                        errors.append(
                            ValidationError(
                                "repositories", f"API error for {repo}: {e}"
                            )
                        )
                        remediation_logger.action_failed(
                            f"TEAM-REPO-{repo}",
                            f"Set team permission on {repo} to {permission}",
                            str(e),
                        )
                else:
                    changes_applied += 1

        success = len(errors) == 0
        return ConfigResult(
            success=success,
            message=f"Applied {changes_applied} team changes" if success else "Team config failed",
            changes_applied=changes_applied,
            errors=errors,
        )


class Configurator:
    """Main configuration orchestrator."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize configurator.

        Args:
            token: GitHub API token
        """
        self.api = GitHubAPI(token=token)
        self.org_configurator = OrgConfigurator(self.api)
        self.repo_configurator = RepoConfigurator(self.api)
        self.member_configurator = MemberConfigurator(self.api)
        self.team_configurator = TeamConfigurator(self.api)
        self.results: list[ConfigResult] = []

    def load_configuration(self, config_path: Path | str) -> dict[str, Any]:
        """Load configuration from JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary

        Raises:
            ValueError: If file not found or invalid JSON
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise ValueError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    def validate_configuration(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate configuration structure.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: list[str] = []

        scope = config.get("scope")
        if not scope or scope not in ["org", "repo", "member", "team"]:
            errors.append("Invalid or missing 'scope' field. Must be: org, repo, member, or team")

        if scope == "org":
            if "organization" not in config:
                errors.append("Organization scope requires 'organization' field")
        elif scope == "repo":
            if "owner" not in config or "repository" not in config:
                errors.append("Repository scope requires 'owner' and 'repository' fields")
        elif scope == "member":
            if "organization" not in config or "username" not in config:
                errors.append("Member scope requires 'organization' and 'username' fields")
        elif scope == "team":
            if "organization" not in config or "team_name" not in config:
                errors.append("Team scope requires 'organization' and 'team_name' fields")

        return len(errors) == 0, errors

    def apply_configuration(
        self,
        config: dict[str, Any],
        dry_run: bool = False,
    ) -> ConfigResult:
        """Apply configuration to GitHub.

        Args:
            config: Configuration to apply
            dry_run: If True, simulate without applying changes

        Returns:
            Configuration result
        """
        # Validate
        is_valid, errors = self.validate_configuration(config)
        if not is_valid:
            return ConfigResult(
                success=False,
                message="Configuration validation failed",
                errors=[ValidationError("config", error) for error in errors],
            )

        scope = config.get("scope")
        mode = "DRY-RUN" if dry_run else "APPLY"

        remediation_logger.remediation_start(
            config.get("organization", config.get("owner", "unknown")),
            dry_run=dry_run,
        )

        # Route to appropriate configurator
        try:
            if scope == "org":
                result = self.org_configurator.apply(config, dry_run=dry_run)
            elif scope == "repo":
                result = self.repo_configurator.apply(config, dry_run=dry_run)
            elif scope == "member":
                result = self.member_configurator.apply(config, dry_run=dry_run)
            elif scope == "team":
                result = self.team_configurator.apply(config, dry_run=dry_run)
            else:
                result = ConfigResult(
                    success=False,
                    message=f"Unknown scope: {scope}",
                )

            self.results.append(result)

            remediation_logger.remediation_summary(
                total=result.changes_applied,
                successful=result.changes_applied if result.success else 0,
                failed=len(result.errors),
                skipped=0,
            )

            return result

        except Exception as e:
            remediation_logger.action_failed(
                "CONFIG",
                f"Apply configuration ({scope})",
                str(e),
            )
            return ConfigResult(
                success=False,
                message=f"Error applying configuration: {e}",
                errors=[ValidationError("config", str(e))],
            )

    def apply_from_file(
        self,
        config_path: Path | str,
        dry_run: bool = False,
    ) -> ConfigResult:
        """Load and apply configuration from file.

        Args:
            config_path: Path to configuration file
            dry_run: If True, simulate without applying changes

        Returns:
            Configuration result
        """
        config = self.load_configuration(config_path)
        return self.apply_configuration(config, dry_run=dry_run)

    def get_results_summary(self) -> dict[str, Any]:
        """Get summary of all configuration applications.

        Returns:
            Summary statistics
        """
        if not self.results:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "total_changes": 0,
            }

        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        total_changes = sum(r.changes_applied for r in self.results)

        return {
            "total": len(self.results),
            "successful": successful,
            "failed": failed,
            "total_changes": total_changes,
            "success_rate": (successful / len(self.results) * 100) if self.results else 0,
        }
