"""JSON Schema validation utilities for configuration files."""

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import ValidationError, validate
except ImportError:
    # Graceful fallback if jsonschema not installed
    jsonschema = None  # type: ignore
    ValidationError = Exception  # type: ignore


class ConfigValidationError(Exception):
    """Configuration validation error."""

    pass


class SchemaValidator:
    """Validates JSON configurations against schemas."""

    def __init__(self, schema_dir: Path | str | None = None) -> None:
        """Initialize validator with schema directory.

        Args:
            schema_dir: Directory containing JSON schema files.
        """
        self.schema_dir = Path(schema_dir) if schema_dir else None
        self._schemas: dict[str, dict[str, Any]] = {}

    def load_schema(self, schema_name: str) -> dict[str, Any]:
        """Load a schema from file or cache.

        Args:
            schema_name: Schema name (without .json).

        Returns:
            Schema dictionary.

        Raises:
            ConfigValidationError: If schema file not found.
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]

        if not self.schema_dir:
            raise ConfigValidationError("Schema directory not configured")

        schema_path = self.schema_dir / f"{schema_name}.json"
        if not schema_path.exists():
            raise ConfigValidationError(f"Schema not found: {schema_path}")

        with open(schema_path) as f:
            schema = json.load(f)

        self._schemas[schema_name] = schema
        return schema

    def validate(
        self, config: dict[str, Any], schema: dict[str, Any] | str
    ) -> tuple[bool, list[str]]:
        """Validate configuration against schema.

        Args:
            config: Configuration dictionary to validate.
            schema: Schema dictionary or schema name string.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        if jsonschema is None:
            return True, []

        if isinstance(schema, str):
            try:
                schema = self.load_schema(schema)
            except ConfigValidationError as e:
                return False, [str(e)]

        errors: list[str] = []
        try:
            validate(instance=config, schema=schema)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error at {'.'.join(str(p) for p in e.path)}: {e.message}")
            return False, errors

    def validate_file(self, config_path: Path | str, schema_name: str) -> tuple[bool, list[str]]:
        """Validate a configuration file against a schema.

        Args:
            config_path: Path to configuration file.
            schema_name: Schema name to validate against.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except IOError as e:
            return False, [f"Cannot read file: {e}"]

        return self.validate(config, schema_name)


# Basic schema templates
ORG_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["organization"],
    "properties": {
        "organization": {"type": "string"},
        "settings": {"type": "object"},
        "enforcement": {"type": "object"},
    },
}

REPO_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["repository"],
    "properties": {
        "repository": {"type": "string"},
        "visibility": {"type": "string", "enum": ["public", "private"]},
        "protection": {"type": "object"},
        "policies": {"type": "array", "items": {"type": "string"}},
    },
}

MEMBER_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["username"],
    "properties": {
        "username": {"type": "string"},
        "role": {"type": "string"},
        "teams": {"type": "array", "items": {"type": "string"}},
    },
}
