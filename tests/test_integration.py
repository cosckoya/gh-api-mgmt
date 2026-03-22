"""Integration tests for CLI and major workflows."""

import pytest
from typer.testing import CliRunner

from gh_audit.cli import app

runner = CliRunner()


class TestCliIntegration:
    """Integration tests for CLI commands."""

    def test_version_command_works(self) -> None:
        """Test that version command executes without error."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "2.0.0" in result.stdout

    def test_config_list_templates_works(self) -> None:
        """Test that config list-templates command works."""
        result = runner.invoke(app, ["config", "list-templates"])
        assert result.exit_code == 0
        # Should show template names
        assert "json" in result.stdout.lower()

    def test_config_validate_example_templates(self) -> None:
        """Test validating example configuration files."""
        # Test org config
        result = runner.invoke(app, [
            "config", "validate",
            "--file", "config/examples/org-security-hardened.json"
        ])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

        # Test repo config
        result = runner.invoke(app, [
            "config", "validate",
            "--file", "config/examples/repo-production.json"
        ])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_config_show_works(self) -> None:
        """Test showing configuration template."""
        result = runner.invoke(app, [
            "config", "show", "org-security-hardened.json"
        ])
        assert result.exit_code == 0
        assert "scope" in result.stdout

    def test_check_command_help(self) -> None:
        """Test check command help."""
        result = runner.invoke(app, ["check", "--help"])
        assert result.exit_code == 0
        assert "Quick security check" in result.stdout

    def test_audit_command_help(self) -> None:
        """Test audit command help."""
        result = runner.invoke(app, ["audit", "--help"])
        assert result.exit_code == 0
        assert "complete audit" in result.stdout.lower()

    def test_remediate_command_help(self) -> None:
        """Test remediate command help."""
        result = runner.invoke(app, ["remediate", "--help"])
        assert result.exit_code == 0
        assert "remediation" in result.stdout.lower()

    def test_config_apply_help(self) -> None:
        """Test config apply help."""
        result = runner.invoke(app, ["config", "apply", "--help"])
        assert result.exit_code == 0
        assert "apply" in result.stdout.lower()

    def test_audit_deep_help(self) -> None:
        """Test audit-deep command help."""
        result = runner.invoke(app, ["audit-deep", "--help"])
        assert result.exit_code == 0
        assert "deep" in result.stdout.lower()
