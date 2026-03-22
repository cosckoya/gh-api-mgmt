"""Template interpolation and rendering engine.

Supports:
- Variable substitution: ${VAR}, ${ORG}, ${REPO}
- Conditionals: if: "condition"
- Loops and iterations
- Jinja2 templates
"""

import json
import re
from pathlib import Path
from typing import Any

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    Template = None  # type: ignore
    Environment = None  # type: ignore


class TemplateError(Exception):
    """Template rendering error."""

    pass


class SimpleTemplateEngine:
    """Simple template interpolation engine for basic variable substitution."""

    @staticmethod
    def interpolate(text: str, context: dict[str, Any]) -> str:
        """Interpolate variables in text.

        Supports: ${VAR}, ${ORG.sub}, ${REPO}

        Args:
            text: Text with ${VAR} placeholders.
            context: Dictionary of variables.

        Returns:
            Interpolated text.
        """
        result = text

        # Replace ${VAR} with context values
        for key, value in context.items():
            pattern = r"\$\{" + re.escape(key) + r"\}"
            result = re.sub(pattern, str(value), result)

        # Handle nested keys: ${SECTION.KEY}
        pattern = r"\$\{(\w+)\.(\w+)\}"

        def replace_nested(match: re.Match[str]) -> str:
            section = match.group(1)
            key = match.group(2)
            if section in context and isinstance(context[section], dict):
                return str(context[section].get(key, match.group(0)))
            return match.group(0)

        result = re.sub(pattern, replace_nested, result)

        return result

    @staticmethod
    def render_json(json_text: str, context: dict[str, Any]) -> dict[str, Any]:
        """Render JSON template with variable substitution.

        Args:
            json_text: JSON string with ${VAR} placeholders.
            context: Dictionary of variables.

        Returns:
            Parsed JSON dictionary.

        Raises:
            TemplateError: If interpolation or JSON parsing fails.
        """
        try:
            interpolated = SimpleTemplateEngine.interpolate(json_text, context)
            return json.loads(interpolated)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON after interpolation: {e}") from e


class Jinja2TemplateEngine:
    """Jinja2-based template rendering for advanced features."""

    def __init__(self, template_dir: Path | str | None = None) -> None:
        """Initialize Jinja2 engine.

        Args:
            template_dir: Directory containing Jinja2 templates.
        """
        if Environment is None:
            raise TemplateError("Jinja2 not installed. Install with: pip install jinja2")

        self.template_dir = Path(template_dir) if template_dir else Path.cwd()
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render_file(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template file.

        Args:
            template_name: Template filename.
            context: Rendering context.

        Returns:
            Rendered content.

        Raises:
            TemplateError: If template not found or rendering fails.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise TemplateError(f"Failed to render {template_name}: {e}") from e

    def render_string(self, template_text: str, context: dict[str, Any]) -> str:
        """Render a template string.

        Args:
            template_text: Jinja2 template text.
            context: Rendering context.

        Returns:
            Rendered content.

        Raises:
            TemplateError: If rendering fails.
        """
        try:
            if Template is None:
                raise TemplateError("Jinja2 not available")
            template = Template(template_text)
            return template.render(**context)
        except Exception as e:
            raise TemplateError(f"Failed to render template: {e}") from e


class TemplateLoader:
    """Loads and manages template files."""

    def __init__(self, template_dir: Path | str) -> None:
        """Initialize template loader.

        Args:
            template_dir: Root directory containing templates.
        """
        self.template_dir = Path(template_dir)
        self._cache: dict[str, str] = {}

    def load(self, path: str) -> str:
        """Load a template file.

        Args:
            path: Relative path to template file.

        Returns:
            Template content.

        Raises:
            TemplateError: If file not found.
        """
        if path in self._cache:
            return self._cache[path]

        full_path = self.template_dir / path
        if not full_path.exists():
            raise TemplateError(f"Template not found: {full_path}")

        with open(full_path) as f:
            content = f.read()

        self._cache[path] = content
        return content

    def load_json(self, path: str) -> dict[str, Any]:
        """Load and parse a JSON template.

        Args:
            path: Relative path to JSON template.

        Returns:
            Parsed JSON.

        Raises:
            TemplateError: If file not found or invalid JSON.
        """
        content = self.load(path)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON in {path}: {e}") from e

    def render(
        self, path: str, context: dict[str, Any], use_jinja2: bool = False
    ) -> str:
        """Load and render a template.

        Args:
            path: Relative path to template.
            context: Rendering context.
            use_jinja2: Use Jinja2 rendering if True, simple interpolation if False.

        Returns:
            Rendered content.

        Raises:
            TemplateError: If rendering fails.
        """
        content = self.load(path)

        if use_jinja2:
            engine = Jinja2TemplateEngine(self.template_dir)
            return engine.render_string(content, context)
        else:
            return SimpleTemplateEngine.interpolate(content, context)

    def render_json(
        self, path: str, context: dict[str, Any], use_jinja2: bool = False
    ) -> dict[str, Any]:
        """Load and render a JSON template.

        Args:
            path: Relative path to JSON template.
            context: Rendering context.
            use_jinja2: Use Jinja2 rendering.

        Returns:
            Rendered JSON as dictionary.

        Raises:
            TemplateError: If rendering fails.
        """
        rendered = self.render(path, context, use_jinja2=use_jinja2)
        try:
            return json.loads(rendered)
        except json.JSONDecodeError as e:
            raise TemplateError(f"Rendered JSON is invalid: {e}") from e
