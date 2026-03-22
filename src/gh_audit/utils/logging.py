"""Structured logging utilities replacing print statements."""

import logging
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """Structured logger with JSON-friendly output."""

    def __init__(self, name: str, log_file: Path | str | None = None) -> None:
        """Initialize structured logger.

        Args:
            name: Logger name.
            log_file: Optional file path to write logs.
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "[%(levelname)s] %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            file_path = Path(log_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log("DEBUG", message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log("INFO", message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log("WARNING", message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._log("ERROR", message, kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._log("CRITICAL", message, kwargs)

    def _log(self, level: str, message: str, context: dict[str, Any]) -> None:
        """Internal log method with context."""
        if context:
            context_str = " | " + " | ".join(
                f"{k}={v}" for k, v in context.items()
            )
        else:
            context_str = ""

        full_message = f"{message}{context_str}"

        getattr(self.logger, level.lower())(full_message)


class AuditLogger(StructuredLogger):
    """Specialized logger for audit operations."""

    def audit_start(self, org: str) -> None:
        """Log audit start."""
        self.info("Starting audit", organization=org, timestamp=datetime.now().isoformat())

    def audit_complete(self, org: str, duration: float, findings: int) -> None:
        """Log audit completion."""
        self.info(
            "Audit complete",
            organization=org,
            duration_seconds=f"{duration:.2f}",
            findings=findings,
        )

    def check_passed(self, check_name: str) -> None:
        """Log passed check."""
        self.debug(f"✓ {check_name}")

    def check_failed(self, check_name: str, reason: str = "") -> None:
        """Log failed check."""
        self.info(f"✗ {check_name}", reason=reason)

    def finding(
        self,
        title: str,
        risk_level: str,
        affected_items: list[str] | None = None,
    ) -> None:
        """Log a finding."""
        items_str = ", ".join(affected_items[:3]) if affected_items else "N/A"
        self.warning(
            f"[{risk_level}] {title}",
            affected_items=items_str,
        )


class RemediationLogger(StructuredLogger):
    """Specialized logger for remediation operations."""

    def remediation_start(self, org: str, dry_run: bool = False) -> None:
        """Log remediation start."""
        mode = "DRY_RUN" if dry_run else "APPLY"
        self.info("Starting remediation", organization=org, mode=mode)

    def action_applied(
        self, action_id: str, action_name: str, repos: list[str] | None = None
    ) -> None:
        """Log successful action."""
        repos_str = ", ".join(repos) if repos else "N/A"
        self.info(f"✓ {action_name}", action_id=action_id, repositories=repos_str)

    def action_failed(
        self, action_id: str, action_name: str, error: str
    ) -> None:
        """Log failed action."""
        self.error(f"✗ {action_name}", action_id=action_id, error=error)

    def remediation_summary(
        self,
        total: int,
        successful: int,
        failed: int,
        skipped: int,
    ) -> None:
        """Log remediation summary."""
        success_rate = (successful / total * 100) if total > 0 else 0
        self.info(
            "Remediation summary",
            total=total,
            successful=successful,
            failed=failed,
            skipped=skipped,
            success_rate=f"{success_rate:.1f}%",
        )


# Global logger instances
audit_logger = AuditLogger("gh_audit.audit")
remediation_logger = RemediationLogger("gh_audit.remediation")
api_logger = StructuredLogger("gh_audit.api")


def get_logger(name: str) -> StructuredLogger:
    """Get or create a logger by name."""
    return StructuredLogger(name)
