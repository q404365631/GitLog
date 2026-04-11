# Configuration Reference

`gitlog` can be configured via a `.gitlog.toml` file in your repository root,
or via environment variables (prefixed `GITLOG_`).

Run `gitlog init` for an interactive setup wizard.

---

## Full `.gitlog.toml` Reference

```toml
[gitlog]
# LLM provider identifier
llm_provider = "openai"          # openai | anthropic | ollama | gemini

# Model name (provider-specific)
model = "gpt-4o-mini"

# Output language
language = "en"                  # en | zh-TW | zh-CN | ja

# Default output format
format = "markdown"              # markdown | json | html | twitter

# Output file path (relative to repo root)
output_file = "CHANGELOG.md"

# Short project description — injected into LLM context for better results
project_description = "A developer tool for..."

# Regex patterns to exclude commits (applied to subject line)
exclude_patterns = [
    "^chore\\(deps\\)",
    "^Merge branch",
    "^Merge pull request",
]

# Group entries by commit scope (e.g. feat(auth): → grouped under 'auth')
group_by_scope = true

# Maximum commits rendered per category per version
max_commits_per_group = 20

# Project name shown in changelog header (defaults to repo directory name)
project_name = ""


[gitlog.prompts]
# Override the default classification system prompt
classify_system = ""

# Override the default summarize/polish system prompt
summarize_system = ""


[gitlog.github]
# GitHub repository in owner/repo format
# Enables auto-generation of commit hash links, PR links, and issue links
repo = "owner/repo"
```

---

## Environment Variables

All settings can be overridden via environment variables:

| Variable | Equivalent setting |
|---|---|
| `GITLOG_LLM_PROVIDER` | `llm_provider` |
| `GITLOG_MODEL` | `model` |
| `GITLOG_LANGUAGE` | `language` |
| `GITLOG_FORMAT` | `format` |
| `GITLOG_OUTPUT_FILE` | `output_file` |
| `GITLOG_PROJECT_DESCRIPTION` | `project_description` |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |

---

## Precedence

CLI flags > environment variables > `.gitlog.toml` > built-in defaults.
