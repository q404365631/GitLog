# Draft PR: Release v0.1.0

Title: chore(release): v0.1.0

Body:
```
This PR prepares the v0.1.0 release for LogForge (CLI: gitlog).

Highlights:
- Robust GitLogParser supporting GitPython and subprocess fallbacks
- Backwards-compatible pydantic models for test fixtures
- JSON and Markdown renderers fixed for stable output
- Added a quick animated demo (docs/demo.svg) and social templates
- Packaging adjustments and dist artifacts produced

CI / Release
- After merging, build artifacts in `dist/` and upload to PyPI with `twine`.

Notes
- Package name for PyPI: `logforge`
- CLI entry point: `gitlog`
```

Suggested steps (maintainer):

```powershell
git checkout -b release/v0.1.0
# (optional) bump version in src/gitlog/__init__.py
git add src/gitlog/__init__.py
git commit -m "chore(release): bump version to v0.1.0"
git push -u origin release/v0.1.0
# Open PR on GitHub with this body
```

---

If you want, I can prepare the local branch and make the commit here; you'll need to push it (I cannot push to your remote).