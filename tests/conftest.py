"""Shared pytest fixtures."""
from __future__ import annotations

import pytest

from gitlog.config import GitlogConfig
from tests.fixtures.sample_commits import ALL_COMMITS, CONVENTIONAL_COMMITS


@pytest.fixture
def default_config() -> GitlogConfig:
    """Return a GitlogConfig with no LLM provider (rule-only mode)."""
    return GitlogConfig(llm_provider="", model="")


@pytest.fixture
def openai_config() -> GitlogConfig:
    """Return a GitlogConfig pointing at OpenAI gpt-4o-mini."""
    return GitlogConfig(llm_provider="openai", model="gpt-4o-mini")


@pytest.fixture
def sample_conventional_commits():
    return list(CONVENTIONAL_COMMITS)


@pytest.fixture
def sample_all_commits():
    return list(ALL_COMMITS)
