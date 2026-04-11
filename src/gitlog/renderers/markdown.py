"""Keep-a-Changelog Markdown renderer."""
from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from gitlog.core.models import Changelog, ChangelogEntry, Commit, CommitType

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig

_SECTION_TITLES: dict[CommitType, str] = {
    CommitType.BREAKING: "\u26a0\ufe0f Breaking Changes",
    CommitType.FEAT:     "\u2728 Features",
    CommitType.FIX:      "\U0001f41b Bug Fixes",
    CommitType.PERF:     "\u26a1 Performance",
    CommitType.REFACTOR: "\u267b\ufe0f Refactors",
    CommitType.DOCS:     "\U0001f4dd Documentation",
    CommitType.CHORE:    "\U0001f527 Chores",
    CommitType.MISC:     "\U0001f4e6 Miscellaneous",
}

_TYPE_ORDER = [
    CommitType.BREAKING, CommitType.FEAT, CommitType.FIX, CommitType.PERF,
    CommitType.REFACTOR, CommitType.DOCS, CommitType.CHORE, CommitType.MISC,
]


class MarkdownRenderer:
    """Render a Changelog to Keep-a-Changelog Markdown.

    Args:
        config: GitlogConfig instance.
    """

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config

    def render(self, changelog: Changelog) -> str:
        """Render the full changelog.

        Args:
            changelog: Structured Changelog object.

        Returns:
            Markdown string.
        """
        lines: list[str] = [
            "# Changelog\n",
            "All notable changes are documented here.  ",
            "Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).\n",
        ]
        for entry in changelog.entries:
            if not entry.is_empty():
                lines.append(self._render_entry(entry))
        return "\n".join(lines)

    def _render_entry(self, entry: ChangelogEntry) -> str:
        """Render a single version section.

        Args:
            entry: ChangelogEntry to render.

        Returns:
            Markdown section string.
        """
        today = date.today().isoformat()
        date_label = entry.date or today
        is_unrel = entry.version == "Unreleased"
        header = f"## [Unreleased]\n" if is_unrel else f"## [{entry.version}] — {date_label}\n"
        parts = [header]

        for ct in _TYPE_ORDER:
            commits = entry.groups.get(ct, [])
            if commits:
                parts.append(f"\n### {_SECTION_TITLES[ct]}\n")
                for commit in commits:
                    parts.append(self._fmt(commit))

        return "\n".join(parts)

    def _fmt(self, commit: Commit) -> str:
        """Format a single commit as a list item.

        Args:
            commit: Commit object.

        Returns:
            Markdown list item string.
        """
        subject = commit.subject or commit.message.split("\n")[0]
        subject = re.sub(r"^\w+(\(.+\))?!?: ", "", subject)
        parts = [f"- {subject}"]

        github_repo = self._config.github.repo
        if commit.pr_number and github_repo:
            url = f"https://github.com/{github_repo}/pull/{commit.pr_number}"
            parts.append(f"([#{commit.pr_number}]({url}))")
        elif commit.pr_number:
            parts.append(f"(#{commit.pr_number})")

        if github_repo:
            sha_url = f"https://github.com/{github_repo}/commit/{commit.sha}"
            parts.append(f"[`{commit.short_sha}`]({sha_url})")
        else:
            parts.append(f"`{commit.short_sha}`")

        return " ".join(parts)
