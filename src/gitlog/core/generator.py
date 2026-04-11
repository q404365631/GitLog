"""Changelog generation engine: group → classify → deduplicate → render."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import TYPE_CHECKING

from gitlog.core.classifier import CommitClassifier
from gitlog.core.git import GitLogParser
from gitlog.core.models import Changelog, ChangelogEntry, Commit, CommitType, Tag

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig

_CATEGORY_ORDER = [
    CommitType.BREAKING,
    CommitType.FEAT,
    CommitType.FIX,
    CommitType.PERF,
    CommitType.REFACTOR,
    CommitType.DOCS,
    CommitType.CHORE,
    CommitType.MISC,
]


def _edit_distance(a: str, b: str) -> int:
    """Compute Levenshtein distance between two strings (capped at 200 chars)."""
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
    """Remove near-duplicate commits using edit distance.

    Args:
        commits: List of commits to deduplicate.
        threshold: Max edit distance to consider two messages duplicates.

    Returns:
        Deduplicated list of commits.
    """
    seen: list[str] = []
    result: list[Commit] = []
    for commit in commits:
        msg = commit.message.strip()
        # strip conventional prefix for comparison
        cleaned = re.sub(r"^[a-z]+(?:\([^)]+\))?!?: ", "", msg, flags=re.IGNORECASE)
        is_dup = any(_edit_distance(cleaned, s) <= threshold for s in seen)
        if not is_dup:
            seen.append(cleaned)
            result.append(commit)
    return result


class ChangelogGenerator:
    """Main changelog generation orchestrator."""

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config
        self._parser = GitLogParser()
        self._classifier = CommitClassifier(config)

    def generate(
        self,
        since: str | None = None,
        until: str | None = None,
        paths: list[str] | None = None,
        commits: list["Commit"] | None = None,
    ) -> Changelog:
        """Generate a full Changelog object.

        Args:
            since: Restrict commits to those after this tag/date/hash.
            until: Restrict commits to those before this tag/date/hash.
            paths: Only consider commits touching these paths.

        Returns:
            A fully populated Changelog instance.
        """
        tags = self._parser.get_tags()
        if commits is None:
            all_commits = self._parser.get_commits(
                since=since, until=until, paths=paths
            )
        else:
            all_commits = commits
        all_commits = self._classifier.classify_all(all_commits)

        entries = self._build_entries(tags, all_commits)
        return Changelog(entries=entries)

    def generate_unreleased(self) -> ChangelogEntry:
        """Generate a ChangelogEntry for commits not yet tagged."""
        commits = self._parser.get_unreleased_commits()
        commits = self._classifier.classify_all(commits)
        return self._build_entry("Unreleased", None, commits)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_entries(
        self, tags: list[Tag], commits: list[Commit]
    ) -> list[ChangelogEntry]:
        """Partition commits into per-version ChangelogEntry objects."""
        if not tags:
            return [self._build_entry("Unreleased", None, commits)]

        # Map tag name → Tag for quick lookup
        tag_map = {t.name: t for t in tags}
        # sort tags newest-first by date
        sorted_tags = sorted(
            tags, key=lambda t: t.date or "", reverse=True
        )

        # Bucket commits by tag boundary
        boundaries: list[tuple[str, str | None, list[Commit]]] = []
        remaining = list(commits)

        for tag in sorted_tags:
            tag_commits = [
                c for c in remaining if c.tags and tag.name in c.tags
            ]
            other = [c for c in remaining if c not in tag_commits]
            # include commits up to this tag that haven't been assigned yet
            boundaries.append((tag.name, tag.date, tag_commits))
            remaining = other

        if remaining:
            boundaries.insert(0, ("Unreleased", None, remaining))

        return [
            self._build_entry(version, date, cmts)
            for version, date, cmts in boundaries
            if cmts
        ]

    def _build_entry(
        self,
        version: str,
        date: str | None,
        commits: list[Commit],
    ) -> ChangelogEntry:
        """Build a single ChangelogEntry from a list of commits."""
        # Exclude patterns from config
        filtered = [
            c
            for c in commits
            if not any(
                re.search(p, c.message) for p in self._config.exclude_patterns
            )
        ]
        deduped = _deduplicate(filtered)

        # Group by commit type
        by_type: dict[CommitType, list[Commit]] = defaultdict(list)
        for commit in deduped:
            by_type[commit.commit_type].append(commit)

        # Respect max_commits_per_group
        max_pg = self._config.max_commits_per_group
        groups = {
            ct: cmts[:max_pg] for ct, cmts in by_type.items() if cmts
        }

        return ChangelogEntry(
            version=version,
            date=date,
            groups=groups,
        )
