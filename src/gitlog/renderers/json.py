"""JSON renderer for machine-readable changelog output."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from gitlog.core.models import Changelog, ChangelogEntry, Commit

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig


class JsonRenderer:
    """Render a Changelog to pretty-printed JSON.

    Args:
        config: GitlogConfig instance.
    """

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config

    def render(self, changelog: Changelog) -> str:
        """Serialize changelog to JSON string.

        Args:
            changelog: Structured Changelog.

        Returns:
            JSON string.
        """
        data: dict[str, object] = {
            "project": changelog.project_name,
            "entries": [self._entry(e) for e in changelog.entries if not e.is_empty()],
        }
        return json.dumps(data, indent=2, default=str)

    def _entry(self, entry: ChangelogEntry) -> dict[str, object]:
        """Serialize a ChangelogEntry.

        Args:
            entry: Entry to serialize.

        Returns:
            Dictionary.
        """
        result: dict[str, object] = {"version": entry.version, "date": entry.date, "groups": {}}
        groups: dict[str, list[dict[str, object]]] = {}
        for ct, commits in entry.groups.items():
            groups[ct.value] = [self._commit(c) for c in commits]
        result["groups"] = groups
        return result

    def _commit(self, commit: Commit) -> dict[str, object]:
        """Serialize a single Commit.

        Args:
            commit: Commit to serialize.

        Returns:
            Flat dictionary.
        """
        return {
            "sha": commit.sha,
            "short_sha": commit.short_sha,
            "subject": commit.subject or commit.message.split("\n")[0],
            "author": commit.author.name,
            "timestamp": commit.timestamp.isoformat(),
            "type": commit.commit_type.value,
            "scope": commit.scope,
            "is_breaking": commit.is_breaking,
            "pr_number": commit.pr_number,
            "issue_refs": commit.issue_refs,
        }
