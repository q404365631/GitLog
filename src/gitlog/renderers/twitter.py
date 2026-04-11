"""Twitter/X release announcement renderer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gitlog.core.models import ChangelogEntry, CommitType

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig


class TwitterRenderer:
    """Generate a tweet-length release announcement.

    Args:
        config: GitlogConfig instance.
    """

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config

    def render(self, entry: ChangelogEntry) -> str:
        """Create a tweet draft from a ChangelogEntry.

        Args:
            entry: The version entry to summarise.

        Returns:
            Tweet-length string.
        """
        project = self._config.project_name or self._config.project_description or "Our project"
        version = "" if entry.version == "Unreleased" else f" {entry.version}"

        highlights: list[str] = []
        feats = entry.groups.get(CommitType.FEAT, [])
        fixes = entry.groups.get(CommitType.FIX, [])
        breaking = entry.groups.get(CommitType.BREAKING, [])

        if feats:
            first = (feats[0].subject or "").split(":")[-1].strip()
            highlights.append(
                f"\u2728 {len(feats)} new feature{'s' if len(feats) > 1 else ''}"
                + (f" (incl. {first})" if first else "")
            )
        if fixes:
            highlights.append(f"\U0001f41b {len(fixes)} bug fix{'es' if len(fixes) > 1 else ''}")
        if breaking:
            highlights.append("\u26a0\ufe0f Breaking changes — see CHANGELOG")

        lines = [f"\U0001f680 {project}{version} is out!"]
        lines.extend(highlights[:3])
        if self._config.github.repo:
            lines.append(f"\n\U0001f4e6 https://github.com/{self._config.github.repo}")
        lines.append("\n#opensource #devtools #changelog")
        return "\n".join(lines)
