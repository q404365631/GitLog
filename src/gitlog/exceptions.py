"""Custom exception hierarchy for gitlog."""
from __future__ import annotations


class GitlogError(Exception):
    """Base exception for all gitlog errors.

    Args:
        message: Human-readable error message.
        hint: Optional fix suggestion shown to the user.
    """

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


class GitError(GitlogError):
    """Raised on git operation failures."""


class LLMError(GitlogError):
    """Raised on LLM API failures."""


class ConfigError(GitlogError):
    """Raised on configuration errors."""
