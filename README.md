# lsimons-llm

Shared LLM client library for OpenAI-compatible APIs.

## Installation

### As a dependency in other projects

Add to your `pyproject.toml`:

```toml
dependencies = [
    "lsimons-llm @ git+https://github.com/lsimons-bot/lsimons-llm.git",
]

# For async support
dependencies = [
    "lsimons-llm[async] @ git+https://github.com/lsimons-bot/lsimons-llm.git",
]
```

### Local development setup

When developing lsimons-llm alongside dependent projects, use editable installs to see changes immediately:

```bash
# In each dependent project directory (lsimons-bot, quarto4sbp, lsimons-agent)
uv pip install -e ../lsimons-llm
```

This overrides the git dependency with your local copy. Changes to lsimons-llm are available without pushing.

**Projects using this library:**
- [lsimons-bot](https://github.com/lsimons-bot/lsimons-bot-code) - Slack bot (async client)
- [quarto4sbp](https://github.com/lsimons-bot/quarto4sbp) - Quarto document tool (sync client)
- [lsimons-agent](https://github.com/lsimons-bot/lsimons-agent) - AI coding agent (sync client)

## Configuration

Set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | (required) | API key for authentication |
| `LLM_BASE_URL` | `https://litellm.sbp.ai/v1` | API endpoint |
| `LLM_MODEL` | `azure/gpt-4o-mini` | Model name |
| `LLM_MAX_TOKENS` | `4096` | Maximum tokens per request |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature |
| `LLM_TIMEOUT` | `120` | Request timeout (seconds) |
| `LLM_MAX_RETRIES` | `3` | Maximum retry attempts |

## Usage

### Simple usage

```python
from lsimons_llm import chat

response = chat([{"role": "user", "content": "Hello!"}])
print(response)
```

### With client instance

```python
from lsimons_llm import LLMClient, load_config

config = load_config()
with LLMClient(config) as client:
    response = client.chat([
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ])
    print(response)
```

### Async client

```python
from lsimons_llm.async_client import AsyncLLMClient
from lsimons_llm import load_config

config = load_config()
async with AsyncLLMClient(config) as client:
    response = await client.chat([{"role": "user", "content": "Hello!"}])
    print(response)
```

### Configuration override

```python
from lsimons_llm import LLMClient, load_config

# Override via load_config
config = load_config(model="gpt-4", temperature=0.9)

# Or override per-request
client = LLMClient(config)
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4-turbo",
    max_tokens=1000,
)
```

### Tool calling

```python
from lsimons_llm import LLMClient, load_config

config = load_config()
client = LLMClient(config)

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
}]

# Use chat_raw to get full response including tool calls
response = client.chat_raw(
    messages=[{"role": "user", "content": "What's the weather in Amsterdam?"}],
    tools=tools,
)
```

## Development

```bash
# Setup
uv venv && uv sync --all-groups

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run pyright
```

## License

See [LICENSE.md](./LICENSE.md).
