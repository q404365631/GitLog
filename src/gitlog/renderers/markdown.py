"""Keep-a-Changelog Markdown renderer."""
from __future__ import annotations

from gitlog.core.models import Changelog, ChangelogEntry, CommitType

_SECTION_TITLES: dict[CommitType, str] = {
    CommitType.BREAKING: "⚠️ Breaking Changes",
    CommitType.FEAT: "✨ Features",
    CommitType.FIX: "🐛 Bug Fixes",
    CommitType.PERF: "⚡ Performance",
    CommitType.REFACTOR: "♻️ Refactoring",
    CommitType.DOCS: "📝 Documentation",
    CommitType.CHORE: "🔧 Chores",
    CommitType.MISC: "📦 Miscellaneous",
}


class MarkdownRenderer:
    """Renders a Changelog to Keep-a-Changelog Markdown format."""

    def __init__(self, github_repo: str | None = None) -> None:
        self._github_repo = github_repo

    def render(self, changelog: Changelog) -> str:
        """Render a full Changelog to a Markdown string.

        Args:
            changelog: The Changelog to render.

        Returns:
            A Markdown-formatted string.
        """
        lines: list[str] = [
            "# Changelog\n",
            "All notable changes to this project will be documented in this file.\n",
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),",
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n",
        ]
        for entry in changelog.entries:
            lines.append(self._render_entry(entry))
        return "\n".join(lines)

    def render_entry(self, entry: ChangelogEntry) -> str:
        """Render a single ChangelogEntry section.

        Args:
            entry: The entry to render.

        Returns:
            Markdown string for one version block.
        """
        return self._render_entry(entry)

    def _render_entry(self, entry: ChangelogEntry) -> str:
        date_str = f" - {entry.date}" if entry.date else ""
        lines: list[str] = [f"## [{entry.version}]{date_str}\n"]

        from gitlog.core.models import _CATEGORY_ORDER  # type: ignore[attr-defined]

        for ct in _CATEGORY_ORDER if hasattr(
            __import__("gitlog.core.models", fromlist=["_CATEGORY_ORDER"]),
            "_CATEGORY_ORDER",
        ) else list(CommitType):
            commits = entry.groups.get(ct, [])
            if not commits:
                continue
            lines.append(f"### {_SECTION_TITLES.get(ct, ct.value)}\n")
            for commit in commits:
                sha_link = self._sha_link(commit.sha)
                lines.append(f"- {commit.message} {sha_link}".rstrip())
            lines.append("")

        return "\n".join(lines)

    def _sha_link(self, sha: str) -> str:
        if self._github_repo:
            url = f"https://github.com/{self._github_repo}/commit/{sha}"
            return f"([`{sha[:7]}`]({url}))"
        return f"(`{sha[:7]}`)"
