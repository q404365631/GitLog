# Release draft: v0.1.0 — LogForge (gitlog)

Tag: `v0.1.0`

Short description
-----------------
LogForge (CLI name: `gitlog`) — AI-powered changelog & release-notes generator.

Highlights
----------
- Robust `GitLogParser`: GitPython preferred with `git` subprocess fallback; test-friendly.
- Backwards-compatible pydantic models: accepts legacy fixture shapes (`author`/`date`).
- Renderers fixed: JSON/Markdown/Twitter outputs normalized and stable.
- UX/docs: Added a quick 5s demo (`docs/demo.svg`) and social post templates (`docs/social_templates.md`).
- Packaging: artifacts built (sdist + wheel). CLI remains `gitlog`, package name for PyPI: `logforge`.

Full release notes
------------------
See `RELEASE_NOTES_v0.1.0.md` for full details, changelog, and publish instructions.

Binary artifacts (local)
------------------------
Attach these artifacts to the GitHub Release as assets:

- `dist/logforge-0.1.0.tar.gz`
- `dist/logforge-0.1.0-py3-none-any.whl`

Installation notes
------------------
- Recommended (PyPI once published):

```bash
pip install logforge
```

- Install from GitHub (current recommendation until PyPI release):

```bash
pip install git+https://github.com/JToSound/LogForge.git
```

Usage (quick)
-------------
```bash
gitlog generate
# or preview without writing
gitlog generate --dry-run
# tweet draft
gitlog tweet
```

Publishing to PyPI (maintainer instructions)
--------------------------------------------
Option A — Upload manually (recommended):
1. Ensure artifacts are present in `dist/`.
2. Install twine: `python -m pip install --upgrade twine`.
3. Upload (example with env vars):

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "<PASTE_YOUR_PYPI_TOKEN_HERE>"
python -m twine upload dist/*
```

Option B — Let me upload now: reply with `upload now` and I will run `twine upload dist/*` using the token you provided.

Verification
------------
- After upload, check https://pypi.org/project/logforge/ and ensure the new version `0.1.0` appears.
- Optionally, install from PyPI in a fresh environment and run `gitlog --version` and `gitlog generate` on a small repo.

Draft release body (copy/paste ready)
------------------------------------
Title: v0.1.0 — LogForge

Body:
```
LogForge (gitlog) v0.1.0

This release introduces:
- Robust git parsing with GitPython/subprocess fallback
- Backwards-compatible models and multiple renderer fixes
- Quick animated demo and social templates for easy outreach

Artifacts: attached wheel and sdist (dist/*)

Installation: `pip install logforge` (or `pip install git+https://github.com/JToSound/LogForge.git`)

See full notes in the repository: RELEASE_NOTES_v0.1.0.md
```
