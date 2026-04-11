# Release v0.1.0 — LogForge (gitlog)

Summary
- Fix: Make `GitLogParser` robust and test-friendly (supports GitPython/`git` fallback).
- Fix: Make pydantic models backward-compatible with fixtures (`author`/`date` aliases).
- Fix: JSON/Markdown renderers adjusted; all tests now pass.
- Docs: Added 5s demo SVG and social post templates.
- Packaging: Add editable install metadata and distribution artifacts (sdist + wheel).

Artifacts
- dist/logforge-0.1.0.tar.gz
- dist/logforge-0.1.0-py3-none-any.whl

Notes
- The package is named `logforge` for PyPI, but CLI entry point remains `gitlog`.
- To publish to PyPI, use `twine` (credentials required).

Commands to publish

```powershell
# Build (already done locally)
.venv\Scripts\python -m build

# (Optional) Inspect artifacts
ls dist\*

# Upload to PyPI (ensure ~/.pypirc or env vars set)
python -m pip install --upgrade twine
python -m twine upload dist/*
```

Creating a GitHub Release (manual)

1. Create a release branch locally:

```powershell
git checkout -b release/v0.1.0
# (Optional) bump version string in src/gitlog/__init__.py
git add -A
git commit -m "chore(release): prepare v0.1.0"
git push origin release/v0.1.0
```

2. Open a PR on GitHub from `release/v0.1.0` → `main` and use this file as release notes.
3. Once merged, tag and push the tag, then create a GitHub Release or use the web UI.

If you'd like, I can create the branch and commit the bump locally (you'd still need to push) or open a draft release PR text file for easy copy/paste.