"""Tests for data collector module."""

import pytest

from gh_audit.collector import GitHubDataCollector, GitHubAPIError


def test_collector_requires_token() -> None:
    """Test that collector requires a GitHub token."""
    # Clear env var if it exists
    import os
    original_token = os.environ.pop("GITHUB_TOKEN", None)

    try:
        with pytest.raises(ValueError, match="GITHUB_TOKEN not found"):
            GitHubDataCollector()
    finally:
        # Restore env var
        if original_token:
            os.environ["GITHUB_TOKEN"] = original_token


def test_collector_accepts_token_parameter() -> None:
    """Test that collector accepts token parameter."""
    collector = GitHubDataCollector(token="ghp_test_token")
    assert collector.token == "ghp_test_token"


@pytest.mark.integration
def test_collector_get_org_info() -> None:
    """Test getting organization info (requires real token)."""
    import os
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        pytest.skip("GITHUB_TOKEN not set")

    collector = GitHubDataCollector(token=token)
    org_info = collector.get_org_info("VoodoOps")

    assert org_info.get("login") == "VoodoOps"
    assert "name" in org_info
    assert "plan" in org_info
