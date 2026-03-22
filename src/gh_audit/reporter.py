"""Report generation - creates JSON and HTML reports."""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .analyzer import SecurityAnalyzer
from .models import AuditSummary, OrganizationData, RepositoryData


class AuditReport:
    """Represents a complete audit report."""

    def __init__(
        self,
        summary: AuditSummary,
        org_data: OrganizationData,
        repos_data: list[RepositoryData],
    ) -> None:
        """Initialize audit report.

        Args:
            summary: Audit summary.
            org_data: Organization data.
            repos_data: List of repository data.
        """
        self.summary = summary
        self.org_data = org_data
        self.repos_data = repos_data

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary.

        Returns:
            Report as dictionary.
        """
        return {
            "audit_metadata": {
                "timestamp": self.summary.timestamp.isoformat(),
                "organization": self.summary.organization,
                "auditor": "gh-audit-framework",
                "framework_version": "1.0.0",
                "scan_duration_seconds": round(self.summary.scan_duration_seconds, 2),
            },
            "summary": self.summary.to_dict(),
            "organization": self.org_data.to_dict(),
            "repositories": [repo.to_dict() for repo in self.repos_data],
            "remediation_priorities": [
                priority.to_dict()
                for priority in SecurityAnalyzer().get_remediation_priorities()
            ],
        }

    def to_json(self) -> str:
        """Convert report to JSON string.

        Returns:
            Report as JSON.
        """
        return json.dumps(self.to_dict(), indent=2)

    def to_file(self, filepath: Path | str) -> None:
        """Save report to JSON file.

        Args:
            filepath: Output file path.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(self.to_json())


class ReportGenerator:
    """Generates reports in various formats."""

    @staticmethod
    def generate_category_breakdown(audit_report: AuditReport) -> str:
        """Generate findings breakdown by category.

        Args:
            audit_report: Audit report.

        Returns:
            HTML for category breakdown.
        """
        all_findings = audit_report.org_data.findings + [
            f for r in audit_report.repos_data for f in r.findings
        ]

        categories: dict[str, int] = {}
        for finding in all_findings:
            cat = finding.category
            categories[cat] = categories.get(cat, 0) + 1

        category_html = ""
        for category, count in sorted(categories.items()):
            category_html += f"""
            <div style="display: inline-block; margin-right: 20px;">
                <div style="font-size: 24px; font-weight: bold; color: #333;">{count}</div>
                <div style="font-size: 12px; color: #666;">{category}</div>
            </div>
            """

        return category_html

    @staticmethod
    def generate_remediation_section(audit_report: AuditReport) -> str:
        """Generate remediation guidance section.

        Args:
            audit_report: Audit report.

        Returns:
            HTML for remediation section.
        """
        all_findings = audit_report.org_data.findings + [
            f for r in audit_report.repos_data for f in r.findings
        ]

        # Prioritize by risk level
        from .config import RISK_LEVEL_ORDER

        sorted_findings = sorted(
            all_findings, key=lambda f: RISK_LEVEL_ORDER.get(f.risk_level, 999)
        )

        remediation_html = ""
        seen = set()

        for finding in sorted_findings:
            key = (finding.title, finding.risk_level.value)
            if key not in seen and finding.remediation:
                risk_color = {
                    "CRITICAL": "#ff6b6b",
                    "HIGH": "#ff922b",
                    "MEDIUM": "#ffd43b",
                    "LOW": "#74c0fc",
                    "INFO": "#b4dbff",
                }.get(finding.risk_level.value, "#999")

                remediation_html += f"""
                <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid {risk_color}; background: #f9f9f9;">
                    <div style="font-weight: bold; color: {risk_color}; margin-bottom: 5px;">
                        [{finding.risk_level.value}] {finding.title}
                    </div>
                    <div style="color: #666; font-size: 14px; margin-bottom: 10px;">
                        {finding.description}
                    </div>
                    <div style="color: #333; margin-bottom: 5px;">
                        <strong>Remediation:</strong> {finding.remediation}
                    </div>
                    {'<div style="color: #777; font-size: 12px;">Template: ' + finding.template_url + '</div>' if finding.template_url else ''}
                </div>
                """
                seen.add(key)

        return remediation_html

    @staticmethod
    def generate_executive_summary(
        audit_report: AuditReport, filepath: Path | str | None = None
    ) -> str:
        """Generate executive summary text.

        Args:
            audit_report: Audit report.
            filepath: Optional output file path.

        Returns:
            Executive summary text.
        """
        summary = audit_report.summary
        lines = [
            "=" * 80,
            "GITHUB ORGANIZATION AUDIT - EXECUTIVE SUMMARY",
            "=" * 80,
            "",
            f"Organization: {summary.organization}",
            f"Scan Date: {summary.timestamp.isoformat()}",
            f"Duration: {summary.scan_duration_seconds:.2f} seconds",
            "",
            "FINDINGS SUMMARY",
            "-" * 80,
            f"Total Findings: {summary.total_findings}",
            f"  Critical: {summary.critical}",
            f"  High:     {summary.high}",
            f"  Medium:   {summary.medium}",
            f"  Low:      {summary.low}",
            f"  Info:     {summary.info}",
            "",
            "COMPLIANCE METRICS",
            "-" * 80,
            f"Compliance Score: {summary.compliance_score:.1f}%",
            f"Repositories Audited: {summary.repos_audited}",
            f"Members Audited: {summary.members_audited}",
            "",
            "NEXT STEPS",
            "-" * 80,
            "1. Review detailed-report.json for complete findings",
            "2. View audit-report.html for visual dashboard",
            "3. Follow remediation-plan.md for prioritized actions",
            "",
            "=" * 80,
        ]

        text = "\n".join(lines)

        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(text)

        return text

    @staticmethod
    def generate_remediation_plan(
        analyzer: SecurityAnalyzer, filepath: Path | str | None = None
    ) -> str:
        """Generate remediation plan markdown.

        Args:
            analyzer: Security analyzer.
            filepath: Optional output file path.

        Returns:
            Remediation plan markdown.
        """
        lines = [
            "# GitHub Organization Audit - Remediation Plan",
            "",
            "## Priority Actions",
            "",
        ]

        priorities = analyzer.get_remediation_priorities()
        for priority in priorities:
            lines.append(f"### {priority.priority}. [{priority.risk_level.value}] {priority.action}")
            lines.append("")
            if priority.template_available:
                lines.append(f"**Template Available**: {priority.template_url}")
                lines.append("")
            lines.append(f"**Affected Items**: {priority.affected_items_count}")
            lines.append("")

        lines.append("## Implementation Timeline")
        lines.append("")
        lines.append("- **Critical**: Implement immediately")
        lines.append("- **High**: Implement within 1-2 weeks")
        lines.append("- **Medium**: Implement within 1 month")
        lines.append("- **Low**: Consider implementing")
        lines.append("")

        text = "\n".join(lines)

        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(text)

        return text

    @staticmethod
    def generate_html(
        audit_report: AuditReport, filepath: Path | str | None = None
    ) -> str:
        """Generate HTML report.

        Args:
            audit_report: Audit report.
            filepath: Optional output file path.

        Returns:
            HTML report.
        """
        summary = audit_report.summary
        org = audit_report.org_data

        # Build findings table rows
        findings_html = ""
        for finding in sorted(
            audit_report.org_data.findings + [f for r in audit_report.repos_data for f in r.findings],
            key=lambda f: f.risk_level.score,
        ):
            findings_html += f"""
            <tr>
                <td><span class="badge badge-{finding.risk_level.value.lower()}">{finding.risk_level.value}</span></td>
                <td>{finding.category.value}</td>
                <td>{finding.title}</td>
                <td>{', '.join(finding.affected_items[:3])}{' ...' if len(finding.affected_items) > 3 else ''}</td>
            </tr>
            """

        # Build repository summary
        repos_html = ""
        for repo in audit_report.repos_data:
            findings_count = len(repo.findings)
            repos_html += f"""
            <tr>
                <td>{repo.name}</td>
                <td><span class="badge badge-{repo.visibility.lower()}">{repo.visibility}</span></td>
                <td>{repo.default_branch}</td>
                <td>{"✓" if repo.branch_protection else "✗"}</td>
                <td>{"✓" if repo.has_secret_scanning else "✗"}</td>
                <td>{findings_count}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Audit Report - {org.login}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        h2 {{
            font-size: 1.8em;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .metric {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-critical {{ background: #ff6b6b; color: white; }}
        .badge-high {{ background: #ff922b; color: white; }}
        .badge-medium {{ background: #ffd43b; color: #333; }}
        .badge-low {{ background: #74c0fc; color: white; }}
        .badge-info {{ background: #b4dbff; color: #333; }}
        .badge-public {{ background: #ff6b6b; color: white; }}
        .badge-private {{ background: #51cf66; color: white; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .score-critical {{ color: #ff6b6b; }}
        .score-high {{ color: #ff922b; }}
        .score-medium {{ color: #ffd43b; }}
        .score-low {{ color: #74c0fc; }}
        footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>GitHub Organization Audit Report</h1>
            <p style="font-size: 1.1em; margin-bottom: 10px;">Organization: <strong>{org.login}</strong></p>
            <p>Scan Date: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </header>

        <h2>📊 Summary</h2>
        <div class="metadata">
            <div class="metric">
                <div class="metric-label">Compliance Score</div>
                <div class="metric-value" style="color: {'#51cf66' if summary.compliance_score >= 80 else '#ff922b' if summary.compliance_score >= 60 else '#ff6b6b'};">
                    {summary.compliance_score:.1f}%
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Findings</div>
                <div class="metric-value">{summary.total_findings}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Critical Issues</div>
                <div class="metric-value score-critical">{summary.critical}</div>
            </div>
            <div class="metric">
                <div class="metric-label">High Priority</div>
                <div class="metric-value score-high">{summary.high}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Repositories</div>
                <div class="metric-value">{summary.repos_audited}</div>
            </div>
        </div>

        <h2>🔍 Findings by Risk Level</h2>
        <table>
            <thead>
                <tr>
                    <th>Risk Level</th>
                    <th>Category</th>
                    <th>Title</th>
                    <th>Affected Items</th>
                </tr>
            </thead>
            <tbody>
                {findings_html}
            </tbody>
        </table>

        <h2>📦 Repository Security Posture</h2>
        <table>
            <thead>
                <tr>
                    <th>Repository</th>
                    <th>Visibility</th>
                    <th>Default Branch</th>
                    <th>Branch Protection</th>
                    <th>Secret Scanning</th>
                    <th>Findings</th>
                </tr>
            </thead>
            <tbody>
                {repos_html}
            </tbody>
        </table>

        <h2>🔧 Remediation Roadmap</h2>
        <p style="color: #666; margin-bottom: 20px;">Follow these actions to improve your security posture, prioritized by risk level:</p>
        {ReportGenerator.generate_remediation_section(audit_report)}

        <h2>📊 Findings by Category</h2>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);">
            {ReportGenerator.generate_category_breakdown(audit_report)}
        </div>

        <footer>
            <p>Generated by <strong>GitHub Audit Framework v2.0.0</strong></p>
            <p>Scan completed in {summary.scan_duration_seconds:.2f} seconds</p>
        </footer>
    </div>
</body>
</html>
"""

        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(html)

        return html
