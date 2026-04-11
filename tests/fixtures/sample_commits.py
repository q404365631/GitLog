"""Reusable fake commit data for tests."""
from __future__ import annotations

from gitlog.core.models import Commit, CommitType

CONVENTIONAL_COMMITS: list[Commit] = [
    Commit(
        sha="aabbcc1",
        message="feat: add dark mode support",
        author="Alice",
        date="2024-01-15",
        commit_type=CommitType.FEAT,
    ),
    Commit(
        sha="aabbcc2",
        message="fix(auth): resolve token expiry race condition",
        author="Bob",
        date="2024-01-14",
        commit_type=CommitType.FIX,
    ),
    Commit(
        sha="aabbcc3",
        message="perf: cache database queries",
        author="Carol",
        date="2024-01-13",
        commit_type=CommitType.PERF,
    ),
    Commit(
        sha="aabbcc4",
        message="chore(deps): bump requests from 2.28 to 2.31",
        author="Dependabot",
        date="2024-01-12",
        commit_type=CommitType.CHORE,
    ),
    Commit(
        sha="aabbcc5",
        message="feat!: redesign public API (BREAKING CHANGE: removed v1 endpoints)",
        author="Alice",
        date="2024-01-11",
        commit_type=CommitType.BREAKING,
    ),
]

NON_CONVENTIONAL_COMMITS: list[Commit] = [
    Commit(
        sha="ddee001",
        message="Fixed the thing that was broken",
        author="Dave",
        date="2024-01-10",
    ),
    Commit(
        sha="ddee002",
        message="Added cool new feature for users",
        author="Eve",
        date="2024-01-09",
    ),
    Commit(
        sha="ddee003",
        message="Update docs",
        author="Frank",
        date="2024-01-08",
    ),
]

ALL_COMMITS = CONVENTIONAL_COMMITS + NON_CONVENTIONAL_COMMITS
