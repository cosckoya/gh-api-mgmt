"""GitHub data collector using centralized API wrapper."""

from typing import Any

from .models import OrganizationData, RepositoryData
from .utils import GitHubAPI, GitHubAPIError


class GitHubDataCollector:
    """Collects audit data from GitHub using REST API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize collector with GitHub token.

        Args:
            token: GitHub token. If None, uses GITHUB_TOKEN env var.

        Raises:
            ValueError: If no token available.
        """
        self.api = GitHubAPI(token=token)
        self.token = self.api.token
        self.headers = self.api.headers

    def get_org_info(self, org: str) -> dict[str, Any]:
        """Get basic organization information."""
        return self.api.get_org(org)

    def get_org_members(self, org: str) -> list[dict[str, Any]]:
        """Get all organization members."""
        return self.api.get_org_members(org)

    def get_org_outside_collaborators(self, org: str) -> list[dict[str, Any]]:
        """Get outside collaborators."""
        return self.api.get_org_outside_collaborators(org)

    def get_org_teams(self, org: str) -> list[dict[str, Any]]:
        """Get all teams in organization."""
        return self.api.get_org_teams(org)

    def get_org_repos(self, org: str) -> list[dict[str, Any]]:
        """Get all organization repositories."""
        return self.api.get_org_repos(org)

    def get_repo_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> dict[str, Any] | None:
        """Get branch protection rules."""
        return self.api.get_repo_branch_protection(owner, repo, branch)

    def get_repo_rulesets(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get repository rulesets."""
        return self.api.get_repo_rulesets(owner, repo)

    def get_repo_workflows(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get GitHub Actions workflows."""
        return self.api.get_repo_workflows(owner, repo)

    def get_repo_file(self, owner: str, repo: str, path: str) -> str | None:
        """Get file content from repository."""
        return self.api.get_repo_file(owner, repo, path)

    def get_repo_details(self, owner: str, repo: str) -> RepositoryData:
        """Get complete repository details.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository data object.
        """
        repo_data = self.api.get_repo(owner, repo)

        repo_obj = RepositoryData(
            name=repo_data.get("name", ""),
            visibility=repo_data.get("visibility", "private"),
            description=repo_data.get("description"),
            is_archived=repo_data.get("archived", False),
            is_fork=repo_data.get("fork", False),
            default_branch=repo_data.get("default_branch", "main"),
            url=repo_data.get("html_url", ""),
            owner=owner,
        )

        # Branch protection
        repo_obj.branch_protection = self.get_repo_branch_protection(
            owner, repo, repo_obj.default_branch
        )

        # Secret scanning
        security_analysis = repo_data.get("security_and_analysis", {})
        secret_scanning = security_analysis.get("secret_scanning", {})
        repo_obj.has_secret_scanning = secret_scanning.get("status") == "enabled"

        # Dependabot
        dependabot_alerts = security_analysis.get("dependabot_alerts", {})
        repo_obj.has_dependabot = dependabot_alerts.get("status") == "enabled"

        # Workflows
        workflows = self.get_repo_workflows(owner, repo)
        repo_obj.workflows_count = len(workflows)

        return repo_obj

    def audit_org_complete(self, org: str) -> tuple[OrganizationData, list[RepositoryData]]:
        """Execute complete organization audit.

        Args:
            org: Organization name.

        Returns:
            Tuple of (organization data, list of repository data).
        """
        # Get org info
        org_info = self.get_org_info(org)
        org_obj = OrganizationData(
            login=org_info.get("login", org),
            name=org_info.get("name"),
            plan=org_info.get("plan", {}).get("name", "unknown"),
            created_at=org_info.get("created_at", ""),
            members_count=len(self.get_org_members(org)),
            public_repos_count=org_info.get("public_repos", 0),
            total_repos_count=org_info.get("total_repos", 0),
        )

        # Get repos
        repos_data = []
        repos = self.get_org_repos(org)
        for repo in repos:
            try:
                repo_details = self.get_repo_details(org, repo["name"])
                repos_data.append(repo_details)
            except GitHubAPIError as e:
                print(f"Warning: Could not audit {repo['name']}: {e}")

        return org_obj, repos_data
