"""HTML report renderer using Jinja2 template."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gitlog.core.models import Changelog, CommitType

if TYPE_CHECKING:
    from gitlog.config import GitlogConfig

_BADGE_COLORS: dict[CommitType, str] = {
    CommitType.FEAT:     "#3b82f6",
    CommitType.FIX:      "#ef4444",
    CommitType.BREAKING: "#f97316",
    CommitType.PERF:     "#eab308",
    CommitType.REFACTOR: "#06b6d4",
    CommitType.DOCS:     "#22c55e",
    CommitType.CHORE:    "#6b7280",
    CommitType.MISC:     "#6b7280",
}

_SECTION_LABELS: dict[CommitType, str] = {
    CommitType.BREAKING: "Breaking Changes",
    CommitType.FEAT:     "Features",
    CommitType.FIX:      "Bug Fixes",
    CommitType.PERF:     "Performance",
    CommitType.REFACTOR: "Refactors",
    CommitType.DOCS:     "Documentation",
    CommitType.CHORE:    "Chores",
    CommitType.MISC:     "Miscellaneous",
}

_TYPE_ORDER = [
    CommitType.BREAKING, CommitType.FEAT, CommitType.FIX, CommitType.PERF,
    CommitType.REFACTOR, CommitType.DOCS, CommitType.CHORE, CommitType.MISC,
]


class HtmlRenderer:
    """Render changelog as a self-contained HTML report.

    Args:
        config: GitlogConfig instance.
    """

    def __init__(self, config: "GitlogConfig") -> None:
        self._config = config

    def render(self, changelog: Changelog) -> str:
        """Build full HTML string.

        Args:
            changelog: Structured Changelog.

        Returns:
            Single-file HTML string.
        """
        github_repo = self._config.github.repo
        entries_html = "".join(
            self._render_entry(e, github_repo)
            for e in changelog.entries
            if not e.is_empty()
        )
        project = changelog.project_name or self._config.project_name or "Changelog"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{project} Changelog</title>
<style>
  :root{{
    --bg:#f8f9fa;--surface:#fff;--text:#1a1a2e;--muted:#6c757d;
    --border:#dee2e6;--radius:8px;--accent:#0d6efd;
  }}
  @media(prefers-color-scheme:dark){{
    :root{{--bg:#0f0f14;--surface:#1a1a2e;--text:#e9ecef;--muted:#adb5bd;--border:#2d2d44}}
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:system-ui,sans-serif;background:var(--bg);color:var(--text);padding:2rem 1rem}}
  .container{{max-width:860px;margin:0 auto}}
  h1{{font-size:2rem;margin-bottom:2rem;color:var(--accent)}}
  .entry{{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
          padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
  .entry-header{{display:flex;align-items:center;gap:1rem;margin-bottom:1rem}}
  .version{{font-size:1.25rem;font-weight:700}}
  .date{{color:var(--muted);font-size:.875rem}}
  .section{{margin-top:1rem}}
  .section-title{{font-size:.875rem;font-weight:600;margin-bottom:.5rem;display:flex;align-items:center;gap:.5rem}}
  .badge{{display:inline-block;padding:.15rem .5rem;border-radius:4px;font-size:.75rem;
          color:#fff;font-weight:600}}
  ul{{list-style:none;padding-left:.5rem}}
  li{{padding:.25rem 0;border-bottom:1px solid var(--border);font-size:.9rem}}
  li:last-child{{border-bottom:none}}
  a{{color:var(--accent);text-decoration:none}}
  a:hover{{text-decoration:underline}}
  code{{background:var(--border);padding:.1rem .3rem;border-radius:3px;font-size:.8rem}}
</style>
</head>
<body>
<div class="container">
  <h1>&#128218; {project} Changelog</h1>
  {entries_html}
</div>
</body>
</html>"""

    def _render_entry(self, entry: "object", github_repo: str) -> str:  # type: ignore[override]
        """Render one version block."""
        from gitlog.core.models import ChangelogEntry
        assert isinstance(entry, ChangelogEntry)

        date_html = f'<span class="date">{entry.date}</span>' if entry.date else ""
        sections_html = ""
        for ct in _TYPE_ORDER:
            commits = entry.groups.get(ct, [])
            if not commits:
                continue
            color = _BADGE_COLORS.get(ct, "#6b7280")
            label = _SECTION_LABELS.get(ct, ct.value)
            items = "".join(self._render_commit(c, github_repo) for c in commits)
            sections_html += f"""
            <div class="section">
              <div class="section-title">
                <span class="badge" style="background:{color}">{label}</span>
              </div>
              <ul>{items}</ul>
            </div>"""

        return f"""
        <div class="entry">
          <div class="entry-header">
            <span class="version">{entry.version}</span>
            {date_html}
          </div>
          {sections_html}
        </div>"""

    def _render_commit(self, commit: "object", github_repo: str) -> str:
        """Render one commit as an <li>."""
        import re
        from gitlog.core.models import Commit
        assert isinstance(commit, Commit)
        subject = commit.subject or commit.message.split("\n")[0]
        subject = re.sub(r"^\w+(\(.+\))?!?: ", "", subject)

        sha_html = ""
        if github_repo:
            sha_url = f"https://github.com/{github_repo}/commit/{commit.sha}"
            sha_html = f' <a href="{sha_url}"><code>{commit.short_sha}</code></a>'
        else:
            sha_html = f" <code>{commit.short_sha}</code>"

        pr_html = ""
        if commit.pr_number and github_repo:
            pr_url = f"https://github.com/{github_repo}/pull/{commit.pr_number}"
            pr_html = f' <a href="{pr_url}">(#{commit.pr_number})</a>'
        elif commit.pr_number:
            pr_html = f" (#{commit.pr_number})"

        return f"<li>{subject}{pr_html}{sha_html}</li>"
