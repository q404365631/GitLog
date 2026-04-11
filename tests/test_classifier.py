"""Tests for the commit classifier module."""
from __future__ import annotations

import pytest

from gitlog.core.classifier import CommitClassifier, RuleClassifier, _rule_classify
from gitlog.core.models import CommitType
from gitlog.config import GitlogConfig
from tests.conftest import make_commit


class TestRuleClassifier:
    def test_feat(self) -> None:
        assert _rule_classify("feat: add dark mode") == "feat"

    def test_feat_scope(self) -> None:
        assert _rule_classify("feat(ui): add dark mode") == "feat"

    def test_fix(self) -> None:
        assert _rule_classify("fix: resolve null pointer") == "fix"

    def test_breaking_bang(self) -> None:
        assert _rule_classify("feat!: drop Python 3.9") == "breaking"

    def test_chore(self) -> None:
        assert _rule_classify("chore: update deps") == "chore"

    def test_ci(self) -> None:
        assert _rule_classify("ci: add release workflow") == "chore"

    def test_docs(self) -> None:
        assert _rule_classify("docs: update README") == "docs"

    def test_perf(self) -> None:
        assert _rule_classify("perf: cache db queries") == "perf"

    def test_refactor(self) -> None:
        assert _rule_classify("refactor: extract helper") == "refactor"

    def test_misc_fallback(self) -> None:
        assert _rule_classify("random commit message") == "misc"

    def test_case_insensitive(self) -> None:
        assert _rule_classify("Feat: new thing") == "feat"


class TestRuleClassifierClass:
    def test_is_excluded(self) -> None:
        rc = RuleClassifier(exclude_patterns=[r"^Merge branch"])
        assert rc.is_excluded("Merge branch 'main' into dev")
        assert not rc.is_excluded("feat: add thing")

    def test_classify_method(self) -> None:
        rc = RuleClassifier()
        assert rc.classify("fix: crash on startup") == "fix"


class TestCommitClassifier:
    def test_classifies_conventional(self) -> None:
        config = GitlogConfig()
        clf = CommitClassifier(config=config)
        commits = [
            make_commit(subject="feat: new feature"),
            make_commit(subject="fix: null error"),
            make_commit(subject="docs: update readme"),
        ]
        result = clf.classify_all(commits)
        assert result[0].commit_type == CommitType.FEAT
        assert result[1].commit_type == CommitType.FIX
        assert result[2].commit_type == CommitType.DOCS

    def test_misc_kept_without_llm(self) -> None:
        config = GitlogConfig(llm_provider="", model="")
        clf = CommitClassifier(config=config)
        commits = [make_commit(subject="random message with no prefix")]
        result = clf.classify_all(commits)
        assert result[0].commit_type == CommitType.MISC
