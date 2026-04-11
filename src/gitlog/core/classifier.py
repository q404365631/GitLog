"""Commit classification engine with rule-based and LLM-powered layers."""
from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_exponential

from gitlog.core.models import Commit, CommitType
from gitlog.exceptions import LLMError

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig

# ---------------------------------------------------------------------------
# Regex patterns for Conventional Commits
# ---------------------------------------------------------------------------
_CC_PATTERN = re.compile(
    r"^(?P<type>feat|fix|perf|refactor|docs|style|test|chore|ci|build|revert)"
    r"(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<desc>.+)$",
    re.IGNORECASE,
)
_BREAKING_FOOTER = re.compile(r"BREAKING[- ]CHANGE:", re.IGNORECASE)

_TYPE_MAP: dict[str, CommitType] = {
    "feat": CommitType.FEAT,
    "fix": CommitType.FIX,
    "perf": CommitType.PERF,
    "refactor": CommitType.REFACTOR,
    "docs": CommitType.DOCS,
    "style": CommitType.CHORE,
    "test": CommitType.CHORE,
    "chore": CommitType.CHORE,
    "ci": CommitType.CHORE,
    "build": CommitType.CHORE,
    "revert": CommitType.FIX,
}


class RuleBasedClassifier:
    """Layer-1: zero-cost rule-engine classifier."""

    def classify(self, commit: Commit) -> CommitType | None:
        """Return CommitType if the commit matches a Conventional Commits pattern.

        Args:
            commit: The commit to classify.

        Returns:
            CommitType if matched, otherwise None.
        """
        msg = commit.message.strip()

        # BREAKING CHANGE footer takes precedence
        full_text = msg + "\n" + (commit.body or "")
        if _BREAKING_FOOTER.search(full_text):
            return CommitType.BREAKING

        m = _CC_PATTERN.match(msg)
        if m:
            if m.group("breaking"):
                return CommitType.BREAKING
            return _TYPE_MAP.get(m.group("type").lower(), CommitType.MISC)

        return None


class LLMClassifier:
    """Layer-2: batched LLM classifier for non-conventional commits."""

    _CHUNK_SIZE = 40  # max commits per LLM request

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_llm(self, messages: list[dict]) -> str:
        """Send a single batched classification request to the LLM.

        Args:
            messages: Chat messages formatted for the LLM API.

        Returns:
            Raw string response from the model.

        Raises:
            LLMError: When the provider call fails after retries.
        """
        try:
            import litellm  # type: ignore[import]

            response = litellm.completion(
                model=self._config.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover
            raise LLMError(f"LLM call failed: {exc}") from exc

    def classify_batch(self, commits: list[Commit]) -> list[CommitType]:
        """Classify a list of commits using the LLM in batches.

        Args:
            commits: Commits that could not be classified by the rule engine.

        Returns:
            List of CommitType values in the same order as the input.
        """
        results: list[CommitType] = []
        for i in range(0, len(commits), self._CHUNK_SIZE):
            chunk = commits[i : i + self._CHUNK_SIZE]
            results.extend(self._classify_chunk(chunk))
        return results

    def _classify_chunk(self, commits: list[Commit]) -> list[CommitType]:
        """Classify a single chunk of commits."""
        numbered = "\n".join(
            f"{idx + 1}. {c.message[:200]}" for idx, c in enumerate(commits)
        )
        system_prompt = (
            "You are a changelog classifier. "
            "Classify each git commit into EXACTLY one of: "
            "feat, fix, perf, refactor, docs, chore, breaking.\n"
            "Return a JSON object with key 'types' containing an array matching the input order.\n"
            "Be concise. Do not explain."
        )
        if self._config.project_description:
            system_prompt += f"\nProject context: {self._config.project_description}"

        user_prompt = (
            f"Classify these {len(commits)} commits:\n{numbered}\n\n"
            'RESPONSE FORMAT: {"types": ["feat", "fix", ...]}'
        )

        try:
            raw = self._call_llm(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            data = json.loads(raw)
            types_raw: list[str] = data.get("types", [])
            mapping = {
                "feat": CommitType.FEAT,
                "fix": CommitType.FIX,
                "perf": CommitType.PERF,
                "refactor": CommitType.REFACTOR,
                "docs": CommitType.DOCS,
                "chore": CommitType.CHORE,
                "breaking": CommitType.BREAKING,
            }
            return [
                mapping.get(t.lower(), CommitType.MISC)
                for t in types_raw[: len(commits)]
            ]
        except Exception:  # noqa: BLE001 – fallback, never crash
            return [CommitType.MISC] * len(commits)


class CommitClassifier:
    """Orchestrates rule-based (Layer 1) + LLM (Layer 2) classification."""

    def __init__(self, config: "GitlogConfig") -> None:
        self._rule = RuleBasedClassifier()
        self._llm = LLMClassifier(config)
        self._use_llm = bool(config.llm_provider)

    def classify_all(self, commits: list[Commit]) -> list[Commit]:
        """Classify a list of commits in-place, returning annotated commits.

        Args:
            commits: Raw commits to classify.

        Returns:
            The same commits with `commit_type` populated.
        """
        unclassified_idx: list[int] = []
        unclassified: list[Commit] = []

        for idx, commit in enumerate(commits):
            ct = self._rule.classify(commit)
            if ct is not None:
                commits[idx] = commit.model_copy(update={"commit_type": ct})
            else:
                unclassified_idx.append(idx)
                unclassified.append(commit)

        if unclassified and self._use_llm:
            llm_types = self._llm.classify_batch(unclassified)
            for idx, ct in zip(unclassified_idx, llm_types):
                commits[idx] = commits[idx].model_copy(update={"commit_type": ct})
        else:
            for idx in unclassified_idx:
                commits[idx] = commits[idx].model_copy(
                    update={"commit_type": CommitType.MISC}
                )

        return commits
