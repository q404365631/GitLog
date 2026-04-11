"""Two-layer commit classifier: regex rules + batch LLM fallback."""
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
# Rule-based classification patterns (zero API cost)
# ---------------------------------------------------------------------------

_CC_RULES: list[tuple[re.Pattern[str], CommitType]] = [
    (re.compile(r"^feat(\(.+\))?(!)?:", re.I), CommitType.FEAT),
    (re.compile(r"^fix(\(.+\))?(!)?:", re.I), CommitType.FIX),
    (re.compile(r"^perf(\(.+\))?(!)?:", re.I), CommitType.PERF),
    (re.compile(r"^refactor(\(.+\))?(!)?:", re.I), CommitType.REFACTOR),
    (re.compile(r"^docs?(\(.+\))?(!)?:", re.I), CommitType.DOCS),
    (re.compile(r"^(chore|build|ci)(\(.+\))?(!)?:", re.I), CommitType.CHORE),
    (re.compile(r"^breaking:", re.I), CommitType.BREAKING),
    (re.compile(r"^(revert|test|style)(\(.+\))?(!)?:", re.I), CommitType.MISC),
]

_TYPE_STR_MAP: dict[str, CommitType] = {
    "feat": CommitType.FEAT,
    "fix": CommitType.FIX,
    "perf": CommitType.PERF,
    "refactor": CommitType.REFACTOR,
    "docs": CommitType.DOCS,
    "chore": CommitType.CHORE,
    "breaking": CommitType.BREAKING,
    "misc": CommitType.MISC,
}


def _rule_classify(message: str) -> str:
    """Classify a commit message string via regex rules only.

    Args:
        message: Commit subject or full message.

    Returns:
        CommitType value string (e.g. 'feat', 'fix', 'misc').
    """
    for pattern, commit_type in _CC_RULES:
        if pattern.match(message):
            # Detect breaking via '!' marker
            if "!:" in message.split(":")[0]:
                return CommitType.BREAKING.value
            return commit_type.value
    return CommitType.MISC.value


# Expose as RuleClassifier for any code that imports it by name
class RuleClassifier:
    """Stateless rule-based classifier.

    Args:
        exclude_patterns: Regex strings for commits to skip.
    """

    def __init__(self, exclude_patterns: list[str] | None = None) -> None:
        self._exclude = [re.compile(p) for p in (exclude_patterns or [])]

    def classify(self, message: str) -> str:
        """Return label string for a commit message.

        Args:
            message: Commit subject or message.

        Returns:
            CommitType value string.
        """
        return _rule_classify(message)

    def is_excluded(self, message: str) -> bool:
        """Check if message matches any exclusion pattern.

        Args:
            message: Commit message.

        Returns:
            True if the commit should be excluded.
        """
        return any(p.search(message) for p in self._exclude)


# ---------------------------------------------------------------------------
# Main CommitClassifier (rules + optional LLM batch)
# ---------------------------------------------------------------------------

class CommitClassifier:
    """Classifies commits using rules first, LLM for remainder.

    Args:
        config: GitlogConfig instance.
    """

    _CHUNK = 50  # max commits per LLM call

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config
        self._rule = RuleClassifier(exclude_patterns=config.exclude_patterns)

    def classify_all(self, commits: list[Commit]) -> list[Commit]:
        """Classify all commits, using LLM only for those rules cannot handle.

        Args:
            commits: Raw commit list.

        Returns:
            Commits with commit_type populated.
        """
        ruled: list[Commit] = []
        needs_llm: list[Commit] = []

        for commit in commits:
            label = _rule_classify(commit.subject or commit.message)
            if label != CommitType.MISC.value:
                ruled.append(commit.model_copy(update={"commit_type": CommitType(label)}))
            else:
                needs_llm.append(commit)

        if needs_llm and self._config.llm_provider and self._config.model:
            try:
                needs_llm = self._llm_batch(needs_llm)
            except LLMError:
                pass  # graceful fallback — keep as MISC

        return ruled + needs_llm

    def _llm_batch(self, commits: list[Commit]) -> list[Commit]:
        """Classify commits in batches via LLM.

        Args:
            commits: Commits that rules could not classify.

        Returns:
            Commits with updated commit_type.
        """
        result: list[Commit] = []
        for i in range(0, len(commits), self._CHUNK):
            chunk = commits[i : i + self._CHUNK]
            labels = self._call_llm(chunk)
            for commit, label in zip(chunk, labels):
                ct = _TYPE_STR_MAP.get(label.lower(), CommitType.MISC)
                result.append(commit.model_copy(update={"commit_type": ct}))
        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _call_llm(self, commits: list[Commit]) -> list[str]:
        """Send one LLM request for a chunk of commits.

        Args:
            commits: Chunk to classify.

        Returns:
            List of label strings in input order.

        Raises:
            LLMError: On API failure after retries.
        """
        try:
            import litellm  # type: ignore[import-untyped]
        except ImportError as exc:
            raise LLMError(
                "litellm not installed.",
                hint="pip install litellm",
            ) from exc

        numbered = "\n".join(
            f"{i + 1}. {c.subject or c.message[:120]}"
            for i, c in enumerate(commits)
        )
        system = (
            self._config.prompts.classify_system
            or "You are a changelog classifier. Classify each git commit into one of: "
               "[feat, fix, perf, refactor, docs, chore, breaking, misc]. "
               "Return a JSON array matching input order. No explanation."
        )
        user = (
            f"Project: {self._config.project_description or 'unknown'}\n\n"
            f"Classify these {len(commits)} commits:\n{numbered}\n\n"
            f'RESPONSE FORMAT: ["feat", "fix", ...]'
        )
        try:
            resp = litellm.completion(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0,
            )
            raw = resp.choices[0].message.content or "[]"
            m = re.search(r"\[.*\]", raw, re.DOTALL)
            if not m:
                return [CommitType.MISC.value] * len(commits)
            labels: list[str] = json.loads(m.group())
            while len(labels) < len(commits):
                labels.append(CommitType.MISC.value)
            return labels[: len(commits)]
        except Exception as exc:
            raise LLMError(f"LLM call failed: {exc}") from exc
