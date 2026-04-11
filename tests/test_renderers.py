"""Tests for all renderers."""
from __future__ import annotations

import json

from gitlog.config import GitlogConfig
from gitlog.core.models import Changelog, ChangelogEntry, CommitType
from gitlog.renderers.html import HtmlRenderer
from gitlog.renderers.json import JsonRenderer
from gitlog.renderers.markdown import MarkdownRenderer
from gitlog.renderers.twitter import TwitterRenderer
from tests.conftest import make_commit, make_entry


def _config(**kw: object) -> GitlogConfig:
    return GitlogConfig(**kw)  # type: ignore[arg-type]


class TestMarkdownRenderer:
    def test_output_contains_header(self) -> None:
        config = _config()
        r = MarkdownRenderer(config=config)
        cl = Changelog(entries=[make_entry()])
        out = r.render(cl)
        assert "# Changelog" in out

    def test_feat_section_present(self) -> None:
        config = _config()
        r = MarkdownRenderer(config=config)
        entry = make_entry()
        cl = Changelog(entries=[entry])
        out = r.render(cl)
        assert "Features" in out

    def test_github_link_injected(self) -> None:
        from gitlog.config import GitHubConfig
        config = _config()
        config.github = GitHubConfig(repo="owner/repo")
        r = MarkdownRenderer(config=config)
        commit = make_commit(subject="feat: new feature", sha="a" * 40, short_sha="aaaaaaa", pr_number=42)
        entry = ChangelogEntry(
            version="v1.0.0",
            groups={CommitType.FEAT: [commit]},
        )
        out = r.render(Changelog(entries=[entry]))
        assert "github.com/owner/repo" in out
        assert "#42" in out


class TestJsonRenderer:
    def test_valid_json(self) -> None:
        config = _config()
        r = JsonRenderer(config=config)
        cl = Changelog(entries=[make_entry()])
        out = r.render(cl)
        data = json.loads(out)
        assert "entries" in data

    def test_entry_structure(self) -> None:
        config = _config()
        r = JsonRenderer(config=config)
        cl = Changelog(entries=[make_entry()])
        data = json.loads(r.render(cl))
        entry = data["entries"][0]
        assert "version" in entry
        assert "groups" in entry


class TestHtmlRenderer:
    def test_output_is_html(self) -> None:
        config = _config()
        r = HtmlRenderer(config=config)
        cl = Changelog(entries=[make_entry()])
        out = r.render(cl)
        assert "<!DOCTYPE html>" in out
        assert "<body" in out

    def test_dark_mode_css(self) -> None:
        config = _config()
        r = HtmlRenderer(config=config)
        out = r.render(Changelog(entries=[make_entry()]))
        assert "prefers-color-scheme" in out


class TestTwitterRenderer:
    def test_contains_rocket(self) -> None:
        config = _config()
        r = TwitterRenderer(config=config)
        entry = make_entry()
        out = r.render(entry)
        assert "\U0001f680" in out

    def test_feature_count_shown(self) -> None:
        config = _config()
        r = TwitterRenderer(config=config)
        entry = make_entry()
        out = r.render(entry)
        assert "feature" in out.lower()
