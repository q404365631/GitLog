"""Shared pytest fixtures and helpers."""
from __future__ import annotations

from datetime import datetime, timezone

from gitlog.core.models import Author, Changelog, ChangelogEntry, Commit, CommitType


def make_commit(
    *,
    sha: str = "a" * 40,
    short_sha: str = "aaaaaaa",
    subject: str = "feat: test commit",
    body: str = "",
    author_name: str = "Alice",
    author_email: str = "alice@example.com",
    commit_type: CommitType = CommitType.MISC,
    pr_number: int | None = None,
    scope: str | None = None,
) -> Commit:
    """Create a Commit instance for testing."""
    return Commit(
        sha=sha,
        short_sha=short_sha,
        message=f"{subject}\n{body}".strip(),
        subject=subject,
        body=body,
        author=Author(name=author_name, email=author_email),
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        commit_type=commit_type,
        scope=scope,
        pr_number=pr_number,
    )


def make_entry(
    version: str = "v1.0.0",
    *,
    include_feat: bool = True,
    include_fix: bool = True,
) -> ChangelogEntry:
    """Create a ChangelogEntry with sample commits."""
    groups: dict[CommitType, list[Commit]] = {}
    if include_feat:
        groups[CommitType.FEAT] = [
            make_commit(subject="feat: add dark mode", sha="f" * 40, short_sha="fffffff"),
        ]
    if include_fix:
        groups[CommitType.FIX] = [
            make_commit(subject="fix: resolve crash", sha="e" * 40, short_sha="eeeeeee"),
        ]
    return ChangelogEntry(version=version, groups=groups)
