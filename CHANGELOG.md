# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> This changelog is maintained by **gitlog** — the tool itself.

## [Unreleased]

### ✨ Features
- Initial project scaffold with full CLI, LLM classifier, and multi-format renderers
- Two-layer commit classification: rule engine + LLM batch fallback
- Keep-a-Changelog Markdown renderer with multilingual support (en, zh-TW, zh-CN, ja)
- JSON renderer for programmatic consumption
- Self-contained HTML report with dark/light mode and version timeline
- Twitter/X release announcement generator
- `gitlog stats` ASCII bar chart for commit type distribution
- `gitlog init` interactive `.gitlog.toml` setup wizard
- GitHub Actions CI/CD with auto-changelog on release
