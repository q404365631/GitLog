"""HTML renderer using Jinja2 templates."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from gitlog.core.models import Changelog, CommitType

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_CATEGORY_COLORS: dict[CommitType, str] = {
    CommitType.BREAKING: "#f97316",
    CommitType.FEAT: "#3b82f6",
    CommitType.FIX: "#ef4444",
    CommitType.PERF: "#8b5cf6",
    CommitType.REFACTOR: "#06b6d4",
    CommitType.DOCS: "#10b981",
    CommitType.CHORE: "#6b7280",
    CommitType.MISC: "#9ca3af",
}


class HtmlRenderer:
    """Renders a Changelog to a self-contained HTML file."""

    def __init__(self, github_repo: str | None = None) -> None:
        self._github_repo = github_repo
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )

    def render(self, changelog: Changelog) -> str:
        """Render a Changelog to HTML.

        Args:
            changelog: The Changelog to render.

        Returns:
            A self-contained HTML string.
        """
        template = self._env.get_template("report.html.j2")
        return template.render(
            changelog=changelog,
            github_repo=self._github_repo,
            category_colors=_CATEGORY_COLORS,
            CommitType=CommitType,
        )
