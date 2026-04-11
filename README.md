<div align="center">

<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="14" fill="#01696f"/>
  <rect x="14" y="18" width="28" height="4" rx="2" fill="white"/>
  <rect x="14" y="26" width="36" height="4" rx="2" fill="white" opacity="0.7"/>
  <rect x="14" y="34" width="22" height="4" rx="2" fill="white" opacity="0.5"/>
  <circle cx="48" cy="42" r="10" fill="#fdab43"/>
  <path d="M44 42h8M48 38v8" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
</svg>

# gitlog

**AI-Powered Changelog & Release Notes Generator**

[![CI](https://github.com/JToSound/LogForge/actions/workflows/ci.yml/badge.svg)](https://github.com/JToSound/LogForge/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/JToSound/LogForge/branch/main/graph/badge.svg)](https://codecov.io/gh/JToSound/LogForge)
[![PyPI](https://img.shields.io/pypi/v/gitlog.svg)](https://pypi.org/project/gitlog/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

One command. From git history to a human-readable, structured CHANGELOG.  
Supports **multiple languages**, **multiple output formats**, and **any LLM**.

</div>

---

## Quick Start

```bash
pip install gitlog
cd your-repo
export OPENAI_API_KEY=sk-...
gitlog generate
```

That's it. Your `CHANGELOG.md` is ready. 🎉

---

## Features

- 🤖 **Two-layer classification** — rule engine (zero API cost) + LLM batch fallback
- 🌍 **Multilingual output** — English, Traditional Chinese, Simplified Chinese, Japanese
- 📄 **Multiple formats** — Markdown (Keep-a-Changelog), JSON, HTML, Twitter drafts
- 🔗 **GitHub integration** — auto-generates PR/issue/commit links
- ⚡ **Batch LLM calls** — never call the LLM in a loop; respects token budgets
- 🔄 **Fallback chain** — LLM failure → rule engine, never interrupts the flow
- 🧩 **CI/CD ready** — GitHub Actions workflow included out of the box
- 🏠 **Local inference** — Ollama support for fully private generation

---

## Installation

```bash
# Recommended: with uv
uv tool install gitlog

# Or pip
pip install gitlog
```

**Requirements:** Python 3.11+, Git

---

## Usage

```bash
# Generate full CHANGELOG
gitlog generate

# From a specific version
gitlog generate --since v1.2.0

# HTML report
gitlog generate --format html

# Traditional Chinese output
gitlog generate --lang zh-TW

# Use a local Ollama model (no API key needed)
gitlog generate --model ollama/llama3

# Preview in terminal without writing a file
gitlog generate --dry-run

# Compare two versions
gitlog diff v1.0.0 v1.1.0

# Generate Twitter/X announcement
gitlog tweet

# ASCII commit statistics
gitlog stats

# Interactive setup
gitlog init
```

---

## Configuration

Create a `.gitlog.toml` in your repo root (or run `gitlog init`):

```toml
[gitlog]
llm_provider = "openai"
model = "gpt-4o-mini"
language = "en"
format = "markdown"
output_file = "CHANGELOG.md"
project_description = "A developer tool for..."
exclude_patterns = ["^chore\\(deps\\)", "^Merge branch"]
group_by_scope = true
max_commits_per_group = 20

[gitlog.github]
repo = "owner/repo"
```

### Full Configuration Parameters

| Parameter | Default | Description |
|---|---|---|
| `llm_provider` | `openai` | LLM provider: `openai`, `anthropic`, `ollama`, `gemini` |
| `model` | `gpt-4o-mini` | Model name |
| `language` | `en` | Output language: `en`, `zh-TW`, `zh-CN`, `ja` |
| `format` | `markdown` | Output: `markdown`, `json`, `html`, `twitter` |
| `output_file` | `CHANGELOG.md` | Output file path |
| `project_description` | `""` | Project context for LLM |
| `exclude_patterns` | `[...]` | Regex patterns to exclude |
| `group_by_scope` | `true` | Group by commit scope |
| `max_commits_per_group` | `20` | Max entries per section |
| `github.repo` | `""` | `owner/repo` for link generation |

See [docs/configuration.md](docs/configuration.md) for the full reference.

---

## GitHub Actions Integration

Add to your release workflow:

```yaml
- name: Generate Changelog
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    pip install gitlog
    gitlog generate --since ${{ github.event.release.tag_name }} \
      --format markdown --output CHANGELOG.md
```

The included [`.github/workflows/release.yml`](.github/workflows/release.yml) does this automatically on every version tag push.

---

## Supported LLM Providers

| Provider | Example model string |
|---|---|
| OpenAI | `gpt-4o-mini`, `gpt-4o` |
| Anthropic | `anthropic/claude-3-haiku-20240307` |
| Ollama (local) | `ollama/llama3`, `ollama/mistral` |
| Google Gemini | `gemini/gemini-1.5-flash` |

---

## Contributing

```bash
git clone https://github.com/JToSound/LogForge.git
cd LogForge
uv sync --extra dev
uv run pytest
```

PRs welcome! Please run `ruff check` and `mypy src/gitlog` before submitting.

---

## License

MIT — see [LICENSE](LICENSE).
