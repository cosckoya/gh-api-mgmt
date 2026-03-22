"""Remediation executor - applies security improvements via GitHub API."""

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from .config import BASE_URL, TIMEOUT
from .utils import GitHubAPIError


@dataclass
class RemediationResult:
    """Result of a remediation action."""

    action_id: str
    action_title: str
    status: str  # "success", "failed", "skipped"
    message: str
    details: dict[str, Any] | None = None


class RemediationExecutor:
    """Executes security improvements on GitHub repositories."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize remediator with GitHub token.

        Args:
            token: GitHub token. If None, uses GITHUB_TOKEN env var.
        """
        self.collector = GitHubDataCollector(token=token)
        self.token = self.collector.token
        self.headers = self.collector.headers
        self.results: list[RemediationResult] = []

    def load_remediation_plan(self, config_path: str | Path) -> dict[str, Any]:
        """Load remediation plan from JSON file.

        Args:
            config_path: Path to remediation plan JSON.

        Returns:
            Remediation plan configuration.
        """
        with open(config_path) as f:
            return json.load(f)

    def create_file_in_repo(
        self, owner: str, repo: str, path: str, content: str, message: str = ""
    ) -> bool:
        """Create or update a file in a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path (e.g., ".github/dependabot.yml").
            content: File content.
            message: Commit message.

        Returns:
            True if successful, False otherwise.
        """
        url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        encoded_content = base64.b64encode(content.encode()).decode()

        # Try to get existing file for update
        try:
            existing = requests.get(url, headers=self.headers, timeout=TIMEOUT)
            existing.raise_for_status()
            sha = existing.json().get("sha")
        except requests.exceptions.RequestException:
            sha = None

        payload = {
            "message": message or f"chore: add {Path(path).name}",
            "content": encoded_content,
            "branch": "main",
        }

        if sha:
            payload["sha"] = sha

        try:
            response = requests.put(url, headers=self.headers, json=payload, timeout=TIMEOUT)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error creating/updating {path}: {e}")
            return False

    def create_branch_protection_ruleset(
        self, owner: str, repo: str, ruleset_config: dict[str, Any]
    ) -> bool:
        """Create branch protection ruleset.

        Args:
            owner: Repository owner.
            repo: Repository name.
            ruleset_config: Ruleset configuration JSON.

        Returns:
            True if successful, False otherwise.
        """
        url = f"{BASE_URL}/repos/{owner}/{repo}/rulesets"

        try:
            response = requests.post(
                url, headers=self.headers, json=ruleset_config, timeout=TIMEOUT
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error creating ruleset for {owner}/{repo}: {e}")
            return False

    def apply_action_branch_protection(
        self, owner: str, repo: str, action: dict[str, Any], template_dir: Path
    ) -> RemediationResult:
        """Apply branch protection rules.

        Args:
            owner: Repository owner.
            repo: Repository name.
            action: Action configuration.
            template_dir: Path to templates directory.

        Returns:
            Remediation result.
        """
        action_id = action.get("id", "unknown")
        title = action.get("title", "Unknown action")

        try:
            configs = action.get("configurations", {})
            repo_config = configs.get(repo)

            if not repo_config:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="skipped",
                    message=f"No configuration for {repo}",
                )

            template_name = repo_config.get("template")
            # template_dir already includes "templates", so just add subdirectory and filename
            template_path = Path(template_dir) / "branch-protection" / template_name

            if not template_path.exists():
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Template not found: {template_path}",
                )

            with open(template_path) as f:
                ruleset_config = json.load(f)

            success = self.create_branch_protection_ruleset(owner, repo, ruleset_config)

            if success:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="success",
                    message=f"Branch protection ruleset created for {owner}/{repo}",
                    details={"template": template_name, "repo": repo},
                )
            else:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Failed to create ruleset for {owner}/{repo}",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action_id,
                action_title=title,
                status="failed",
                message=f"Error: {str(e)}",
            )

    def apply_action_governance_file(
        self, owner: str, repo: str, action: dict[str, Any], template_dir: Path
    ) -> RemediationResult:
        """Apply governance file (CODEOWNERS, SECURITY.md, dependabot.yml).

        Args:
            owner: Repository owner.
            repo: Repository name.
            action: Action configuration.
            template_dir: Path to templates directory.

        Returns:
            Remediation result.
        """
        action_id = action.get("id", "unknown")
        title = action.get("title", "Unknown action")

        try:
            file_config = action.get("file_content", {})
            source = file_config.get("source")
            target_path = file_config.get("path")

            if not source or not target_path:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="skipped",
                    message="Missing source or target path",
                )

            template_path = Path(template_dir) / source

            # Handle cases where source might start with "templates/"
            if "templates/" in source:
                # Source already contains "templates/", extract relative path
                source_relative = source.split("templates/", 1)[1]
                template_path = Path(template_dir) / source_relative

            if not template_path.exists():
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Template not found: {template_path}",
                )

            with open(template_path) as f:
                content = f.read()

            success = self.create_file_in_repo(
                owner, repo, target_path, content, message=f"chore: add {Path(target_path).name}"
            )

            if success:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="success",
                    message=f"File created: {owner}/{repo}/{target_path}",
                    details={"file": target_path, "repo": repo},
                )
            else:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Failed to create {target_path} in {owner}/{repo}",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action_id,
                action_title=title,
                status="failed",
                message=f"Error: {str(e)}",
            )

    def apply_action_workflow(
        self, owner: str, repo: str, action: dict[str, Any], template_dir: Path
    ) -> RemediationResult:
        """Apply GitHub Actions workflows.

        Args:
            owner: Repository owner.
            repo: Repository name.
            action: Action configuration.
            template_dir: Path to templates directory.

        Returns:
            Remediation result.
        """
        action_id = action.get("id", "unknown")
        title = action.get("title", "Unknown action")

        try:
            workflows = action.get("workflows", [])
            created_workflows = []
            failed_workflows = []

            for workflow in workflows:
                source = workflow.get("source")
                name = workflow.get("name")

                template_path = Path(template_dir) / source

                # Handle cases where source might start with "templates/"
                if "templates/" in source:
                    source_relative = source.split("templates/", 1)[1]
                    template_path = Path(template_dir) / source_relative

                if not template_path.exists():
                    failed_workflows.append(f"{name} (template not found: {template_path})")
                    continue

                with open(template_path) as f:
                    content = f.read()

                target_path = f".github/workflows/{name}"
                success = self.create_file_in_repo(
                    owner, repo, target_path, content, message=f"ci: add {name}"
                )

                if success:
                    created_workflows.append(name)
                else:
                    failed_workflows.append(name)

            if created_workflows and not failed_workflows:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="success",
                    message=f"Workflows created for {owner}/{repo}: {', '.join(created_workflows)}",
                    details={"workflows": created_workflows, "repo": repo},
                )
            elif created_workflows and failed_workflows:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Partial success. Created: {created_workflows}. Failed: {failed_workflows}",
                    details={"created": created_workflows, "failed": failed_workflows},
                )
            else:
                return RemediationResult(
                    action_id=action_id,
                    action_title=title,
                    status="failed",
                    message=f"Failed to create workflows for {owner}/{repo}",
                )

        except Exception as e:
            return RemediationResult(
                action_id=action_id,
                action_title=title,
                status="failed",
                message=f"Error: {str(e)}",
            )

    def apply_remediation(
        self, org: str, config_path: str | Path, template_dir: str | Path | None = None
    ) -> list[RemediationResult]:
        """Apply all remediations from a plan.

        Args:
            org: Organization name.
            config_path: Path to remediation plan JSON.
            template_dir: Path to templates directory.

        Returns:
            List of remediation results.
        """
        if template_dir is None:
            # Look for templates directory relative to project root
            config_file = Path(config_path).resolve()
            project_root = config_file.parent.parent
            template_dir = project_root / "templates"

            # Fallback to src location
            if not template_dir.exists():
                template_dir = Path(__file__).parent.parent.parent / "templates"
        else:
            template_dir = Path(template_dir)

        # Debug output
        print(f"[DEBUG] Templates directory: {template_dir}")
        print(f"[DEBUG] Templates exist: {template_dir.exists()}")

        plan = self.load_remediation_plan(config_path)
        actions = plan.get("remediation_plan", {}).get("actions", [])

        self.results = []

        for action in actions:
            action_type = action.get("type")
            affected_repos = action.get("affected_repositories", [])

            for repo in affected_repos:
                if action_type == "branch-protection":
                    result = self.apply_action_branch_protection(org, repo, action, template_dir)
                elif action_type == "governance-file":
                    result = self.apply_action_governance_file(org, repo, action, template_dir)
                elif action_type == "workflow":
                    result = self.apply_action_workflow(org, repo, action, template_dir)
                else:
                    result = RemediationResult(
                        action_id=action.get("id", "unknown"),
                        action_title=action.get("title", "Unknown"),
                        status="skipped",
                        message=f"Unknown action type: {action_type}",
                    )

                self.results.append(result)

        return self.results

    def get_results_summary(self) -> dict[str, Any]:
        """Get summary of remediation results.

        Returns:
            Summary dictionary.
        """
        total = len(self.results)
        successful = sum(1 for r in self.results if r.status == "success")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
        }
