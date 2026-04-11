# Configuration Reference

`gitlog` is configured via a `.gitlog.toml` file in the root of your repository,
or via environment variables prefixed with `GITLOG_`.

Run `gitlog init` for an interactive setup wizard.

---

## Full Example

```toml
[gitlog]
llm_provider = "openai"
model = "gpt-4o-mini"
language = "en"
format = "markdown"
output_file = "CHANGELOG.md"
project_description = "A developer tool that automates changelog generation."
exclude_patterns = [
  "^chore\\(deps\\)",
  "^Merge branch",
  "^Merge pull request",
]
group_by_scope = true
max_commits_per_group = 20

[gitlog.prompts]
classify_system = ""  # override the default classify system prompt
summarize_system = ""  # override the default summarize system prompt

[gitlog.github]
repo = "owner/repo"  # enables clickable PR/issue/commit links
```

---

## Parameters

### `[gitlog]`

| Key | Type | Default | Description |
|---|---|---|---|
| `llm_provider` | string | `"openai"` | LLM backend. One of `openai`, `anthropic`, `ollama`. |
| `model` | string | `"gpt-4o-mini"` | Model name passed to litellm. |
| `language` | string | `"en"` | Output language. One of `en`, `zh-TW`, `zh-CN`, `ja`. |
| `format` | string | `"markdown"` | Output format. One of `markdown`, `json`, `html`, `twitter`. |
| `output_file` | string | `"CHANGELOG.md"` | Path to write the changelog. |
| `project_description` | string | `""` | Injected into LLM context for better classification. |
| `exclude_patterns` | list[string] | see default | Regex patterns — matching commits are skipped. |
| `group_by_scope` | bool | `true` | Sub-group commits within a category by their scope. |
| `max_commits_per_group` | int | `20` | Truncate large groups to this count. |

### `[gitlog.prompts]`

| Key | Default | Description |
|---|---|---|
| `classify_system` | `""` | Override the system prompt for the classifier LLM call. |
| `summarize_system` | `""` | Override the system prompt for the summarization LLM call. |

### `[gitlog.github]`

| Key | Default | Description |
|---|---|---|
| `repo` | `""` | `owner/repo` slug. Enables hyperlinks in Markdown and HTML output. |

---

## Environment Variables

Every setting can also be provided as an environment variable:

```bash
export GITLOG_MODEL=claude-3-5-haiku-20241022
export GITLOG_LANGUAGE=zh-TW
export GITLOG_FORMAT=html
```

Environment variables take precedence over `.gitlog.toml`.

---

## Prompt Templates

Prompt templates live in `src/gitlog/templates/prompts/` as TOML files.
You can override them project-wide via `[gitlog.prompts]` in your config.
