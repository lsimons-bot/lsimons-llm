# Agent Instructions for lsimons-llm

Shared LLM client library for OpenAI-compatible APIs. Provides sync and async clients with unified configuration.

## Quick Reference

- **Setup**: `uv venv && uv sync --all-groups`
- **Test**: `uv run pytest`
- **Lint**: `uv run ruff check . && uv run basedpyright`
- **Format**: `uv run ruff format .`

## Structure

```
lsimons_llm/
├── __init__.py       # Public API exports
├── client.py         # Synchronous LLMClient
├── async_client.py   # Asynchronous AsyncLLMClient
├── config.py         # LLMConfig and load_config()
└── exceptions.py     # LLMError, LLMRequestError, LLMResponseError
```

## Guidelines

**Code quality:**
- Full type annotations (pyright strict: 0 errors)
- 80%+ test coverage
- ruff for linting and formatting

**Design principles:**
- Sync client uses httpx (no external deps beyond httpx)
- Async client uses openai SDK (optional dependency)
- Config via env vars, with argument overrides
- Explicit error types (no silent failures)

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

## Session Completion

Work is NOT complete until `git push` succeeds.

1. **Quality gates** (if code changed):
   ```bash
   uv run pytest
   uv run ruff check . && uv run basedpyright
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

Never stop before pushing. If push fails, resolve and retry.
