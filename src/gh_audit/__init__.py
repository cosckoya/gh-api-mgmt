"""GitHub Organization Audit Framework v2.0.

Professional framework for auditing GitHub organizations against
GitHub best practices, community standards, and compliance requirements.

Modules:
    - config: Enums and configuration constants
    - models: Data models and structures
    - utils: Utility modules (API, validation, templates, logging)
    - collector: GitHub data collection
    - analyzer: Security analysis and scoring
    - reporter: Report generation (JSON, HTML, text)
    - remediator: Configuration application via GitHub API
    - cli: Command-line interface
"""

__version__ = "2.0.0"
__author__ = "DevSecOps Team"

from .analyzer import ComplianceScore, RemediationEffortCalculator, RiskMatrix, SecurityAnalyzer
from .auditor import AuditCheck, DeepDiveAuditor
from .config import Category, RiskLevel
from .configurator import (
    BaseConfigurator,
    Configurator,
    ConfigChange,
    MemberConfigurator,
    OrgConfigurator,
    RepoConfigurator,
    TeamConfigurator,
)
from .models import (
    AuditSummary,
    ConfigChange,
    ConfigResult,
    Finding,
    MemberData,
    OrganizationData,
    RemediationPriority,
    RepositoryData,
    TeamData,
    ValidationError,
)
from .utils import (
    AuditLogger,
    ConfigValidationError,
    GitHubAPI,
    GitHubAPIError,
    Jinja2TemplateEngine,
    RemediationLogger,
    SchemaValidator,
    SimpleTemplateEngine,
    StructuredLogger,
    TemplateError,
    TemplateLoader,
    audit_logger,
    get_logger,
)

__all__ = [
    # Config
    "RiskLevel",
    "Category",
    # Models
    "Finding",
    "OrganizationData",
    "RepositoryData",
    "TeamData",
    "MemberData",
    "RemediationPriority",
    "AuditSummary",
    "ConfigChange",
    "ValidationError",
    "ConfigResult",
    # Core Classes - Auditing
    "DeepDiveAuditor",
    "AuditCheck",
    "SecurityAnalyzer",
    "ComplianceScore",
    "RiskMatrix",
    "RemediationEffortCalculator",
    # Core Classes - Configuration
    "Configurator",
    "BaseConfigurator",
    "OrgConfigurator",
    "RepoConfigurator",
    "MemberConfigurator",
    "TeamConfigurator",
    # Utils - API
    "GitHubAPI",
    "GitHubAPIError",
    # Utils - Validation
    "SchemaValidator",
    "ConfigValidationError",
    # Utils - Templates
    "SimpleTemplateEngine",
    "Jinja2TemplateEngine",
    "TemplateLoader",
    "TemplateError",
    # Utils - Logging
    "StructuredLogger",
    "AuditLogger",
    "RemediationLogger",
    "audit_logger",
    "get_logger",
]
