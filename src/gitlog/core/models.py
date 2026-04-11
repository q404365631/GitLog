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
    """Commit author."""

    name: str
    email: str


class Commit(BaseModel):
    """A single parsed git commit."""

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
    tags: list[str] = Field(default_factory=list)


class Tag(BaseModel):
    """A git version tag."""

    name: str
    sha: str
    date: Optional[datetime] = None  # noqa: UP007


class ChangelogEntry(BaseModel):
    """Changelog content for one version."""

    version: str
    date: Optional[str] = None  # noqa: UP007
    groups: dict[CommitType, list[Commit]] = Field(default_factory=dict)

    def is_empty(self) -> bool:
        """Return True if entry has no commits.

        Returns:
            Boolean indicating emptiness.
        """
        return not any(self.groups.values())


class Changelog(BaseModel):
    """Complete changelog containing all version entries."""

    project_name: str = ""
    entries: list[ChangelogEntry] = Field(default_factory=list)
