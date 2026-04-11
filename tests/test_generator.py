"""Tests for the changelog generator."""
from __future__ import annotations

from gitlog.config import GitlogConfig
from gitlog.core.generator import ChangelogGenerator, _deduplicate
from gitlog.core.models import CommitType
from tests.conftest import make_commit


class TestDeduplicate:
    def test_exact_duplicates_removed(self) -> None:
        c1 = make_commit(subject="feat: add button")
        c2 = make_commit(subject="feat: add button", sha="abc000")
        result = _deduplicate([c1, c2])
        assert len(result) == 1

    def test_near_duplicates_removed(self) -> None:
        c1 = make_commit(subject="fix: resolve null pointer error in parser")
        c2 = make_commit(subject="fix: resolve null pointer error in parser  ", sha="abc001")
        result = _deduplicate([c1, c2])
        assert len(result) == 1

    def test_distinct_commits_kept(self) -> None:
        c1 = make_commit(subject="feat: dark mode")
        c2 = make_commit(subject="fix: login crash", sha="abc002")
        result = _deduplicate([c1, c2])
        assert len(result) == 2


class TestChangelogGenerator:
    def test_generate_no_tags(self) -> None:
        config = GitlogConfig(llm_provider="", model="")
        gen = ChangelogGenerator(config=config)
        commits = [
            make_commit(subject="feat: add search"),
            make_commit(subject="fix: crash on empty input", sha="fix001"),
        ]
        changelog = gen.generate(commits=commits, tags=[])
        assert len(changelog.entries) == 1
        entry = changelog.entries[0]
        assert entry.version == "Unreleased"
        assert CommitType.FEAT in entry.groups
        assert CommitType.FIX in entry.groups

    def test_exclude_patterns(self) -> None:
        config = GitlogConfig(llm_provider="", model="", exclude_patterns=[r"^Merge branch"])
        gen = ChangelogGenerator(config=config)
        commits = [
            make_commit(subject="feat: new feature"),
            make_commit(subject="Merge branch 'dev'", sha="merge01"),
        ]
        changelog = gen.generate(commits=commits, tags=[])
        entry = changelog.entries[0]
        all_commits = [c for cs in entry.groups.values() for c in cs]
        subjects = [c.subject for c in all_commits]
        assert "Merge branch 'dev'" not in subjects

    def test_max_per_group_respected(self) -> None:
        config = GitlogConfig(llm_provider="", model="", max_commits_per_group=2)
        gen = ChangelogGenerator(config=config)
        commits = [
            make_commit(subject=f"feat: feature {i}", sha=f"sha{i:03d}")
            for i in range(5)
        ]
        changelog = gen.generate(commits=commits, tags=[])
        entry = changelog.entries[0]
        assert len(entry.groups.get(CommitType.FEAT, [])) <= 2
