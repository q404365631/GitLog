"""JSON renderer for programmatic consumption."""
from __future__ import annotations

import json

from gitlog.core.models import Changelog


class JsonRenderer:
    """Renders a Changelog to a JSON string."""

    def render(self, changelog: Changelog) -> str:
        """Render a Changelog to a pretty-printed JSON string.

        Args:
            changelog: The Changelog to render.

        Returns:
            JSON-formatted string.
        """
        data = {
            "entries": [
                {
                    "version": entry.version,
                    "date": entry.date,
                    "groups": {
                        ct.value: [
                            {
                                "sha": c.sha,
                                "message": c.message,
                                "author": c.author,
                                "date": c.date,
                                "scope": c.scope,
                                "breaking": c.breaking,
                                "issues": c.issue_refs,
                                "prs": c.pr_refs,
                            }
                            for c in commits
                        ]
                        for ct, commits in entry.groups.items()
                    },
                }
                for entry in changelog.entries
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
