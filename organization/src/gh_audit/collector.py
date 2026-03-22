"""GitHub Data Collector - Recolecta datos de la organización."""

import os
from typing import Any

import requests

from .config import API_VERSION, BASE_URL, TIMEOUT
from .models import OrganizationData, RepositoryData


class GitHubAPIError(Exception):
    """GitHub API error."""

    pass


class GitHubDataCollector:
    """Recolecta datos de GitHub usando REST API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize collector with GitHub token.

        Args:
            token: GitHub token. If None, uses GITHUB_TOKEN env var.

        Raises:
            ValueError: If no token available.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GITHUB_TOKEN not found in environment. "
                "Set it via: export GITHUB_TOKEN=your_token"
            )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
        }

    def _rest_get(self, endpoint: str) -> dict[str, Any] | list[Any]:
        """Execute GET request to REST API.

        Args:
            endpoint: API endpoint (without base URL).

        Returns:
            JSON response.

        Raises:
            GitHubAPIError: If request fails.
        """
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"API request failed for {endpoint}: {e}") from e

    def get_org_info(self, org: str) -> dict[str, Any]:
        """Get basic organization information.

        Args:
            org: Organization name.

        Returns:
            Organization data.
        """
        data = self._rest_get(f"/orgs/{org}")
        if isinstance(data, dict):
            return data
        return {}

    def get_org_members(self, org: str) -> list[dict[str, Any]]:
        """Get all organization members.

        Args:
            org: Organization name.

        Returns:
            List of members.
        """
        members = []
        page = 1
        while True:
            data = self._rest_get(f"/orgs/{org}/members?per_page=100&page={page}")
            if not data or not isinstance(data, list):
                break
            members.extend(data)
            if len(data) < 100:
                break
            page += 1
        return members

    def get_org_outside_collaborators(self, org: str) -> list[dict[str, Any]]:
        """Get outside collaborators.

        Args:
            org: Organization name.

        Returns:
            List of outside collaborators.
        """
        collaborators = []
        page = 1
        while True:
            data = self._rest_get(
                f"/orgs/{org}/outside_collaborators?per_page=100&page={page}"
            )
            if not data or not isinstance(data, list):
                break
            collaborators.extend(data)
            if len(data) < 100:
                break
            page += 1
        return collaborators

    def get_org_repos(self, org: str) -> list[dict[str, Any]]:
        """Get all organization repositories.

        Args:
            org: Organization name.

        Returns:
            List of repositories.
        """
        repos = []
        page = 1
        while True:
            data = self._rest_get(
                f"/orgs/{org}/repos?per_page=100&page={page}&type=all&sort=updated"
            )
            if not data or not isinstance(data, list):
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
        return repos

    def get_repo_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> dict[str, Any] | None:
        """Get branch protection rules.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Branch name.

        Returns:
            Branch protection data or None if not protected.
        """
        try:
            return self._rest_get(f"/repos/{owner}/{repo}/branches/{branch}/protection")
        except GitHubAPIError:
            return None

    def get_repo_rulesets(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get repository rulesets.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            List of rulesets.
        """
        try:
            data = self._rest_get(f"/repos/{owner}/{repo}/rulesets")
            return data if isinstance(data, list) else []
        except GitHubAPIError:
            return []

    def get_repo_workflows(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get GitHub Actions workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            List of workflows.
        """
        try:
            data = self._rest_get(f"/repos/{owner}/{repo}/actions/workflows")
            workflows = data.get("workflows", []) if isinstance(data, dict) else []
            return workflows
        except GitHubAPIError:
            return []

    def get_repo_file(self, owner: str, repo: str, path: str) -> str | None:
        """Get file content from repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path.

        Returns:
            File content or None if not found.
        """
        try:
            import base64

            data = self._rest_get(f"/repos/{owner}/{repo}/contents/{path}")
            if isinstance(data, dict) and "content" in data:
                content = data["content"]
                return base64.b64decode(content).decode("utf-8")
        except GitHubAPIError:
            pass
        return None

    def get_repo_details(self, owner: str, repo: str) -> RepositoryData:
        """Get complete repository details.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository data object.
        """
        repo_data = self._rest_get(f"/repos/{owner}/{repo}")

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
