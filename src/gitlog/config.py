"""Configuration management for gitlog using pydantic-settings."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PromptsConfig(BaseSettings):
    """Custom prompt overrides."""

    model_config = SettingsConfigDict(extra="ignore")

    classify_system: str = ""
    summarize_system: str = ""


class GitHubConfig(BaseSettings):
    """GitHub integration settings."""

    model_config = SettingsConfigDict(extra="ignore")

    repo: str = ""  # owner/repo


class GitlogConfig(BaseSettings):
    """Main gitlog configuration.

    Can be loaded from .gitlog.toml or environment variables (GITLOG_ prefix).
    """

    model_config = SettingsConfigDict(
        env_prefix="GITLOG_",
        extra="ignore",
    )

    llm_provider: str = "openai"
    model: str = "gpt-4o-mini"
    language: str = "en"
    format: str = "markdown"
    output_file: str = "CHANGELOG.md"
    project_description: str = ""
    project_name: str = ""
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["^chore\\(deps\\)", "^Merge branch", "^Merge pull request"]
    )
    group_by_scope: bool = True
    max_commits_per_group: int = 20

    prompts: PromptsConfig = Field(default_factory=PromptsConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code."""
        allowed = {"en", "zh-TW", "zh-CN", "ja"}
        if v not in allowed:
            raise ValueError(f"language must be one of {allowed}")
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate output format."""
        allowed = {"markdown", "json", "html", "twitter"}
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v


def load_settings(repo_path: Path | None = None) -> GitlogConfig:
    """Load settings from .gitlog.toml and environment variables.

    Args:
        repo_path: Path to the repository root. Defaults to cwd.

    Returns:
        Populated GitlogConfig instance.
    """
    base = repo_path or Path.cwd()
    toml_path = base / ".gitlog.toml"

    if toml_path.exists():
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore[no-reattr]

        with toml_path.open("rb") as f:
            raw: dict[str, Any] = tomllib.load(f)

        section = raw.get("gitlog", {})
        prompts_data = section.pop("prompts", {})
        github_data = section.pop("github", {})

        return GitlogConfig(
            **section,
            prompts=PromptsConfig(**prompts_data),
            github=GitHubConfig(**github_data),
        )

    return GitlogConfig()


# Alias for backward compat
GitlogSettings = GitlogConfig
