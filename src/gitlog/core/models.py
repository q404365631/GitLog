"""Pydantic v2 data models for gitlog."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CommitType(str, Enum):
    """Semantic commit type categories."""

    FEAT = "feat"
    FIX = "fix"
    PERF = "perf"
    REFACTOR = "refactor"
    DOCS = "docs"
    CHORE = "chore"
    BREAKING = "breaking"
    MISC = "misc"


class Author(BaseModel):
    """Commit author information."""

    name: str
    email: str


class Commit(BaseModel):
    """A single git commit."""

    sha: str
    short_sha: str
    message: str
    subject: str = ""
    body: str = ""
    author: Author
    timestamp: datetime
    commit_type: CommitType = CommitType.MISC
    scope: Optional[str] = None  # noqa: UP007
    is_breaking: bool = False
    pr_number: Optional[int] = None  # noqa: UP007
    issue_refs: list[int] = Field(default_factory=list)
    co_authors: list[Author] = Field(default_factory=list)


class Tag(BaseModel):
    """A git version tag."""

    name: str
    sha: str
    date: Optional[datetime] = None  # noqa: UP007


class ChangelogEntry(BaseModel):
    """Changelog content for a single version."""

    version: str
    date: Optional[datetime] = None  # noqa: UP007
    breaking_changes: list[Commit] = Field(default_factory=list)
    features: list[Commit] = Field(default_factory=list)
    fixes: list[Commit] = Field(default_factory=list)
    performance: list[Commit] = Field(default_factory=list)
    refactors: list[Commit] = Field(default_factory=list)
    docs: list[Commit] = Field(default_factory=list)
    misc: list[Commit] = Field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True if entry has no commits."""
        return not any([
            self.breaking_changes, self.features, self.fixes,
            self.performance, self.refactors, self.docs, self.misc,
        ])


class Changelog(BaseModel):
    """Complete changelog with all version entries."""

    project_name: str = ""
    entries: list[ChangelogEntry] = Field(default_factory=list)
    unreleased: Optional[ChangelogEntry] = None  # noqa: UP007
