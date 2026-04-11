# Configuration Reference

`gitlog` is configured via a `.gitlog.toml` file in the root of your repository.
Run `gitlog init` to generate one interactively.

## Full Configuration Reference

```toml
[gitlog]
# LLM provider: openai | anthropic | ollama | gemini
llm_provider = "openai"

# Model name (provider-specific)
model = "gpt-4o-mini"

# Output language: en | zh-TW | zh-CN | ja
language = "en"

# Output format: markdown | json | html | twitter
format = "markdown"

# Output file path
output_file = "CHANGELOG.md"

# Short description of the project (used as LLM context)
project_description = "A developer tool for generating changelogs."

# Commit messages matching these regex patterns are excluded
exclude_patterns = [
    "^chore\\(deps\\)",
    "^Merge branch",
    "^Merge pull request",
]

# Group commits by scope (e.g. feat(ui): ... -> ui group)
group_by_scope = true

# Max commits shown per category per version
max_commits_per_group = 20

[gitlog.prompts]
# Override default classification system prompt (leave empty to use built-in)
classify_system = ""
# Override default summarization system prompt
summarize_system = ""

[gitlog.github]
# Your GitHub repo slug -- enables clickable PR/commit/issue links
repo = "owner/repo"
```

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GITLOG_MODEL` | Override model via env |
| `GITLOG_LANGUAGE` | Override language via env |
| `GITLOG_FORMAT` | Override format via env |

## Supported LLM Providers

| Provider | Example model string |
|---|---|
| OpenAI | `openai/gpt-4o-mini` |
| Anthropic | `anthropic/claude-3-5-haiku-20241022` |
| Google Gemini | `gemini/gemini-1.5-flash` |
| Local Ollama | `ollama/llama3` |
| Any OpenAI-compatible | `openai/custom-model` |

## GitHub Actions Integration

```yaml
- name: Generate Changelog
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    pip install gitlog
    gitlog generate --since v1.0.0 --format markdown --output CHANGELOG.md
```
