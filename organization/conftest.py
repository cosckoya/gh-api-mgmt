"""Shared pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_org_data():
    """Fixture for mock organization data."""
    return {
        "login": "test-org",
        "name": "Test Organization",
        "plan": {"name": "free"},
        "created_at": "2024-01-01T00:00:00Z",
        "public_repos": 2,
        "total_repos": 5,
    }


@pytest.fixture
def mock_repo_data():
    """Fixture for mock repository data."""
    return {
        "name": "test-repo",
        "visibility": "private",
        "description": "Test repository",
        "archived": False,
        "fork": False,
        "default_branch": "main",
        "html_url": "https://github.com/test-org/test-repo",
        "security_and_analysis": {
            "secret_scanning": {"status": "enabled"},
            "dependabot_alerts": {"status": "enabled"},
        },
    }
