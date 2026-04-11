"""Changelog generation engine: group -> classify -> deduplicate -> render."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING

from gitlog.core.classifier import CommitClassifier
from gitlog.core.models import Changelog, ChangelogEntry, Commit, CommitType, Tag

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig


def _edit_distance(a: str, b: str) -> int:
    """Compute Levenshtein distance between two strings (capped at 200 chars).

    Args:
        a: First string.
        b: Second string.

    Returns:
        Integer edit distance.
    """
    a, b = a[:200], b[:200]
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(
                min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (0 if ca == cb else 1))
            )
        prev = curr
    return prev[-1]


def _deduplicate(commits: list[Commit], threshold: int = 10) -> list[Commit]:
    """Remove near-duplicate commits using edit distance on subjects.

    Args:
        commits: Input list.
        threshold: Max edit distance to consider duplicates.

    Returns:
        Deduplicated commit list.
    """
    seen: list[str] = []
    result: list[Commit] = []
    for commit in commits:
        msg = (commit.subject or commit.message).strip()
        cleaned = re.sub(r"^[a-z]+(?:\([^)]+\))?!?: ", "", msg, flags=re.IGNORECASE)
        if not any(_edit_distance(cleaned, s) <= threshold for s in seen):
            seen.append(cleaned)
            result.append(commit)
    return result


class ChangelogGenerator:
    """Orchestrates commit fetching, classification, grouping, and rendering.

    Args:
        config: Active GitlogConfig instance.
    """

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config
        self._classifier = CommitClassifier(config=config)

    def generate(
        self,
        since: str | None = None,
        until: str | None = None,
        paths: list[str] | None = None,
        commits: list[Commit] | None = None,
        tags: list[Tag] | None = None,
    ) -> Changelog:
        """Generate a full Changelog from git history or a provided commit list.

        Args:
            since: Start ref (tag / date / hash).
            until: End ref.
            paths: Restrict to these file paths.
            commits: Pre-fetched commits (skips git fetch).
            tags: Pre-fetched tags (skips git tag fetch).

        Returns:
            Populated Changelog object.
        """
        from gitlog.core.git import GitLogParser
        parser = GitLogParser()

        resolved_tags = tags if tags is not None else parser.get_tags()
        resolved_commits = (
            commits
            if commits is not None
            else parser.get_commits(since=since, until=until, paths=paths)
        )
        classified = self._classifier.classify_all(resolved_commits)
        entries = self._build_entries(resolved_tags, classified)
        return Changelog(entries=entries)

    def generate_unreleased(self) -> ChangelogEntry:
        """Build a ChangelogEntry for commits not yet tagged.

        Returns:
            ChangelogEntry labelled 'Unreleased'.
        """
        from gitlog.core.git import GitLogParser
        parser = GitLogParser()
        commits = parser.get_unreleased_commits()
        classified = self._classifier.classify_all(commits)
        return self._build_entry("Unreleased", None, classified)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _build_entries(
        self, tags: list[Tag], commits: list[Commit]
    ) -> list[ChangelogEntry]:
        """Partition commits into per-version ChangelogEntry objects.

        Args:
            tags: All repo tags, newest first.
            commits: Classified commits.

        Returns:
            List of ChangelogEntry objects.
        """
        if not tags:
            entry = self._build_entry("Unreleased", None, commits)
            return [entry] if not entry.is_empty() else []

        sorted_tags = sorted(tags, key=lambda t: (t.date or ""), reverse=True)
        remaining = list(commits)
        entries: list[ChangelogEntry] = []

        for tag in sorted_tags:
            tag_commits = [c for c in remaining if tag.name in (getattr(c, 'tags', None) or [])]
            remaining = [c for c in remaining if c not in tag_commits]
            if tag_commits:
                entries.append(self._build_entry(tag.name, str(tag.date) if tag.date else None, tag_commits))

        if remaining:
            e = self._build_entry("Unreleased", None, remaining)
            if not e.is_empty():
                entries.insert(0, e)

        return entries

    def _build_entry(
        self,
        version: str,
        date: str | None,
        commits: list[Commit],
    ) -> ChangelogEntry:
        """Build a single ChangelogEntry from commits.

        Args:
            version: Version label.
            date: ISO date string or None.
            commits: Commits for this version.

        Returns:
            Populated ChangelogEntry.
        """
        filtered = [
            c for c in commits
            if not any(re.search(p, c.message) for p in self._config.exclude_patterns)
        ]
        deduped = _deduplicate(filtered)

        max_pg = self._config.max_commits_per_group
        by_type: dict[CommitType, list[Commit]] = defaultdict(list)
        for commit in deduped:
            by_type[commit.commit_type].append(commit)

        groups = {ct: cmts[:max_pg] for ct, cmts in by_type.items() if cmts}
        return ChangelogEntry(version=version, date=date, groups=groups)
