"""Tests for GitLogParser (uses a real temporary git repo)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gitlog.core.git import GitLogParser
from gitlog.exceptions import GitError


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Create a minimal real git repository with a few commits."""
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=tmp_path, check=True, capture_output=True)

    for i, msg in enumerate(
        ["feat: initial commit", "fix: resolve startup crash", "chore: update deps"]
    ):
        f = tmp_path / f"file{i}.txt"
        f.write_text(f"content {i}")
        subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=tmp_path, check=True, capture_output=True)

    return tmp_path


class TestGitLogParser:
    def test_get_commits_returns_list(self, git_repo: Path) -> None:
        parser = GitLogParser(repo_path=git_repo)
        commits = parser.get_commits()
        assert len(commits) == 3

    def test_commit_fields_populated(self, git_repo: Path) -> None:
        parser = GitLogParser(repo_path=git_repo)
        commits = parser.get_commits()
        c = commits[0]
        assert c.sha and len(c.sha) == 40
        assert c.short_sha
        assert c.author.name == "Tester"
        assert c.timestamp is not None

    def test_conventional_commits_classified(self, git_repo: Path) -> None:
        from gitlog.core.models import CommitType
        parser = GitLogParser(repo_path=git_repo)
        commits = parser.get_commits()
        subjects = {c.subject: c.commit_type for c in commits}
        assert subjects.get("feat: initial commit") == CommitType.FEAT
        assert subjects.get("fix: resolve startup crash") == CommitType.FIX

    def test_invalid_repo_raises(self, tmp_path: Path) -> None:
        with pytest.raises(GitError):
            GitLogParser(repo_path=tmp_path)

    def test_get_tags_empty(self, git_repo: Path) -> None:
        parser = GitLogParser(repo_path=git_repo)
        assert parser.get_tags() == []

    def test_detect_languages(self, git_repo: Path) -> None:
        # .txt files won't match any language, should return empty
        parser = GitLogParser(repo_path=git_repo)
        langs = parser.detect_languages()
        assert isinstance(langs, list)
