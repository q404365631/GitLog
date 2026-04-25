<div align="center">

# LogForge — gitlog

**LogForge — AI-Powered Changelog & Release Notes Generator**

[![CI](https://github.com/JToSound/LogForge/actions/workflows/ci.yml/badge.svg)](https://github.com/JToSound/LogForge/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/JToSound/LogForge/branch/main/graph/badge.svg)](https://codecov.io/gh/JToSound/LogForge)
[![GitHub Releases](https://img.shields.io/github/v/release/JToSound/LogForge)](https://github.com/JToSound/LogForge/releases)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

One command. From git history to a human-readable, structured CHANGELOG.
Supports **multiple languages**, **multiple output formats**, and **any LLM**.

</div>

---

## Quick Start

### 1. Install

```bash
# Recommended: uv (fastest)
uv tool install gitlog

# Or pip
pip install gitlog

# Or install directly from GitHub
pip install git+https://github.com/JToSound/LogForge.git
```

**Requirements:** Python 3.11+ and Git.

### 2. Configure your API key

```bash
# Option A: environment variable (recommended for CI)
export OPENAI_API_KEY="***"

# Option B: .env file in your repo root
echo "OPENAI_API_KEY=***" > .env

# Option C: use a local model (no key needed)
gitlog generate --model ollama/llama3
```

### 3. Generate your first changelog

```bash
cd your-repo
gitlog generate
```

That's it. Your `CHANGELOG.md` is ready. 🎉

> **New to gitlog?** Run `gitlog init` for an interactive setup wizard that creates a `.gitlog.toml` tailored to your project.

---

## 5s Demo

Below is a very short demo that shows `gitlog generate` producing a changelog in under 5 seconds on small repos.

![Quick demo](docs/demo.svg)

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

## Installation Guide

### Prerequisites

Before installing gitlog, make sure you have:

1. **Python 3.11 or higher**
   - Check with: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Git installed and configured**
   - Check with: `git --version`
   - Make sure git is in your PATH

3. **(Optional) API keys for LLM providers**
   - OpenAI: Get from https://platform.openai.com/api-keys
   - Anthropic: Get from https://console.anthropic.com/
   - Ollama: Install locally for free inference

### Installation Methods

#### Method 1: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install gitlog
uv tool install gitlog
```

#### Method 2: Using pip

```bash
# Standard pip installation
pip install gitlog

# Or with user installation (recommended for development)
pip install --user gitlog
```

#### Method 3: Development Installation

```bash
# Clone the repository
git clone https://github.com/JToSound/LogForge.git
cd LogForge

# Install in development mode
pip install -e .

# Or with all dependencies
pip install -e ".[dev]"
```

---

## Configuration Guide

### Basic Configuration

Create a `.gitlog.toml` file in your repository root:

```toml
[gitlog]
llm_provider = "openai"
model = "gpt-4o-mini"
language = "en"
format = "markdown"
output_file = "CHANGELOG.md"
project_description = "A developer tool for generating changelogs from git history"
exclude_patterns = ["^chore\\(deps\\)", "^Merge branch"]
group_by_scope = true
max_commits_per_group = 20

[gitlog.github]
repo = "your-username/your-repo"
```

### Advanced Configuration Examples

#### Example 1: Local Ollama Setup

```toml
[gitlog]
llm_provider = "ollama"
model = "ollama/llama3"
language = "zh-CN"
format = "markdown"
output_file = "CHANGELOG_zh.md"
```

#### Example 2: Multiple Output Formats

```toml
[gitlog]
llm_provider = "openai"
model = "gpt-4o-mini"
language = "en"
format = "json"
output_file = "CHANGELOG.json"

[gitlog]
format = "html"
output_file = "CHANGELOG.html"
```

### Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `llm_provider` | `openai` | LLM provider: `openai`, `anthropic`, `ollama` |
| `model` | `gpt-4o-mini` | Model identifier |
| `language` | `en` | Output language: `en`, `zh-TW`, `zh-CN`, `ja` |
| `format` | `markdown` | Output format: `markdown`, `json`, `html`, `twitter` |
| `output_file` | `CHANGELOG.md` | Output file path |
| `project_description` | `""` | Project context injected into LLM prompts |
| `exclude_patterns` | see default | Regex list of commit messages to skip |
| `group_by_scope` | `true` | Group commits by conventional commit scope |
| `max_commits_per_group` | `20` | Max commits shown per category per version |

---

## Usage Examples

### Basic Commands

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

### Common Workflows

#### CI/CD Integration

```bash
# In GitHub Actions
name: Generate Changelog
run: |
  pip install gitlog
  export OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
  gitlog generate --since ${{ github.ref_name }}
```

#### Custom Commit Filtering

```bash
# Exclude specific types of commits
gitlog generate --exclude-pattern "^test\\(|^docs:"

# Include only feature commits
gitlog generate --include-pattern "^feat:"
```

---

## CI/CD Integration

### GitHub Actions

Add to your release workflow:

```yaml
- name: Generate Changelog
  uses: JToSound/LogForge/.github/workflows/release.yml@main
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

Or use the included `release.yml` which automatically:
1. Builds and publishes to PyPI on tag push
2. Generates the changelog using gitlog itself
3. Creates a GitHub Release with the generated notes

### GitLab CI

```yaml
generate-changelog:
  image: python:3.11
  script:
    - pip install gitlog
    - export OPENAI_API_KEY=$OPENAI_API_KEY
    - gitlog generate --since $CI_COMMIT_TAG
  artifacts:
    paths:
      - CHANGELOG.md
```

---

## Troubleshooting

### Common Issues

#### "Command not found" after installation
```bash
# Check if gitlog is in your PATH
which gitlog

# If using virtual environment, activate it first
source venv/bin/activate
pip install gitlog
```

#### API Key Authentication Failed
```bash
# Verify your API key is set correctly
echo $OPENAI_API_KEY

# Test with a simple command
OPENAI_API_KEY="your-key-here" gitlog generate --dry-run
```

#### Git Not Found
```bash
# Install Git if missing
# On Ubuntu/Debian: sudo apt-get install git
# On macOS: brew install git
# On Windows: Download from git-scm.com
```

#### Permission Denied Errors
```bash
# Use --user flag for local installation
pip install --user gitlog

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install gitlog
```

---

## Supported LLM Providers

| Provider | Model Example | Env Var |
|----------|---------------|---------|
| OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `claude-3-5-haiku-20241022` | `ANTHROPIC_API_KEY` |
| Ollama (local) | `ollama/llama3` | *(none required)* |
| Gemini | `gemini/gemini-1.5-flash` | `GEMINI_API_KEY` |

---

## License

MIT © gitlog contributors