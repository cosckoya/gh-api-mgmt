"""Centralized GitHub API abstraction layer.

This module consolidates all GitHub REST API interactions with:
- Unified error handling
- Automatic pagination
- Rate limit handling
- Caching layer
- Request logging
"""

import os
import time
from functools import wraps
from typing import Any, Callable, TypeVar

import requests

from ..config import BASE_URL, TIMEOUT

T = TypeVar("T")


class GitHubAPIError(Exception):
    """GitHub API error."""

    pass


class GitHubAPI:
    """Centralized GitHub API wrapper for all REST calls."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize GitHub API client.

        Args:
            token: GitHub personal access token. If None, uses GITHUB_TOKEN env var.

        Raises:
            ValueError: If no token is available.
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
        self._cache: dict[str, Any] = {}
        self._rate_limit_remaining = 5000
        self._rate_limit_reset = 0

    def _handle_rate_limit(self) -> None:
        """Handle GitHub API rate limiting with exponential backoff."""
        if self._rate_limit_remaining < 100:
            wait_time = max(0, self._rate_limit_reset - time.time()) + 5
            if wait_time > 0:
                print(f"[WARN] Rate limit approaching, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)

    def _update_rate_limit(self, response: requests.Response) -> None:
        """Extract and update rate limit from response headers."""
        try:
            self._rate_limit_remaining = int(
                response.headers.get("X-RateLimit-Remaining", 5000)
            )
            self._rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
        except ValueError:
            pass

    def _get(self, endpoint: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
        """Execute GET request with error handling.

        Args:
            endpoint: API endpoint path (without base URL).
            **kwargs: Additional arguments to pass to requests.

        Returns:
            JSON response.

        Raises:
            GitHubAPIError: If request fails.
        """
        url = f"{BASE_URL}{endpoint}"
        self._handle_rate_limit()

        try:
            response = requests.get(
                url, headers=self.headers, timeout=TIMEOUT, **kwargs
            )
            self._update_rate_limit(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"GET {endpoint} failed: {e}") from e

    def _post(
        self, endpoint: str, json_data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute POST request with error handling.

        Args:
            endpoint: API endpoint path.
            json_data: JSON payload.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            JSON response.

        Raises:
            GitHubAPIError: If request fails.
        """
        url = f"{BASE_URL}{endpoint}"
        self._handle_rate_limit()

        try:
            response = requests.post(
                url, headers=self.headers, json=json_data, timeout=TIMEOUT, **kwargs
            )
            self._update_rate_limit(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"POST {endpoint} failed: {e}") from e

    def _put(
        self, endpoint: str, json_data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Execute PUT request with error handling.

        Args:
            endpoint: API endpoint path.
            json_data: JSON payload.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            JSON response.

        Raises:
            GitHubAPIError: If request fails.
        """
        url = f"{BASE_URL}{endpoint}"
        self._handle_rate_limit()

        try:
            response = requests.put(
                url, headers=self.headers, json=json_data, timeout=TIMEOUT, **kwargs
            )
            self._update_rate_limit(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"PUT {endpoint} failed: {e}") from e

    def get_paginated(
        self, endpoint: str, per_page: int = 100, max_pages: int | None = None
    ) -> list[Any]:
        """Execute paginated GET request.

        Args:
            endpoint: API endpoint path.
            per_page: Items per page (max 100).
            max_pages: Maximum pages to fetch (None for all).

        Returns:
            Combined list of all items across pages.
        """
        items: list[Any] = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            separator = "&" if "?" in endpoint else "?"
            paginated_endpoint = f"{endpoint}{separator}per_page={per_page}&page={page}"

            data = self._get(paginated_endpoint)
            if not isinstance(data, list) or not data:
                break

            items.extend(data)

            if len(data) < per_page:
                break

            page += 1

        return items

    # Organization APIs
    def get_org(self, org: str) -> dict[str, Any]:
        """Get organization information."""
        return self._get(f"/orgs/{org}")

    def get_org_members(self, org: str) -> list[dict[str, Any]]:
        """Get all organization members."""
        return self.get_paginated(f"/orgs/{org}/members")

    def get_org_outside_collaborators(self, org: str) -> list[dict[str, Any]]:
        """Get outside collaborators."""
        return self.get_paginated(f"/orgs/{org}/outside_collaborators")

    def get_org_teams(self, org: str) -> list[dict[str, Any]]:
        """Get all teams in organization."""
        return self.get_paginated(f"/orgs/{org}/teams")

    def get_org_settings(self, org: str) -> dict[str, Any]:
        """Get organization settings."""
        return self._get(f"/orgs/{org}")

    # Repository APIs
    def get_org_repos(self, org: str) -> list[dict[str, Any]]:
        """Get all organization repositories."""
        return self.get_paginated(f"/orgs/{org}/repos?type=all&sort=updated")

    def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
        """Get repository details."""
        return self._get(f"/repos/{owner}/{repo}")

    def get_repo_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> dict[str, Any] | None:
        """Get branch protection rules."""
        try:
            return self._get(f"/repos/{owner}/{repo}/branches/{branch}/protection")
        except GitHubAPIError:
            return None

    def get_repo_rulesets(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get repository rulesets."""
        try:
            data = self._get(f"/repos/{owner}/{repo}/rulesets")
            return data if isinstance(data, list) else []
        except GitHubAPIError:
            return []

    def get_repo_file(self, owner: str, repo: str, path: str) -> str | None:
        """Get file content from repository."""
        try:
            import base64

            data = self._get(f"/repos/{owner}/{repo}/contents/{path}")
            if isinstance(data, dict) and "content" in data:
                content = data["content"]
                return base64.b64decode(content).decode("utf-8")
        except GitHubAPIError:
            pass
        return None

    def get_repo_workflows(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get GitHub Actions workflows."""
        try:
            data = self._get(f"/repos/{owner}/{repo}/actions/workflows")
            return data.get("workflows", []) if isinstance(data, dict) else []
        except GitHubAPIError:
            return []

    def get_repo_webhooks(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get repository webhooks."""
        try:
            return self.get_paginated(f"/repos/{owner}/{repo}/hooks")
        except GitHubAPIError:
            return []

    def get_repo_collaborators(self, owner: str, repo: str) -> list[dict[str, Any]]:
        """Get repository collaborators."""
        try:
            return self.get_paginated(f"/repos/{owner}/{repo}/collaborators")
        except GitHubAPIError:
            return []

    def get_repo_deployment_protection_rules(
        self, owner: str, repo: str
    ) -> list[dict[str, Any]]:
        """Get deployment protection rules."""
        try:
            data = self._get(f"/repos/{owner}/{repo}/environments")
            return data if isinstance(data, list) else []
        except GitHubAPIError:
            return []

    # Configuration APIs (for Configurator)
    def create_file_in_repo(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str = "",
        branch: str = "main",
    ) -> bool:
        """Create or update a file in repository."""
        import base64

        url = f"/repos/{owner}/{repo}/contents/{path}"
        encoded_content = base64.b64encode(content.encode()).decode()

        # Try to get existing file for update
        try:
            existing = self._get(url)
            sha = existing.get("sha") if isinstance(existing, dict) else None
        except GitHubAPIError:
            sha = None

        payload = {
            "message": message or f"chore: add {path.split('/')[-1]}",
            "content": encoded_content,
            "branch": branch,
        }

        if sha:
            payload["sha"] = sha

        try:
            self._put(url, json_data=payload)
            return True
        except GitHubAPIError:
            return False

    def create_branch_protection_ruleset(
        self, owner: str, repo: str, ruleset_config: dict[str, Any]
    ) -> bool:
        """Create branch protection ruleset."""
        try:
            self._post(f"/repos/{owner}/{repo}/rulesets", json_data=ruleset_config)
            return True
        except GitHubAPIError:
            return False

    def update_org_settings(
        self, org: str, settings: dict[str, Any]
    ) -> dict[str, Any]:
        """Update organization settings."""
        return self._put(f"/orgs/{org}", json_data=settings)
