"""CLI commands for GitHub audit framework."""

import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from .analyzer import SecurityAnalyzer
from .collector import GitHubDataCollector, GitHubAPIError
from .remediator import RemediationExecutor
from .reporter import AuditReport, ReportGenerator

app = typer.Typer()
console = Console()


@app.command()
def audit(
    organization: str = typer.Argument(..., help="GitHub organization name"),
    token: str | None = typer.Option(None, "--token", "-t", help="GitHub personal access token"),
    output: str = typer.Option(
        "reports", "--output", "-o", help="Output directory for reports"
    ),
    no_html: bool = typer.Option(False, "--no-html", help="Skip HTML report generation"),
) -> None:
    """Run a complete audit of a GitHub organization.

    Examples:
        # Basic usage (uses GITHUB_TOKEN env var)
        gh-audit audit VoodoOps

        # Specify token
        gh-audit audit VoodoOps --token $GITHUB_TOKEN

        # Custom output directory
        gh-audit audit VoodoOps --output ./my-reports

        # Skip HTML generation
        gh-audit audit VoodoOps --no-html
    """
    console.print(f"[bold blue]GitHub Organization Audit[/bold blue]")
    console.print(f"Organization: [bold]{organization}[/bold]")
    console.print()

    try:
        with Progress() as progress:
            # Initialize collector
            task1 = progress.add_task("[cyan]Initializing...", total=1)
            try:
                collector = GitHubDataCollector(token=token)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                sys.exit(1)
            progress.update(task1, completed=1)

            # Collect data
            task2 = progress.add_task("[cyan]Collecting organization data...", total=1)
            try:
                org_data, repos_data = collector.audit_org_complete(organization)
                outside_collab = collector.get_org_outside_collaborators(organization)
            except GitHubAPIError as e:
                console.print(f"[red]API Error:[/red] {e}")
                sys.exit(1)
            progress.update(task2, completed=1)

            # Analyze
            task3 = progress.add_task("[cyan]Analyzing security posture...", total=1)
            analyzer = SecurityAnalyzer()
            findings, summary = analyzer.analyze(org_data, repos_data, outside_collab)
            progress.update(task3, completed=1)

            # Generate reports
            task4 = progress.add_task("[cyan]Generating reports...", total=1)
            output_path = Path(output) / f"{organization}_{summary.timestamp.strftime('%Y%m%d_%H%M%S')}"
            output_path.mkdir(parents=True, exist_ok=True)

            # Create audit report
            audit_report = AuditReport(summary, org_data, repos_data)

            # Save JSON report
            json_path = output_path / "audit-report.json"
            audit_report.to_file(json_path)

            # Save executive summary
            exec_summary_path = output_path / "executive-summary.txt"
            ReportGenerator.generate_executive_summary(audit_report, exec_summary_path)

            # Save remediation plan
            remediation_path = output_path / "remediation-plan.md"
            ReportGenerator.generate_remediation_plan(analyzer, remediation_path)

            # Save HTML report
            if not no_html:
                html_path = output_path / "audit-report.html"
                ReportGenerator.generate_html(audit_report, html_path)

            progress.update(task4, completed=1)

        # Print summary
        console.print()
        console.print("[bold green]✓ Audit Complete![/bold green]")
        console.print()

        summary_table = Table(title="Audit Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Organization", org_data.login)
        summary_table.add_row("Total Findings", str(summary.total_findings))
        summary_table.add_row("Critical", str(summary.critical), style="red")
        summary_table.add_row("High", str(summary.high), style="yellow")
        summary_table.add_row("Medium", str(summary.medium))
        summary_table.add_row("Low", str(summary.low))
        summary_table.add_row("Compliance Score", f"{summary.compliance_score:.1f}%")
        summary_table.add_row("Repositories Audited", str(summary.repos_audited))
        summary_table.add_row("Scan Duration", f"{summary.scan_duration_seconds:.2f}s")

        console.print(summary_table)
        console.print()

        # Show output paths
        console.print("[bold blue]📁 Reports Generated:[/bold blue]")
        console.print(f"  JSON Report: {json_path}")
        console.print(f"  Executive Summary: {exec_summary_path}")
        console.print(f"  Remediation Plan: {remediation_path}")
        if not no_html:
            console.print(f"  HTML Report: {html_path}")

        console.print()
        console.print("[dim]Run the audit command again to check compliance progress[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def check(
    organization: str = typer.Argument(..., help="GitHub organization name"),
    repository: str | None = typer.Argument(None, help="Repository name (optional)"),
    token: str | None = typer.Option(None, "--token", "-t", help="GitHub personal access token"),
) -> None:
    """Quick security check for organization or repository.

    Examples:
        # Check entire organization
        gh-audit check VoodoOps

        # Check specific repository
        gh-audit check VoodoOps Lab4PurpleSec
    """
    console.print(f"[bold blue]Quick Security Check[/bold blue]")

    try:
        collector = GitHubDataCollector(token=token)

        if repository:
            console.print(f"Repository: [bold]{organization}/{repository}[/bold]")
            repo_data = collector.get_repo_details(organization, repository)

            # Quick checks
            checks = [
                ("Private", repo_data.visibility == "private"),
                ("Branch Protection", repo_data.branch_protection is not None),
                ("Secret Scanning", repo_data.has_secret_scanning),
                ("Dependabot", repo_data.has_dependabot),
            ]

            table = Table(title="Security Checks")
            table.add_column("Check", style="cyan")
            table.add_column("Status")

            for name, passed in checks:
                status = "[green]✓[/green]" if passed else "[red]✗[/red]"
                table.add_row(name, status)

            console.print(table)
        else:
            console.print(f"Organization: [bold]{organization}[/bold]")
            org_data, repos_data = collector.audit_org_complete(organization)

            console.print(f"Total Repositories: {len(repos_data)}")
            console.print(f"Total Members: {org_data.members_count}")

            # Summary
            protected = sum(1 for r in repos_data if r.branch_protection is not None)
            scanned = sum(1 for r in repos_data if r.has_secret_scanning)
            private = sum(1 for r in repos_data if r.visibility == "private")

            console.print()
            table = Table(title="Organization Overview")
            table.add_column("Metric", style="cyan")
            table.add_column("Value")

            table.add_row("Private Repos", f"{private}/{len(repos_data)}")
            table.add_row("Branch Protection", f"{protected}/{len(repos_data)}")
            table.add_row("Secret Scanning", f"{scanned}/{len(repos_data)}")

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def remediate(
    organization: str = typer.Argument(..., help="GitHub organization name"),
    config: str = typer.Option(
        "config/remediation-plan.json", "--config", "-c", help="Path to remediation plan JSON"
    ),
    token: str | None = typer.Option(None, "--token", "-t", help="GitHub personal access token"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate without applying changes"),
) -> None:
    """Apply security improvements to organization repositories.

    This command applies branch protection, governance files, and workflows
    based on the remediation plan.

    Examples:
        # Apply recommended improvements
        gh-audit remediate VoodoOps

        # Dry run to see what would be applied
        gh-audit remediate VoodoOps --dry-run

        # Use custom remediation plan
        gh-audit remediate VoodoOps --config custom-plan.json
    """
    console.print(f"[bold blue]GitHub Organization Remediation[/bold blue]")
    console.print(f"Organization: [bold]{organization}[/bold]")
    console.print(f"Config: {config}")
    if dry_run:
        console.print("[yellow]⚠️  DRY RUN MODE - No changes will be applied[/yellow]")
    console.print()

    try:
        # Load remediation plan
        config_path = Path(config)
        if not config_path.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config}")
            sys.exit(1)

        remediator = RemediationExecutor(token=token)

        if dry_run:
            console.print("[cyan]Loading remediation plan...[/cyan]")
            plan = remediator.load_remediation_plan(config_path)
            actions = plan.get("remediation_plan", {}).get("actions", [])

            console.print(f"[bold]Remediation Plan Summary[/bold]")
            console.print(f"Total actions: {len(actions)}")
            console.print()

            for action in actions:
                risk_level = action.get("risk_level", "UNKNOWN")
                title = action.get("title", "Unknown")
                repos = action.get("affected_repositories", [])

                risk_color = {
                    "CRITICAL": "red",
                    "HIGH": "yellow",
                    "MEDIUM": "blue",
                    "LOW": "cyan",
                }.get(risk_level, "white")

                console.print(
                    f"[{risk_color}]●[/{risk_color}] [{risk_level}] {title}"
                )
                console.print(f"  Repos: {', '.join(repos)}")
                console.print()

            console.print("[yellow]Would apply these changes. Run without --dry-run to execute.[/yellow]")

        else:
            with Progress() as progress:
                task = progress.add_task("[cyan]Applying remediations...", total=1)

                # Use absolute template path
                template_dir = Path(__file__).parent.parent.parent / "templates"
                results = remediator.apply_remediation(organization, config_path, template_dir)

                progress.update(task, completed=1)

            console.print()
            console.print("[bold green]✓ Remediation Complete![/bold green]")
            console.print()

            # Show results
            results_table = Table(title="Remediation Results")
            results_table.add_column("Action", style="cyan")
            results_table.add_column("Status", style="green")
            results_table.add_column("Details")

            for result in results:
                status_color = {
                    "success": "green",
                    "failed": "red",
                    "skipped": "yellow",
                }.get(result.status, "white")

                status_symbol = {
                    "success": "✓",
                    "failed": "✗",
                    "skipped": "⊘",
                }.get(result.status, "?")

                results_table.add_row(
                    result.action_title,
                    f"[{status_color}]{status_symbol} {result.status}[/{status_color}]",
                    result.message,
                )

            console.print(results_table)
            console.print()

            # Summary
            summary = remediator.get_results_summary()
            console.print("[bold]Summary[/bold]")
            console.print(f"Total: {summary['total']} | ✓ {summary['successful']} | ✗ {summary['failed']} | ⊘ {summary['skipped']}")
            console.print(f"Success Rate: {summary['success_rate']:.1f}%")

            console.print()
            console.print("[cyan]Next Steps:[/cyan]")
            console.print("1. Review changes in GitHub repository")
            console.print("2. Enable Secret Scanning in organization settings")
            console.print("3. Run audit again to verify compliance improvement")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]GitHub Audit Framework[/bold]")
    console.print("Version: 1.0.0")
    console.print("Python: 3.12+")


if __name__ == "__main__":
    app()
