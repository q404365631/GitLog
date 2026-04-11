# Social Distribution Templates

This file contains copy templates you can use to post the project on Hacker News, Reddit, and Twitter/X.

## Hacker News (title + body)

Title:
- LogForge — generate changelogs from git history using rules + LLMs

Body:
- Short description: LogForge (repo: JToSound/LogForge) turns your git history into
  a Keep-a-Changelog formatted `CHANGELOG.md` with a fast rule-based classifier
  and an LLM fallback for edge cases. Works locally or in CI, supports OpenAI,
  Anthropic, and local Ollama models.

- Link: https://github.com/JToSound/LogForge

- Why it might be interesting: It gives maintainer a zero-effort changelog with
  a focus on batch LLM calls (low cost) and a rule-first classifier so small
  projects see useful results immediately.

## Reddit (r/programming / r/python)

Title:
- LogForge — AI + rules to auto-generate CHANGELOG.md from your git commits

Body:
- TL;DR: Run `gitlog generate` and get a polished `CHANGELOG.md`.
- Features: local-first (Ollama), CI-ready, semantic grouping, multilingual.
- Install: `pip install git+https://github.com/JToSound/LogForge.git`
- Demo: include the GIF/SVG in the post (docs/demo.svg)

## Twitter / X (thread starter)

Tweet 1:
- Built LogForge — generate changelogs from git history in one command.

Tweet 2:
- Uses a rule-first classifier (zero API cost) + LLM fallback when needed.

Tweet 3:
- Works locally (Ollama) or with OpenAI/Anthropic. Try: `pip install git+https://github.com/JToSound/LogForge.git` then `gitlog generate`.

Tweet 4:
- Quick demo: attach the demo GIF (docs/demo.svg) — results in <5s on small repos.

---

Use these as a starting point and A/B test variations. If you want, I can prepare a ready-to-post text file for each platform and schedule suggestions.